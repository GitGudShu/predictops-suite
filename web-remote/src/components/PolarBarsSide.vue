<template>
  <q-icon class="description-icon" name="info" size="xs">
      <q-tooltip anchor="center right" self="center left" :offset="[10, 10]" class="tooltip">
        Un créneau vide indique que la valeur prédite ou réelle est 0.
      </q-tooltip>
    </q-icon>
  <div class="polar-bars-panel">
    <PolarBarChart  v-if="!loading" v-for="(group, index) in sortedGroups" :key="group.codeGeom" :data="group.data" :name="group.name"
      :codeGeom="group.codeGeom" />
    <q-inner-loading :showing="loading" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import { api } from 'src/boot/axios';
import PolarBarChart from './PolarBarChart.vue';
import { notifyUser } from 'src/utils/notifyUser';
import { useRoute } from 'vue-router';

const location = useRoute();


const dpt = computed(() => {
  return localStorage.getItem('dpt') || location.params.dpt;
});

const props = defineProps({
  geometries: String,
  uuid: String
});

let refreshInterval;

const data = ref([]);
const bounds = ref({});
const loading = ref(false);

const timeRanges = [
  '01h-03h', '03h-05h', '05h-07h', '07h-09h', '09h-11h', '11h-13h',
  '13h-15h', '15h-17h', '17h-19h', '19h-21h', '21h-23h', '23h-01h'
];

const fetchData = async () => {
  loading.value = true;

  try {
    const response = await api.get(`/data/mv`, {
      params: {
        mv: `mv_${props.geometries.replace('-', '_')}_${dpt.value}_t`,
        uuid: props.uuid
      },
    });

    data.value = response.data;
    const codeGeoms = [...new Set(data.value.map(item => item.code_geom))];
    const boundsResponse = await api.get('/data/map-bounds', {
      params: {
        dpt: dpt.value,
        type: props.geometries.toUpperCase() === "CIS" ? "CIS-SAP" : props.geometries.toUpperCase(),
        code_geom: codeGeoms.join(','),
        horizon: timeRanges.join(','),
        uuid: props.uuid
      }
    });

    // Process bounds response
    codeGeoms.forEach(codeGeom => {
      bounds.value[codeGeom] = {};
      timeRanges.forEach(tranche => {
        bounds.value[codeGeom][tranche] = boundsResponse.data.find(b => b.code_geom == codeGeom && b.tranche == tranche);
        if (bounds.value[codeGeom][tranche]) {
          bounds.value[codeGeom].name = bounds.value[codeGeom][tranche].name;
        }
      });
    });

  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la création des graphiques.", color: "red", position: "bottom", timeout: 2500 })
  } finally {
    loading.value = false;
  }
};

const groupedData = computed(() => {
  return data.value.reduce((acc, item) => {
    if (!acc[item.code_geom]) {
      acc[item.code_geom] = [];
    }
    acc[item.code_geom].push(item);
    return acc;
  }, {});
});

const determineFontColor = (color) => {
  switch (color) {
    case "#23A97B": // Green
    case "#C92A2A": // Red
      return "white";
    case "#FED330": // Yellow
    case "#ED9205": // Orange
      return "black";
    default:
      return "black";
  }
};

const colorMap = {
  "green": "#23A97B", // Green
  "yellow": "#FED330", // Yellow
  "orange": "#ED9205", // Orange
  "red": "#C92A2A", // Red
  "gray": "#CED4DA", // Gray
};

const filterAllTranches = (group) => {
  return timeRanges.map(tranche => {
    const found = group.find(item => item.tranche === tranche);
    let color = found && found.color ? colorMap[found.color] : "#CED4DA";
    return {
      tranche: tranche,
      value: found ? found.value : 0,
      type: found ? found.type : 'predit',
      color: color,
      fontColor: determineFontColor(color),
    };
  });
};

const colorPriority = {
  "#C92A2A": 4, // Red
  "#ED9205": 3, // Orange
  "#FED330": 2, // Yellow
  "#23A97B": 1, // Green
  "#CED4DA": 0, // Gray for reel
  "#CCCCCC": 0  // Default
};

const sortedGroups = computed(() => {
  const groups = groupedData.value;
  const sortedArray = Object.entries(groups).map(([codeGeom, data]) => {
    const allTranchesData = filterAllTranches(data);
    const highestPriority = Math.max(...allTranchesData
      .filter(item => item.value !== 0)
      .map(item => colorPriority[item.color] || 0)
    );
    return { codeGeom, data: allTranchesData, highestPriority, name: bounds.value[codeGeom]?.name };
  }).sort((a, b) => b.highestPriority - a.highestPriority);
  return sortedArray;
});

onMounted(async () => {
  fetchData();
  clearInterval(refreshInterval)
  refreshInterval = setInterval(() => {
    fetchData()
  }, 45000)
});

onUnmounted(() => {
  clearInterval(refreshInterval);
  refreshInterval = null
});
</script>

<style scoped>
.polar-bars-panel {
  height: 100%;
  width: 100%;
  overflow: hidden;
  position: absolute;
  overflow-y: auto;
  color: var(--sad-nightblue);
  display: grid;
  place-items: center;
}

.description-icon {
  position: absolute;
  right: 5%;
  top: 0;
  z-index: 100000;
}
</style>
