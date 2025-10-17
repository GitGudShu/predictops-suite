<template>
  <div class="guideline-card">
    <div class="checkbox-container flex" v-if="editable">
      <q-checkbox v-model="selected" @update:model-value="handleSelect" />
    </div>
    <div class="guideline-card-header" :class="{ 'guideline-card-disabled': !guideline.active }">
      <div class="guideline-card-date text-italic text-weight-medium text-h6 q-pa-sm">
        {{ guideline.start_date }}
        <span v-if="guideline.start_time"> {{ guideline.start_time }}
        </span>
        - {{ guideline.end_date }}
        <span v-if="guideline.end_time"> {{ guideline.end_time }}</span>
        <div class="guideline-metadata" v-if="guideline.author && editable">
          Auteur.e : <span class="text-bold">{{ guideline.author }}</span>
        </div>
        <div class="guideline-metadata" v-if="guideline.last_updated_by && editable">
          Dernière modification par : <span class="text-bold">{{ guideline.last_updated_by }}</span>
        </div>
        <div class="guideline-metadata" v-if="guideline.last_updated_at && editable">
          Dernière modification : <span class="text-bold">{{ guideline.last_updated_at }}</span>
        </div>
      </div>
      <div class="guideline-card-theme text-weight-bold text-h6 q-pa-sm">{{ guideline.theme }}
      </div>

    </div>
    <div class="guideline-card-body" :class="{ 'guideline-card-disabled': !guideline.active }">
      <div class="guideline-card-message" v-if="truncate">
        {{ truncatedMessage }}
        <span v-if="guideline.message.length > 275" class="toggle-text" @click="toggleText">
          <q-icon :name="showFullText ? 'fa-solid fa-caret-up' : 'fa-solid fa-caret-down'"></q-icon>
        </span>
      </div>
      <div v-else class="guideline-card-message">{{ guideline.message }}</div>
      <Button v-if="guideline.active && isAllowed" left-icon-size="16px" left-icon="fa-solid fa-bullhorn" @click="showDiffusionDialog = true"  class="diffusion-btn"/>
    </div>
    <div class="guideline-card-footer" v-if="editable">
      <q-toggle v-model="active" left-label dense label="Active" color="secondary"
        @update:model-value="handleToggleActive" />
      <q-separator vertical inset />
      <Button bg-color="transparent" left-icon="fa-solid fa-pen" @click="showEditGuideline = true"
        txt-color="var(--sad-nightblue)" />
      <q-separator vertical inset />
      <Button bg-color="transparent" left-icon="mdi-delete-empty" @click="handleDelete" txt-color="var(--sad-red)" />
    </div>

    <q-dialog v-model="showEditGuideline">
      <div class="edit-guideline-form">
        <div class="edit-guideline-form-header">
          <div class="text-h4 text-bold text-center q-pa-lg">Modifier une consigne</div>
        </div>
        <div class="form-body">
          <div v-if="errorMessage" class="text-warning text-bold text-center">{{ errorMessage }}</div>
          <div class="dates flex" :style="{ 'gap': '1em' }">
            <div class="input-wrapper" :style="{ 'flex': '1 1 40%' }">
              <span class="text-h7 text-bold q-mb-sm">Début :</span>
              <q-input input-class="text-black" dense v-model="guidelineStartDate" bg-color="white" type="text" standout
              :style="{ 'flex': '1 0 40%' }" mask="##/##/####" fill-mask>
                <template v-slot:append>
                  <q-icon name="event" class="cursor-pointer" color="primary">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date v-model="guidelineStartDate" mask="DD/MM/YYYY" />
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
              <q-input standout bg-color="white" dense input-class="text-black" :disable="!guidelineStartDate" v-model="guidelineStartTime" mask="time" :rules="['time']" no-error-icon>
                <template v-slot:append>
                  <q-icon name="access_time" class="cursor-pointer" color="primary">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-time v-model="guidelineStartTime">
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
              <q-input input-class="text-black" dense v-model="guidelineEndDate" bg-color="white" type="text" standout
                :style="{ 'flex': '1 0 40%' }" mask="##/##/####" fill-mask>
                <template v-slot:append>
                  <q-icon name="event" class="cursor-pointer" color="primary">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date v-model="guidelineEndDate" mask="DD/MM/YYYY" />
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
              <q-input standout bg-color="white" dense input-class="text-black" :disable="!guidelineEndDate" v-model="guidelineEndTime" mask="time" :rules="['time']" no-error-icon>
                <template v-slot:append>
                  <q-icon name="access_time" class="cursor-pointer" color="primary">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-time v-model="guidelineEndTime">
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
            <q-input input-class="text-black" dense v-model="guidelineTheme" label="Theme" label-color="primary"
              bg-color="white" type="text" standout></q-input>
          </div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Message : </span>
            <q-input input-class="text-black" dense label="Consigne" label-color="primary" bg-color="white" type="text"
              standout v-model="guidelineMessage" autogrow />
          </div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Active : </span>
            <q-toggle v-model="active" color="secondary" />
          </div>
          <Button :loading="loading" btn-text="Modifier" btn-type="submit" left-icon="fa-solid fa-pen" btn-size="md-btn"
            bg-color="var(--sad-orange)" txt-color="white" style="margin-top: auto;" @click="updateGuideline" />
        </div>
      </div>
    </q-dialog>

    <q-dialog v-model="showDiffusionDialog">
      <div class="diffusion-dialog">
        <q-inner-loading :showing="diffusing" style="z-index: 10000;">
          <q-spinner-tail size="50px" color="primary" />
        </q-inner-loading>
        <div class="diffusion-dialog-header">
          <div class="text-h4 text-bold text-center q-pa-lg">Diffuser la consigne</div>
        </div>
        <div class="diffusion-dialog-body">

            <div class="text-h7 text-bold q-mb-sm">Listes de diffusion : </div>
            <Dropdown :list="processedDiffusionLists" btn-size="md-btn" @update:selected="onDiffusionListSelected" btn-bg-color="white" immediate/>
            <div class="recipients-list" style="max-height: 300px; overflow-y: auto;" v-if="diffusionList">
              <div class="text-h7 text-bold q-mb-sm q-mt-md">Destinataires : </div>
              <q-list bordered separator v-if="processedDiffusionLists.find(list => list.value === diffusionList).recipients.length > 0">
                <q-item v-for="(recipient, index) in processedDiffusionLists.find(list => list.value === diffusionList).recipients" :key="index">
                  <q-item-section>
                    <q-item-label>{{ recipient }}</q-item-label>
                  </q-item-section>

                </q-item>
              </q-list>

              <div v-else class="text-center q-pa-lg text-grey">
                Aucun destinataire ajouté pour le moment
              </div>
            </div>

        </div>
        <div class="diffusion-dialog-footer">
          <Button btn-text="Diffuser" btn-type="submit" left-icon="fa-solid fa-bullhorn" btn-size="md-btn"
            bg-color="var(--sad-orange)" txt-color="white" style="margin-top: auto;" @click="diffuseGuideline" />
        </div>
      </div>
    </q-dialog>
  </div>
</template>

<script setup>
import { computed, watch, ref } from 'vue';
import Dropdown from "src/components/Dropdown.vue";
import Button from './Button.vue';
import { showDialog } from 'src/utils/dialogUtil';
import { notifyUser } from "src/utils/notifyUser";
import { api } from 'src/boot/axios';
import { Base64 } from 'js-base64';
import { Cookies, date } from 'quasar'


const props = defineProps({
  guideline: Object,
  isSelected: Boolean,
  editable: Boolean,
  truncate: Boolean,
  diffusionLists: Array
})

let decodedUser = (Cookies.get('user') || '{}');
try {
  decodedUser = JSON.parse(Base64.decode(decodedUser));
} catch (e) {
  decodedUser = {};
}

const isAllowed = computed(() => {
  return decodedUser.role === 'admin' || decodedUser.role === 'maintainer';
});

const emit = defineEmits(['toggleActive', 'deleteGuideline', 'selectGuideline', 'updateGuideline']);

const loading = ref(false)
const diffusing = ref(false)

const showFullText = ref(false);

const truncatedMessage = computed(() => {
  if (props.guideline.message.length > 275) {
    return showFullText.value ? props.guideline.message : props.guideline.message.slice(0, 275) + '...';
  }
  return props.guideline.message;
});

const toggleText = () => {
  showFullText.value = !showFullText.value;
};

const active = ref(props.guideline.active)
const selected = ref(props.isSelected)

const errorMessage = ref()

const guidelineId = ref(props.guideline._id)
const guidelineAuthor = ref(props.guideline.author)
const guidelineStartDate = ref(props.guideline.start_date)
const guidelineStartTime = ref(props.guideline.start_time)
const guidelineEndDate = ref(props.guideline.end_date)
const guidelineEndTime = ref(props.guideline.end_time)
const guidelineTheme = ref(props.guideline.theme)
const guidelineMessage = ref(props.guideline.message)
const showEditGuideline = ref(false)

const showDiffusionDialog = ref(false)
const diffusionList = ref()

const onDiffusionListSelected = (list) => {
  diffusionList.value = list;
}

const processedDiffusionLists = computed(() => {
  return props.diffusionLists.map((list) => {
    return {
      label: list.name,
      value: list._id,
      recipients: list.recipients
    };
  });
});

const diffuseGuideline = async () => {
  const data = {
    guideline_id: guidelineId.value,
    diffusion_list_id: diffusionList.value,
    dpt: decodedUser.dpt
  };
  try {
    diffusing.value = true;
    const response = await api.post('/admin-cta/diffuse-guideline', data);
    notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 });
    showDiffusionDialog.value = false;
  } catch (error) {
    errorMessage.value = error.response.data.message;
    notifyUser({ icon: "error", message: error.response.data.message, color: "red", position: "bottom", timeout: 2500 });
  }
  finally {
    diffusing.value = false;
  }
}

watch(() => props.isSelected, (newVal) => {
  selected.value = newVal;
});

const handleToggleActive = () => {
  emit('toggleActive', props.guideline._id, active.value);
}

const handleDelete = () => {
  showDialog({
    focus: "none",
    style: { width: "50%", },
    dark: true,
    message: "Êtes-vous sûr de vouloir supprimer cette consigne ?",
    ok: {
      label: 'OK',
      color: 'secondary',
    },
    cancel: {
      label: 'Annuler',
      color: 'warning',
    },

  },
    () => {
      emit('deleteGuideline', props.guideline._id);
    });

}

const handleSelect = () => {
  emit('selectGuideline', props.guideline._id);
}

const updateGuideline = async () => {
  loading.value = true
  const data = {
    _id: guidelineId.value,
    author: guidelineAuthor.value,
    last_updated_by: decodedUser.email ? decodedUser.email : 'Indéterminé',
    theme: guidelineTheme.value,
    message: guidelineMessage.value,
    start_date: guidelineStartDate.value && guidelineStartDate.value !== '__/__/____' ? guidelineStartDate.value : 'Indéterminée',
    end_date: guidelineEndDate.value && guidelineEndDate.value !== '__/__/____' ? guidelineEndDate.value : 'Indéterminée',
    start_time: guidelineStartTime.value ? guidelineStartTime.value : null,
    end_time: guidelineEndTime.value ? guidelineEndTime.value : null,
    active: active.value
  }
  try {
    const response = await api.patch(`/admin-cta/update-guideline`, data);
    showEditGuideline.value = false
    loading.value = false
    emit('updateGuideline', response.data.guideline)
    notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
  }
  catch (error) {
    errorMessage.value = error.response.data.message
    loading.value = false
  }
}


</script>

<style scoped>
.guideline-card {
  flex: 1 1 100%;
  height: auto;
  flex-wrap: wrap;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  color: var(--sad-nightblue);
  position: relative;
}

.guideline-card-disabled {
  background-color: var(--sad-grey);
  filter: grayscale(100%) opacity(0.7);
}


.guideline-card-header {
  position: relative;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1em;
}

.guideline-card-theme {
  color: var(--sad-red);
}

.guideline-metadata {
  font-style: normal;
  font-weight: 400;
}

.guideline-card-body {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  flex-wrap: wrap;
  flex: 1;
  gap: 1em;
}

.guideline-card-message {
  margin-bottom: 16px;
  padding: 10px 16px;
  text-align: center;
  font-size: clamp(1rem, 3vw, 1.5rem);
  font-weight: 500;
}

.toggle-text {
  cursor: pointer;
  color: var(--sad-orange);
  font-size: 1rem;
  font-weight: bold;
}

.guideline-card-footer {
  padding: 1em;
  display: flex;
  justify-content: center;
  margin-left: auto;
  gap: 1em;
  align-items: center;
  position: absolute;
  bottom: -25px;
  right: 50px;
  background: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  z-index: 10000;
  opacity: 0;
  transition: all 0.3s ease;
}

.guideline-card:hover .guideline-card-footer {
  opacity: 1;
  transition: all 0.3s ease;
}

.calendar-icon {
  cursor: pointer;
  width: 2em;
  height: 2em;
  background: white;
  border-radius: 50%;
}

.edit-guideline-form {
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

.diffusion-btn {
  position: absolute;
  background-color: white;
  color: var(--sad-nightblue);
  bottom: 10px;
  right: 10px;
  border: 1px solid var(--sad-nightblue);
  padding: 7px;
  transition: background-color 0.4s ease;
}

.diffusion-btn:hover {
  background-color: var(--sad-nightblue);
  color: white;
}

.diffusion-dialog {
  background: var(--sad-nightblue);
  display: flex;
  flex-direction: column;
  gap: 2em;
  padding: 1em;
  color: white;
  min-height: 350px;
}

.diffusion-dialog-header {
  display: flex;
  justify-content: center;
  align-items: center;
}

.diffusion-dialog-body {
  /* display: flex; */
  flex-direction: column;
  gap: 1em;
}

.diffusion-dialog-footer {
  margin-top: auto;
}

</style>
