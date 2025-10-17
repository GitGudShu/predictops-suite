<template>
  <div v-if="quality || alerts" class="quality-container">
    <QualityCard v-if="quality" v-for="qual in qualityData" :text="qual.value" :title="qual.label" :color="qual.color"
      :description="qual.description" />
    <QualityCard v-if="alerts" v-for="qual in alertsData" :text="qual.value" :title="qual.label" :color="qual.color"
      :icon="qual.icon" :title-icon="qual.titleIcon" />
  </div>
  <div class="controls" v-if="controls">
    <Dropdown v-if="indicators" btn-size="md-btn" :list="indicators" @update:selected="onIndicatorSelected" />
    <Dropdown v-show="horizonDropdown && mapTableToggle != 'history' && (type != 'delays' || !delaysPickedDates)"
      btn-size="md-btn" :list="horizons" @update:selected="onHorizonSelected" />
    <Dropdown v-if="geometriesDropdown && mapTableToggle != 'history'" btn-size="md-btn" :list="predictionsGeometries"
      @update:selected="onGeometrySelected" />

    <q-btn round flat color="transparent" icon="mdi-chevron-right" text-color="primary"
      v-if="(opacitySlider || satelliteToggle) && indicator != 'vitesse_vent'">
      <q-menu>
        <q-list style="min-width: 100px; color: black">
          <q-item>
            <div class="slider">
              <label>Opacité</label>
              <q-slider v-model="layerOpacity" :min="0" :max="0.9" :step="0" />
            </div>
          </q-item>
          <q-item>
            <q-toggle v-if="satelliteToggle" color="secondary" v-model="toggleSatellite" label="Vue satellite"
              left-label />
          </q-item>
        </q-list>
      </q-menu>
    </q-btn>
    <div class="map-table-toggle flex" v-if="layer && indicator != 'vitesse_vent'">

      <q-icon name="mdi-calendar" class="cursor-pointer q-mr-sm q-mt-sm" color="primary" v-if="type == 'delays'"
        size="sm">
        <q-popup-proxy transition-show="scale" transition-hide="scale">
          <q-date v-model="delaysPickedDates" mask="YYYY-MM-DD" range :options="(date) => date >= '2023/12/24'">
          </q-date>
        </q-popup-proxy>
      </q-icon>

      <q-btn-toggle size="md" outline unelevated v-model="mapTableToggle" toggle-color="info" text-color="primary"
        :options="toggleBtnsOptions" class="center">
        <template v-slot:map>
          <q-icon name="map"></q-icon>
        </template>
        <template v-slot:table>
          <q-icon name="mdi-table"></q-icon>
        </template>
        <template v-slot:history v-show="type == 'interventions_predictions'">
          <q-icon name="mdi-history"></q-icon>
        </template>
      </q-btn-toggle>
    </div>
    <q-btn-toggle v-if="type == 'cdc'" size="md" outline unelevated v-model="cdcType" toggle-color="info"
      text-color="primary" :options="toggleCdcTypeOptions">
    </q-btn-toggle>
  </div>
  <div id="windy" v-if="indicator === 'vitesse_vent'"></div>
  <highcharts :options="historyChartOptions" v-show="mapTableToggle == 'history'" />
  <div class="map-container-wrapper">
    <div class="in-map-cdc-table" v-if="type == 'cdc'" draggable="true">
      <Table :data="cdcTableData" :rows-per-page="10" :exclude-columns="['cs']" :columns="[{ field: 'fonction', label: 'Fonction' },
      { field: 'grade', label: 'Grade' },
      { field: 'nom', label: 'Nom' },
      { field: 'prenom', label: 'Prénom' }]" />
    </div>

    <div ref="mapContainer" class="map-container" :id="randomId" :style="{ height: height + 'px' }"
      v-show="mapTableToggle == 'map' && indicator != 'vitesse_vent'">
      <div v-if="type == 'delays' && delaysPickedDates != null" class="picked-delays flex items-center text-bold">
        <q-icon name="mdi-calendar" class="q-mr-sm" color="primary" size="xs"></q-icon>
        <span v-if="delaysPickedDates instanceof Object">{{ delaysPickedDates.from }} - {{ delaysPickedDates.to
          }}</span>
        <span v-else>{{ delaysPickedDates }}</span>
        <q-icon name="close" class="cursor-pointer q-ml-sm" color="primary" size="xs"
          @click="delaysPickedDates = null"></q-icon>
      </div>
      <q-btn size="md" icon="download" @click="exportCompleteMapAsImage" color="white" unelevated outline
        text-color="black" class="q-ma-sm download-map" />
      <ContinuousMapLegend :font-color="toggleSatellite ? 'white' : 'black'" v-if="indicator && legend"
        :indicator-type="indicator" />
      <DiscreteMapLegend v-if="type != 'weather' || type != 'fires' && legend" :indicator-type="type" />
      <transition name="slide">
        <div class="overlay" v-if="click" v-show="drawerOpen">
          <q-list separator v-if="type == 'weather'">
            <q-item v-for="indicator in indicators" :key="indicator"
              v-if="selectedHexagoneInfo[indicator] !== undefined & type != 'interventions_predictions'">
              <q-item-section>
                <q-item-label>
                  {{ indicatorsDropdownData[indicator] }} ({{ getUnit(indicatorsDropdownData[indicator]) }})
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-input filled readonly v-model="selectedHexagoneInfo[indicatorsDropdownData[indicator]]" />
              </q-item-section>
            </q-item>
          </q-list>
          <q-list separator v-if="type == 'delays' && Object.keys(selectedHexagoneInfo).length">
            <q-item v-for="(value, key) in Object.entries(selectedHexagoneInfo)" :key="key">
              <q-item-section>
                <q-item-label>{{ value[0] }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-input filled readonly :model-value="value[1]" />
              </q-item-section>
            </q-item>
          </q-list>
          <q-list separator v-if="type == 'interventions_predictions' && Object.keys(selectedCISInfo).length">
            <q-item v-for="(value, key) in Object.entries(selectedCISInfo)" :key="key">
              <q-item-section>
                <q-item-label>{{ value[0] }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-input filled readonly :model-value="value[1]" />
              </q-item-section>
            </q-item>
          </q-list>
          <q-btn label="Fermer" color="secondary" @click="closeDrawer" :style="{ margin: 'auto' }" />
        </div>
      </transition>
      <HeightMeasureGraph v-if="selectedStation" :station-name="selectedStation" @close="selectedStation = null"
        :type="type" />
      <q-inner-loading :showing="loading" style="z-index: 10000;">
        <q-spinner-tail size="50px" color="primary" />
      </q-inner-loading>
      <div></div>
    </div>
    <div class="side-panel" v-if="polarBars && mapTableToggle == 'map'">
      <PolarBarsSide :key="geometries" :geometries="geometries" :uuid="uuid" />
    </div>
  </div>
  <Table :data="tableData" :rows-per-page="5" v-if="mapTableToggle == 'table'" :loading="tableLoading"
    :exclude-columns="excludedColumns" />
</template>

<script setup>
import { ref, onMounted, computed, watch } from "vue"
import Table from 'src/components/Table.vue'
import QualityCard from 'src/components/QualityCard.vue'
import Dropdown from "src/components/Dropdown.vue"
import Button from "./Button.vue"
import HeightMeasureGraph from "src/components/HeightMeasureGraph.vue"
import ContinuousMapLegend from "src/components/ContinuousMapLegend.vue"
import DiscreteMapLegend from "./DiscreteMapLegend.vue"
import PolarBarsSide from "./PolarBarsSide.vue"
import { notifyUser } from "src/utils/notifyUser"
import 'ol/ol.css'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import OSM from 'ol/source/OSM'
import VectorLayer from 'ol/layer/Vector'
import VectorImageLayer from 'ol/layer/VectorImage';
import VectorSource from 'ol/source/Vector'
import HeatmapLayer from 'ol/layer/Heatmap'
import { Feature } from 'ol'
import { Point } from 'ol/geom'
import GeoJSON from 'ol/format/GeoJSON'
import XYZ from 'ol/source/XYZ'
import { fromLonLat } from "ol/proj"
import { Fill, Stroke, Style, Circle, Text } from 'ol/style'
import chroma from 'chroma-js'
import { api } from "src/boot/axios"
import axios from 'axios'
import Overlay from 'ol/Overlay'
import { bbox as bboxStrategy } from 'ol/loadingstrategy';
import { transformExtent } from 'ol/proj';
import html2canvas from 'html2canvas';
import { formatHistory, formatPredictions } from "src/utils/areasplineUtils"
import { useRoute } from "vue-router"

const location = useRoute();

const props = defineProps({
  type: String,
  geometries: String,
  contour: Boolean,
  hexagones: Boolean,
  firePredictionMethod: String,
  click: Boolean,
  hover: Boolean,
  height: Number,
  controls: Boolean,
  opacitySlider: Boolean,
  satelliteToggle: Boolean,
  horizonDropdown: Boolean,
  geometriesDropdown: Boolean,
  legend: Boolean,
  quality: Boolean,
  alerts: Boolean,
  polarBars: Boolean,
  cdcType: {
    type: String,
    default: 'grps'
  },
  zoomDuration: {
    type: Number,
    default: 1000
  },
  defaultView: {
    type: String,
    default: "map"
  },
  uuid: String,
})

const loading = ref(false)

const publicPath = process.env.PUBLIC_PATH || '/predictops/'

const geoserverWorkspace = props.type != "delays" && ["development", "preprod"].includes(process.env.CONTEXT) ? "predictops_test" : "predictops"
// const geoserverWorkspace = "predictops"

const dpt = computed(() => {
  return localStorage.getItem("dpt") || location.params.dpt
})

const excludedColumns = ref([])

const tableLoading = ref(false)

const options = {
  key: process.env.WINDY_API_KEY
};

const toggleBtnsOptions = ref([
  { value: 'map', slot: 'map' },
  { value: 'table', slot: 'table' },
])

const cdcType = ref(props.cdcType)

const toggleCdcTypeOptions = ref([
  { value: 'grps', label: 'Groupements' },
  { value: 'cdg', label: 'Chefs de groupe' },
])

const mapTableToggle = ref(props.defaultView)

if (props.type === "interventions_predictions" && props.geometries != 'AGGLO' && props.geometries != 'SUAP') {
  toggleBtnsOptions.value.push({ value: 'history', slot: 'history' })
  if (props.defaultView == 'history') {
    setTimeout(() => {
      mapTableToggle.value = 'history'
    }, 1000)
  }

}
else {
  mapTableToggle.value = 'map'
}

const showDelaysDatePicker = ref(false)
const delaysPickedDates = ref(null)

const map = ref()

const vectorSource = ref()
const vectorLayer = ref()

const highlightSource = ref()
const highlightLayer = ref()

const heatmapLayer = ref()

const dptGeoJSONURL = `${publicPath}departement_${dpt.value}.geojson`

const contourSource = new VectorSource({
  format: new GeoJSON(),
  url: dptGeoJSONURL
})

const contourLayer = new VectorLayer({
  source: contourSource,
  style: new Style({
    fill: new Fill({
      color: 'rgba(188, 210, 247, 0.1)'
    }),
    stroke: new Stroke({
      color: 'black'
    })
  }),
  zIndex: 3
})


const layer = ref()

const randomId = computed(() => generateRandomId())

const generateRandomId = function (length = 6) {
  return Math.random().toString(36).substring(2, length + 2);
};

const delaysData = ref()


const chainOfCommandData = ref()
const cdcTableData = ref()

const tableData = ref()

const alertsData = ref([])

const colorMap = {
  "1": "#23a97b",
  "2": "#fed330",
  "3": "#ed9205",
  "4": "#c92a2a",
  'green': '#23a97b',
  'yellow': '#fed330',
  'orange': '#ed9205',
  'red': '#c92a2a',
}

const drawerOpen = ref(false)
const selectedHexagoneInfo = ref({})
const selectedCISInfo = ref({})
const selectedStation = ref(null)
const selectedPointInfo = ref({})
const mapping = ref({})
const delaysDate = ref(new Date().toLocaleDateString("es-CL"))

const timeRanges = [
  "01h-03h", "03h-05h", "05h-07h", "07h-09h",
  "09h-11h", "11h-13h", "13h-15h", "15h-17h",
  "17h-19h", "19h-21h", "21h-23h", "23h-01h"
];

const geoserverBaseUrl = "https://dashboard.predictops.fr/geoserver/"
// const geoserverBaseUrl = "http://localhost:8080/geoserver/"
const horizon = ref()
const horizons = ref()

const predictionsGeometries = ref(dpt.value === "78" ? { 'CIS': 'CIS', 'Tous': 'Tous' } : { 'SAP': 'CIS', 'INC': 'CIS-INC', 'Tous': 'Tous' })
const geometries = ref(props.geometries)
const qualityData = ref({})


function closeDrawer() {
  drawerOpen.value = false
  highlightSource.value.clear()
}

async function fetchTimeRanges() {
  try {
    const response = await api.get(`/data/time-ranges?dpt=${dpt.value}&type=${props.geometries}&uuid=${props.uuid}`);
    if (response.status === 200) {
      return response.data;
    } else {
      notifyUser({ icon: "error", message: "Erreur lors de la récupération tranches horaires.", color: "red", position: "bottom", timeout: 2500 })
      return [];
    }
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la création des tranches horaires.", color: "red", position: "bottom", timeout: 2500 })
    return [];
  }
}

function getCurrentAndNextTimeRanges() {

  const now = new Date();
  const currentHour = now.getHours();
  let currentRangeIndex;

  // Calculate the current range index based on the current hour
  if (currentHour === 23 || currentHour < 1) {
    // Special case for 23h-01h range
    currentRangeIndex = 11;
  } else {
    // General case for all other time ranges
    currentRangeIndex = Math.floor((currentHour - 1) / 2);
  }

  const resultingRanges = [];

  // Add the current time range and the next 5 time ranges to the array
  for (let i = 0; i <= 5; i++) {
    const index = (currentRangeIndex + i) % timeRanges.length;
    resultingRanges.push(timeRanges[index]);
    return resultingRanges;
  }
}


const historyData = ref()
const processedHistory = ref()
const historyChartOptions = ref({
  chart: {
    type: 'areaspline',
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



const getHorizon = (horizon) => {
  if (horizon === "Aujourd'hui") {
    return "today"
  }
  else if (horizon === "Demain") {
    return "tomorrow"
  }
  else {
    return horizon
  }
}

const onHorizonSelected = (selected) => {
  horizon.value = getHorizon(selected)
}

const indicators = ref()
const indicator = ref()
const indicatorsDropdownData = ref()

const onIndicatorSelected = (selected) => {
  if (selected === 'Vitesse du vent') {
    horizons.value = ['3h', '6h', '9h', '12h']
    windyInit(options, windyAPI => {

      const { map } = windyAPI;
      fetch(dptGeoJSONURL)
        .then(response => response.json())
        .then(data => {
          // Create a GeoJSON layer and add it to the map
          const geoJsonLayer = L.geoJson(data, {
            style: () => ({
              fillColor: 'rgba(188, 210, 247, 0.1)',
              weight: 2,
              opacity: 1,
              color: 'black',
              fillOpacity: 0.1
            })
          }).addTo(map);

          map.flyToBounds(geoJsonLayer.getBounds(), { duration: 1.5 });
        });

      let delaysLayer;

      watch(horizon, () => {
        if (delaysLayer) {
          map.removeLayer(delaysLayer)
        }
        const wfsURL = `${geoserverBaseUrl}ows?service=WFS&version=1.0.0&request=GetFeature&typeName=predictops:delays_hexagones_${horizon.value}_${dpt.value}&outputFormat=application/json`;
        fetch(wfsURL)
          .then(response => response.json())
          .then(geoJsonData => {
            delaysLayer = L.geoJson(geoJsonData, {
              style: feature => ({
                fillColor: feature.properties.color,
                weight: 2,
                opacity: 1,
                color: 'black',
                fillOpacity: 0.5
              }),

            }).addTo(map);
          });
      }, { immediate: true })
    });
  }
  else {
    horizons.value = ["Aujourd'hui", 'Demain']
  }
  if (props.type === 'fires') {
    indicator.value = selected
  }
  if (props.type === 'weather') {
    indicator.value = indicatorsDropdownData.value[selected]
  }

  colors.value = mapping.value[indicator.value][2]
  range.value = mapping.value[indicator.value][1]
  domain.value = [range.value[0], range.value.slice(-1)[0]]
  colorScale.value = chroma.scale(colors.value).domain(domain.value)
}

const onGeometrySelected = (selected) => {
  geometries.value = selected
}

const colors = ref()
const range = ref()
const domain = ref()
const colorScale = ref()
const averageColor = ref()

const constructWFSObject = (layer) => {
  return {
    format: new GeoJSON(),
    url: function (extent) {
      return (
        `${geoserverBaseUrl}wfs?service=WFS&` +
        `version=1.1.0&request=GetFeature&typename=${geoserverWorkspace}:${layer}&` +
        `outputFormat=application/json&bbox=${transformExtent(extent, 'EPSG:3857', 'EPSG:4326').join(',')},EPSG:4326`
      );
    },
    strategy: bboxStrategy,
  }
}

function formatNumber(value) {
  if (!isNaN(parseFloat(value)) && isFinite(value)) {
    return parseFloat(value).toFixed(2)
  }
  return value
}

function getUnit(indicator) {
  const units = {
    'temperature': '°C',
    'vitesse_vent': 'km/h',
    'humidite': '%',
    'neige': 'cm',
    'precipitations': 'mm',
  }
  return units[indicator] || ''
}


const layerOpacity = ref(0.5)

const toggleSatellite = ref(false)

const mapContainer = ref(null)



function generateUniqueId(prefix = 'info') {
  return `${prefix}-${Math.random().toString(36).substring(2, 9)}`
}


const exportCompleteMapAsImage = async () => {
  const mapContainerElement = document.getElementById(`${randomId.value}`)

  try {
    const canvas = await html2canvas(mapContainerElement, {
      useCORS: true,
      logging: true,
      scale: 2,
    });

    canvas.getContext("2d", {
      willReadFrequently: true,
    });

    // Convert canvas to an image and trigger download
    canvas.toBlob((blob) => {
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${layer.value || props.type}-map.png`
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }, 'image/png');
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération de l'export de la carte.", color: "red", position: "bottom", timeout: 2500 })
  }
};

function parseTimeRange(range) {
  const [start, end] = range.split('-');
  return {
    start: parseInt(start.replace('h', '')),
    end: parseInt(end.replace('h', '')),
  };
}

const createPointFeature = (data, getStyle, prop, colorMap) => {
  const feature = new Feature({
    geometry: new Point(fromLonLat([data.long, data.lat])),
  })


  // Attach all data properties to the feature, excluding geometry information.
  Object.keys(data).forEach(key => {
    if (key !== 'long' && key !== 'lat') {
      if (typeof data[key] !== "object") {
        feature.set(key, data[key])
      }
    }
  })

  const style = getStyle(data, prop, colorMap)
  feature.setStyle(style)

  return feature
}


onMounted(async () => {
  mapping.value = await (await api.get("/static/mapping.json")).data
  const dptHexagonesURL = `${publicPath}hexagones_${dpt.value}.geojson`
  const dptGeoJSON = await (await fetch(dptGeoJSONURL)).json()
  const waterwaysURL = `${publicPath}waterways_${dpt.value}.geojson`
  const departmentFeature = new GeoJSON().readFeature(dptGeoJSON, {
    dataProjection: 'EPSG:4326',
    featureProjection: 'EPSG:3857'
  })
  const extent = departmentFeature.getGeometry().getExtent()
  if (props.type === 'delays') {
    horizons.value = ['3h', '6h', '9h', '12h'];
    horizon.value = horizons.value[0];
  } else if (props.type === 'interventions_predictions') {
    horizons.value = await fetchTimeRanges();
    horizon.value = horizons.value[0];
  }
  else if (props.type === 'vigicrues') {
    horizons.value = getCurrentAndNextTimeRanges();
    horizon.value = horizons.value[0];
  }
  else {
    horizons.value = ['Aujourd\'hui', 'Demain'];
    horizon.value = horizons.value[0];
  }
  const alertsResponse = await api.get(`/data/alerts?dpt=${dpt.value}&uuid=${props.uuid}`)
  alertsData.value = alertsResponse.data
  alertsData.value.sort((a, b) => (a.label > b.label) ? 1 : -1);



  const getTableData = async (layer) => {
    try {
      const response = await axios.get(`${geoserverBaseUrl}wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=${geoserverWorkspace}:${layer}&outputFormat=application/json`);
      const features = response.data.features;
      const propertiesArray = features.map(feature => {
        const properties = feature.properties
        for (let key in properties) {
          if (typeof properties[key] === 'number') {
            properties[key] = Math.round(properties[key])
          }
        }
        return properties
      });

      return propertiesArray;
    } catch (e) {
      notifyUser({ icon: "error", message: "Erreur lors de la récupération des données du tableau.", color: "red", position: "bottom", timeout: 2500 })
      return [];
    }
  };

  const aggregateTableData = async (timeRanges) => {
    tableLoading.value = true
    try {
      const aggregatedData = [];

      for (const timeRange of timeRanges) {
        const layer = `${props.type}_${geometries.value}_${timeRange}_${dpt.value}`;
        const data = await getTableData(layer);
        aggregatedData.push(...data);
      }

      // Group by 'centre' and sum 'value'
      const groupedData = aggregatedData.reduce((acc, curr) => {
        const centre = curr.centre;
        if (!acc[centre]) {
          acc[centre] = { ...curr, tranche: "Toutes" };
        } else {
          acc[centre].value += curr.value;
        }
        return acc;
      }, {});

      // Convert the grouped data object back to an array
      tableData.value = Object.values(groupedData);
      tableLoading.value = false
    } catch (e) {
      tableLoading.value = false
      notifyUser({ icon: "error", message: "Erreur lors de l'aggregation des données du tableau.", color: "red", position: "bottom", timeout: 2500 })
    }
  };



  const constructWMSObject = (layer, style) => {
    return {
      url: `${geoserverBaseUrl}/wms`,
      params: { 'LAYERS': `${geoserverWorkspace}:${layer}`, 'TILED': true, 'STYLES': style },
      serverType: 'geoserver',
      crossOrigin: 'anonymous',
    }
  }

  const createPointStyle = (data, prop, colorMap) => {
    let color;
    let radius;
    if (prop === undefined) {
      color = "#74c0fc",
        radius = 6
    }
    else {
      color = colorMap[data[prop].toString()]
      radius = 4
    }
    return new Style({
      image: new Circle({
        radius: radius,
        fill: new Fill({ color: color }),
        stroke: new Stroke({
          color: 'black',
        })
      }),
    })
  }


  const layers = ref([
    new TileLayer({
      source: new OSM(),
      visible: false,
    })
  ])

  const osmLayer = new TileLayer({
    source: new XYZ({
      attributions: '@OpenStreetMap contributors, @CARTO',
      url: 'https://cartodb-basemaps-a.global.ssl.fastly.net/rastertiles/voyager/{z}/{x}/{y}.jpg',
      // url: 'https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/{z}/{x}/{y}.jpg',
      visible: true,
      crossOrigin: 'anonymous'
    })
  })

  layers.value.push(osmLayer)

  const satelliteLayer = new TileLayer({
    source: new XYZ({
      attributions: '@MapTiler',
      url: 'https://api.maptiler.com/maps/satellite/{z}/{x}/{y}.jpg?key=rmBDquxIaSuC3uGIdqI0',
    })
  })

  layers.value.push(satelliteLayer)
  satelliteLayer.setVisible(toggleSatellite.value)

  if (props.type === "fires" && props.firePredictionMethod === "canada") {
    const response = await api.get(`/data/radioitems?page=fire-map-v2&uuid=${props.uuid}`)
    indicatorsDropdownData.value = response.data["radioitems"]
    indicators.value = Object.keys(indicatorsDropdownData.value).map(key => ({
      label: key,
      value: indicatorsDropdownData.value[key].value,
      tooltip: indicatorsDropdownData.value[key].tooltip,
    }));
    indicator.value = indicators.value[0].value;
    // indicator.value = "fwi"
    colors.value = mapping.value[indicator.value][2]
    range.value = mapping.value[indicator.value][1]
    domain.value = [range.value[0], range.value.slice(-1)[0]]
    colorScale.value = chroma.scale(colors.value).domain(domain.value)
    averageColor.value = chroma.average(colors.value)
  }

  if (props.type === "fires" && props.firePredictionMethod === "sad") {
    indicator.value = "fire_prediction"
    colors.value = mapping.value[indicator.value][2]
    range.value = mapping.value[indicator.value][1]
    domain.value = [range.value[0], range.value.slice(-1)[0]]
    colorScale.value = chroma.scale(colors.value).domain(domain.value)
    averageColor.value = chroma.average(colors.value)
  }

  if (props.type === "weather") {
    const response = await api.get(`/data/radioitems?page=weather-map&uuid=${props.uuid}`);
    indicatorsDropdownData.value = response.data["radioitems"];
    indicators.value = Object.keys(indicatorsDropdownData.value);

    // Reorder the array so "Temperature" is first, if it exists
    if (indicators.value.includes("Temperature")) {
      indicators.value = [
        "Temperature",
        ...indicators.value.filter(item => item !== "Temperature")
      ];
    }

    // Set the default indicator after reordering
    indicator.value = indicatorsDropdownData.value[indicators.value[0]];
    colors.value = mapping.value[indicator.value][2];
    range.value = mapping.value[indicator.value][1];
    domain.value = [range.value[0], range.value.slice(-1)[0]];
    colorScale.value = chroma.scale(colors.value).domain(domain.value);
    averageColor.value = chroma.average(colors.value);
  }


  if (props.type === "air") {
    const response = await api.get(`/data/air-quality?dpt=${dpt.value}&uuid=${props.uuid}`)
    const airQualityData = response.data
    const features = airQualityData.map(point => {
      const feature = createPointFeature(point, createPointStyle, "code_qual", colorMap)
      feature.set('isAirQualityFeature', true)
      return feature
    })
    vectorSource.value = new VectorSource({
      features: features
    })
    vectorLayer.value = new VectorLayer({
      source: vectorSource.value,
      zIndex: 5
    })
    layers.value.push(vectorLayer.value)
  }

  if (props.hexagones) {
    const hexagonesSource = new VectorSource({
      format: new GeoJSON(),
      url: dptHexagonesURL
    })

    const hexagonesLayer = new VectorImageLayer({
      source: hexagonesSource,
      style: new Style({
        stroke: new Stroke({
          color: 'rgba(111, 152, 222, 1)',
        }),
      }),
      opacity: 0.5
    })

    layers.value.push(hexagonesLayer)
  }

  if (props.type === "vigicrues") {
    const response = await api.get(`/data/vigicrues?dpt=${dpt.value}&uuid=${props.uuid}`)
    const vigicruesData = response.data
    const features = vigicruesData.map(point => {
      const feature = createPointFeature(point, createPointStyle, "vigilance", colorMap)
      feature.set('isVigicruesFeature', true)
      return feature
    })

    vectorSource.value = new VectorSource({
      features: features,
    })
    vectorLayer.value = new VectorLayer({
      source: vectorSource.value,
      zIndex: 1000
    })
    layer.value = `interventions_predictions_INONDATION_${horizon.value}_${dpt.value}`
    const floodsSource = new VectorSource(constructWFSObject(layer.value))
    const floodsLayer = new VectorImageLayer({
      source: floodsSource,
      opacity: 0.5,
      style: function (feature) {
        const color = feature.get("couleur")
        return new Style({
          fill: new Fill({
            color: colorMap[color]
          }),
          stroke: new Stroke({
            color: 'white'
          })
        })
      }
    })
    const waterwaysSource = new VectorSource({
      format: new GeoJSON(),
      url: waterwaysURL
    })
    const waterwaysLayer = new VectorImageLayer({
      source: waterwaysSource,
      style: new Style({
        stroke: new Stroke({
          color: '#74c0fc',
          width: 2
        })
      }),
      zIndex: 2
    })
    layers.value.push(waterwaysLayer)
    layers.value.push(floodsLayer)
    layers.value.push(vectorLayer.value)
  }
  if (props.type === "groundwater") {
    const response = await api.get(`/data/viginappes?dpt=${dpt.value}&uuid=${props.uuid}`)
    const groundwaterData = response.data
    const features = groundwaterData.map(point => {
      const feature = createPointFeature(point, createPointStyle, undefined, colorMap)
      feature.set('isGroundwaterFeature', true)
      return feature
    })

    vectorSource.value = new VectorSource({
      features: features,
    })
    vectorLayer.value = new VectorLayer({
      source: vectorSource.value,
      zIndex: 1000
    })
    const waterwaysSource = new VectorSource({
      format: new GeoJSON(),
      url: waterwaysURL
    })
    const waterwaysLayer = new VectorImageLayer({
      source: waterwaysSource,
      style: new Style({
        stroke: new Stroke({
          color: '#74c0fc',
          width: 2
        })
      }),
      zIndex: 2
    })

    layers.value.push(waterwaysLayer)
    layers.value.push(vectorLayer.value)
  }

  if (props.contour) {
    layers.value.push(contourLayer)
  }

  if (props.type == "weather" || props.type == "fires") {
    layer.value = `${props.type}_${geometries.value}_${horizon.value}_${dpt.value}`
    vectorSource.value = new VectorSource(constructWFSObject(layer.value))
    if (props.type === "weather") {
      excludedColumns.value = ['index', 'hex_id', 'geometry', 'index_right', 'wikipedia', 'surf_km2', 'distance', 'code_insee', 'nuts3', 'nom', 'dwpt', 'pres',
        'prec24h12', 'temp16', 'dwpt16', 'rhum16', 'prcp16', 'wdir16', 'wspd16', 'prec24h16', 'temp12', 'dwpt12', 'rhum12', 'prcp12', 'wdir12', 'wspd12', 'temp15h',
        'rhum15h', 'temp12h', 'rhum12', 'temp24max', 'prec24veille', 'sum_last_7_days', 'sum_consecutive_rainfall', 'dc', 'days_since_rain', 'ffmc', 'dmc', 'isi',
        'bui', 'fwi', 'daily_severity_rating', 'nesterov', 'munger', 'kbdi', 'angstroem', 'departement_encoding', 'prec24h', 'rhum12h', 'timestamp']
    }
    if (props.type === "fires") {
      excludedColumns.value = ['index', 'hex_id', 'geometry', 'index_right', 'wikipedia', 'surf_km2', 'distance', 'code_insee', 'nuts3', 'nom', 'dwpt', 'pres',
        'prec24h12', 'temp16', 'dwpt16', 'rhum16', 'prcp16', 'wdir16', 'wspd16', 'prec24h16', 'temp12', 'dwpt12', 'rhum12', 'prcp12', 'wdir12', 'wspd12', 'temp15h',
        'rhum15h', 'temp12h', 'rhum12', 'temp24max', 'prec24veille', 'sum_last_7_days', 'sum_consecutive_rainfall', 'dc', 'days_since_rain', 'ffmc', 'dmc', 'isi',
        'bui', 'fwi', 'daily_severity_rating', 'nesterov', 'munger', 'kbdi', 'angstroem', 'departement_encoding', 'prec24h', 'rhum12h', 'neige', 'timestamp']
    }
    tableLoading.value = true
    getTableData(layer.value).then(data => {
      tableData.value = data;
      tableLoading.value = false;
    });

    vectorLayer.value = new VectorImageLayer({
      source: vectorSource.value,
      style: hexagonesStyleFunction,
      opacity: layerOpacity.value
    })

    highlightSource.value = new VectorSource()
    highlightLayer.value = new VectorLayer({
      source: highlightSource.value,
      style: new Style({
        stroke: new Stroke({ color: "black" }),
      })
    })
    layers.value.push(vectorLayer.value)
    layers.value.push(highlightLayer.value)
  }
  const fetchDelaysData = async (start, end, uuid) => {
    loading.value = true
    try {
      const response = await api.get(`/data/delays?dpt=${dpt.value}&start=${start}&stop=${end}&uuid=${uuid}`)
      delaysData.value = response.data
      qualityData.value = delaysData.value.quality
      loading.value = false
    } catch (error) {
      notifyUser({ icon: "error", message: "Erreur lors de la récupération des retards.", color: "red", position: "bottom", timeout: 2500 })
      loading.value = false
    }
  }
  const fetchQualityData = async () => {
    try {
      const response = await api.get(`/data/quality?dpt=${dpt.value}&horizon=${horizon.value}&uuid=${props.uuid}`)
      qualityData.value = response.data
    } catch (error) {
      notifyUser({ icon: "error", message: error, color: "red", position: "bottom", timeout: 2500 })
    }
  }
  if (props.type == "delays") {
    watch(delaysPickedDates, async () => {
      if (!delaysPickedDates.value) {
        await fetchQualityData()
        if (heatmapLayer.value) {
          map.value.removeLayer(heatmapLayer.value);
          heatmapLayer.value = null;
        }
        layer.value = `${props.type}_${geometries.value}_${horizon.value}_${dpt.value}`
        vectorSource.value = new VectorSource(constructWFSObject(layer.value))

        excludedColumns.value = ['color', 'on_time_interventions']

        tableLoading.value = true
        getTableData(`delays_hexagones_12h_${dpt.value}`).then(data => { tableData.value = data; tableLoading.value = false; });


        vectorLayer.value = new VectorImageLayer({
          source: vectorSource.value,
          opacity: 0.9,
          style: function (feature) {
            const color = feature.get("color");
            const delays = feature.get("delayed_interventions");
            const delaysText = delays > 0 ? delays.toString() : '';

            return new Style({
              fill: new Fill({
                color: colorMap[color]
              }),
              stroke: new Stroke({
                color: 'white'
              }),
              text: new Text({
                font: 'Roboto,sans-serif',

                fill: new Fill({
                  color: '#fff'
                }),
                stroke: new Stroke({
                  color: 'black',
                  width: 3
                }),
                text: delaysText,
                overflow: false,
                offsetX: 0,
                offsetY: 0,
                placement: 'point',
                textAlign: 'center',
                textBaseline: 'middle'
              })
            });
          }
        })

        highlightSource.value = new VectorSource()
        highlightLayer.value = new VectorLayer({
          source: highlightSource.value,
          style: new Style({
            stroke: new Stroke({ color: "black" }),
          })
        })
        layers.value.push(vectorLayer.value)
        layers.value.push(highlightLayer.value)
        if (map.value) {
          map.value.addLayer(vectorLayer.value)
          map.value.addLayer(highlightLayer.value)
        }
      }
      else if (delaysPickedDates.value instanceof Object) {
        await fetchDelaysData(delaysPickedDates.value.from, delaysPickedDates.value.to, props.uuid)
        if (heatmapLayer.value) {
          map.value.removeLayer(heatmapLayer.value)
        }
        heatmapLayer.value = new HeatmapLayer({
          source: new VectorSource({
            features: new GeoJSON().readFeatures(delaysData.value, { dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857' }),
          }),
          radius: 10,
          blur: 10,
          weight: function (feature) {
            const weight = feature.get("weight");
            return weight;
          }
        })
        layers.value.push(heatmapLayer.value)
        if (map.value) {
          map.value.addLayer(heatmapLayer.value)
          map.value.removeLayer(vectorLayer.value)
          map.value.removeLayer(highlightLayer.value)
        }
      }
      else if (delaysPickedDates.value instanceof String || typeof delaysPickedDates.value === 'string') {
        await fetchDelaysData(delaysPickedDates.value, delaysPickedDates.value, props.uuid)
        if (heatmapLayer.value) {
          map.value.removeLayer(heatmapLayer.value)
        }
        heatmapLayer.value = new HeatmapLayer({
          source: new VectorSource({
            features: new GeoJSON().readFeatures(delaysData.value, { dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857' }),
          }),
          radius: 10,
          blur: 30,
          weight: function (feature) {
            const weight = feature.get("weight");
            return weight;
          }
        })
        layers.value.push(heatmapLayer.value)
        if (map.value) {
          map.value.addLayer(heatmapLayer.value)
          map.value.removeLayer(vectorLayer.value)
          map.value.removeLayer(highlightLayer.value)
        }
      }
    }, { deep: true, immediate: true })


  }


  if (props.type == "interventions_predictions") {
    layer.value = `${props.type}_${geometries.value}_${horizon.value}_${dpt.value}`
    vectorSource.value = new VectorSource(constructWFSObject(layer.value))
    excludedColumns.value = ['id', 'couleur', 'timestamp']
    aggregateTableData(timeRanges);

    const historyResponse = await api.get(`/data/history?dpt=${dpt.value}&uuid=${props.uuid}`);
    const predictionsResponse = await api.get(`/data/future-predictions?dpt=${dpt.value}&uuid=${props.uuid}`);
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

    vectorLayer.value = new VectorImageLayer({
      source: vectorSource.value,
      opacity: 0.75,
      style: function (feature) {
        const color = feature.get("couleur")
        return new Style({
          fill: new Fill({
            color: colorMap[color]
          }),
          stroke: new Stroke({
            color: 'white'
          })
        })
      }
    })

    highlightSource.value = new VectorSource()
    highlightLayer.value = new VectorLayer({
      source: highlightSource.value,
      style: new Style({
        stroke: new Stroke({ color: "black" }),
      })
    })

    layers.value.push(vectorLayer.value)
    layers.value.push(highlightLayer.value)

  }

  if (props.type == "cdc") {
    const response = await api.get(`/data/chain-of-command?dpt=${dpt.value}&uuid=${props.uuid}`);
    chainOfCommandData.value = response.data;
    cdcTableData.value = chainOfCommandData.value.filter(item => item.cs === "EM");

    const centroidsLayer = new VectorLayer({
      source: new VectorSource({
        features: [] // Initialize with an empty array of features
      }),
      style: function (feature) {
        const cs = feature.get("CODE_CS");
        const grade = feature.get("grade");
        const nom = feature.get("nom");
        const prenom = feature.get("prenom");

        const csStr = cs ? cs : "";
        const gradeStr = grade ? grade : "";
        const nomStr = nom ? nom : "";
        const prenomStr = prenom ? prenom[0] + ". " : "";
        const text = `${csStr}\n${gradeStr}\n${prenomStr}${nomStr}`;

        return new Style({

          text: new Text({
            font: 'bold 14px sans-serif',
            fill: new Fill({
              color: '#fff'
            }),
            stroke: new Stroke({
              color: 'black',
              width: 3
            }),
            text: text,
            overflow: true,
            scale: 1.1,
            padding: [5, 5, 5, 5],
          })
        });
      },
      zIndex: 5,
    });

    // Initialize vectorLayer without a source at first
    vectorLayer.value = new VectorImageLayer({
      style: function (feature) {

        return new Style({
          fill: new Fill({
            color: "#b8e994"
          }),
          stroke: new Stroke({
            color: 'white',
            width: 2
          }),

        });
      },
      zIndex: 2,
    });

    layers.value.push(vectorLayer.value);
    layers.value.push(centroidsLayer);

    // Watch for changes in cdcType and recreate vectorSource with updated URL
    watch(cdcType, () => {
      const newUrl = `${publicPath}${dpt.value}/${cdcType.value}.geojson`;
      const newCentroidsUrl = `${publicPath}${dpt.value}/${cdcType.value}_centroides.geojson`;
      // Recreate vectorSource with the new URL
      vectorSource.value = new VectorSource({
        format: new GeoJSON(),
        url: newUrl,
      });

      const centroidsSource = new VectorSource({
        url: newCentroidsUrl,
        format: new GeoJSON(),
      })

      centroidsSource.on('featuresloadend', () => {
        const features = centroidsSource.getFeatures();
        features.forEach((feature) => {
          const codeCs = feature.get('CODE_CS');
          const matchingData = chainOfCommandData.value.find(data => data.cs === codeCs);
          if (matchingData) {
            feature.setProperties({
              etat_admin: matchingData.etat_admin,
              fonction: matchingData.fonction,
              grade: matchingData.grade,
              nom: matchingData.nom,
              prenom: matchingData.prenom,
            });
          }
        });
      })


      // Set the updated vectorSource to the layer
      vectorLayer.value.setSource(vectorSource.value);
      centroidsLayer.setSource(centroidsSource);


    }, { immediate: true });
  }



  map.value = new Map({
    target: mapContainer.value,
    layers: layers.value,
    view: new View({
      center: new fromLonLat([2.432708043560393, 46.568368777322884]),
      zoom: 6,
    }),
  })




  const createOverlay = () => {
    const uniqueId = generateUniqueId()
    const overlayDiv = document.createElement('div')
    overlayDiv.id = uniqueId
    overlayDiv.style = 'background: black;  padding: 5px;  border: 1px; solid black;  display: block; color: white'
    document.body.appendChild(overlayDiv)
    const infoOverlay = new Overlay({
      element: document.getElementById(uniqueId),
      positioning: 'bottom-center',
      stopEvent: false,
      offset: [0, 75],
    })

    map.value.addOverlay(infoOverlay)
    return { "infoOverlay": infoOverlay, "uniqueId": uniqueId }
  }

  function hexagonesStyleFunction(feature) {

    const value = feature.get(indicator.value)
    const fillColor = colorScale.value(Math.round(value * 10) / 10).alpha(0.8).css();

    const style = new Style({
      fill: new Fill({ color: fillColor }),
      stroke: new Stroke({ color: averageColor.value, width: 1 })
    });

    return style
  }


  if (props.click && props.type == "weather" || props.type == "interventions_predictions" || props.type == "delays") {

    let selectedFeaturesIds = []
    const featureCache = {};

    map.value.on('click', async (evt) => {
      const coordinate = evt.coordinate;
      const viewResolution = map.value.getView().getResolution()
      const tolerance = 0.01 * viewResolution

      const bbox = [coordinate[0] - tolerance, coordinate[1] - tolerance, coordinate[0] + tolerance, coordinate[1] + tolerance]
      const precision = 4
      const bboxKey = bbox.map(coord => coord.toFixed(precision)).join(',')


      try {
        let data = featureCache[bboxKey];
        if (!data) {
          data = await fetchFeatures(bbox);
          featureCache[bboxKey] = data;
        }
        const features = new GeoJSON().readFeatures(data)
        if (features.length > 0) {
          features.forEach((feature) => {
            let geometry = feature.getGeometry()
            if (geometry) {
              geometry = geometry.clone().transform('EPSG:4326', 'EPSG:3857')
              feature.setGeometry(geometry)
            }
          })
          const feature = features[0]
          const featureId = feature.getId()
          if (selectedFeaturesIds.includes(featureId)) {
            highlightSource.value.clear()
            highlightSource.value.removeFeature(feature)
            selectedFeaturesIds = selectedFeaturesIds.filter(id => id !== featureId)
            drawerOpen.value = false
          } else {
            highlightSource.value.clear()
            highlightSource.value.addFeature(feature)
            const featureProps = feature.getProperties()
            selectedFeaturesIds = [featureId]
            Object.keys(featureProps).forEach(key => {
              featureProps[key] = formatNumber(featureProps[key])
            })
            selectedHexagoneInfo.value = featureProps
            selectedCISInfo.value = featureProps
            delete selectedCISInfo.value.geometry
            drawerOpen.value = true
          }
        }
      } catch (error) {
        notifyUser({ icon: "error", message: "Erreur lors de la récupération de la feature.", color: "red", position: "bottom", timeout: 2500 })
      }
    })
  }

  const featureTypeConfig = {
    fires: {
      fetchFeatures: true,
      createContent: (feature, indicator) => `${indicator.value}: ${feature.get(indicator.value)}`,
    },
    air: {
      fetchFeatures: false,
      checkFeature: (feat) => feat.get('isAirQualityFeature'),
      createContent: (feature) => `Zone : ${feature.get("lib_zone")} <br> Qualité : ${feature.get("lib_qual")}`,
    },
    vigicrues: {
      fetchFeatures: false,
      checkFeature: (feat) => feat.get('isVigicruesFeature'),
      createContent: (feature) => `Station : ${feature.get("code_geom")} <br> Vigilance : ${feature.get("vigilance")}`,
    },
    delays: {
      fetchFeatures: true,
      createContent: (feature) => `Temps d'arrivée (min) : ${Math.round(feature.get("time_difference"))}`,
    },
    interventions_predictions: {
      fetchFeatures: true,
      createContent: (feature) => {
        const content = `Prédictions : ${feature.get("value")}`
        if (feature.get("ressources") && dpt.value != "01") {
          return content + `<br> Ressources : ${feature.get("ressources")} engins`
        }
        return content
      },
    },
    groundwater: {
      fetchFeatures: false,
      checkFeature: (feat) => feat.get('isGroundwaterFeature'),
      createContent: (feature) => `Nappe : ${feature.get("nom")}`,
    },
  };


  function createGenericOverlayHandler(props, map, highlightSource, indicator) {
    const { infoOverlay, uniqueId } = createOverlay();
    const featureCache = {};

    const config = featureTypeConfig[props.type];
    if (!config) return;

    map.on('pointermove', async (evt) => {
      if (evt.dragging) return;
      const coordinate = evt.coordinate;


      if (config.fetchFeatures) {
        const viewResolution = map.getView().getResolution()
        const tolerance = 1 * viewResolution

        const bbox = [coordinate[0] - tolerance, coordinate[1] - tolerance, coordinate[0] + tolerance, coordinate[1] + tolerance]
        const precision = 4
        const bboxKey = bbox.map(coord => coord.toFixed(precision)).join(',')

        let data = featureCache[bboxKey];
        if (!data) {
          data = await fetchFeatures(bbox);
          featureCache[bboxKey] = data;
        }

        try {
          const features = new GeoJSON().readFeatures(data);
          processFeature(features[0], coordinate);
        }
        catch {
          return
        }
      } else {
        // Directly find feature for static types like 'air' and 'vigicrues'
        const feature = map.forEachFeatureAtPixel(evt.pixel, (feat) => {
          if (config.checkFeature(feat)) return feat;
        });

        processFeature(feature, coordinate);
      }
    });

    function processFeature(feature, coordinate) {
      if (!feature) {
        if (highlightSource.value) {
          highlightSource.value.clear()
        }
        infoOverlay.setPosition(undefined);
        return;
      }

      const content = config.createContent(feature, indicator);
      document.getElementById(uniqueId).innerHTML = content;
      infoOverlay.setPosition(coordinate);

      // Highlight the feature if necessary
      if (config.fetchFeatures) {
        let geometry = feature.getGeometry();
        if (geometry) {
          geometry = geometry.clone().transform('EPSG:4326', 'EPSG:3857');
          feature.setGeometry(geometry);
        }
        highlightSource.value.clear();
        highlightSource.value.addFeature(feature);
      }
    }
  }

  if (props.hover) {
    watch(delaysPickedDates, () => {
      if (!delaysPickedDates.value) {
        createGenericOverlayHandler(props, map.value, highlightSource, indicator)
      }
      else {
        map.value.getOverlays().clear()
      }

    }, { deep: true, immediate: true })
  }


  if (props.click && props.type == "vigicrues") {
    const { infoOverlay, uniqueId } = createOverlay()

    map.value.on('singleclick', (evt) => {

      const feature = map.value.forEachFeatureAtPixel(evt.pixel, (feat) => {
        if (feat.get('isVigicruesFeature')) {
          return feat
        }
      }, { hitTolerance: 10 })

      if (feature) {
        selectedStation.value = feature.get('code_geom')
      }
    })
  }
  if (props.click && props.type == "groundwater") {
    const { infoOverlay, uniqueId } = createOverlay()

    map.value.on('singleclick', (evt) => {

      const feature = map.value.forEachFeatureAtPixel(evt.pixel, (feat) => {
        if (feat.get('isGroundwaterFeature')) {
          return feat
        }
      }, { hitTolerance: 10 })

      if (feature) {
        selectedStation.value = feature.get('code_geom')
      }
    })
  }


  async function fetchFeatures(bbox) {
    layer.value = `${props.type}_${geometries.value}_${horizon.value}_${dpt.value}`
    const wfsUrl = constructWFSObject(layer.value).url(bbox)

    try {
      const response = await fetch(wfsUrl)
      if (!response.ok) {
        throw new Error('Network response was not ok')
      }
      return await response.json()
    } catch (error) {
      return null
    }
  }

  map.value.getView().fit(extent, {
    padding: [50, 50, 50, 50],
    duration: props.zoomDuration,
    maxZoom: 15
  })


  watch(toggleSatellite, (newVal) => {
    satelliteLayer.setVisible(newVal)
  })

  watch(layerOpacity, (newVal) => {
    vectorLayer.value.setOpacity(newVal)
  })

  watch(horizon, async () => {
    if (indicator.value === "vitesse_vent") {
      layer.value = `delays_hexagones_${horizon.value}_${dpt.value}`
    }
    if (props.type === "weather" || props.type === "fires" || props.type === "interventions_predictions" || props.type === "delays") {
      layer.value = `${props.type}_${geometries.value}_${horizon.value}_${dpt.value}`
      vectorSource.value = new VectorSource(constructWFSObject(layer.value))
      if (props.type != "interventions_predictions" && indicator.value != "vitesse_vent") {
        tableLoading.value = true
        getTableData(layer.value).then(data => {
          tableData.value = data;
          tableLoading.value = false;
        });
      }

      if (vectorLayer.value) {
        vectorLayer.value.setSource(vectorSource.value);
      } else {
        vectorLayer.value = new VectorImageLayer({
          source: vectorSource.value,
          style: hexagonesStyleFunction,
        });
      }
    }

    if (props.quality) {
      await fetchQualityData()
    }
  }, { immediate: true })

  watch(indicator, () => {
    if (indicator.value != "vitesse_vent") {
      layer.value = `${props.type}_${geometries.value}_${horizon.value}_${dpt.value}`
      vectorSource.value = new VectorSource(constructWFSObject(layer.value))
      tableLoading.value = true
      getTableData(layer.value).then(data => {
        tableData.value = data;
        tableLoading.value = false;
      });
      if (vectorLayer.value) {
        vectorLayer.value.setSource(vectorSource.value);
      } else {
        vectorLayer.value = new VectorImageLayer({
          source: vectorSource.value,
          style: hexagonesStyleFunction,
        });
      }
    }

  })

  watch(geometries, () => {
    if (props.type === "interventions_predictions") {
      layer.value = `${props.type}_${geometries.value}_${horizon.value}_${dpt.value}`
      vectorSource.value = new VectorSource(constructWFSObject(layer.value))
      aggregateTableData(timeRanges);
      if (vectorLayer.value) {
        vectorLayer.value.setSource(vectorSource.value);
      } else {
        vectorLayer.value = new VectorImageLayer({
          source: vectorSource.value,
          style: hexagonesStyleFunction,
        });
      }
    }
  })
})

</script>

<style>
.map-container-wrapper {
  position: relative;
  display: flex;
  flex: 1;
  flex-wrap: wrap;
  overflow: auto;
}

.map-container {
  min-height: 400px;
  border-bottom-right-radius: 15px;
  border-bottom-left-radius: 15px;
  flex: 1 1 60%;
  height: 100%;
  position: relative;
  min-width: 300px;
  overflow: hidden;
}

.side-panel {
  flex: 1 1 40%;
  height: 100%;
  min-width: 250px;
  position: relative;
}

#windy {
  height: 100%;
}

#windy #logo-wrapper {
  position: relative !important;
}

.quality-container {
  display: flex;
  gap: 1em;
  padding: 15px;
  flex-wrap: wrap;
}

.table-container {
  position: relative;
}

.map-table-toggle {
  margin-left: auto;
  margin-right: 10px;
  position: relative;
}

.in-map-controls {
  position: absolute;
  left: 5%;
  top: 5%;
  z-index: 100;
}

.overlay {
  position: absolute;
  display: grid;
  z-index: 100;
  top: 0;
  left: 0;
  height: 100%;
  background-color: white;
  color: var(--sad-nightblue);
  transition: all 0.3s ease;
  transform: translateX(0%);
  overflow-y: scroll;
}

.slider {
  display: flex;
  align-items: center;
  gap: 1em;
  width: 20%;
  max-width: 300px;
  min-width: 200px;
}

.download-map {
  position: absolute;
  right: 5%;
  z-index: 10;
  opacity: 0;
  transition: opacity 0.3s;
}

.map-container:hover .download-map {
  opacity: 1;
}

.in-map-cdc-table {
  position: absolute;
  z-index: 100;
  right: 0;
  bottom: 0;
  /* height: clamp(300px, 50vh, 600px); */
  background-color: white;
  transition: all 0.3s ease;
}

.in-map-cdc-table>div {
  height: 100%;
}

.picked-delays {
  position: absolute;
  left: 2%;
  top: 2%;
  z-index: 100;
  background: white;
  padding: 10px;
  border-radius: 15px;
  box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.25);
}

/* Initial state (off-screen) */
.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}

/* Final state (on-screen) */
.slide-enter-to,
.slide-leave-from {
  transform: translateX(0);
}

/* Transition effect */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}
</style>
