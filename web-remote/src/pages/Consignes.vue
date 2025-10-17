<template>
  <q-page>
    <q-page-sticky position="bottom-right" :offset="[18, 18]" style="z-index: 1;" v-if="isAllowed">
      <q-btn dense fab color="primary" @click="toggleView" size="sm">
        <q-icon :name="view === 'visualize' ? 'fa-solid fa-pen' : 'fa-solid fa-eye'" size="15px"></q-icon>
      </q-btn>
    </q-page-sticky>
    <div class="actions-bar" v-if="isAllowed && view !== 'visualize'">
      <div class="right-buttons">
        <Button left-icon="fa-solid fa-plus" btn-text="Nouvelle consigne" bg-color="var(--sad-nightblue)"
          btn-size="sm-btn" @click="openAddGuideline" txt-color="white" />
        <q-checkbox v-model="selectAll" @update:model-value="handleSelectAll" label="Tout séléctionner" dense
          class="text-black text-bold" :disable="guidelinesList.length === 0" />
        <Button v-if="selectedGuidelines.length" left-icon="fa-solid fa-trash" btn-text="Supprimer" btn-size="sm-btn"
          @click="deleteSelectedGuidelines" class="delete-selected" bg-color="var(--sad-red)" txt-color="white" />
      </div>
    </div>
    <div class="container">
      <div class="q-mt-xl empty"
        v-if="(guidelinesList.length === 0 && isAllowed) || (!guidelinesList.some(guideline => guideline.active) && !isAllowed) && view !== 'visualize'">
        <div class="text-bold text-h5 text-center text-black q-ma-sm">Aucune consigne</div>
        <div class="text-h6 text-center text-black q-mb-lg" v-if="isAllowed">Ajouter une consigne pour commencer</div>
        <Button left-icon="fa-solid fa-plus" btn-text="Nouvelle consigne" bg-color="var(--sad-nightblue)"
          btn-size="sm-btn" @click="openAddGuideline" txt-color="white" v-if="isAllowed" />
      </div>
      <GuidelineCard v-for="guideline in guidelinesList" :key="guideline._id" :guideline="guideline"
        @selectGuideline="selectGuideline" :is-selected="selectedGuidelines.includes(guideline._id)"
        @updateGuideline="updateGuideline" @deleteGuideline="deleteGuideline" @toggleActive="toggleActive"
        :editable="isAllowed && view !== 'visualize'" truncate v-show="showGuideline(guideline)" :diffusion-lists="diffusionLists"/>
    </div>
    <q-dialog v-model="showAddGuideline" style="z-index: 100000;">
      <div class="add-guideline-form">
        <div class="add-guideline-form-header">
          <div class="text-h4 text-bold text-center q-pa-lg">Ajouter une consigne</div>
        </div>
        <div class="form-body">
          <div v-if="errorMessage" class="text-warning text-bold text-center">{{ errorMessage }}</div>
          <div class="dates flex" :style="{ 'gap': '1em' }">
            <div class="input-wrapper" :style="{ 'flex': '1 1 40%' }">
              <span class="text-h7 text-bold q-mb-sm">Début :</span>
              <q-input input-class="text-black" dense v-model="startDate" bg-color="white" type="text" standout
              :style="{ 'flex': '1 0 40%' }" mask="##/##/####" fill-mask>
                <template v-slot:append>
                  <q-icon name="event" class="cursor-pointer" color="primary">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date v-model="startDate" mask="DD/MM/YYYY" />
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
              <q-input standout bg-color="white" dense input-class="text-black" :disable="!startDate" v-model="startTime" mask="time" :rules="['time']" no-error-icon>
                <template v-slot:append>
                  <q-icon name="access_time" class="cursor-pointer" color="primary">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-time v-model="startTime">
                        <div class="row items-center justify-end">
                          <q-btn v-close-popup label="Close" color="primary" flat />
                        </div>
                      </q-time>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>
            <div class="input-wrapper" :style="{ 'flex': '1 1 40%' }">
              <span class="text-h7 text-bold q-mb-sm">Fin :</span>
              <q-input input-class="text-black" dense v-model="endDate" bg-color="white" type="text" standout
                :style="{ 'flex': '1 0 40%' }" mask="##/##/####" fill-mask>
                <template v-slot:append>
                  <q-icon name="event" class="cursor-pointer" color="primary">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date v-model="endDate" mask="DD/MM/YYYY" />
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
              <q-input standout bg-color="white" dense input-class="text-black" :disable="!endDate" v-model="endTime" mask="time" :rules="['time']" no-error-icon>
                <template v-slot:append>
                  <q-icon name="access_time" class="cursor-pointer" color="primary">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-time v-model="endTime">
                        <div class="row items-center justify-end">
                          <q-btn v-close-popup label="Close" color="primary" flat />
                        </div>
                      </q-time>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>
          </div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Thème : </span>
            <q-input input-class="text-black" dense v-model="guidelineTheme" bg-color="white" type="text"
              standout></q-input>
          </div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Consigne : </span>
            <q-input input-class="text-black" dense bg-color="white" type="text" standout v-model="guidelineMessage"
              autogrow />
          </div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Active : </span>
            <q-toggle v-model="guidelineActive" color="secondary" />
          </div>
          <Button :loading="loading" btn-text="Ajouter" btn-type="submit" left-icon="fa-solid fa-plus" btn-size="md-btn"
            bg-color="var(--sad-orange)" txt-color="white" style="margin-top: auto;" @click="addGuideline" />
        </div>
      </div>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from "vue";
import { api } from "src/boot/axios";
import { notifyUser } from "src/utils/notifyUser";
import GuidelineCard from "src/components/GuidelineCard.vue";
import Button from "src/components/Button.vue";
import { showDialog } from "src/utils/dialogUtil";
import { Base64 } from "js-base64";
import { Cookies, is } from "quasar";
import { useRoute } from "vue-router";

const location = useRoute();

const decodedUser = JSON.parse(Base64.decode(Cookies.get('user')))
const view = ref('visualize')
const isAllowed = ref(decodedUser.role === 'maintainer' || decodedUser.role === 'admin-cta' || decodedUser.role === 'admin')

const dpt = computed(() => { return localStorage.getItem("dpt") || location.params.dpt })
const guidelinesList = ref([])

let refreshInterval;

const startDate = ref()
const startTime = ref()
const endDate = ref()
const endTime = ref()
const guidelineTheme = ref('')
const guidelineMessage = ref('')
const guidelineActive = ref(true)

const errorMessage = ref('')

const loading = ref()
const selectAll = ref(false)

const showAddGuideline = ref(false)

const selectedGuidelines = ref([])

const diffusionLists = ref([])

const toggleView = () => {
  view.value = view.value === 'visualize' ? 'edit' : 'visualize';
}

const handleSelectAll = (value) => {
  if (value) {
    selectedGuidelines.value = guidelinesList.value
      .map(guideline => guideline._id);
  } else {
    selectedGuidelines.value = [];
  }
}

const showGuideline = (guideline) => {
  if (isAllowed.value) {
    return true
  }
  else if (guideline.active && decodedUser.role === 'user') {
    return true
  }
  else {
    return false
  }
}

const selectGuideline = (_id) => {
  if (selectedGuidelines.value.includes(_id)) {
    selectedGuidelines.value = selectedGuidelines.value.filter(e => e !== _id);
  } else {
    selectedGuidelines.value.push(_id);
  }
}

const openAddGuideline = () => {
  showAddGuideline.value = true
}

const getGuidelines = async () => {
  try {
    const response = await api.get(`/data/guidelines?dpt=${dpt.value}`);
    guidelinesList.value = response.data
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la sélection des consignes.", color: "red", position: "bottom", timeout: 2500 })
  }
}
const addGuideline = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await api.post(`/admin-cta/create-guideline`, {
      author: decodedUser.email,
      start_date: startDate.value && startDate.value !== '__/__/____' ? startDate.value : 'Indéterminée',
      start_time: startTime.value ? startTime.value : null,
      end_date: endDate.value && endDate.value !== '__/__/____' ? endDate.value : 'Indéterminée',
      end_time: endTime.value ? endTime.value : null,
      theme: guidelineTheme.value,
      active: guidelineActive.value,
      message: guidelineMessage.value,
      dpt: dpt.value
    });
    guidelinesList.value = [response.data.guideline, ...guidelinesList.value]
    showAddGuideline.value = false
    loading.value = false
    startDate.value = ''
    startTime.value = ''
    endDate.value = ''
    endTime.value = ''
    guidelineTheme.value = ''
    guidelineMessage.value = ''
    guidelineActive.value = true
    notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
  } catch (error) {
    errorMessage.value = error.response.data.message
    loading.value = false
  }
}

const updateGuideline = (updatedGuideline) => {
  const index = guidelinesList.value.findIndex(guideline => guideline._id === updatedGuideline._id)
  if (index !== -1) {
    guidelinesList.value.splice(index, 1, updatedGuideline)
  }
}

const toggleActive = async (_id, active) => {
  try {
    const response = await api.patch(`/admin-cta/toggle-guideline-active`, { _id, active });
    const guideline = guidelinesList.value.find(u => u._id === _id);
    if (guideline) {
      guideline.active = active;
    }
    notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la modification de la consigne.", color: "red", position: "bottom", timeout: 2500 });
  }
}


const deleteGuideline = async (_id) => {
  try {
    const response = await api.delete(`/admin-cta/delete-guideline`, { data: { _id } });
    guidelinesList.value = guidelinesList.value.filter(guideline => guideline._id !== _id);
    notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la suppression de la consigne.", color: "red", position: "bottom", timeout: 2500 });
  }
}

const deleteSelectedGuidelines = () => {
  showDialog({
    focus: "none",
    style: { width: "50%", },
    dark: true,
    message: "Êtes-vous sûr de vouloir supprimer ces consignes ?",
    ok: {
      label: 'OK',
      color: 'secondary',
    },
    cancel: {
      label: 'Annuler',
      color: 'warning',
    },

  },
    async () => {
      try {
        const response = await api.delete(`/admin-cta/delete-guidelines`, { data: { _ids: selectedGuidelines.value } });
        guidelinesList.value = guidelinesList.value.filter(guideline => !selectedGuidelines.value.includes(guideline._id));
        selectAll.value = false
        selectedGuidelines.value = [];
        notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
      } catch (error) {
        notifyUser({ icon: "error", message: "Erreur lors de la suppression des consignes.", color: "red", position: "bottom", timeout: 2500 });
      }
    });
}
onMounted(async () => {
  getGuidelines()
  if(isAllowed.value) {
      const dlResponse = await api.get(`/admin/diffusion-lists?dpt=${dpt.value}`);
      diffusionLists.value = dlResponse.data
    }
  refreshInterval = setInterval(getGuidelines, 15000)
})

onUnmounted(() => {
  clearInterval(refreshInterval);
});

</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  margin: 0 auto;
  gap: 1em;
  width: 90%;
}

.actions-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
  width: 100%;
}

.add-guideline-form {
  background: var(--sad-nightblue);
  display: flex;
  flex-direction: column;
  gap: 2em;
  padding: 1em;
  color: white;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5em;
  width: 100%;
}

.input-wrapper span {
  margin: 0;

}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 2em;
  height: 100%;
}


.calendar-icon {
  cursor: pointer;
  width: 2em;
  height: 2em;
  background: white;
  border-radius: 50%;
}
</style>
