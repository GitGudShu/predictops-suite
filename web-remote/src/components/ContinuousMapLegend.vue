<template>
  <div class="legend" v-if="colors.length">
    <div class="legend-gradient" :style="gradientStyle"></div>
    <div class="legend-labels" >
      <span :style="{color: fontColor}" v-for="(label, index) in labels" :key="index">{{ label }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { api } from 'src/boot/axios';
import { notifyUser } from 'src/utils/notifyUser';

const props = defineProps({
  indicatorType: String,
  fontColor: String,
});

const mappingData = ref({});

const fetchMappingData = async (indicator) => {
  try {
    const response = await api.get('/static/mapping.json');
    mappingData.value = response.data[indicator];
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération du fichier mapping.", color: "red", position: "bottom", timeout: 2500 })
  }
};

watch(() => props.indicatorType, (newIndicator) => {
  fetchMappingData(newIndicator);
}, { immediate: true });

const labels = computed(() => mappingData.value?.[0] || []);
const colors = computed(() => mappingData.value?.[2] || []);

const gradientStyle = computed(() => {
  const colorStops = colors.value
    .map((color, index, arr) => `${color} ${index / (arr.length - 1) * 100}%`)
    .join(', ');
  return { backgroundImage: `linear-gradient(to right, ${colorStops})` };
});
</script>

<style scoped>
.legend {
  position: absolute;
  z-index: 100;
  top: 2%;
  left: 2%;
  max-width: 60%;
}

.legend-gradient {
  border: 1px var(--sad-nightblue) solid;
  height: 8px;
  border-radius: 5px;
  margin-bottom: 10px;
}

.legend-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  position: relative;
  font-weight: 900;
  gap: 15px;
}

.legend-labels span {
  width: 40px;
  min-width: fit-content;
  text-align: center;
  overflow-wrap: normal;
}

.legend-labels span:first-child {
  text-align: left;
}
.legend-labels span:last-child {
  text-align: right;
}

</style>
