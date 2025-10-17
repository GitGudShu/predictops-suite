<template>
  <q-page>
    <BackButton />
    <div class="container">
      <div ref="mapContainer" class="map-container" :style="{ height: '600px', width: '350px', minWidth: '250px' }">
      </div>
      <div class="bounds">
        <div class="dropdowns-container">
          <!-- Types List as Dropdown -->
          <Dropdown immediate btn-size="md-btn" :list="typesList" :selected-value="typesList[0].value"
            @update:selected="onTypeSelected" />
          <!-- Features List as Select -->
          <Select immediate searchable btn-size="md-btn" :list="featuresList" multiple
            @update:selected="onFeatureSelected" @hover="onFeatureHover" v-if="map" search-placeholder="Centre" />
          <!-- Horizons List as Select -->
          <Select immediate btn-size="md-btn" :list="horizonsList" multiple @update:selected="onHorizonSelected"
            v-if="type" :disabled="selectedFeatures.length === 0" />
        </div>

        <div class="bounds-form">
          <div class="checkbox-container">
            <q-checkbox v-model="groupingValues" label="Insértion groupée" @update:model-value="groupValues" />
          </div>
          <div class="centre" v-if="groupingValues">
            <h5 class="text-center text-weight-medium">Bornes</h5>
            <div class="q-mb-md flex">
              <span class="form-label text-bold underline-yellow">Jaune :</span>
              <div class="form-input flex">
                <q-input square v-model="yellowGroupValue" filled dense
                  style="width: 135px; flex: 1; transform: translateY(12px);" type="number" step="any"
                  :rules="[yellowRule]" />
              </div>
              <span class="form-label text-bold underline-orange">Orange :</span>
              <div class="form-input flex">
                <q-input square v-model="orangeGroupValue" filled dense
                  style="width: 135px; flex: 1; transform: translateY(12px);" type="number" step="any"
                  :rules="[orangeRule(yellowGroupValue)]" />
              </div>
              <span class="form-label text-bold underline-red">Rouge :</span>
              <div class="form-input flex">
                <q-input square v-model="redGroupValue" filled dense
                  style="width: 135px; flex: 1; transform: translateY(12px);" type="number" step="any"
                  :rules="[redRule(orangeGroupValue)]" />
              </div>
            </div>
          </div>
          <div v-for="feature in selectedFeatures" :key="feature" class="centre" v-if="!groupingValues">
            <h5 class="text-center text-weight-medium">{{featuresList.find(f => f.value === feature).label}}</h5>
            <div v-for="horizon in selectedHorizons" :key="horizon.value" class="flex-column">
              <h6 class="text-underline">{{ horizon.label }}</h6>
              <div class="q-mb-md flex">
                <span class="form-label text-bold underline-yellow">Jaune :</span>
                <div class="form-input flex">
                  <q-skeleton width="100px" height="40px" v-if="loading" type="QInput"></q-skeleton>
                  <q-input v-if="!loading && data[feature] && data[feature][horizon.value]" square
                    v-model="data[feature][horizon.value].yellow" filled dense
                    style="width: 135px; flex: 1; transform: translateY(12px);" type="number" step="any"
                    :rules="[yellowRule]" />
                </div>
              </div>
              <div class="q-mb-md flex">
                <span class="form-label text-bold underline-orange">Orange :</span>
                <div class="form-input flex">
                  <q-skeleton width="100px" height="40px" v-if="loading" type="QInput"></q-skeleton>
                  <q-input v-if="!loading && data[feature] && data[feature][horizon.value]" square
                    v-model="data[feature][horizon.value].orange" filled dense
                    style="width: 135px; flex: 1; transform: translateY(12px);" type="number" step="any"
                    :rules="[orangeRule(data[feature][horizon.value].yellow)]" />
                </div>
              </div>
              <div class="q-mb-md flex">
                <span class="form-label text-bold underline-red">Rouge :</span>
                <div class="form-input flex">
                  <q-skeleton width="100px" height="40px" v-if="loading" type="QInput"></q-skeleton>
                  <q-input v-if="!loading && data[feature] && data[feature][horizon.value]" square
                    v-model="data[feature][horizon.value].red" filled dense
                    style="width: 135px; flex: 1; transform: translateY(12px);" type="number" step="any"
                    :rules="[redRule(data[feature][horizon.value].orange)]" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <Button @click="updateData" btn-text="Enregistrer" btn-type="submit" btn-size="lg-btn"
          bg-color="var(--sad-nightblue)" txt-color="white" left-icon="fa-solid fa-floppy-disk"
          :loading="updating || loading" v-if="selectedFeatures.length && selectedHorizons.length"
          :disabled="!isFormValid" :style="{ minHeight: '50px' }" />
      </div>
    </div>
  </q-page>
</template>


<script setup>
import BackButton from 'src/components/BackButton.vue';
import Button from 'src/components/Button.vue';
import Dropdown from 'src/components/Dropdown.vue';
import Select from 'src/components/Select.vue';
import { onMounted, ref, computed, watch } from 'vue';
import { fromLonLat } from 'ol/proj';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import XYZ from 'ol/source/XYZ';
import GeoJSON from 'ol/format/GeoJSON';
import VectorSource from 'ol/source/Vector';
import VectorLayer from 'ol/layer/Vector';
import { Fill, Stroke, Style } from 'ol/style';
import { api } from 'src/boot/axios';
import { notifyUser } from 'src/utils/notifyUser';
import { debounce } from 'quasar';
import { useRoute } from 'vue-router';

const location = useRoute();

const publicPath = process.env.PUBLIC_PATH || '/predictops/';

const dpt = computed(() => {
  return localStorage.getItem("dpt") || location.params.dpt;
});

const yellowRule = (val) => val != undefined && val != null && val != '' && val > 0 || 'Veuillez entrer une valeur supérieure à 0';
const orangeRule = (yellowValue) => (val) => val > parseFloat(yellowValue) || `Doit être supérieur à ${yellowValue}`;
const redRule = (orangeValue) => (val) => val > parseFloat(orangeValue) || `Doit être supérieur à ${orangeValue}`;

const data = ref({})
const loading = ref(true);
const updating = ref(false);
const groupingValues = ref(false);

const type = ref();
const typesList = ref([]);
const horizonsList = ref([]);
const featuresList = ref([]);

const yellowGroupValue = ref(0);
const orangeGroupValue = ref(0);
const redGroupValue = ref(0);

const selectedFeatures = ref([]);
const selectedHorizons = ref([]);

if (dpt.value == '01') {
  typesList.value.push(
    { label: 'CIS-SAP', value: 'CIS-SAP' },
    { label: 'CIS-INC', value: 'CIS-INC' },
    { label: 'Tous', value: 'TOUS' },
    { label: 'Inondations', value: 'INONDATION' },
  );
}
if (dpt.value == '25') {
  typesList.value.push(
    { label: 'CIS-SAP', value: 'CIS-SAP' },
    { label: 'CIS-INC', value: 'CIS-INC' },
    { label: 'Tous', value: 'TOUS' },
    { label: 'SAP Total Agglo', value: 'AGGLO' },
    { label: 'SAP Total CH', value: 'SUAP' },
    { label: 'Inondations', value: 'INONDATION' },
  );
}
if (dpt.value == '78') {
  typesList.value.push(
    { label: 'CIS-SAP', value: 'CIS-SAP' },
    { label: 'Tous', value: 'TOUS' },
    { label: 'SAP Total Agglo', value: 'AGGLO' },
    { label: 'Inondations', value: 'INONDATION' },
  );
}

const mapContainer = ref(null);
const map = ref();

const vectorLayer = ref();
const selectedHighlightLayer = ref();
const hoverHighlightLayer = ref();
const additionalHighlightLayer = ref();

const isFormValid = computed(() => {
  // Check if data for selected features and horizons exists
  if (!selectedFeatures.value.length || !selectedHorizons.value.length) {
    return false;
  }

  if (groupingValues.value) {
    const y = Number(yellowGroupValue.value);
    const o = Number(orangeGroupValue.value);
    const r = Number(redGroupValue.value);

    return y > 0 && o > y && r > o
  }

  return selectedFeatures.value.every(feature =>
    selectedHorizons.value.every(horizon => {
      const horizonData = data.value[feature]?.[horizon.value];
      if (!horizonData) return false;

      return (
        yellowRule(horizonData.yellow) === true &&
        orangeRule(horizonData.yellow)(horizonData.orange) === true &&
        redRule(horizonData.orange)(horizonData.red) === true
      );
    })
  );
});

const onTypeSelected = (selectedType) => {
  type.value = selectedType;
  selectedFeatures.value = [];
  selectedHorizons.value = [];

  horizonsList.value = [
    { label: '01h-03h', value: 1 },
    { label: '03h-05h', value: 3 },
    { label: '05h-07h', value: 5 },
    { label: '07h-09h', value: 7 },
    { label: '09h-11h', value: 9 },
    { label: '11h-13h', value: 11 },
    { label: '13h-15h', value: 13 },
    { label: '15h-17h', value: 15 },
    { label: '17h-19h', value: 17 },
    { label: '19h-21h', value: 19 },
    { label: '21h-23h', value: 21 },
    { label: '23h-01h', value: 23 },
  ];

}

const onFeatureSelected = debounce((selectedFeatureValues) => {
  selectedFeatures.value = selectedFeatureValues;
  highlightSelectedFeature(selectedFeatures.value);
  fetchData()
},)

const onHorizonSelected = debounce((selectedHorizonValues) => {
  selectedHorizons.value = selectedHorizonValues.map(value => {
    const horizon = horizonsList.value.find(h => h.value === value);
    return horizon ? { value: horizon.value, label: horizon.label } : null;
  }).filter(h => h !== null);
  fetchData()
},)

const groupValues = () => {
  if (!groupingValues.value) {
    yellowGroupValue.value = 0;
    orangeGroupValue.value = 0;
    redGroupValue.value = 0;
  }
}

const onFeatureHover = (hoveredFeature) => {
  if (hoverHighlightLayer.value) {
    map.value.removeLayer(hoverHighlightLayer.value);
    hoverHighlightLayer.value = null;
  }

  const feature = vectorLayer.value.getSource().getFeatures().find(f => f.get('code_geom') === hoveredFeature);

  if (feature) {
    const highlightSource = new VectorSource({
      features: [feature]
    });

    hoverHighlightLayer.value = new VectorLayer({
      source: highlightSource,
      style: new Style({
        fill: new Fill({ color: '#ed9205' })
      }),
      opacity: 0.75,
      zIndex: 5
    });

    map.value.addLayer(hoverHighlightLayer.value);
  }

  // Always ensure selected features are visible
  if (additionalHighlightLayer.value) {
    map.value.removeLayer(additionalHighlightLayer.value);
    map.value.addLayer(additionalHighlightLayer.value);
  }
}

const addVectorLayer = async (url) => {
  const response = await fetch(url);
  const geojsonData = await response.json();

  const newVectorSource = new VectorSource({
    features: new GeoJSON().readFeatures(geojsonData, {
      dataProjection: 'EPSG:4326',
      featureProjection: 'EPSG:3857'
    })
  });

  const newVectorLayer = new VectorLayer({
    source: newVectorSource,
    style: new Style({
      fill: new Fill({ color: '#181632' }),
      stroke: new Stroke({ color: 'white' })
    }),
    zIndex: 3
  });

  if (vectorLayer.value) {
    map.value.removeLayer(vectorLayer.value);
    map.value.removeLayer(hoverHighlightLayer.value);
    map.value.removeLayer(selectedHighlightLayer.value);
    map.value.removeLayer(additionalHighlightLayer.value);
  }

  vectorLayer.value = newVectorLayer;
  map.value.addLayer(vectorLayer.value);

  featuresList.value = newVectorSource.getFeatures().map(feature => ({
    label: feature.get('nom'),
    value: feature.get('code_geom')
  }));
}

const highlightSelectedFeature = (selectedFeatures) => {
  if (additionalHighlightLayer.value) {
    map.value.removeLayer(additionalHighlightLayer.value);
    additionalHighlightLayer.value = null;
  }

  const features = vectorLayer.value.getSource().getFeatures().filter(f => selectedFeatures.includes(f.get('code_geom')));

  if (features.length > 0) {
    const highlightSource = new VectorSource({
      features: features
    });

    additionalHighlightLayer.value = new VectorLayer({
      source: highlightSource,
      style: new Style({
        stroke: new Stroke({ color: '#ed9205', width: 2 })
      }),
      zIndex: 4
    });

    map.value.addLayer(additionalHighlightLayer.value);
  }
}

const fetchData = debounce(async () => {
  loading.value = true;
  const horizonValues = selectedHorizons.value.map(horizon => horizon.value);
  const params = {
    dpt: dpt.value,
    type: type.value,
    code_geom: selectedFeatures.value.join(','),
    horizon: horizonValues.join(',')
  };
  try {
    const response = await api.get('/data/map-bounds', { params });
    processFetchedData(response.data);
    loading.value = false;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des bornes.", color: "red", position: "bottom", timeout: 2500 });
  } finally {
    loading.value = false;
  }
}, 0);

const processFetchedData = (rdata) => {
  const groupedData = {};

  // Initialize the grouped data structure with default values
  selectedFeatures.value.forEach(feature => {
    groupedData[feature] = {};
    selectedHorizons.value.forEach(horizon => {
      groupedData[feature][horizon.value] = { yellow: 0, orange: 0, red: 0 };
    });
  });

  // Populate the grouped data structure with fetched data
  rdata.forEach(item => {
    if (groupedData[item.code_geom] && groupedData[item.code_geom][item.horizon]) {
      groupedData[item.code_geom][item.horizon] = {
        yellow: item.yellow,
        orange: item.orange,
        red: item.red
      };
    }
  });

  data.value = groupedData;
}

const updateData = async () => {
  const payload = [];

  Object.keys(data.value).forEach(code_geom => {
    selectedHorizons.value.forEach(horizon => {
      let horizonData = {};
      if (groupingValues.value) {
        horizonData = {
          yellow: yellowGroupValue.value,
          orange: orangeGroupValue.value,
          red: redGroupValue.value
        };
      }
      else {
        horizonData = data.value[code_geom][horizon.value];
      }
      const feature = featuresList.value.find(f => f.value == code_geom);

      const doc = {
        dpt: dpt.value,
        code_geom: parseInt(code_geom),
        name: feature ? feature.label : '',
        horizon: horizon.value,
        tranche: horizon.label,
        type: type.value,
        yellow: horizonData.yellow,
        orange: horizonData.orange,
        red: horizonData.red
      };

      payload.push(doc);
    });
  });

  try {
    updating.value = true;
    await api.put('/admin/update/map-bounds', payload);
    notifyUser({ icon: "check", message: "Enregistrement avec succès.", color: "green", position: "bottom", timeout: 2500 });
    if(groupingValues.value) {
     fetchData();
    }
    updating.value = false;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la sauvegarde.", color: "red", position: "bottom", timeout: 2500 });
  }
  finally {
    updating.value = false;
  }
}


onMounted(async () => {
  const dptGeoJSONURL = `${publicPath}departement_${dpt.value}.geojson`;
  const dptGeoJSON = await (await fetch(dptGeoJSONURL)).json();
  const departmentFeature = new GeoJSON().readFeature(dptGeoJSON, {
    dataProjection: 'EPSG:4326',
    featureProjection: 'EPSG:3857'
  });
  const extent = departmentFeature.getGeometry().getExtent();

  const osmLayer = new TileLayer({
    source: new XYZ({
      attributions: '@OpenStreetMap contributors, @CARTO',
      url: 'https://cartodb-basemaps-a.global.ssl.fastly.net/rastertiles/voyager/{z}/{x}/{y}.jpg',
      visible: true,
      crossOrigin: 'anonymous'
    })
  });

  map.value = new Map({
    target: mapContainer.value,
    layers: [osmLayer],
    view: new View({
      center: fromLonLat([2.432708043560393, 46.568368777322884]),
      zoom: 5
    }),
    interactions: []
  });

  map.value.getView().fit(extent, {
    padding: [15, 15, 15, 15],
    duration: 1000,
    maxZoom: 15
  });



  if (type.value) {
    const geojsonURL = `${publicPath}${dpt.value}/${type.value}.geojson`;
    await addVectorLayer(geojsonURL);
    fetchData()
  }

  watch(type, async (newVal) => {
    if (newVal) {
      const geojsonURL = `${publicPath}${dpt.value}/${newVal}.geojson`;
      await addVectorLayer(geojsonURL);
    }
  });

});

</script>


<style scoped>
.container {
  width: 80vw;
  height: 100%;
  display: flex;
  margin: 0 auto;
  flex-wrap: wrap;
  gap: 1em;
}

.dropdowns-container {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 1em;
  height: min-content;
}

.map-container {
  flex: 1 1 30%;
}

.bounds {
  flex: 1 1 60%;
  display: flex;
  flex-direction: column;
  gap: 1em;
  height: 100%;
  max-height: 600px;
}

.checkbox-container {
  width: 100%;
}

.bounds-form {
  margin: 10px auto;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 1em;
  padding: 1em;
  overflow-y: auto;
}

.centre {
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  flex-wrap: wrap;
  gap: 0.5em;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  padding: 1em;
  flex: 1 1 50%;
}

.centre h5 {
  margin: 0;
  width: 100%;
}

.centre h6 {
  margin: 10px 0;
}

.form-label {
  min-width: 50px;
  position: relative;
}

.form-input {
  flex: 0;
}

.form-input label {
  flex: 1;
}

.form-input span {
  flex: 0;
}

.flex {
  display: flex;
  align-items: center;
  gap: 1em;
}

.form-label::before {
  height: 5px;
  content: "";
  position: absolute;
  width: 100%;
  top: 100%;
}

.underline-yellow::before {
  background-color: var(--sad-yellow);
}

.underline-orange::before {
  background-color: var(--sad-orange);
}

.underline-red::before {
  background-color: var(--sad-red);
}
</style>
