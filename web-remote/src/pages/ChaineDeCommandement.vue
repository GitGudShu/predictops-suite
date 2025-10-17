<template>

  <q-page>
    <q-page-sticky position="bottom-right" :offset="[18, 18]" style="z-index: 1;" v-if="isAllowed && dpt !== '01'">
      <q-btn dense fab color="primary" @click="toggleView" size="sm">
        <q-icon :name="view === 'visualize' ? 'fa-solid fa-pen' : 'fa-solid fa-eye'" size="15px"></q-icon>
      </q-btn>
    </q-page-sticky>
    <div class="cards-container" v-if="dpt === '01' && !creatingCard && cards.length === 0">
        <Card icon="explore" header-text-size="fs-md" header-text="Carte"
          style="min-width: 350px;">
          <template #body>
            <Map type="cdc" controls />
          </template>
        </Card>
        <!-- <Card icon="link" header-text-size="fs-md" header-text="Chaine de commandement"
          style="min-width: 350px;">
          <template #body>
            <div class="card-body full-height relative-position">

              <div v-if="loading" class="absolute-full flex flex-center">
                <q-spinner-tail size="100px" color="secondary" />
              </div>
              <Table v-if="!loading" :data="chainOfCommandData" :columns="[
                { field: 'fonction', label: 'Fonction' },
                { field: 'grade', label: 'Grade' },
                { field: 'nom', label: 'Nom' },
                { field: 'prenom', label: 'Prénom' },
              ]" :rows-per-page="10">
              </Table>

            </div>
          </template>
        </Card> -->
      </div>
    <div class="actions-bar" v-if="isAllowed && dpt !== '01'">
      <Button btn-text="Ajouter une carte" @click="creatingCard = true" btn-size="md-btn" left-icon="fa-solid fa-plus"
        bg-color="var(--sad-nightblue)" txt-color="white" v-if="view !== 'visualize'" />
      <Button v-if="!specialCardPresent && cards.length > 0 && view !== 'visualize'" btn-text="Ajouter en-tête"
        @click="addSpecialCard" btn-size="md-btn" left-icon="fa-solid fa-plus" bg-color="var(--sad-nightblue)"
        txt-color="white" />
      <div class="right-buttons">
        <Button v-if="view !== 'visualize'" @click="refreshData" left-icon="mdi-refresh" bg-color="var(--sad-nightblue)"
          txt-color="white" />
      </div>
    </div>
    <VueDraggable v-model="cards" @end="onDragEnd" class="container" handle=".handle" v-if="dpt !== '01'">
      <div class="q-mt-xl empty"
        v-if="!loading && activeChainOfCommandData.length === 0 && !creatingCard && view !== 'visualize' && dpt !== '01'"
        style="width: 50%; margin: 0 auto">
        <div class="text-bold text-h5 text-center text-black">Aucune chaine de commandement active</div>
        <Button left-icon="fa-solid fa-plus" btn-text="Nouvelle carte" bg-color="var(--sad-nightblue)" btn-size="sm-btn"
          @click="creatingCard = true" txt-color="white" v-if="isAllowed" />
      </div>


      <div v-for="(card, index) in cards" :key="card.id" class="cdc-card" :class="{ 'special-card': card.special }">
        <!-- Special Card -->
        <template v-if="card.special">
          <div class="special-card-content">

            <div class="special-coat-of-arms-container" v-if="!card.editing && card.image">
              <img :src="card.image" alt="Logo" class="special-card-image" />
            </div>
            <div class="special-coat-of-arms-picker" v-if="card.editing && !card.image">
              <q-icon name="fa-solid fa-plus" size="24px" color="primary" />
              <input type="file" accept="image/*"
                style="opacity: 0; position: absolute; max-width: 50px; height: 100%; cursor: pointer; z-index: 100000"
                @change="onFileChange($event, card)" />
            </div>
            <div class="special-coat-of-arms-preview" v-if="card.image && card.editing">
              <q-icon name="mdi-close-circle" @click="clearImage(card)" class="special-clear-image" size="24px"
                color="primary" />
              <img :src="card.image" alt="Logo" class="special-card-image" />
            </div>
            <input v-if="card.editing" v-model="card.title" class="special-card-title-input" type="text"
              placeholder="Title" style="text-align: center;" />
            <fit-text v-if="!card.editing" :text="card.title" :min-font-size="16" :step="1" :grow="true" class="agent"
              style="margin-bottom: 10px; padding: 5px" />

            <q-icon name="fa-solid fa-grip" class="handle" color="var(--sad-nightblue)" size="20px"
              v-if="!card.editing && isAllowed && view !== 'visualize'"></q-icon>
            <div class="special-card-footer" v-if="!card.editing && isAllowed && view !== 'visualize'">
              <Button left-icon="fa-solid fa-pen" @click="editCard(card)" bg-color="transparent"
                txt-color="var(--sad-nightblue)" />
              <q-separator vertical inset />
              <Button left-icon="mdi-delete-empty" @click="deleteCard(card)" bg-color="transparent"
                txt-color="var(--sad-red)" />
            </div>

            <div class="special-card-footer editing" v-if="card.editing && isAllowed">
              <Button left-icon="fa-solid fa-xmark" @click="discardEdit(card)" bg-color="transparent"
                txt-color="var(--sad-red)" />
              <q-separator vertical inset />
              <Button left-icon="fa-solid fa-check" @click="confirmEdit(card)" bg-color="transparent"
                txt-color="var(--sad-nightblue)" />
            </div>
          </div>
        </template>


        <!-- Regular Card -->
        <template v-else>
          <div class="cdc-card-header drag-handle"
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
              <q-icon name="mdi-close-circle" @click="clearImage(card)" class="clear-image" size="24px"
                color="primary" />
              <img :src="card.image" alt="Coat of Arms" class="coat-of-arms" />
            </div>

            <fit-text v-if="!card.editing" :text="card.title" :min-font-size="16" :step="0.1" :grow="true"
              class="cdc-title" :style="{ 'width': card.image ? 'calc(100% - 50px)' : '100%', 'height': '100%' }" />
            <input v-if="card.editing" v-model="card.title" class="cdc-title-input" type="text"
              :style="{ 'width': card.image ? 'calc(100% - 75px)' : '100%' }" />

            <input v-if="card.editing" type="color" v-model="card.color" class="color-picker" />
          </div>

          <div class="cdc-card-body">
            <fit-text v-if="!card.editing"
              :text="card.auto ? (functionMap[card.function] && functionMap[card.function][0] ? (functionMap[card.function][0] === 'undefined. ' ? card.body : functionMap[card.function][0]) : card.body) : card.body"
              :min-font-size="16" :step="1" :grow="true" class="agent" />
            <!-- Body input that binds directly to card.body -->
            <input v-model="card.body" class="cdc-body-input" type="text" placeholder="Agent"
              v-if="card.auto && card.editing" readonly />
            <input v-model="card.body" class="cdc-body-input" type="text" placeholder="Agent"
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
            <q-icon name="fa-solid fa-grip" class="handle" color="var(--sad-nightblue)" size="20px"
              v-if="!card.editing && isAllowed && view !== 'visualize'"></q-icon>
          </div>

          <div class="cdc-card-footer"
            v-if="!card.editing && !editingCard && !creatingCard && isAllowed && view !== 'visualize'">
            <Button @click="editCard(card)" left-icon="fa-solid fa-pen" bg-color="transparent"
              txt-color="var(--sad-nightblue)" />
            <q-separator vertical inset />
            <Button @click="duplicateCard(card)" left-icon="fa-solid fa-clone" bg-color="transparent"
              txt-color="var(--sad-nightblue)" />
            <q-separator vertical inset />
            <Button left-icon="mdi-delete-empty" @click="deleteCard(card)" bg-color="transparent"
              txt-color="var(--sad-red)" />
          </div>

          <div class="cdc-card-footer editing" v-if="card.editing && isAllowed">
            <Button left-icon="fa-solid fa-xmark" @click="discardEdit(card)" bg-color="transparent"
              txt-color="var(--sad-red)" />
            <q-separator vertical inset />
            <Button left-icon="fa-solid fa-check" @click="confirmEdit(card)" bg-color="transparent"
              txt-color="var(--sad-nightblue)" />
          </div>
        </template>
      </div>
      <!-- New Card Form -->
      <div v-if="creatingCard" class="cdc-card">
        <div class="cdc-card-header" :style="{ 'background-color': 'transparent', 'color': 'var(--sad-nightblue)' }">
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
          <input v-model="newCard.title" class="cdc-title-input" type="text" placeholder="Titre"
            :style="{ 'width': 'calc(100% - 75px)' }" />
          <input type="color" v-model="newCard.color" class="color-picker" />
        </div>

        <div class="cdc-new-card-body">
          <input v-model="newCard.body" class="cdc-body-input" type="text" placeholder="Agent" v-if="!newCard.auto" />
          <input v-model="computedBody" class="cdc-body-input" type="text" placeholder="Agent" v-if="newCard.auto"
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

        <div class="cdc-card-footer editing" v-if="isAllowed">
          <Button left-icon="fa-solid fa-xmark" @click="discardNewCard" bg-color="transparent"
            txt-color="var(--sad-red)" />
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
import Card from 'src/components/Card.vue';
import Map from 'src/components/Map.vue';
import Table from 'src/components/Table.vue';
import { determineTextColor } from 'src/utils/textUtils';
import FitText from 'src/components/FitText.vue';
import { Base64 } from 'js-base64';
import { Cookies } from 'quasar';
import { VueDraggable } from 'vue-draggable-plus'
import { notifyUser } from 'src/utils/notifyUser';
import { getCachedImage, cacheImageInDB, clearExpiredImages } from 'src/utils/indexedDB';
import { useRoute } from 'vue-router'

const location = useRoute();

const publicPath = process.env.PUBLIC_PATH || '/predictops/';

const decodedUser = JSON.parse(Base64.decode(Cookies.get('user')));
const isAllowed = computed(() => decodedUser.role == 'admin-cta' || decodedUser.role == 'maintainer' || decodedUser.role == 'admin');


const view = ref('visualize');

const dpt = computed(() => { return localStorage.getItem("dpt") || location.params.dpt })
const loading = ref(true);
const creatingCard = ref(false);
const editingCard = ref(false);
const currentCard = ref({});
const specialCardPresent = ref(false);
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

const computedBody = computed(() => {
  if (newCard.value.auto && newCard.value.function) {
    const entries = functionMap.value[newCard.value.function];
    return entries[0]
  }
  return newCard.value.body; // Return the manual body if auto is off
});

const toggleView = () => {
  view.value = view.value === 'visualize' ? 'edit' : 'visualize';
};


watch(() => newCard.value.function, (newValue) => {
  if (newCard.value.auto) {
    newCard.value.body = computedBody.value; // Update body when the function changes
  }
});


const chainOfCommandData = ref([]);
const activeChainOfCommandData = ref([]);

const uniqueFunctions = ref([]);

const cards = ref([]);


const computeBodyFromFunction = (card) => {
  if (card.auto && card.function) {
    const entries = functionMap.value[card.function];
    return entries[0] // Join the entries if multiple
  }
  return card.body; // Return the manual body if auto is off
};


// Function to fetch the chain of command data
const fetchChainOfCommand = async () => {
  loading.value = true;
  try {
    const chainOfCommandResponse = await api.get(`/data/chain-of-command?dpt=${dpt.value}`);
    chainOfCommandData.value = chainOfCommandResponse.data;
    uniqueFunctions.value = [...new Set(chainOfCommandData.value.map(item => item.fonction))];

    chainOfCommandData.value.forEach(item => {
      if (!functionMap.value[item.fonction]) {
        functionMap.value[item.fonction] = [];
      }
      functionMap.value[item.fonction].push(`${item.grade === 'PAT' ? item.prenom[0] + '.' : item.grade} ${item.nom}`);
    });
    loading.value = false;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération de la chaine de commandement.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false;
  }
};

const fetchActiveChainOfCommand = async () => {
  loading.value = true;
  try {
    const activeChainOfCommandResponse = await api.get(`/data/active-chain-of-command?dpt=${dpt.value}`);
    activeChainOfCommandData.value = activeChainOfCommandResponse.data;

    // Populate cards array with fetched data
    cards.value = activeChainOfCommandData.value.map(item => ({
      id: item.id,
      title: item.title,
      body: item.body,
      image: '', // Initially empty, we'll load the image asynchronously
      color: item.color,
      editing: false,
      special: item.special || false,
      order: item.order,
      dpt: item.dpt,
      auto: item.auto,
      function: item.function,
    }));

    checkSpecialCard();
    cards.value = cards.value.sort((a, b) => a.order - b.order);

    // Load images for each card with caching
    cards.value.forEach((card, index) => {
      loadCardImageWithCache(card, index);
    });

    // Watch for changes in each card's function when editing
    cards.value.forEach((card) => {
      watch(() => card.function, (newValue) => {
        card.body = computeBodyFromFunction(card);
      });

      watch(() => card.auto, (newAuto) => {
        if (newAuto) {
          card.body = computeBodyFromFunction(card);
        } else {
          card.body = functionMap.value[card.function][0];
        }
      });
    });

    // Clear expired images from the cache
    clearExpiredImages();

    loading.value = false;
  } catch (error) {
    notifyUser({
      icon: "error",
      message: "Erreur lors de la récupération de la chaine de commandement active.",
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
    const imageResponse = await api.get(`/data/image/active_cdc/${card.id}`);
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



const checkSpecialCard = () => {
  specialCardPresent.value = cards.value.some(card => card.special);
  if (specialCardPresent.value) {
    // Ensure the special card is always at the second position
    const index = cards.value.findIndex(card => card.special);
    if (index !== 1) {
      const specialCard = cards.value.splice(index, 1)[0];
      cards.value.splice(1, 0, specialCard);
    }
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
    const response = await api.patch(`/admin-cta/update-card-order`, { cards: cards.value });
    if (!response.data.success) {
      notifyUser({ icon: "error", message: "Erreur lors de la mise à jour de l'ordre.", color: "red", position: "bottom", timeout: 2500 })
    }
    loading.value = false;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la mise à jour de l'ordre.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false;
  }
};
const fetchImageAsBase64 = async (imagePath) => {
  try {
    // Fetch the image from the specified path
    const response = await fetch(imagePath);
    const blob = await response.blob();

    // Convert the Blob to a base64 string using FileReader
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        resolve(reader.result); // This is the base64-encoded image
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob); // Read the blob as a data URL (base64)
    });
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la conversion de l'image en base64.", color: "red", position: "bottom", timeout: 2500 })
    return null;
  }
};

const addSpecialCard = async () => {
  try {
    const specialCardData = {
      title: 'Permanence opérationnelle',
      image: await fetchImageAsBase64(`${publicPath}logo-${dpt.value}.png`),
      body: 'Permanence opérationnelle',
      dpt: dpt.value
    };
    loading.value = true;
    const response = await api.post(`/admin-cta/create-special-chain-of-command`, specialCardData);
    if (response.data.success) {
      cards.value.splice(1, 0, { ...specialCardData, id: response.data.id, order: 2, special: true });
      specialCardPresent.value = true;
      loading.value = false;
    }
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la création de la carte spéciale.", color: "red", position: "bottom", timeout: 2500 })
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

    const response = await api.post(`/admin-cta/create-active-chain-of-command`, duplicatedCard);
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
    const response = await api.patch(`/admin-cta/update-active-chain-of-command`, card);
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
    const response = await api.post(`/admin-cta/create-active-chain-of-command`, newCard.value);
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
    const endpoint = card.special
      ? `/admin-cta/delete-special-chain-of-command/${card.id}`
      : `/admin-cta/delete-active-chain-of-command/${card.id}`;

    const response = await api.delete(endpoint);
    if (response.data.success) {
      const index = cards.value.findIndex(c => c.id === card.id);
      if (index !== -1) {
        cards.value.splice(index, 1);
      }
      checkSpecialCard();
    }
    loading.value = false;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la suppression.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false;
  }
};

const refreshData = () => {
  fetchChainOfCommand();
  fetchActiveChainOfCommand();
}

onMounted(() => {
  fetchChainOfCommand();
  fetchActiveChainOfCommand();
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

.cards-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-wrap: wrap;
  flex: 1;
  gap: 1em;
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

.body-select {
  width: 100%;
}

.cdc-card-footer {
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

.cdc-card:hover .cdc-card-footer {
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
