<template>
  <div class="discrete-legend" v-if="colors.length && labels.length">
    <div class="legend-items">
      <div v-for="(label, index) in labels" :key="index" class="legend-item">
        <div class="color-box" :style="{ backgroundColor: colors[index] }"></div>
        <span>{{ label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect } from 'vue';
import { api } from 'src/boot/axios';
import { notifyUser } from 'src/utils/notifyUser';

const props = defineProps({
  indicatorType: String,
});

const labels = ref([]);
const colors = ref([]);

watchEffect(async () => {
  try {
    const response = await api.get('/static/mapping.json');
    const mapping = response.data[props.indicatorType];
    if (mapping) {
      labels.value = mapping[0];
      colors.value = mapping[2];
    }
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération du fichier mapping.", color: "red", position: "bottom", timeout: 2500 })
  }
});
</script>

<style scoped>
.discrete-legend {
  color: black;
  position: absolute;
  z-index: 100;
  bottom: 2%;
  left: 2%;
  padding: 5px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.color-box {
  width: 15px;
  height: 15px;
  border: 1px solid #ddd;
  border-radius: 50%; /* Circular color boxes */
}

@media screen and (min-width: 2000px) {
  .discrete-legend {
    font-size: 32px;
    padding: 10px;
    gap: 15px;
  }

  .color-box {
    width: 30px;
    height: 30px;
  }

  .legend-item {
    gap: 25px;
  }
}
</style>
