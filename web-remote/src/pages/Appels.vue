<template>
  <q-page>
    <BreakingNews :page="location.path.replace('/', '')" height="80px" font-size="clamp(0.75rem, 1.75vw, 2rem)">
    </BreakingNews>
    <div class="cards-container">

      <Card icon="mdi-chart-areaspline-variant" header-text-size="fs-md"
        header-text="Suivi du temps de décroché des appels">

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

      <Card icon="call" header-text-size="fs-md" header-text="Prévisions du nombre d'appels (tranches de 3h)">
        <template #body>
          <div class="full-height flex flex-center" v-if="loading">
            <q-spinner-tail size="100px" color="secondary" />
          </div>
          <highcharts :options="callsChartOptions" v-if="!loading" />
          <Legend :dpt-bounds="bounds" data-object="Horloge des appels" details="Nombre d'opérateurs" icon-size="md"
            v-if="!loading" />
        </template>
      </Card>
    </div>


  </q-page>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from "vue"
import BreakingNews from 'src/components/BreakingNews.vue';
import Card from 'src/components/Card.vue';
import Legend from 'src/components/Legend.vue'
import { notifyUser } from "src/utils/notifyUser";
import { generateChartData } from "src/utils/polarAreaUtils"
import { api } from 'src/boot/axios';
import QualityCard from "src/components/QualityCard.vue";
import { useRoute } from 'vue-router'
const location = useRoute();

const dpt = computed(() => {
  return localStorage.getItem("dpt") || location.params.dpt
})
const loading = ref(true)

const isMobile = computed(() => window.innerWidth <= 768)

const bounds = ref(JSON.parse(localStorage.getItem("dptBounds") || {}))
const goalThreshold = bounds.value["Graphique décrochés d'appels"]["Objectif du temps de décroché"]["seuil"].value

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
      // description: "Part des appels décrochés sur le dernier créneau dans un délai inférieur à la moyenne des 100 derniers jours."
      description: goalThreshold ? "Part des appels décrochés sur le dernier créneau dans un délai inférieur à " + goalThreshold + "s" : "Part des appels décrochés sur le dernier créneau dans un délai inférieur à la moyenne des 100 derniers jours."
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
    height: "500",
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
  responsive: {
    rules: [{
      condition: {
        maxWidth: 600
      },
      chartOptions: {
        chart: {
          height: '400'
        },
      }
    }]
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


const callsQualityData = ref()
const callsAverageChartOptions = ref({})


const callsPeriods = ['01h-04h', '04h-07h', '07h-10h', '10h-13h', '13h-16h', '16h-19h', '19h-22h', '22h-01h']
const callsDayPeriods = ["07h-10h", "10h-13h", "13h-16h", "16h-19h"]
const callsNightPeriods = ["19h-22h", "22h-01h", "01h-04h", "04h-07h"]



const fetchData = async () => {
  bounds.value = JSON.parse(localStorage.getItem("dptBounds") || {})
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
    const callsResponse = await api.get(`/data/mv?mv=mv_appels_${dpt.value}_t`);
    callsData.value = callsResponse.data;
    processedCalls.value = generateChartData(callsData.value, callsPeriods, callsDayPeriods, callsNightPeriods, callsBounds.value)
    callsChartOptions.value.series[0].data = processedCalls.value
    if(!isMobile.value) {
      callsChartOptions.value.annotations = [{
        labels: processedCalls.value.map(dataPoint => {
          const labelOptions = {
            point: dataPoint.id,
            text: dataPoint.reliability > 0
              ? `Valeur : ${dataPoint.y} <br> Fiabilité : ${dataPoint.reliability}`
              : `Valeur : ${dataPoint.y}`,
            distance: 0,
            y: 0,
            allowOverlap: true,
          };
          return labelOptions;
        }),
        draggable: false,

      }];
    }


    const callsQualityResponse = await api.get(`/data/calls-quality?dpt=${dpt.value}`);
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
        // height: "500"
      },
      title: {
        text: ''
      },
      legend: {
        enabled: false
      },
      responsive: {
        rules: [{
          condition: {
            maxWidth: 800
          },
          chartOptions: {
            chart: {
              // height: '400'
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
  }, 45000)
})

onUnmounted(() => {
  clearInterval(refreshInterval);
  refreshInterval = null
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

.quality-container {
  display: flex;
  gap: 1em;
  padding: 15px;
  flex-wrap: wrap;
}

.card {
  min-height: 600px;
}

.card-body>div {
  border-radius: 15px;
}

#q-app>div>div.q-page-container>main>div.cards-container>div:nth-child(1)>div.card-body>div.card-body.row.full-height.relative-position>div {
  flex: 1;
}
</style>
