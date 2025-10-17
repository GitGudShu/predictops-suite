<template>
  <q-page>
    <BreakingNews :page="location.path.replace('/', '')" height="80px" font-size="clamp(0.75rem, 1.75vw, 2rem)">
    </BreakingNews>

    <div class="cards-container">

      <Card v-if="hasAirQuality" icon="masks" header-text-size="fs-md" header-text="Qualité de l'air">
        <template #body>
          <Map hover contour type="air" geometries="hexagones" />
        </template>
      </Card>

      <Card v-if="hasEpidemics" icon="coronavirus" header-text-size="fs-md" header-text="Épidémies">
        <template #body>
          <div class="card-body row full-height relative-position">

            <div v-if="loading" class="absolute-full flex flex-center">
              <q-spinner-tail size="100px" color="secondary" />
            </div>
            <highcharts :options="epidemicsChartOptions" v-if="!loading" />

          </div>
        </template>
      </Card>
    </div>

  </q-page>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from "vue"
import BreakingNews from 'src/components/BreakingNews.vue';
import Card from 'src/components/Card.vue';
import Table from 'src/components/Table.vue';
import { notifyUser } from "src/utils/notifyUser";
import { formatEpidemics } from "src/utils/areasplineUtils"
import { api } from 'src/boot/axios';
import Map from "src/components/Map.vue";
import { useRoute } from 'vue-router'
const location = useRoute();

const dpt = computed(() => {
  return localStorage.getItem("dpt") || location.params.dpt
})
const loading = ref(true)

const incidenceNamesMap = {
  'grippe_inc': 'Grippe',
  'diarrhee_inc': 'Diarrhée',
  'varicelle_inc': 'Varicelle',
  'ira_inc': 'Infection Respiratoire Aiguë',
}

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}
let refreshInterval;


const hasEpidemics = ref()
const hasAirQuality = ref()

const config = ref({})

const epidemicsData = ref()
const epidemicsChartOptions = ref({
  chart: {
    type: 'spline',  // This is crucial for smooth curves
    // height: "500"
  },
  title: {
    text: ''
  },
  xAxis: {
    type: 'datetime'
  },
  yAxis: {
    title: {
      text: "Taux d'incidence"
    }
  },
  legend: {
    enabled: true,
    labelFormatter: function () {
      return incidenceNamesMap[this.name];
    }
  },
  plotOptions: {
    spline: {  // Apply specifically to spline series
      turboThreshold: 0,
      threshold: 0,
      marker: {
        enabled: false
      },
      lineWidth: 2,
      connectNulls: true,
      animation: {
        duration: 1500
      },
      // These are important for smoothing
      smoothing: 1.3,  // Higher value = smoother curve (try values between 0.7-1.5)
      // The number of points used for smoothing
      pointStart: 0,
      pointInterval: 1
    }
  },

});

const fetchData = async () => {
  loading.value = true;
  try {
    const configResponse = await api.get(`/data/config?dpt=${dpt.value}`)
    config.value = configResponse.data[0]


    /* QUALITE D'AIR */
    if (config.value.has.air) {
      hasAirQuality.value = true
    }

    /* EPIDEMIES */
    if (config.value.has.epidemies) {
      hasEpidemics.value = true
      const epidemicsResponse = await api.get(`/data/epidemics?dpt=${dpt.value}`)
      epidemicsData.value = epidemicsResponse.data
      epidemicsChartOptions.value.series = formatEpidemics(epidemicsData.value);
    }

  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des données.", color: "red", position: "bottom", timeout: 2500 })
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchData()
  clearInterval(refreshInterval)
  refreshInterval = setInterval(() => {
    fetchData()
  }, 75000)

})

onUnmounted(() => {
  clearInterval(refreshInterval);
});

</script>

<style scoped>
.cards-container {
  width: 100%;
  height: 100%;
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
}

.chart-container {
  display: grid;
  place-items: center;
}

.reliability-legend {
  font-weight: bold;
  font-size: 14px;
  display: flex;
  width: 100%;
  align-items: center;
  gap: 5px;
  padding: 5px;
  color: black;
}

.card-body>div {
  border-radius: 15px;
  flex: 1;
  min-height: 500px;
}
</style>
