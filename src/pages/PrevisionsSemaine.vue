<template>
  <q-page>
    <BreakingNews :page="location.path.replace('/', '')" height="80px" font-size="clamp(0.75rem, 1.75vw, 2rem)" ></BreakingNews>

    <div class="cards-container" v-if="dataReady">
      <Card icon="fire_truck" header-text-size="fs-md" header-text="Prévisions des interventions" height="500px">
        <template #body>
          <div class="full-height relative-position">
            <VueApexCharts v-if="!loading" width="100%" height="100%" type="bar" :options="interventionsChartOptions" :series="interventionsChartOptions.series">
            </VueApexCharts>
            <div v-if="loading" class="absolute-full flex flex-center">
              <q-spinner-tail size="100px" color="secondary"/>
            </div>
          </div>
        </template>
      </Card>
      <Card icon="phone" header-text-size="fs-md" header-text="Prévisions des appels" height="500px">
        <template #body>
          <div class="full-height relative-position">
            <VueApexCharts v-if="!loading" width="100%" height="100%" type="bar" :options="callsChartOptions" :series="callsChartOptions.series">
            </VueApexCharts>
            <div v-if="loading" class="absolute-full flex flex-center">
              <q-spinner-tail size="100px" color="secondary"/>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import Card from 'src/components/Card.vue';
import BreakingNews from 'src/components/BreakingNews.vue';
import VueApexCharts from "vue3-apexcharts";
import { api } from 'src/boot/axios';
import { notifyUser } from "../utils/notifyUser";
import { createChartOptions } from "../utils/groupedStackedColumnsUtils"
import { useRoute } from 'vue-router'
import { debounce } from "quasar";
const location = useRoute();
const interventionsData = ref()
const callsData = ref()
const loading = ref(true)
const dataReady = ref(false);
const dpt = computed(() => {
  return localStorage.getItem("dpt") || location.params.dpt
})
const interventionsChartOptions = ref()
const callsChartOptions = ref()

const fetchData = debounce(async () => {
  loading.value = true;
  try {
    const response = await api.get(`/data/mv?mv=mv_semaine_${dpt.value}`);
    interventionsData.value = response.data.filter(item => item.objet === "interventions")
    callsData.value = response.data.filter(item => item.objet === "appels")
    interventionsChartOptions.value = createChartOptions(interventionsData.value)
    callsChartOptions.value = createChartOptions(callsData.value)
    dataReady.value = true;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des données.", color: "red", position: "bottom", timeout: 2500 })
  } finally {
    loading.value = false;
  }
}, 500);

const formatDate = (date) => {
  return `${Date.shortMonths[date.getMonth()]} ${String(date.getDate()).padStart(2, '0')}`;
};

onMounted(async () => {
  try {
    fetchData()
    dataReady.value = true;

  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des données.", color: "red", position: "bottom", timeout: 2500 })
  }
});



</script>

<style scoped>
.cards-container {
  width: 100%;
  height: 100%;
  display: grid;
  flex: 1;
  gap: 1em;
}

</style>

