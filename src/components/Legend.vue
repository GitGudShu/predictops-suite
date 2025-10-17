<template>
  <div class="wrapper">
    <div class="details-container" v-if="details">
      <h5 class="details">{{ details }}</h5>
    </div>
    <div class="legend-container">
      <div class="time-legend" v-for="(timeData, timeKey) in callClockData" :key="timeKey">
        <q-icon :name="timeKey === 'Jour' ? 'sunny' : 'dark_mode'" color="black" :size="dynamicIconSize"></q-icon>
        <p class="time-indicator">{{ timeKey }}</p>
        <span v-for="(item, colorKey) in timeData" :key="colorKey" :class="colorKey" class="legend-element">
          {{ item.prefix }} {{ item.operators || item.value }}{{ item.unit }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
  dptBounds: Object,
  dataObject: String,
  details: String,
  iconSize: String,
});

const publicPath = process.env.PUBLIC_PATH || '/predictops/';
let refreshInterval;
const bounds = ref(JSON.parse(localStorage.getItem("dptBounds")) || props.dptBounds);
const windowWidth = ref(window.innerWidth);

// Dynamic sizing based on viewport - keeps original size for desktop
const dynamicIconSize = computed(() => {
  const baseSize = parseInt(props.iconSize) || 24;

  // Keep original size until larger breakpoints
  if (windowWidth.value < 1200) {
    return props.iconSize || `${baseSize}px`;
  }
  // Start scaling at larger screens
  else if (windowWidth.value < 1800) {
    const scaleFactor = 1 + (windowWidth.value - 1200) / 1500;
    return `${baseSize * scaleFactor}px`;
  }
  // Aggressive scaling for wall displays
  else {
    const scaleFactor = 1.4 + (windowWidth.value - 1800) / 800;
    return `${baseSize * Math.min(scaleFactor, 4)}px`;
  }
});

const sortColorsAndAddGray = (data) => {
  const colorOrder = ['vert', 'jaune', 'orange', 'rouge', 'violet'];
  const grayObject = {
    "gray": {
      "color": "gray",
      "operators": "Réel",
    }
  };

  // Function to sort and add gray object
  const sortAndAddGray = (timeData) => {
    const sorted = {};
    colorOrder.forEach(color => {
      if (timeData[color]) {
        sorted[color] = timeData[color];
      }
    });
    // Add gray object at the end
    sorted.gray = grayObject.gray;
    return sorted;
  };

  // Sort both 'Jour' and 'Nuit' according to the color order and add gray
  const sortedData = {};
  Object.keys(data).forEach(time => {
    sortedData[time] = sortAndAddGray(data[time]);
  });
  return sortedData;
};

const callClockData = computed(() => {
  // Retrieve the relevant object based on props.dataObject
  const data = bounds.value[props.dataObject];
  const sortedData = sortColorsAndAddGray(data);
  return sortedData ? sortedData : {};
});

// Track window resizing
const handleResize = () => {
  windowWidth.value = window.innerWidth;
};

onMounted(() => {
  clearInterval(refreshInterval);
  refreshInterval = setInterval(() => {
    bounds.value = JSON.parse(localStorage.getItem("dptBounds")) || props.dptBounds;
  }, 10000);

  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  clearInterval(refreshInterval);
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
/* Base styles - almost identical to original for desktop */
.wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 3vw;
  width: fit-content;
  padding: 10px;
  color: black;
  width: 100%;
  height: auto;
}

.legend-container {
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-grow: 1;
  align-items: center;
  flex-direction: column;
  flex-wrap: wrap;
  max-width: 380px;
  min-width: 300px;
}

.details,
.time-indicator {
  margin: 0;
  color: black;
  font-weight: bold;
  font-size: 16px;
  text-align: center;
}

.time-legend {
  width: 100%;
  font-weight: bold;
  flex: 1;
  display: flex;
  align-items: center;
}

p.time-indicator {
  margin: 10px;
}

.legend-element {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 90%;
  white-space: nowrap;
}

.gray {
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
  background-color: var(--sad-lightgray);
  color: var(--sad-nightblue);
}

.vert,
.vert:focus {
  border-bottom-left-radius: 4px;
  border-top-left-radius: 4px;
  background-color: var(--sad-green);
  color: white;
}

.jaune,
.jaune:focus {
  background-color: var(--sad-yellow);
  color: var(--sad-nightblue);
}

.orange,
.orange:focus {
  background-color: var(--sad-orange);
  color: var(--sad-nightblue);
}

.rouge,
.rouge:focus {
  background-color: var(--sad-red);
  color: white;
}

.violet,
.violet:focus {
  background-color: var(--sad-purple);
  color: white;
}


/* Extra large wall displays */
@media (min-width: 2400px) {
  .wrapper {
    padding: calc(10px + 0.5vw);
  }

  .legend-container {
    max-width: 1800px;
    min-width: 900px;
  }

  .details,
  .time-indicator {
    font-size: calc(16px + 1vw);
  }

  p.time-indicator {
    margin: calc(10px + 0.75vw);
  }

  .legend-element {
    padding: 0.6rem 0;
    font-size: calc(14px + 1vw);
  }

  .gray {
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
  }

  .vert,
  .vert:focus {
    border-bottom-left-radius: 8px;
    border-top-left-radius: 8px;
  }
}
</style>
