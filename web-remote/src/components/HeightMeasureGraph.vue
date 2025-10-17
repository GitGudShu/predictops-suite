<template>
  <transition name="slide-up">
    <div v-show="showChart" class="height-measure-graph">
      <div class="handlebars" @click="startClose">
        <div class="handlebar one"></div>
        <div class="handlebar two"></div>
      </div>
      <div v-if="loading" class="absolute-full flex flex-center">
        <q-spinner-tail size="100px" color="secondary" />
      </div>
      <highcharts v-if="!loading" :options="chartOptions"></highcharts>
    </div>
  </transition>
</template>

<script setup>
import { ref, watchEffect, watch } from 'vue'
import { api } from 'src/boot/axios'
import { notifyUser } from "src/utils/notifyUser"

const props = defineProps({
  stationName: String,
  type: String,
})

const showChart = ref(false)
const loading = ref(true)

const startClose = () => {
  showChart.value = false
}


const chartOptions = ref({
  chart: {
    type: 'spline',
    // height: "30%",
  },
  title: {
    text: '',
    style: {
      fontSize: '22px',
    }
  },
  xAxis: {
    type: 'datetime',
    title: {
      text: 'Time'
    }
  },
  yAxis: [{
    title: {
      text: 'Hauteur (cm)'
    }
  }, {
    title: {
      text: 'Moyenne (cm)'
    },
    opposite: true
  }],
  series: [{
    name: 'Hauteur (cm)',
    data: [],
    color: "#181632",
    marker: {
      enabled: false
    }
  }, {
    name: 'Moyenne (cm)',
    data: [],
    color: "#ed9205",
    marker: {
      enabled: false
    }
  }],
  responsive: {
    rules: [{
      condition: {
        maxWidth: 1000
      },
      chartOptions: {
        title: {
          style: {
            fontSize: '18px',
          }
        }
      }
    }, {
      condition: {
        maxWidth: 500
      },
      chartOptions: {
        title: {
          style: {
            fontSize: '14px',
          }
        }
      }
    }, {
      condition: {
        maxWidth: 300
      },
      chartOptions: {
        title: {
          style: {
            fontSize: '10px',
          }
        }
      }
    }]
  },
})

const fetchStationData = async (stationName) => {
  loading.value = true
  try {
    let url;
    if(props.type === "vigicrues") {
      url = `/data/water-station-measure?station=${stationName}`
    }
    if(props.type === "groundwater") {
      url = `/data/groundwater-measure?groundwater=${stationName}`
    }
    const response = await api.get(url)
    const measurements = response.data
    const sortedMeasurements = measurements.sort((a, b) => new Date(a.date) - new Date(b.date));
    chartOptions.value.series[0].data = measurements.map(measure => [new Date(measure.date).getTime(), Math.round(measure.height)])
    chartOptions.value.series[1].data = measurements.map(measure => [new Date(measure.date).getTime(), Math.round(measure.moyenne)])
    chartOptions.value.title.text = measurements.length ? measurements[0].nom : 'Station Data'

    loading.value = false
    showChart.value = true
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des données.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false
    showChart.value = false
  }
}

watchEffect(() => {
  if (props.stationName) {
    fetchStationData(props.stationName)
  } else {
    showChart.value = false
  }
})

</script>

<style scoped>
.height-measure-graph {
  border-top-right-radius: 7%;
  border-top-left-radius: 7%;
  position: absolute;
  background: white;
  z-index: 100;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  bottom: 0;
  width: 100%;
  height: 65%;
}

text.highcharts-title {
  display: none;
}

.handlebars {
  display: flex;
  width: max-content;
  margin: 10px auto;
}

.height-measure-graph>*:last-child {
  flex: 1;
}

.handlebar {
  width: 50px;
  height: 10px;
  border-radius: 15px;
  background: var(--sad-nightblue);
  cursor: pointer;
  transition: all 0.1s ease-in;
}

.handlebar.one {
  transform: translateX(5px);
}

.handlebar.two {
  transform: translateX(-5px);
}

.handlebars:hover .handlebar.one {
  transform: rotate(15deg) translateX(5px);
}

.handlebars:hover .handlebar.two {
  transform: rotate(-15deg) translateX(-5px);
}


.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}

.slide-up-enter-to,
.slide-up-leave-from {
  transform: translateY(0);
}
</style>
