<template>
  <div class="dropdown" ref="dropdownRef">
    <Button @click="toggleDropdown" :btn-text="selectedItemLabel" right-icon="fa-solid fa-chevron-down"
      :right-icon-rotation="isOpen ? 'rotate-180' : ''" :btn-size="btnSize" txt-color="var(--sad-nightblue)"
      :bg-color="btnBgColor">
    </Button>
    <div v-if="isOpen" class="dropdown-list" :key="selectedItem.value">
      <div class="dropdown-item" v-for="item in normalizedList" :key="item.value" @mouseover="onHover(item.value)" @mouseleave="onHover(null)">
        <input class="radio-input" :id="item.value" type="radio" :value="item.value" v-model="selectedValue" />
        <label class="radio-label" :for="item.value">
          {{ item.label }}
          <span class="radio-custom"></span>
        </label>
        <q-icon v-if="item.tooltip" name="info" size="xs">
          <q-tooltip class="tooltip"> {{ item.tooltip }} </q-tooltip>
        </q-icon>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import Button from './Button.vue';

const props = defineProps({
  list: [Array, Object],
  persistent: Boolean,
  selectedValue: String,
  storageKey: String,
  btnSize: String,
  btnBgColor: {
    type: String,
    default: 'transparent'
  },
  immediate: {
    type: Boolean,
    default: false
  },
  autoSelect: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['update:modelValue', 'update:selected', 'hover']);

const isOpen = ref(false);
const selectedItem = ref({});
const dropdownRef = ref(null);
const STORAGE_KEY = props.storageKey;

// Normalizes the input list to an array of objects { label, value }
const normalizedList = computed(() => {
  const list = props.list || []; // Default to empty array if undefined or null
  if (Array.isArray(list)) {
    return list.map(item => {
      if (typeof item === 'object') {
        return { ...item, label: item.label || item.value, value: item.value, tooltip: item.tooltip };
      } else {
        return { label: item, value: item };
      }
    });
  } else {
    return Object.keys(list).map(key => {
      const value = list[key];
      if (typeof value === 'object') {
        return { label: key, value: value.value, tooltip: value.tooltip };
      } else {
        return { label: key, value: value };
      }
    });
  }
});

const selectedValue = ref(props.selectedValue);

// Helper to find the label for the current selected value
const selectedItemLabel = computed(() => {
  const item = normalizedList.value.find(item => item.value === selectedValue.value);
  return item ? item.label : '';
});

onMounted(() => {
  if (props.persistent) {
    const persistedValue = localStorage.getItem(STORAGE_KEY);
    if (persistedValue) {
      selectedValue.value = persistedValue;
    } else if (normalizedList.value.length > 0) {
      selectedValue.value = normalizedList.value[0].value;
      localStorage.setItem(STORAGE_KEY, selectedValue.value);
    }
  }
  else if (props.selectedValue) {
    selectedValue.value = props.selectedValue;
  }
  else if (normalizedList.value.length > 0 && props.autoSelect) {
    selectedValue.value = normalizedList.value[0].value;
  }
  document.addEventListener('click', outsideClickListener);
});

onUnmounted(() => {
  document.removeEventListener('click', outsideClickListener);
});

const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

const outsideClickListener = (event) => {
  if (!dropdownRef.value.contains(event.target)) {
    isOpen.value = false;
  }
};

const onHover = (value) => {
  emit('hover', value);
};

watch(selectedValue, (newValue) => {
  if (props.persistent) localStorage.setItem(STORAGE_KEY, newValue);
  emit('update:selected', newValue);
});

// Watch for changes in the list prop to update the selection
watch(() => props.list, (newList) => {
  if (normalizedList.value.length > 0 && props.autoSelect === true) {
    selectedValue.value = normalizedList.value[0].value;
    if (props.persistent) {
      localStorage.setItem(STORAGE_KEY, selectedValue.value);
    }
    emit('update:selected', selectedValue.value);
  }
}, { deep: true, immediate: props.immediate });
</script>

<style scoped>
button {
  border: solid 1px var(--sad-nightblue);
  font-weight: 400;
}

.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-list {
  position: absolute;
  top: 110%;
  left: 0;
  color: var(--sad-nightblue);
  border-radius: 10px;
  background-color: white;
  box-shadow: 0px 3px 24px 0px #2526281F;
  border: 1px solid var(--sad-lightgray);
  width: 100%;
  min-width: fit-content;
  white-space: nowrap;
  padding: 0.25rem;
  z-index: 1000;
  max-height: 250px;
  overflow-y: auto;
}

.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1em;
  padding: 0.25rem;
}

.dropdown-item label {
  flex: 1 0 auto;
}

.radio-input {
  position: absolute;
  opacity: 0;
  z-index: -1;
}

.radio-label {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  padding-right: 25px;
}

.radio-custom {
  display: inline-block;
  width: 15px;
  height: 15px;
  margin-left: 5px;
  border-radius: 50%;
  background-color: white;
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  box-sizing: border-box;
}

.radio-input:checked+.radio-label .radio-custom {
  background-color: var(--sad-orange);
  border-color: var(--sad-orange);
  /* Custom radio border when checked */
  background-image: url("data:image/svg+xml,%3Csvg width='8' height='6' viewBox='0 0 8 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M6.66634 1.66663L3.33301 4.99996L1.33301 2.99996' stroke='white' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E%0A");
  background-repeat: no-repeat;
  background-position: center;
  background-size: 10px;
}


button:hover,
button:focus,
button:active {
  background: inherit;
  color: inherit;
  border: solid 1px #727191;
  color: #727191 !important;
  box-shadow: none;
}
</style>
