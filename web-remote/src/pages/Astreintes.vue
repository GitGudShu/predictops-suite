<template>

  <q-page>
    <q-page-sticky position="bottom-right" :offset="[18, 18]" style="z-index: 1;" v-if="isAllowed">
      <q-btn dense fab color="primary" @click="toggleView" size="sm">
        <q-icon :name="view === 'visualize' ? 'fa-solid fa-pen' : 'fa-solid fa-eye'" size="15px"></q-icon>
      </q-btn>
    </q-page-sticky>
    <div class="actions-bar" v-if="isAllowed && view !== 'visualize'">
      <Button btn-text="Ajouter une carte" @click="creatingCard = true" btn-size="md-btn" left-icon="fa-solid fa-plus"
        bg-color="var(--sad-nightblue)" txt-color="white" />
      <div class="right-buttons">
        <Button v-if="view !== 'visualize'" @click="fetchActiveDuty" left-icon="mdi-refresh" bg-color="var(--sad-nightblue)"
          txt-color="white" />
      </div>
    </div>
    <VueDraggable v-model="cards" @end="onDragEnd" class="container" handle=".handle">
      <div class="q-mt-xl empty" v-if="cards.length === 0 && !creatingCard && view !== 'visualize'"
        style="width: 50%; margin: 0 auto">
        <div class="text-bold text-h5 text-center text-black">Aucune astreinte active</div>
        <div class="text-h6 text-center text-black" v-if="isAllowed">Ajoutez une carte d'astreinte pour commencer</div>
        <Button btn-text="Ajouter une carte" @click="creatingCard = true" btn-size="md-btn" left-icon="fa-solid fa-plus"
          bg-color="var(--sad-nightblue)" txt-color="white" v-if="isAllowed" />
      </div>
      <div v-for="(card, index) in cards" :key="card.id" class="duty-card">
        <div class="duty-card-header drag-handle"
          :style="{ 'background-color': card.editing ? 'transparent' : card.color || '#181632', 'color': determineTextColor(card.color || '#fff') }">
          <div class="coat-of-arms-container" v-if="!card.editing && card.image">
            <img :src="card.image" alt="Coat of Arms" class="coat-of-arms" />
          </div>
          <div class="coat-of-arms-picker" v-if="!card.image && card.editing">
            <q-icon name="fa-solid fa-plus" size="24px" color="primary" />
            <input type="file" accept="image/*"
              style="opacity: 0; position: absolute; max-width: 50px; height: 100%; cursor: pointer; z-index: 100000"
              @change="onFileChange($event, card)" />
          </div>

          <div class="coat-of-arms-preview" v-if="card.image && card.editing">
            <q-icon name="mdi-close-circle" @click="clearImage(card)" class="clear-image" size="24px" color="primary" />
            <img :src="card.image" alt="Coat of Arms" class="coat-of-arms" />
          </div>

          <fit-text v-if="!card.editing" :text="card.title" :min-font-size="16" :step="1" :grow="true"
            class="duty-title" :style="{ 'width': card.image ? 'calc(100% - 50px)' : '100%', 'height': '100%' }" />
          <input v-if="card.editing" v-model="card.title" class="duty-title-input" type="text"
            :style="{ 'width': card.image ? 'calc(100% - 75px)' : '100%' }" />

          <input v-if="card.editing" type="color" v-model="card.color" class="color-picker" />
        </div>

        <div class="duty-card-body">
          <fit-text v-if="!card.editing"
          :text="card.auto ? (functionMap[card.function] && functionMap[card.function][0] ? (functionMap[card.function][0] === 'undefined. ' ? card.body : functionMap[card.function][0]) : card.body) : card.body"
          :min-font-size="16" :step="1" :grow="true" class="agent" />
          <input v-model="card.body" class="duty-body-input" type="text" placeholder="Agent"
            v-if="card.auto && card.editing" readonly />
          <input v-model="card.body" class="duty-body-input" type="text" placeholder="Agent"
            v-if="!card.auto && card.editing" />

          <div class="auto-or-free" v-if="card.editing">
            <q-select v-model="card.function" fill-input dense :options="uniqueFunctions"
              style="width: 100%; font-size: 20px; padding: 5px; text-wrap: nowrap" v-if="card.auto"
              @update:model-value="(value) => card.body = functionMap[value][0]">
              <template v-slot:no-option>
                <q-item>
                  <q-item-section class="text-grey">
                    Aucun résultat
                  </q-item-section>
                </q-item>
              </template>
            </q-select>
            <q-toggle v-model="card.auto" label="Auto" color="secondary" />
          </div>
          <q-icon name="fa-solid fa-grip" class="handle" color="var(--sad-nightblue)" size="20px" v-if="!card.editing && isAllowed && view !== 'visualize'"></q-icon>
        </div>

        <div class="duty-card-footer"
          v-if="!card.editing && !editingCard && !creatingCard && isAllowed && view !== 'visualize'">
          <Button left-icon="mdi-delete-empty" @click="deleteCard(card)" bg-color="transparent" txt-color="var(--sad-red)" />
          <q-separator vertical inset />
          <Button @click="editCard(card)" left-icon="fa-solid fa-pen" bg-color="transparent"
            txt-color="var(--sad-nightblue)" />
          <q-separator vertical inset />
          <Button @click="duplicateCard(card)" left-icon="fa-solid fa-clone" bg-color="transparent"
            txt-color="var(--sad-nightblue)" />
        </div>

        <div class="duty-card-footer editing" v-if="card.editing && isAllowed">
          <Button left-icon="fa-solid fa-xmark" @click="discardEdit(card)" bg-color="transparent" txt-color="var(--sad-red))" />
          <q-separator vertical inset />
          <Button left-icon="fa-solid fa-check" @click="confirmEdit(card)" bg-color="transparent"
            txt-color="var(--sad-nightblue)" />
        </div>

      </div>
      <!-- New Card Form -->
      <div v-if="creatingCard" class="duty-card">
        <div class="duty-card-header" :style="{ 'background-color': 'transparent', 'color': 'var(--sad-nightblue)' }">
          <div class="coat-of-arms-picker" v-if="!newCard.image">
            <q-icon name="fa-solid fa-plus" size="24px" color="primary" />
            <input type="file" accept="image/*"
              style="opacity: 0; position: absolute; max-width: 50px; height: 100%; cursor: pointer; z-index: 100000"
              @change="onFileChange($event, newCard)" />
          </div>
          <div class="coat-of-arms-preview" v-if="newCard.image && newCard.editing">
            <q-icon name="mdi-close-circle" @click="clearImage(newCard)" class="clear-image" size="24px"
              color="primary" />
            <img :src="newCard.image" alt="Coat of Arms" class="coat-of-arms" />
          </div>
          <input v-model="newCard.title" class="duty-title-input" type="text" placeholder="Titre"
            :style="{ 'width': 'calc(100% - 75px)' }" />
          <input type="color" v-model="newCard.color" class="color-picker" />
        </div>

        <div class="duty-card-body">
          <input v-model="newCard.body" class="duty-body-input" type="text" placeholder="Agent" v-if="!newCard.auto" />
          <input v-model="computedBody" class="duty-body-input" type="text" placeholder="Agent" v-if="newCard.auto"
            readonly />
          <div class="auto-or-free">
            <q-select v-model="newCard.function" fill-input dense :options="uniqueFunctions"
              style="width: 100%; font-size: 20px; padding: 5px; text-wrap: nowrap" v-if="newCard.auto">
              <template v-slot:no-option>
                <q-item>
                  <q-item-section class="text-grey">
                    Aucun résultat
                  </q-item-section>
                </q-item>
              </template>
            </q-select>

            <q-toggle v-model="newCard.auto" label="Auto" color="secondary" />
          </div>
        </div>

        <div class="duty-card-footer editing" v-if="isAllowed">
          <Button left-icon="fa-solid fa-xmark" @click="discardNewCard" bg-color="transparent" txt-color="var(--sad-red)" />
          <q-separator vertical inset />
          <Button left-icon="fa-solid fa-check" @click="saveNewCard" bg-color="transparent"
            txt-color="var(--sad-nightblue)" />
        </div>
      </div>
    </VueDraggable>

  </q-page>
</template>


<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { api } from 'src/boot/axios';
import Button from 'src/components/Button.vue';
import { determineTextColor } from 'src/utils/textUtils';
import FitText from 'src/components/FitText.vue';
import { Base64 } from 'js-base64';
import { Cookies } from 'quasar';
import { VueDraggable } from 'vue-draggable-plus'
import { notifyUser } from 'src/utils/notifyUser';
import { getCachedImage, cacheImageInDB, clearExpiredImages } from 'src/utils/indexedDB';
import { useRoute } from 'vue-router'

const location = useRoute();

const view = ref('visualize')

const decodedUser = JSON.parse(Base64.decode(Cookies.get('user')));
const isAllowed = computed(() => decodedUser.role == 'admin-cta' || decodedUser.role == 'maintainer' || decodedUser.role == 'admin');

let refreshInterval;

const dpt = computed(() => { return localStorage.getItem("dpt") || location.params.dpt })
const loading = ref(true);
const creatingCard = ref(false);
const editingCard = ref(false);
const currentCard = ref({});
const functionMap = ref({});
const newCard = ref({
  id: 0,
  title: '',
  body: '',
  image: '',
  color: '#181632',
  editing: true,
  dpt: dpt.value,
  auto: false,
  function: 'OAD',
});

const toggleView = () => {
  view.value = view.value === 'visualize' ? 'edit' : 'visualize';
};

const computedBody = computed(() => {
  if (newCard.value.auto && newCard.value.function) {
    const entries = functionMap.value[newCard.value.function];
    return entries[0]
  }
  return newCard.value.body; // Return the manual body if auto is off
});

watch(() => newCard.value.function, (newValue) => {
  if (newCard.value.auto) {
    newCard.value.body = computedBody.value; // Update body when the function changes
  }
});

const chainOfCommandData = ref([]);
const activeDutyData = ref([]);
const uniqueFunctions = ref([]);
const cards = ref([]);

const computeBodyFromFunction = (card) => {
  if (card.auto && card.function) {
    const entries = functionMap.value[card.function];
    return entries[0] // Join the entries if multiple
  }
  return card.body; // Return the manual body if auto is off
};

const fetchActiveDuty = async () => {
  loading.value = true;
  try {
    const chainOfCommandResponse = await api.get(`/data/chain-of-command?dpt=${dpt.value}`);
    chainOfCommandData.value = chainOfCommandResponse.data;

    const activeDutyResponse = await api.get(`/data/active-duty?dpt=${dpt.value}`);
    activeDutyData.value = activeDutyResponse.data;

    uniqueFunctions.value = [...new Set(chainOfCommandData.value.map(item => item.fonction))];

    chainOfCommandData.value.forEach(item => {
      if (!functionMap.value[item.fonction]) {
        functionMap.value[item.fonction] = [];
      }
      functionMap.value[item.fonction].push(
        `${item.grade === 'PAT' ? item.prenom[0] + '.' : item.grade} ${item.nom}`
      );
    });

    // Populate cards array with fetched data
    cards.value = activeDutyData.value.map(item => ({
      id: item.id,
      title: item.title,
      body: item.body,
      image: '',
      color: item.color,
      editing: false,
      special: item.special || false,
      order: item.order,
      dpt: item.dpt,
      auto: item.auto,
      function: item.function,
    }));

    // Sort cards based on order
    cards.value = cards.value.sort((a, b) => a.order - b.order);

    // Load images with caching support
    cards.value.forEach((card, index) => {
      loadCardImageWithCache(card, index);
    });

    // Clear expired images from the cache
    clearExpiredImages();

    loading.value = false;
  } catch (error) {
    notifyUser({
      icon: "error",
      message: "Erreur lors de la récupération des astreintes.",
      color: "red",
      position: "bottom",
      timeout: 2500
    });
    loading.value = false;
  }
};

// Function to load the image with caching support using IndexedDB
const loadCardImageWithCache = async (card, index) => {
  const cachedImage = await getCachedImage(card.id);
  if (cachedImage) {
    // Use the cached image
    cards.value[index].image = cachedImage;
    return;
  }

  // If not cached, fetch the image from the API
  try {
    const imageResponse = await api.get(`/data/image/active_astreintes/${card.id}`);
    cards.value[index].image = imageResponse.data.image;

    // Cache the newly fetched image
    await cacheImageInDB(card.id, imageResponse.data.image);
  } catch (error) {
    notifyUser({
      icon: "error",
      message: "Erreur lors de la récupération de l'image.",
      color: "red",
      position: "bottom",
      timeout: 2500
    });
    cards.value[index].image = ''; // Clear the image if the request fails
  }
};



const onDragEnd = async () => {
  // Update the order of cards after dragging
  cards.value.forEach((card, index) => {
    card.order = index + 1; // Reassign order based on the new position
  });
  loading.value = true;
  try {
    // Send updated order to the backend
    const response = await api.patch(`/admin-cta/update-card-order`, { cards: cards.value, page: 'astreintes' });
    if (!response.data.success) {
      notifyUser({ icon: "error", message: "Erreur lors de la mise à jour de l'ordre.", color: "red", position: "bottom", timeout: 2500 })
    }
    loading.value = false;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la mise à jour de l'ordre.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false;
  }
};

const editCard = (card) => {
  if (editingCard.value) return; // Prevent editing another card if one is already being edited
  currentCard.value = { ...card };
  card.editing = true;
  editingCard.value = true;
};

const duplicateCard = async (card) => {
  try {
    const duplicatedCard = {
      ...card,
      id: null, // New ID will be generated by the backend
      order: cards.value.length + 1, // Add to the end
      dpt: dpt.value
    };

    const response = await api.post(`/admin-cta/create-active-duty`, duplicatedCard);
    if (response.data.success) {
      cards.value.push({ ...duplicatedCard, id: response.data.id });
    }
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la duplication.", color: "red", position: "bottom", timeout: 2500 })
  }
};

const discardEdit = (card) => {
  Object.assign(card, currentCard.value);
  card.editing = false;
  editingCard.value = false;
};

const confirmEdit = async (card) => {
  try {
    // Check if card.image is a file object
    if (card.image instanceof File) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        card.image = e.target.result;
        await saveCard(card);
      };
      reader.readAsDataURL(card.image);
    } else {
      await saveCard(card);
    }
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la sauvegarde.", color: "red", position: "bottom", timeout: 2500 })
  }
};

const saveCard = async (card) => {
  loading.value = true;
  try {
    if (card.auto) {
      card.body = computeBodyFromFunction(card);
    }
    const response = await api.patch(`/admin-cta/update-active-duty`, card);
    const index = cards.value.findIndex(c => c.id === card.id);
    if (index !== -1) {
      cards.value[index] = { ...card, editing: false };
    }
    editingCard.value = false;
    loading.value = false;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la sauvegarde.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false;
  }
};

const onFileChange = (event, card) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      card.image = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const clearImage = (card) => {
  card.image = '';
};

const discardNewCard = () => {
  creatingCard.value = false;
  newCard.value = {
    id: 0,
    title: '',
    body: '',
    image: '',
    color: '#181632',
    editing: true,
    dpt: dpt.value,
    auto: false,
    function: 'OAD',
  };
};

const saveNewCard = async () => {
  loading.value = true;
  try {
    const response = await api.post(`/admin-cta/create-active-duty`, newCard.value);
    if (response.data.success) {
      cards.value.push({ ...newCard.value, id: response.data.id, editing: false });
      creatingCard.value = false;
      newCard.value = {
        id: 0,
        title: '',
        body: '',
        image: '',
        color: '#181632',
        editing: true,
        dpt: dpt.value,
        auto: false,
        function: 'OAD',
      };
    }
    loading.value = false;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la création.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false;
  }
};

const deleteCard = async (card) => {
  loading.value = true;
  try {
    const response = await api.delete(`/admin-cta/delete-active-duty/${card.id}`);
    if (response.data.success) {
      const index = cards.value.findIndex(c => c.id === card.id);
      if (index !== -1) {
        cards.value.splice(index, 1);
      }
    }
    loading.value = false;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la suppression.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false;
  }
};

onMounted(() => {
  fetchActiveDuty();
});

</script>


<style scoped>
.overlay {
  overflow: hidden;
  background: rgba(0, 0, 0, 0.7);
  z-index: 100000;
}

.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1em;
  position: sticky;
  top: 0;
  z-index: 100;
}

.container {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  flex-wrap: wrap;
  gap: 1em;
  color: var(--sad-nightblue);
  flex: 1;
}

.clear-image,
.special-clear-image {
  position: absolute;
  top: -15px;
  right: 0;
  width: 25px;
  height: 25px;
  cursor: pointer;
}

.special-clear-image {
  right: -15px;
}

.coat-of-arms-picker {
  width: 100%;
  max-width: 50px;
  height: 100%;
  margin-right: 10px;
  border: dashed 2px var(--sad-nightblue);
  display: grid;
  place-items: center;
}

.special-coat-of-arms-picker {
  width: 100px;
  height: 100px;
  border: dashed 2px var(--sad-nightblue);
  display: grid;
  place-items: center;
}

.special-coat-of-arms-preview {
  position: relative;
}

.color-picker {
  max-width: 25px;
  height: 25px;
}

.duty-body-input {
  width: 100%;
  height: 50%;
  background: inherit;
  border: none;
  color: var(--sad-nightblue);
  text-align: center;
  font-weight: 700;
  font-size: clamp(1rem, 4vw, 2rem);
}

.duty-card-footer {
  position: absolute;
  bottom: -12px;
  right: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: white;
  gap: 1em;
  border: 1px solid var(--sad-nightblue);
  border-radius: 5px;
  z-index: 10000;
  opacity: 0;
  transition: all 0.3s ease;
}

.duty-card:hover .duty-card-footer {
  opacity: 1;
  transition: all 0.3s ease;
}

input[type="color"] {
  padding: 0;
  cursor: pointer;
  border-radius: 3px;
}

input[type="color"]::-moz-color-swatch {
  border: none;
}

input[type="color"]::-webkit-color-swatch-wrapper {
  padding: 0;
}

input[type="color"]::-webkit-color-swatch {
  border: none;
}

.special-card-footer {
  position: absolute;
  bottom: -15px;
  right: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: white;
  gap: 1em;
  width: 100px;
  border: 1px solid var(--sad-nightblue);
  border-radius: 5px;
  z-index: 10000;
  opacity: 0;
  transition: all 0.3s ease;
}

.special-card:hover .special-card-footer {
  opacity: 1;
  transition: all 0.3s ease;
}
</style>
