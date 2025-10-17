<template>
  <span ref="fitTextElement" class="fit-text">{{ text }}</span>
</template>

<script setup>
import { ref, watch, onMounted, nextTick, onUnmounted } from 'vue';

const props = defineProps({
  text: {
    type: String,
    required: true
  },
  minFontSize: {
    type: Number,
    default: 10
  },
  maxFontSize: {
    type: Number,
    default: 120
  },
  step: {
    type: Number,
    default: 1
  },
  grow: {
    type: Boolean,
    default: false
  }
});

const fitTextElement = ref(null);
let adjustInterval;

const adjustFontSize = async (element, minFontSize, maxFontSize, step, grow) => {
  await nextTick(); // Ensure the DOM updates are completed before checking sizes

  let currentFontSize = parseFloat(getComputedStyle(element).fontSize);
  let lastFontSize = currentFontSize; // Keep track of the last font size
  let isChanged = false;

  const adjustDown = () => {
    while ((element.scrollWidth > element.offsetWidth || element.scrollHeight > element.offsetHeight) && currentFontSize > minFontSize) {
      currentFontSize -= step; // Decrease font size in steps
      element.style.fontSize = `${currentFontSize}px`; // Apply the new font size
      isChanged = true; // Mark as changed
    }
  };

  const adjustUp = () => {
    while ((element.scrollWidth <= element.offsetWidth && element.scrollHeight <= element.offsetHeight) && currentFontSize < maxFontSize) {
      currentFontSize += step; // Increase font size in steps
      element.style.fontSize = `${currentFontSize}px`; // Apply the new font size
      isChanged = true; // Mark as changed
    }

    adjustDown();
  };

  if (grow) {
    adjustUp();
  } else {
    adjustDown();
  }

  // Log only if font size has changed
  if (isChanged && lastFontSize !== currentFontSize) {
    lastFontSize = currentFontSize; // Update lastFontSize
  }
};

const adjustFontSizeHandler = () => {
  if (fitTextElement.value) {
    adjustFontSize(fitTextElement.value, props.minFontSize, props.maxFontSize, props.step, props.grow);
  }
};

// Debounce function to limit the rate at which a function can fire
const debounce = (func, delay) => {
  let timeout;
  return function (...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), delay);
  };
};

const debouncedAdjustFontSizeHandler = debounce(adjustFontSizeHandler, 100); // Debounce with 300ms delay

onMounted(() => {
  debouncedAdjustFontSizeHandler();
  window.addEventListener('resize', debouncedAdjustFontSizeHandler);
  adjustInterval = setInterval(() => {
    debouncedAdjustFontSizeHandler();
  }, 1000);
});

watch(() => [props.text, props.minFontSize, props.step, props.grow], debouncedAdjustFontSizeHandler);

onUnmounted(() => {
  clearInterval(adjustInterval);
  window.removeEventListener('resize', debouncedAdjustFontSizeHandler);
});
</script>

<style scoped>
.fit-text {
  overflow: hidden; /* Prevent scrollbars */
  text-wrap: nowrap;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: grid;
  place-items: center;
}
</style>
