<template>
  <div class="select-container">
    <div class="select" ref="selectRef">
      <Button @click="toggleDropdown" :btn-text="buttonLabel" right-icon="fa-solid fa-chevron-down"
        :right-icon-rotation="isOpen ? 'rotate-180' : ''" :btn-size="btnSize" txt-color="var(--sad-nightblue)"
        :bg-color="btnBgColor" :disabled="disabled" />
      <div class="dropdowns-container">
        <div v-if="isOpen" class="select-dropdown">
          <div class="actions">
            <q-input v-model="searchQuery" type="search" placeholder="Rechercher" dense clearable>
              <template v-slot:append>
                <q-icon name="fa-solid fa-search" size="15px"/>
              </template>
            </q-input>
            <q-checkbox v-model="selectAll" @update:model-value="handleSelectAll" label="Tout sélectionner" dense
              class="text-black text-bold" />
          </div>
          <!-- <q-separator></q-separator> -->
          <div class="select-item" v-for="item in filteredList" :key="item.value" @mouseover="onHover(item.value)"
            @mouseleave="onHover(null)">
            <input class="checkbox-input" :id="item.value" type="checkbox" :value="item.value"
              v-model="selectedValues" />
            <label class="checkbox-label" :for="item.value">
              {{ item.label }}
              <span class="checkbox-custom"></span>
            </label>
          </div>
        </div>
        <div v-if="selectedValues.length && isOpen" class="selected-values">
          <div class="chip" v-for="value in selectedValues" :key="value">
            <p style="margin: 0; line-height: normal;">{{ findLabelByValue(value) }}</p>
            <q-icon name="fa-solid fa-xmark" size="10px" class="close-chip" @click.stop="removeValue(value)" />
          </div>
          <q-icon name="fa-solid fa-trash" size="15px" class="clear-button" @click.stop="clearSelected" color="red"/>
          <!-- <q-btn round dense icon="fa-solid fa-trash" size="sm" @click.stop="clearSelected" text-color="var(--sad-red)"
            :style="{ border: 'none' }" /> -->
        </div>
      </div>
    </div>
  </div>
</template>



<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import Button from './Button.vue';

const props = defineProps({
  list: {
    type: [Array, Object],
    required: true
  },
  selectedValues: {
    type: Array,
    default: () => []
  },
  storageKey: String,
  btnSize: String,
  btnBgColor: {
    type: String,
    default: 'transparent'
  },
  searchable: {
    type: Boolean,
    default: false
  },
  immediate: {
    type: Boolean,
    default: false
  },
  searchPlaceholder: {
    type: String,
    default: 'Rechercher'
  },
  disabled: Boolean
});

const emit = defineEmits(['update:selected', 'hover']);

const isOpen = ref(false);
const selectRef = ref(null);
const searchQuery = ref('');
const selectedValues = ref([props.selectedValues]);
const selectAll = ref(false);
const searching = ref(false);

const normalizedList = computed(() => {
  if (Array.isArray(props.list)) {
    return props.list.map(item => (typeof item === 'object' ? item : { label: item, value: item }));
  } else {
    return Object.keys(props.list).map(key => ({ label: props.list[key], value: key }));
  }
});

const toggleSearch = () => {
  searching.value = !searching.value;
  if (!searching.value) {
    searchQuery.value = '';
  }
}

const clearSearch = () => {
  searchQuery.value = '';
};

const filteredList = computed(() => {
  if (searchQuery.value) {
    return normalizedList.value.filter(item => item.label.toLowerCase().includes(searchQuery.value.toLowerCase()));
  }
  return normalizedList.value;
});

const buttonLabel = computed(() => {
  return `Sélection (${selectedValues.value.length})`;
});

const findLabelByValue = (value) => {
  const item = normalizedList.value.find(item => item.value === value);
  return item ? item.label : '';
};

onMounted(() => {
  document.addEventListener('click', outsideClickListener);
  if (normalizedList.value.length > 0 && selectedValues.value.length === 0) {
    selectedValues.value.push(normalizedList.value[0].value);
  }
});

onUnmounted(() => {
  document.removeEventListener('click', outsideClickListener);
});

const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

const outsideClickListener = (event) => {
  if (!selectRef.value.contains(event.target)) {
    isOpen.value = false;
  }
};

const onHover = (value) => {
  emit('hover', value);
};

const removeValue = (value) => {
  selectedValues.value = selectedValues.value.filter(val => val !== value);
  emit('update:selected', selectedValues.value);
};

const clearSelected = () => {
  selectedValues.value = [];
  emit('update:selected', selectedValues.value);
};

const handleSelectAll = (value) => {
  if (value) {
    selectedValues.value = normalizedList.value.map(item => item.value);
  } else {
    selectedValues.value = [];
  }
  emit('update:selected', selectedValues.value);
};

watch(selectedValues, (newValues) => {
  emit('update:selected', newValues);
  selectAll.value = newValues.length === normalizedList.value.length;
});

watch(() => props.list, () => {
  if (normalizedList.value.length > 0) {
    selectedValues.value = [normalizedList.value[0].value];
    emit('update:selected', selectedValues.value);
  }
}, { deep: true, immediate: props.immediate });
</script>


<style scoped>
button {
  border: solid 1px var(--sad-nightblue);
  font-weight: 400;
}


.select-container {
  display: flex;
  flex-wrap: wrap;
}

.select {
  position: relative;
  display: inline-block;
}

.select-dropdown,
.selected-values {
  position: absolute;
  top: 110%;
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
  max-height: 200px;
  overflow-y: auto;
}

.actions {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  position: relative;
  gap: 10px;
  padding: 0.25rem;
  flex-wrap: wrap;
}

.input-container {
  position: relative;

}

.search-input {
  border-radius: 25px;
  border: 1px solid var(--sad-lightgray);
  padding: 4px 10px;
  background: white;
  color: var(--sad-nightblue);
}

.clear-search {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #999;
  margin: 0;
}


.actions .expand {
  width: 140px;
  transition: width 0.3s ease;
}

.actions .collapse {
  width: 0px;
  transition: width 0.3s ease;
  opacity: 0;
  padding: 0;
}

.select-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1em;
  padding: 0.25rem;
}

.select-item label {
  flex: 1 0 auto;
}

.checkbox-input {
  position: absolute;
  opacity: 0;
  z-index: -1;
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  padding-right: 25px;
}

.checkbox-custom {
  display: inline-block;
  width: 15px;
  height: 15px;
  margin-left: 5px;
  border-radius: 2px;
  background-color: white;
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  box-sizing: border-box;
}

.checkbox-input:checked+.checkbox-label .checkbox-custom {
  background-color: var(--sad-orange);
  border-color: var(--sad-orange);
  background-image: url("data:image/svg+xml,%3Csvg width='8' height='6' viewBox='0 0 8 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M6.66634 1.66663L3.33301 4.99996L1.33301 2.99996' stroke='white' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E%0A");
  background-repeat: no-repeat;
  background-position: center;
  background-size: 10px;
  border-radius: 4px;
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

.selected-values {
  display: flex;
  flex-wrap: wrap;
  gap: 0.2rem;
  align-items: center;
  justify-content: flex-start;
  right: 100%;
  transform: translateX(-5px);
  left: auto;
  width: 200px;
  padding: 0.5em;
  /* max-height: 150px; Adjust the height as needed */
}

.chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  font-weight: bold;
  color: white;
  background-color: var(--sad-nightblue);
  padding: 0.25rem 0.5rem;
  border-radius: 10px;
  flex: 0 1 auto;
  height: 25px;
}

.close-chip {
  margin-left: 0.5rem;
  cursor: pointer;
}

.clear-button {

  cursor: pointer;
  padding: 0;
}

.clear-button:hover {
  color: var(--sad-orange);
}

/* Responsive styles */
@media only screen and (max-width: 600px) {

  .select-dropdown,
  .selected-values {
    position: static;
    width: 100%;
  }
}
</style>

