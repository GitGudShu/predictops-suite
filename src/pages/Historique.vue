<template>
  <q-page>
    <div class="cards-container">
      <Card icon="fmd_bad" header-text-size="fs-md" header-text="Historique des interventions">
        <template #body>
          <Map controls legend contour quality hover click horizon-dropdown type="delays" geometries="hexagones" />
        </template>
      </Card>
      <Card icon="history" header-text-size="fs-md" header-text="Historique des interventions">
        <template #body>
          <highcharts :options="historyChartOptions" />
        </template>
      </Card>
    </div>
  </q-page>
</template>

<script setup>

import { computed, ref, onMounted } from "vue"
import Card from 'src/components/Card.vue';
import Map from "src/components/Map.vue";
import { useRoute } from 'vue-router'
import { formatHistory, formatPredictions } from "src/utils/areasplineUtils"
import { api } from 'src/boot/axios';


const location = useRoute();
const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value <= 1050)

const historyData = ref()
const processedHistory = ref()
const historyChartOptions = ref({
  chart: {
    type: 'spline',
  },
  title: {
    text: ''
  },
  plotOptions: {
    areaspline: {
      stacking: 'normal',
    },
    series: {
      turboThreshold: 5000,
      marker: {
        enabled: false
      }
    },
  },
  time: {
    useUTC: true
  },
  xAxis: {
    type: 'datetime'
  },
  yAxis: {
    title: {
      text: ''
    }
  },
})

onMounted(async () => {
  const historyResponse = await api.get(`/data/history?dpt=${dpt.value}`);
  const predictionsResponse = await api.get(`/data/future-predictions?dpt=${dpt.value}`);
  historyData.value = historyResponse.data;
  processedHistory.value = formatHistory(historyData.value);
  let latestTimestamp = 0;
  processedHistory.value.forEach(series => {
    series.data.forEach(point => {
      if (point.x > latestTimestamp) {
        latestTimestamp = point.x;
      }
    });
  });
  const predictionsData = predictionsResponse.data;
  formatPredictions(predictionsData, processedHistory.value, latestTimestamp);
  // const allSeries = [...processedHistory.value, ...formatPredictions(predictionsResponse.data)];
  // historyChartOptions.value.series = processedHistory.value;
  historyChartOptions.value.series = processedHistory.value;
})

const updateWindowWidth = () => {
  windowWidth.value = window.innerWidth;
}
const flex = computed(() => isMobile.value ? '1' : '0')

const dpt = computed(() => {
  return localStorage.getItem("dpt") || location.params.dpt
})

window.addEventListener('resize', updateWindowWidth)

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
</style>
