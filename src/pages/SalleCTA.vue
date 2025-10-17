<template>
  <q-page>
    <BreakingNews :page="page" height="10vh" font-size="clamp(0.75rem, 1.75vw, 2rem)" :uuid="uuid"
      :style="{ width: '100%', margin: '0 auto' }" v-if="!excludedNewsPages.includes(page) && dpt != '01'">
    </BreakingNews>
    <div class="cards-container" v-if="page == 'synthese'">
      <Card icon="call" header-text="Prévisions du nombre d'appels (tranches de 3h)" class="calls-card"
        v-if="dpt != '01'">
        <template #body>
          <div class="full-height flex flex-center" v-if="loading">
            <q-spinner-tail size="100px" color="secondary" />
          </div>
          <highcharts :options="callsChartOptions" v-if="!loading" />
          <Legend :dpt-bounds="bounds" data-object="Horloge des appels" details="Nombre d'opérateurs" icon-size="md"
            v-if="!loading" />
        </template>
      </Card>
      <Card icon="mdi-binoculars" :header-text="'Prévisions interventions' + ' (' + getInterTitle(geometries) + ')'">
        <template #body>
          <Map legend alerts hover click type="interventions_predictions" :geometries="geometries" :uuid="uuid"
            :key="geometries" :zoom-duration="0" />
        </template>
      </Card>
    </div>
    <div class="cdc-container" v-if="page == 'chaine-de-commandement'">
      <div v-for="(card, index) in cards" :key="card.id" class="cdc-card" :class="{ 'special-card': card.special }">
        <!-- Special Card -->
        <template v-if="card.special">
          <div class="special-card-content">
            <img :src="card.image" alt="Logo" class="special-card-image" />
            <fit-text class="special-card-text" :text="card.title" :min-font-size="16" :step="1" :grow="true" />
          </div>
        </template>

        <!-- Regular Card -->
        <template v-else>
          <div class="cdc-card-header drag-handle"
            :style="{ 'background-color': card.editing ? 'transparent' : card.color || '#181632', 'color': determineTextColor(card.color || '#fff') }">
            <div class="coat-of-arms-container" v-if="!card.editing && card.image">
              <img :src="card.image" alt="Coat of Arms" class="coat-of-arms" />
            </div>
            <div class="coat-of-arms-preview" v-if="card.image && card.editing">
              <img :src="card.image" alt="Coat of Arms" class="coat-of-arms" />
            </div>
            <fit-text v-if="!card.editing" :text="card.title" :min-font-size="16" :step="0.1" :grow="true"
              class="cdc-title" :style="{ 'width': card.image ? 'calc(100% - 50px)' : '100%', 'height': '100%' }" />
          </div>

          <div class="cdc-card-body">
            <fit-text v-if="!card.editing"
              :text="card.auto ? (functionMap[card.function] && functionMap[card.function][0] ? (functionMap[card.function][0] === 'undefined. ' ? card.body : functionMap[card.function][0]) : card.body) : card.body"
              :min-font-size="16" :step="1" :grow="true" class="agent" />
          </div>

        </template>
      </div>
      <Card v-if="dpt === '01'" icon="explore" :header-text="getCdcTitle(cdcType)" style="min-width: 350px;">
        <template #body>
          <Map type="cdc" :cdc-type="cdcType" :uuid="uuid" :key="cdcType" :zoom-duration="0" />
        </template>
      </Card>
    </div>
    <div class="cdc-container" v-if="page == 'astreintes'">
      <div v-for="(card, index) in cards" :key="card.id" class="duty-card">
        <div class="duty-card-header drag-handle"
          :style="{ 'background-color': card.editing ? 'transparent' : card.color || '#181632', 'color': determineTextColor(card.color || '#fff') }">
          <div class="coat-of-arms-container" v-if="!card.editing && card.image">
            <img :src="card.image" alt="Coat of Arms" class="coat-of-arms" />
          </div>
          <div class="coat-of-arms-preview" v-if="card.image && card.editing">
            <img :src="card.image" alt="Coat of Arms" class="coat-of-arms" />
          </div>
          <fit-text v-if="!card.editing" :text="card.title" :min-font-size="16" :step="1" :grow="true"
            class="duty-title" :style="{ 'width': card.image ? 'calc(100% - 50px)' : '100%', 'height': '100%' }" />
        </div>
        <div class="duty-card-body">
          <fit-text v-if="!card.editing"
            :text="card.auto ? (functionMap[card.function] && functionMap[card.function][0] ? (functionMap[card.function][0] === 'undefined. ' ? card.body : functionMap[card.function][0]) : card.body) : card.body"
            :min-font-size="16" :step="1" :grow="true" class="agent" />
        </div>


      </div>
    </div>
    <div class="cdc-container" v-if="page == 'specialistes'">
      <div v-for="(card, index) in cards" :key="card.id" class="specialist-card">
        <div class="specialist-card-header drag-handle"
          :style="{ 'background-color': card.editing ? 'transparent' : card.color || '#181632', 'color': determineTextColor(card.color || '#fff') }">
          <div class="coat-of-arms-container" v-if="!card.editing && card.image">
            <img :src="card.image" alt="Coat of Arms" class="coat-of-arms" />
          </div>
          <div class="coat-of-arms-preview" v-if="card.image && card.editing">
            <img :src="card.image" alt="Coat of Arms" class="coat-of-arms" />
          </div>
          <fit-text v-if="!card.editing" :text="card.title" :min-font-size="16" :step="1" :grow="true"
            class="specialist-title"
            :style="{ 'width': card.image ? 'calc(100% - 50px)' : '100%', 'height': '100%' }" />
        </div>

        <div class="specialist-card-body">
          <fit-text v-if="!card.editing"
            :text="card.auto ? (functionMap[card.function] && functionMap[card.function][0] ? (functionMap[card.function][0] === 'undefined. ' ? card.body : functionMap[card.function][0]) : card.body) : card.body"
            :min-font-size="16" :step="1" :grow="true" class="agent" />
        </div>
      </div>
    </div>
    <div class="vigicrues-container" v-if="page == 'inondations'">
      <Card icon="fmd_bad" header-text="Prévisions des inondations">
        <template #body>
          <Map contour click legend hover type="vigicrues" :uuid="uuid" />
        </template>
      </Card>
    </div>
    <div class="weather-container" v-if="page == 'meteo'">
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
    <div class="cards-container" v-if="page == 'appels'">
      <Card icon="mdi-chart-areaspline-variant" header-text="Suivi du temps de décroché des appels"
        class="graph-calls-card" v-if="dpt != '01'">
        <template #body>
          <div class="quality-container">
            <QualityCard v-for="qual in qualityCardsData" :text="qual.value" :title="qual.label" :color="qual.color"
              :icon="qual.icon" :title-icon="qual.titleIcon" :description="qual.description"></QualityCard>
          </div>
          <div class="card-body row full-height relative-position">
            <div v-if="loading" class="absolute-full flex flex-center">
              <q-spinner-tail size="100px" color="secondary" />
            </div>
            <highcharts :options="callsAverageChartOptions" v-if="!loading" />
          </div>
        </template>
      </Card>

      <Card icon="call" header-text="Prévisions du nombre d'appels (tranches de 3h)" class="calls-card">
        <template #body>
          <div class="full-height flex flex-center" v-if="loading">
            <q-spinner-tail size="100px" color="secondary" />
          </div>
          <highcharts :options="callsChartOptions" v-if="!loading" />
          <Legend :dpt-bounds="bounds" data-object="Horloge des appels" details="Nombre d'opérateurs" icon-size="lg"
            v-if="!loading" />
        </template>
      </Card>

    </div>
    <div class="cards-container" v-if="page == 'horloges'">
      <Card icon="call" header-text="Prévisions du nombre d'appels (tranches de 3h)" class="calls-card">
        <template #body>
          <div class="full-height flex flex-center" v-if="loading">
            <q-spinner-tail size="100px" color="secondary" />
          </div>
          <highcharts :options="callsChartOptions" v-if="!loading" />
          <Legend :dpt-bounds="bounds" data-object="Horloge des appels" details="Nombre d'opérateurs" icon-size="md"
            v-if="!loading" />
        </template>
      </Card>
      <Card icon="mdi-binoculars" header-text="Prévisions du nombre d'interventions (tranches de 2h)"
        class="calls-card">
        <template #body>
          <div class="full-height flex flex-center" v-if="loading">
            <q-spinner-tail size="100px" color="secondary" />
          </div>
          <highcharts :options="interventionsChartOptions" v-if="!loading" />

        </template>
      </Card>
    </div>
    <div class="guidelines-container" v-if="page == 'consignes'">
      <GuidelineCard v-for="guideline in guidelinesList" :key="guideline._id" :guideline="guideline" :editable="false"
        v-show="guideline.active" />
    </div>
  </q-page>
</template>


<script setup>
import { ref, onMounted, onUnmounted, toRaw, computed } from 'vue'
import BreakingNews from 'src/components/BreakingNews.vue';
import Card from 'src/components/Card.vue';
import AlertCard from 'src/components/AlertCard.vue';
import FitText from 'src/components/FitText.vue';
import GuidelineCard from 'src/components/GuidelineCard.vue';
import { notifyUser } from 'src/utils/notifyUser';
import { determineTextColor } from 'src/utils/textUtils';
import Map from 'src/components/Map.vue';
import { useRoute } from 'vue-router'
import { generateChartData } from "src/utils/polarAreaUtils"
import { createAlertsChartOptions } from "src/utils/rangeBarsUtils";
import QualityCard from 'src/components/QualityCard.vue';
import Legend from 'src/components/Legend.vue';
import axios from 'axios'
import VueApexCharts from "vue3-apexcharts";
import { getCachedImage, cacheImageInDB, clearExpiredImages } from 'src/utils/indexedDB';

const location = useRoute();
const page = location.params.page
const dpt = ref(location.params.dpt)
const uuid = process.env.UUID
const ainKey = ref(0)
const geometries = ref("CIS")

const functionMap = ref({});

const cdcType = ref('cdg')

const screenSize = ref(window.innerWidth)

const alertsChartOptions = ref({})
let baseURL;

if (process.env.CONTEXT === 'production') {
  baseURL = 'https://dashboard.predictops.fr/api/'
}
if (process.env.CONTEXT === 'development') {
  baseURL = 'http://127.0.0.1:5030/api/'
}
if (process.env.CONTEXT === 'preprod') {
  baseURL = 'https://preprod.predictops.fr/api/'
}
const publicPath = process.env.PUBLIC_PATH || '/predictops/'
const api = axios.create({
  baseURL: baseURL
})

const chainOfCommandData = ref([]);
const cards = ref([]);
const guidelinesList = ref([]);
// const dpt = ref('25');

const excludedNewsPages = ["chaine-de-commandement", "astreintes", "specialistes", "consignes"]

// Function to fetch the chain of command data
const fetchDataAndImages = async (dataType, imageEndpoint) => {
  try {
    // Fetch chain of command data
    const chainOfCommandResponse = await api.get(`/data/chain-of-command?dpt=${dpt.value}&uuid=${uuid}`);
    chainOfCommandData.value = chainOfCommandResponse.data;

    // Fetch active data (Chain of Command, Duty, or Specialist) based on the dataType argument
    const activeDataResponse = await api.get(`/data/${dataType}?dpt=${dpt.value}&uuid=${uuid}`);
    const activeData = activeDataResponse.data;

    // Populate functionMap
    chainOfCommandData.value.forEach(item => {
      if (!functionMap.value[item.fonction]) {
        functionMap.value[item.fonction] = [];
      }
      functionMap.value[item.fonction].push(`${item.grade === 'PAT' ? item.prenom[0] + '.' : item.grade} ${item.nom}`);
    });

    // Populate cards array with fetched data (without images)
    cards.value = activeData.map(item => ({
      id: item.id,
      title: item.title,
      body: item.body,
      image: '', // Initially empty, we'll load the image asynchronously
      color: item.color,
      editing: false,
      special: item.special || false,
      order: item.order,
      auto: item.auto,
      function: item.function,
    }));

    // Sort cards based on order
    cards.value = cards.value.sort((a, b) => a.order - b.order);

    // Load images for each card with caching
    cards.value.forEach((card, index) => {
      loadCardImageWithCache(card, index, imageEndpoint);
    });

    // Clear expired images from the cache
    clearExpiredImages();

  } catch (error) {
    notifyUser({
      icon: "error",
      message: `Erreur lors de la récupération des données de ${dataType}.`,
      color: "red",
      position: "bottom",
      timeout: 2500
    });
  }
};

// Function to load the image with caching support using IndexedDB
const loadCardImageWithCache = async (card, index, imageEndpoint) => {
  const cachedImage = await getCachedImage(card.id);
  if (cachedImage) {
    // Use the cached image
    cards.value[index].image = cachedImage;
    return;
  }

  // If not cached, fetch the image from the API
  try {
    const imageResponse = await api.get(`/data/image/${imageEndpoint}/${card.id}?uuid=${uuid}`);
    cards.value[index].image = imageResponse.data.image;

    // Cache the newly fetched image
    await cacheImageInDB(card.id, imageResponse.data.image);
  } catch (error) {
    notifyUser({
      icon: "error",
      message: "Erreur lors de la récupération de l'image.",
      color: "red",
      position: "bottom",
      timeout: 2500
    });
    cards.value[index].image = ''; // Clear the image if the request fails
  }
};

// Specific functions to fetch each type of data
const fetchChainOfCommand = () => {
  fetchDataAndImages('active-chain-of-command', 'active_cdc');
};

const fetchDuty = () => {
  fetchDataAndImages('active-duty', 'active_astreintes');
};

const fetchSpecialists = () => {
  fetchDataAndImages('active-specialist', 'active_specialistes');
};

const getSubDpt = (dpt) => {
  if (dpt === '25') {
    return '25 - Doubs'
  }
  else if (dpt === '01') {
    return '01 - Ain'
  }
  else if (dpt === '78') {
    return '78 - Yvelines'
  }
}

const getCdcTitle = (cdcType) => {
  return {
    'grps': 'Chefs de colonne',
    'cdg': 'Chefs de groupe',
  }[cdcType]
}

const getInterTitle = (interType) => {
  return {
    'CIS': 'Secours à personne',
    'CIS-INC': 'Incendies',
    'Tous': 'Tous'
  }[interType]
}

const loading = ref(true)

const subDpt = ref(getSubDpt(dpt.value))
const weatherData = ref()
const alertsData = ref()

const calculateFontSize = () => {
  const screenWidth = window.innerWidth;

  // Formule adaptative pour grands écrans
  // Base: 14px à 1920px, scale jusqu'à 32px à 3840px (4K)
  let fontSize;

  if (screenWidth < 1920) {
    // Petits écrans: 12-14px
    fontSize = 12 + (screenWidth - 1280) / 640 * 2;
  } else if (screenWidth < 2560) {
    // HD/Full HD: 14-20px
    fontSize = 14 + (screenWidth - 1920) / 640 * 6;
  } else if (screenWidth < 3840) {
    // 2K/QHD: 20-28px
    fontSize = 20 + (screenWidth - 2560) / 1280 * 8;
  } else {
    // 4K et plus: 28-36px
    fontSize = 28 + Math.min((screenWidth - 3840) / 1920 * 8, 8);
  }

  return Math.round(fontSize);
};

// État réactif pour la taille de police
const annotationFontSize = ref(calculateFontSize());


const fetchWeatherData = async () => {
  try {
    const weatherDataResponse = await api.get(`/data/weather?dpt=${dpt.value}&sub-dpt=${subDpt.value}&uuid=${uuid}`)
    weatherData.value = weatherDataResponse.data[0]
    const alertsDataReponse = await api.get(`/data/weather-alerts?dpt=${dpt.value}&sub-dpt=${subDpt.value}&uuid=${uuid}`)
    alertsData.value = alertsDataReponse.data
    alertsChartOptions.value = createAlertsChartOptions(alertsData.value)
    loading.value = false
  } catch (e) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des données météo.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false
  }
}

function getIconUrl(iconCode) {
  return `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
}

const bounds = ref()
function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}
let refreshInterval;

const totalAverage = ref()
const totalBeyondAverage = ref()
const latestAverage = ref()

const getQualityColor = (value) => {
  const qualityBounds = bounds.value["Qualité des appels"]["Qualité"];
  if (value < qualityBounds.rouge.value) return 'red';
  if (value >= qualityBounds.rouge.value && value < qualityBounds.orange.value) return 'orange';
  if (value >= qualityBounds.orange.value && value < qualityBounds.jaune.value) return 'yellow';
  return 'green';
}

const getLatestAverageTimeColor = (value) => {
  const latestAverageBounds = bounds.value["Qualité des appels"]["Délai de décroché moyen"];
  if (value < latestAverageBounds.vert.value) return 'green';
  if (value >= latestAverageBounds.vert.value && value < latestAverageBounds.jaune.value) return 'yellow';
  if (value >= latestAverageBounds.jaune.value && value < latestAverageBounds.orange.value) return 'orange';
  return 'red';
};

const generateQualityCardsData = (totalAverage, totalBeyondAverage, latestAverage) => {
  return [
    {
      titleIcon: "",
      label: "Qualité",
      color: getQualityColor(Math.round(totalAverage)),
      value: `${Math.round(totalAverage)}%`,
      icon: "",
      description: "Part des appels décrochés sur le dernier créneau dans un délai inférieur à la moyenne des 100 derniers jours."
    },
    {
      titleIcon: "",
      label: "Nb décrochés > moyenne",
      // color: getTotalBeyondAverageColor(Math.round(totalBeyondAverage)),
      color: 'transparent',
      value: Math.round(totalBeyondAverage).toString(),
      icon: "",
      description: "Nombre des appels décrochés sur le dernier créneau dans un délai supérieur à la moyenne des 100 derniers jours."
    },
    {
      titleIcon: "",
      label: "Délai de décroché moyen",
      color: getLatestAverageTimeColor(Math.round(latestAverage)),
      value: `${Math.round(latestAverage)} s`,
      icon: "",
      description: "Temps moyen de décroché de l'appel sur la dernière heure."
    }
  ];
};

const qualityCardsData = ref([])

const callsData = ref()
const processedCalls = ref()
const callsBounds = ref()
const callsChartOptions = ref({
  chart: {
    polar: true,
    type: 'column',
    // height: "500",
  },
  title: {
    text: ""
  },
  legend: {
    enabled: false,
  },
  pane: {
    startAngle: 15,
    endAngle: 375
  },
  tooltip: {
    followPointer: true,
    useHTML: true,
    formatter: function () {
      const pointData = this.point.options;
      return pointData.reliability > 0 ? `<table>
        <tr>
          <th colspan="2">Type : ${capitalizeFirstLetter(pointData.type)}</th>
        </tr>
        <tr>
          <td style="backgroundColor: ${pointData.color}; color: ${pointData.fontColor}; fontWeight: bold">
            Valeur : ${pointData.y}
          </td>
        </tr>
        <tr>
          <td>
            Fiabilité : ${pointData.reliability}
          </td>
        </tr>
      </table>` : `<table>
        <tr>
          <th colspan="2">Type : ${capitalizeFirstLetter(pointData.type)}</th>
        </tr>
        <tr>
          <td style="backgroundColor: ${pointData.color}; color: ${pointData.fontColor}; fontWeight: bold">
            Valeur : ${pointData.y}
          </td>
        </tr>
      </table>`
    }
  },

  xAxis: {
    tickInterval: 45,
    min: 0,
    max: 360,
    labels: {
      formatter: function () {
        let hours = (this.value / 15) + 1;
        hours = hours > 23 ? hours - 24 : hours;
        return hours + 'H';
      },
      style: {
        fontSize: 'clamp(12px, 4vw, 56px)',
        fontFamily: 'Roboto, sans-serif',
        fontWeight: 'bold'
      }
    }
  },
  yAxis: {
    endOnTick: false,
    labels: {
      enabled: false
    },
    lineWidth: 0,
    gridLineWidth: 0,
    tickLength: 0
  },
  plotOptions: {
    series: {
      pointStart: 0, // Start at the top of the circle
      pointInterval: 45, // Same as your tickInterval

    },
    column: {
      pointPadding: 0,
      groupPadding: 0,
      borderWidth: 1,
      borderColor: 'white',
    }
  },
  series: [{
    type: 'column',
    name: 'Appels',
    pointPlacement: 'between'
  }]
});
const interventionsData = ref([])
const interventionsChartOptions = computed(() => ({
  chart: {
    polar: true,
    type: 'column',
    borderRadius: 15,
  },
  title: {
    text: ""
  },
  legend: {
    enabled: false,
  },
  pane: {
    startAngle: 15,
    endAngle: 375
  },
  tooltip: {
    followPointer: true,
    useHTML: true,
    formatter: function () {
      const pointData = this.point.options;
      return `<table>
        <tr>
          <th colspan="2">Type : ${pointData.type}</th>
        </tr>
        <tr>
          <td style="background-color: ${pointData.color}; color: ${pointData.fontColor}; font-weight: bold">
            Valeur : ${pointData.y}
          </td>
        </tr>
      </table>`;
    }
  },
  xAxis: {
    tickInterval: 30,
    min: 0,
    max: 360,
    labels: {
      formatter: function () {
        let hours = (this.value / 30) * 2 + 1;
        hours = hours > 23 ? hours - 24 : hours;
        return hours + 'H';
      },
      style: {
        fontSize: 'clamp(12px, 4vw, 56px)',
        fontFamily: 'Roboto, sans-serif',
        fontWeight: 'bold'
      }
    }
  },
  yAxis: {
    endOnTick: false,
    labels: {
      enabled: false
    },
    lineWidth: 0,
    gridLineWidth: 0,
    tickLength: 0
  },
  plotOptions: {
    series: {
      pointStart: 15,
      pointInterval: 30,
    },
    column: {
      pointPadding: 0,
      groupPadding: 0,
      borderWidth: 1,
      borderColor: 'white',
    }
  },
  series: [{
    type: 'column',
    name: 'Values',
  }],

}));


const callsQualityData = ref()
const callsAverageChartOptions = ref({})


const callsPeriods = ['01h-04h', '04h-07h', '07h-10h', '10h-13h', '13h-16h', '16h-19h', '19h-22h', '22h-01h']
const callsDayPeriods = ["07h-10h", "10h-13h", "13h-16h", "16h-19h"]
const callsNightPeriods = ["19h-22h", "22h-01h", "01h-04h", "04h-07h"]

const interventionsPeriods = ['01h-03h', '03h-05h', '05h-07h', '07h-09h', '09h-11h', '11h-13h', '13h-15h', '15h-17h', '17h-19h', '19h-21h', '21h-23h', '23h-01h']
const interventionsDayPeriods = ["07h-09h", "09h-11h", "11h-13h", "13h-15h", "15h-17h"]
const interventionsNightPeriods = ["19h-21h", "21h-23h", "23h-01h", "01h-03h", "03h-05h", "05h-07h", "17h-19h"]


const fetchCallsData = async () => {
  bounds.value = (await api.get(`/data/bounds?dpt=${dpt.value}&uuid=${uuid}`)).data[0].bounds
  const goalThreshold = bounds.value["Graphique décrochés d'appels"]["Objectif du temps de décroché"]["seuil"].value

  loading.value = true;
  try {


    const grayObject = {
      "gray": {
        "color": "gray",
        "operators": "Réel",
        "value": "Réel",
      }
    };
    const temp = { ...bounds.value["Horloge des appels"] };
    temp["Jour"] = { ...temp["Jour"], gray: grayObject.gray };
    temp["Nuit"] = { ...temp["Nuit"], gray: grayObject.gray };
    callsBounds.value = temp;
    const callsResponse = await api.get(`/data/mv?mv=mv_appels_${dpt.value}_t&uuid=${uuid}`);
    callsData.value = callsResponse.data;
    processedCalls.value = generateChartData(callsData.value, callsPeriods, callsDayPeriods, callsNightPeriods, callsBounds.value)
    callsChartOptions.value.series[0].data = processedCalls.value
    callsChartOptions.value.annotations = [{
      labels: processedCalls.value.map(dataPoint => {
        const labelOptions = {
          point: dataPoint.id,
          text: dataPoint.reliability > 0
            ? `Valeur : ${dataPoint.y} <br> Fiabilité : ${dataPoint.reliability}`
            : `Valeur : ${dataPoint.y}`,
          distance: 10,
          y: -10,
          allowOverlap: true,
          style: {
            fontSize: `${annotationFontSize.value}px`,
            fontFamily: 'Roboto, sans-serif',
            fontWeight: 'bold'
          }
        };
        return labelOptions;
      }),
      draggable: false,
    }];


    const callsQualityResponse = await api.get(`/data/calls-quality?dpt=${dpt.value}&uuid=${uuid}`);
    callsQualityData.value = callsQualityResponse.data;

    totalAverage.value = 100 - callsQualityData.value[callsQualityData.value.length - 1].pourcentage
    totalBeyondAverage.value = callsQualityData.value[callsQualityData.value.length - 1].nb_au_dela
    latestAverage.value = callsQualityData.value[callsQualityData.value.length - 1].moyenne

    qualityCardsData.value = generateQualityCardsData(totalAverage.value, totalBeyondAverage.value, latestAverage.value)

    const averageData = callsQualityData.value.map(item => [new Date(item.creneau).getTime(), parseFloat(item.moyenne.toFixed(2)), item.nb]);
    const beyondAverageData = callsQualityData.value.map(item => [new Date(item.creneau).getTime(), item.nb_au_dela]);
    const callsPerHourData = callsQualityData.value.map(item => [new Date(item.creneau).getTime(), parseInt(item.nb)])
    const goalThresholdData = callsQualityData.value.map(item => [new Date(item.creneau).getTime(), parseInt(goalThreshold)])
    averageData.sort((a, b) => a[0] - b[0]);
    beyondAverageData.sort((a, b) => a[0] - b[0]);
    callsAverageChartOptions.value = {
      chart: {
        type: 'line',
        height: "600"
      },
      title: {
        text: ''
      },
      legend: {
        enabled: true
      },
      responsive: {
        rules: [{
          condition: {
            maxWidth: 800
          },
          chartOptions: {
            chart: {
              height: '500'
            },
          }
        }]
      },
      plotOptions: {
        series: {
          marker: {
            enabled: false
          }
        }
      },
      xAxis: {
        type: 'datetime',
        title: {
          text: 'Date'
        }
      },
      yAxis: {
        title: {
          text: "Temps moyen (s)"
        }
      },
      series: [
        {
          name: 'Moyenne',
          data: averageData,
          color: "#ed9205",
          tooltip: {
            pointFormatter: function () {
              // Get the additional data (third value in the data array)
              const additionalData = this.series.userOptions.data[this.index][2];

              // Format the tooltip content
              return `<span style="color:${this.color}">●</span> ${this.series.name}: <b>${this.y}</b><br/><span style="color: #181632">●</span> Nombre d'appels: <b>${additionalData}</b><br/>`;
            }
          }
        },
        {
          name: 'Objectif',
          data: goalThresholdData,
          color: "#181632"
        },
        {
          name: "Nombre d'appels",
          data: callsPerHourData,
          color: "#1864ab"
        }
      ]
    }

  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des données d'appels.", color: "red", position: "bottom", timeout: 2500 })
  } finally {
    loading.value = false;
  }
}

const fetchInterventionsData = async () => {
  try {
    const response = await api.get(`/data/mv?mv=mv_Tous_${dpt.value}_t&uuid=${uuid}`);
    interventionsData.value = response.data;
    const processedInterventions = generateChartData(interventionsData.value, interventionsPeriods, interventionsDayPeriods, interventionsNightPeriods)
    interventionsChartOptions.value.series[0].data = processedInterventions
    interventionsChartOptions.value.annotations = [{
      labels: processedInterventions.map(dataPoint => {
        const labelOptions = {
          point: dataPoint.id,
          text: dataPoint.reliability > 0
            ? `Valeur : ${dataPoint.y} <br> Fiabilité : ${dataPoint.reliability}`
            : `Valeur : ${dataPoint.y}`,
          distance: 0,
          y: 0,
          style: {
            fontSize: `${annotationFontSize.value}px`,
            fontFamily: 'Roboto, sans-serif',
            fontWeight: 'bold'
          }
        };
        return labelOptions;
      }),
      draggable: false,

    }];
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la supplementation des données d'interventions.", color: "red", position: "bottom", timeout: 2500 })
  }
}
const fetchGuidelines = async () => {
  try {
    const response = await api.get(`/data/guidelines?dpt=${dpt.value}&uuid=${uuid}`);
    guidelinesList.value = response.data
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la sélection des consignes.", color: "red", position: "bottom", timeout: 2500 })
  }
}

onMounted(() => {

  if (page === "synthese") {
    const values = ['CIS', 'CIS-INC'];
    let index = 0;

    const intervalId = setInterval(() => {
      // if(dpt.value === "01"){
      //   ainKey.value += 1
      //   geometries.value = "Tous";
      // }
      // else {
      index = (index + 1) % values.length;
      geometries.value = values[index];
      // }
    }, 45000);

    // Optionally clear the interval when the page changes
    window.addEventListener('beforeunload', () => clearInterval(intervalId));
  }

  if (page === "appels" || page === "synthese" || page === "horloges") {
    fetchCallsData()
    fetchInterventionsData()
    clearInterval(refreshInterval)
    refreshInterval = setInterval(() => {
      fetchCallsData()
      fetchInterventionsData()
    }, 45000)

  }

  if (page === "chaine-de-commandement") {
    fetchChainOfCommand()
    clearInterval(refreshInterval)
    if (dpt.value === "01") {
      const cdcTypeValues = ['cdg', 'grps'];
      let cdcTypeIndex = 0;

      const intervalId = setInterval(() => {
        cdcTypeIndex = (cdcTypeIndex + 1) % cdcTypeValues.length;
        cdcType.value = cdcTypeValues[cdcTypeIndex];
      }, 45000);

      // Optionally clear the interval when the page changes
      window.addEventListener('beforeunload', () => clearInterval(intervalId));
    }
    refreshInterval = setInterval(() => {
      fetchChainOfCommand()
    }, 15000)
  }

  if (page === "astreintes") {
    fetchDuty()
    clearInterval(refreshInterval)
    refreshInterval = setInterval(() => {
      fetchDuty()
    }, 15000)
  }

  if (page === "specialistes") {
    fetchSpecialists()
    clearInterval(refreshInterval)
    refreshInterval = setInterval(() => {
      fetchSpecialists()
    }, 15000)
  }

  if (page === "meteo") {
    fetchWeatherData()
  }

  if (page === "consignes") {
    fetchGuidelines()
    clearInterval(refreshInterval)
    refreshInterval = setInterval(() => {
      fetchGuidelines()
    }, 15000)
  }

});

onUnmounted(() => {
  clearInterval(refreshInterval);
});

</script>

<style scoped>
.guidelines-container {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  margin: 0 auto;
  gap: 1em;
  width: 95%;
}

.scaled-legend {
  transform: scale(2.5);
}

.cards-container {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  flex: 1;
  gap: 1em;
}

.cdc-container {
  color: var(--sad-nightblue);
  font-weight: bold;
  width: 100%;
  height: 100%;
  display: flex;
  flex-wrap: wrap;
  flex: 1;
  gap: 1em;
}

.cdc-card,
.duty-card,
.specialist-card {
  height: calc(90vh / 3)
}

.vigicrues-container,
.weather-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-wrap: wrap;
  flex: 1;
  gap: 1em;
}

.wrapper {
  width: 100%;
  color: var(--sad-nightblue);
  display: flex;
  flex-wrap: wrap;
  font-weight: bold;
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

.quality-container {
  display: flex;
  gap: 1em;
  padding: 15px;
  flex-wrap: wrap;
}

.card-body>div {
  border-radius: 15px;
}

.calls-card .card-body>div:first-child {
  flex: 1;
}

.graph-calls-card .card-body>div:last-child {
  flex: 1;
}
</style>
