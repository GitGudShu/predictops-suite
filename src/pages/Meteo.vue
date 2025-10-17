<template>
  <q-page>
    <BreakingNews :page="location.path.replace('/', '')" height="80px" font-size="clamp(0.75rem, 1.75vw, 2rem)">
    </BreakingNews>

    <div class="cards-container">
      <Card v-if="!loading" icon="sunny_snowing" header-text="Indicateurs météo">
        <template #body>

          <Map click satellite-toggle type="weather" geometries="hexagones" controls horizon-dropdown legend
            opacity-slider />
        </template>
      </Card>
      <div class="sub-container" v-if="!loading">
        <Card icon="warning" header-text="Vigilances météo" style="flex: 1 0 min-content">
          <template #body>
            <div class="full-height relative-position flex flex-center" v-if="!loading && alertsData.length > 0">
              <VueApexCharts v-if="!loading" width="100%" height="100%" type="rangeBar" :options="alertsChartOptions"
                :series="toRaw(alertsChartOptions.series)" :style="{ flex: 1 }">
              </VueApexCharts>
              <div v-if="loading" class="absolute-full flex flex-center">
                <q-spinner-tail size="100px" color="secondary" />
              </div>
            </div>

            <div class="alerts-container" v-if="alertsData.length === 0">
              <AlertCard :alert-level="0" alert-title="Rien à signaler">
                <template #alert-body>
                  <div class="alert-body">
                    Aucune vigilance météo n’a été annoncée dans les prochaines 24 heures
                  </div>
                </template>
              </AlertCard>
            </div>
          </template>
        </Card>
        <Card icon="cloud" header-text="Informations météo" style="flex: 1 0 max-content">
          <template #body>

            <div class="weather-info">
              <!-- Sunrise -->
              <div class="weather-card">
                <i class="fa-solid fa-sun"></i>
                <div>
                  <p class="weather-indicator">Lever du soleil</p>
                  <p class="weather-value">{{ weatherData.sunrise }}</p>
                </div>
              </div>

              <!-- Sunset -->
              <div class="weather-card">
                <i class="fa-solid fa-moon"></i>
                <div>
                  <p class="weather-indicator">Coucher du soleil</p>
                  <p class="weather-value">{{ weatherData.sunset }}</p>
                </div>
              </div>

              <!-- Pressure -->
              <div class="weather-card">
                <i class="fa-solid fa-gauge-high"></i>
                <div>
                  <p class="weather-indicator">Pression</p>
                  <p class="weather-value">{{ weatherData.pressure }} hPa</p>
                </div>
              </div>

              <!-- Humidity -->
              <div class="weather-card">
                <i class="fa-solid fa-droplet"></i>
                <div>
                  <p class="weather-indicator">Humidité</p>
                  <p class="weather-value">{{ weatherData.humidity }}%</p>
                </div>
              </div>

              <!-- Temperature -->
              <div class="weather-card temperature-card">
                <img class="weather-icon" :src="getIconUrl(weatherData.icon)" alt="Weather Icon">
                <p class="current-temp">{{ weatherData.current_temp }}°</p>
                <div class="min-max-temp">
                  <p>Min: <span class="weather-value">{{ weatherData.temp_min }}°</span></p>
                  <p>Max: <span class="weather-value">{{ weatherData.temp_max }}°</span></p>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed, toRaw } from "vue";
import Card from 'src/components/Card.vue';
import BreakingNews from 'src/components/BreakingNews.vue';
import VueApexCharts from "vue3-apexcharts";
import Map from "src/components/Map.vue";
import { notifyUser } from "src/utils/notifyUser";
import { api } from "src/boot/axios";
import { createAlertsChartOptions } from "src/utils/rangeBarsUtils";
import AlertCard from "src/components/AlertCard.vue";
import { useRoute } from 'vue-router'

const location = useRoute();

const loading = ref(true)
const dpt = computed(() => {
  return localStorage.getItem("dpt") || location.params.dpt
})

const subDpt = ref()
const subDpts = ref([])
const weatherData = ref()
const alertsData = ref()

const alertsChartOptions = ref({

})

const fetchData = async () => {
  try {
    const weatherDataResponse = await api.get(`/data/weather?dpt=${dpt.value}&sub-dpt=${subDpt.value}`)
    weatherData.value = weatherDataResponse.data[0]
    const alertsDataReponse = await api.get(`/data/weather-alerts?dpt=${dpt.value}&sub-dpt=${subDpt.value}`)
    alertsData.value = alertsDataReponse.data
    alertsChartOptions.value = createAlertsChartOptions(alertsData.value)
    loading.value = false
  } catch (e) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des données.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false
  }
}

function getIconUrl(iconCode) {
  return `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
}

const onSubDptSelected = async (selected) => {
  subDpt.value = selected
  await fetchData()
}

onMounted(async () => {
  try {
    const subDptsResponse = await api.get(`/data/radioitems?page=var-exp-${dpt.value}`)
    subDpts.value = subDptsResponse.data["radioitems-meteo"]
    subDpt.value = subDpts.value[0]
    await fetchData()
  }
  catch (e) {
    const subDptsResponse = await api.get(`/data/radioitems?page=var-exp-${dpt.value}`)
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des départements.", color: "red", position: "bottom", timeout: 2500 })
  }
});


</script>

<style scoped>
.cards-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-wrap: wrap;
  flex: 1;
  gap: 1em;
}

.sub-container {
  display: flex;
  flex-direction: column;
  flex: 1 0 40%;
  align-items: center;
  gap: 1em;
}

.alerts-container {
  max-height: 200px;
  overflow-y: auto;
  display: flex;
  flex-wrap: wrap;
}

.alert-body {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.weather-info {
  color: black;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-gap: 1rem;
  padding: 1em;
  flex: 1;
}

.weather-card {
  background: white;
  border-radius: 10px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  font-size: 1.5em;
  padding: 0.5em;
  gap: 1rem;
  filter: drop-shadow(0 0 2px hsl(220, 100%, 15%));
}

.weather-card div {
  flex: 1;
  text-align: center;
}

.weather-indicator {
  font-size: 0.75em;
}

.weather-value {
  font-weight: bold;
  margin: 0;
}

.weather-card i {
  font-size: 1.5em;
}

.temperature-card {
  grid-column: 3;
  grid-row: 1 / span 2;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.weather-icon {
  width: 100px;
  height: auto;
  filter: drop-shadow(0 0 8px hsl(220, 100%, 15%));
}

.current-temp {
  font-size: 2rem;
  font-weight: bold;
}

.min-max-temp p {
  font-size: 1rem;
  margin: 0;
}

@media(max-width: 768px) {
  .weather-info {
    grid-template-columns: repeat(2, 1fr);
  }

  .temperature-card {
    grid-column: 1 / span 2;
    /* Take full width on smaller screens */
    grid-row: auto;
  }
}

@media(max-width: 480px) {
  .weather-info {
    grid-template-columns: 1fr;
    /* Stack all cards on very small screens */
  }

  .weather-card,
  .temperature-card {
    grid-column: auto;
    grid-row: auto;
  }

  .current-temp {
    font-size: 1.5rem;
  }

  .min-max-temp p {
    font-size: 0.8rem;
  }

  .weather-icon {
    width: 40px;
    /* Smaller icon for very small screens */
  }
}
</style>
