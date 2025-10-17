<template>
  <q-page>
    <Card icon="insights" header-text-size="fs-md" header-text="Fiabilité" height="100%" v-if="dataReady">
      <template #body>
        <div class="controls">
          <Dropdown btn-size="md-btn" :list="types" @update:selected="onTypeSelected"></Dropdown>
          <Dropdown btn-size="md-btn" :list="decoupes" @update:selected="onDecoupeSelected"></Dropdown>
          <Dropdown btn-size="md-btn" :list="horizons" @update:selected="onHorizonSelected"></Dropdown>
        </div>
        <highcharts :options="chartOptions" v-if="!loading" style="flex: 1;" />
        <div v-if="loading" class="absolute-full flex flex-center">
          <q-spinner-tail size="100px" color="secondary" />
        </div>
      </template>
    </Card>
  </q-page>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import Card from 'src/components/Card.vue';
import { api } from 'src/boot/axios';
import { notifyUser } from "../utils/notifyUser";
import Dropdown from "src/components/Dropdown.vue";
import { debounce } from "quasar";
import { useRoute } from "vue-router";

const location = useRoute();

const data = ref([]);
const mae = ref(0);
const dropdownData = ref();
const loading = ref(true);
const types = ref([]);
const decoupes = ref([]);
const horizons = ref([]);
const selectedType = ref();
const decoupe = ref();
const horizon = ref();
const dataReady = ref(false);
const dpt = ref(localStorage.getItem("dpt") || location.params.dpt);
const publicPath = process.env.PUBLIC_PATH || '/predictops/';

const chartOptions = ref({
  time: {
    useUTC: false
  },
  chart: {
    type: 'line',
    zoomType: 'x'
  },
  title: {
    text: ''
  },
  xAxis: {
    type: 'datetime',
    tickInterval: 4 * 3600 * 1000,
    dateTimeLabelFormats: {
      day: '%e %b',
      hour: '%H:%M'
    },
    labels: {
      style: {
        fontSize: '10px',
        fontFamily: 'Roboto, sans-serif',
        fontWeight: 'bold'
      }
    },

  },
  yAxis: {
    title: {
      text: 'Valeur'
    },
    labels: {
      formatter: function () {
        return this.value.toFixed(2).replace('.00', '');
      }
    },
  },
  tooltip: {
    shared: true,
    crosshairs: true,
    useHTML: true,
    style: {
      fontSize: '14px',
      padding: '10px',
      fontFamily: 'Roboto, sans-serif'
    },
    formatter: function () {
      const points = this.points || [];
      const date = formatTooltipDate(new Date(this.x));
      const tooltip = [`<b style="display: flex;">${date}</b>`];
      points.forEach(point => {
        tooltip.push(`<span style="color:${point.series.color}">\u25CF</span> ${point.series.name}: <b>${point.y.toFixed(2).replace('.00', '')}</b>`);
      });
      return `<div style="padding: 10px;">${tooltip.join('<br/>')}</div>`;
    }
  },
  plotOptions: {
    series: {
      turboThreshold: 0,
      marker: {
        enabled: false,
        radius: 3
      }
    },
    line: {
      marker: {
        enabled: false,
        radius: 3
      }
    }
  },
  annotations: [],
  series: [
    {
      name: 'Réel',
      color: '#181632',
      data: [] // Data points should be in the form [timestamp, value]
    },
    {
      name: 'Prédit',
      color: '#ED9205',
      data: [] // Data points should be in the form [timestamp, value]
    }
  ]
});

const processData = (rawData, maeValue) => {
  const reelData = rawData.filter((item) => item.cas === 'reel').map((item) => {
    return [new Date(item.creneau).getTime(), item.value];
  });

  const preditData = rawData.filter((item) => item.cas === 'predit').map((item) => {
    return [new Date(item.creneau).getTime(), item.mean];
  });

  const sortedReelData = sortData(reelData);
  const sortedPredData = sortData(preditData);

  chartOptions.value.series[0].data = sortedReelData;
  chartOptions.value.series[1].data = sortedPredData;

  chartOptions.value.annotations = [{
    labels: [{
      point: {
        x: 100,
        y: 20
      },
      text: `MAE: ${maeValue.toFixed(2)}`,
      style: {
        fontSize: '18px',
        color: 'white',
        fontFamily: 'Roboto, sans-serif',
        fontWeight: 'bold'
      },
      backgroundColor: 'rgba(237, 146, 5, 0.75)',
      borderRadius: 5,
      borderWidth: 0,
      padding: 8,
    }],
    draggable: false

  }];
};

const sortData = (data) => {
  return data.sort((a, b) => a[0] - b[0]);
};

const fetchData = debounce(async () => {
  loading.value = true;
  try {
    const response = await api.get(`/data/reliability?dpt=${dpt.value}&type=${selectedType.value}&decoupe=${decoupe.value}&horizon=${horizon.value}`);
    data.value = response.data.data;
    mae.value = response.data.mae;
    processData(data.value, mae.value);
    dataReady.value = true;
    loading.value = false;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des données.", color: "red", position: "bottom", timeout: 2500 });
  } finally {
    loading.value = false;
  }
}, 700);

const fetchGeojson = debounce(async (selectedType) => {
  const typeValue = selectedType === 'Appels' || selectedType === 'Tous' ? 'TOUS' : selectedType;
  const geojsonURL = `${publicPath}${dpt.value}/${typeValue}.geojson`;

  try {
    const response = await fetch(geojsonURL);
    if (!response.ok) {
      notifyUser({ icon: "error", message: "Erreur lors de la récupration du GEOJSON.", color: "red", position: "bottom", timeout: 2500 });
    }
    const geojson = await response.json();
    const features = geojson.features.map(feature => ({
      label: feature.properties.nom,
      value: feature.properties.code_geom
    }));
    decoupes.value = features;
  } catch {
    notifyUser({ icon: "error", message: "Erreur lors de la récupration du GEOJSON.", color: "red", position: "bottom", timeout: 2500 });
    return [];
  }
});

onMounted(async () => {
  try {
    const response = await api.get(`/data/reliability-options?dpt=${dpt.value}`);
    dropdownData.value = response.data;
    types.value = dropdownData.value.map(item => {
      let type = item.type_interv;
      switch (type) {
        case 'CIS':
          return dpt.value === '25' ? 'CIS' : 'CIS-SAP';
        case 'CIS_INC':
          return 'CIS-INC';
        case 'appels':
          return 'Appels';
        default:
          return type;
      }
    });
    selectedType.value = types.value[0];
    fetchData();
    dataReady.value = true;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des options.", color: "red", position: "bottom", timeout: 2500 })
  }

  watch(selectedType, async (newType) => {
    if (newType) {
      fetchGeojson(newType);
      const typeIndex = types.value.indexOf(newType);
      if (typeIndex !== -1) {
        horizons.value = dropdownData.value[typeIndex].horizons;
        horizon.value = horizons.value[0];
      }
    }
    fetchData();
  });
});

const onTypeSelected = async (selected) => {
  selectedType.value = selected;
  const typeIndex = types.value.indexOf(selectedType.value);
  if (typeIndex !== -1) {
    horizons.value = dropdownData.value[typeIndex].horizons;
    horizon.value = horizons.value[0];
  }
  fetchGeojson(selectedType.value);
  loading.value = false;
};

const onDecoupeSelected = async (selected) => {
  decoupe.value = selected;
  fetchData();
};
const onHorizonSelected = async (selected) => {
  horizon.value = selected;
  fetchData();
};

const formatDate = (date) => {
  const shortMonths = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec'];

  // Show the date at midnight, otherwise show the hour
  if (date.getHours() === 0) {
    return `${shortMonths[date.getMonth()]} ${String(date.getDate()).padStart(2, '0')}`;
  } else {
    return `${String(date.getHours()).padStart(2, '0')}:00`;
  }
};


const formatTooltipDate = (date) => {
  return `${date.getDate().toString().padStart(2, '0')}/${(date.getMonth() + 1).toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
};
</script>
