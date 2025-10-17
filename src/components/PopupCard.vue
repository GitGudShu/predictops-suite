<template>
  <div class="popup-card">
    <div class="checkbox-container flex">
      <q-checkbox v-model="selected" @update:model-value="handleSelect" />
    </div>
    <div class="popup-card-header">
      <div class="popup-card-date text-italic text-weight-medium">{{ popup.date }}</div>
    </div>
    <div class="popup-card-body">
      <div class="popup-card-message" v-html="popup.message"></div>
    </div>
    <div class="popup-card-footer">
      <q-toggle v-model="visible" left-label label="Visible" color="secondary"
      @update:model-value="handleToggleVisible" />
      <Button btn-size="xs-btn" bg-color="var(--sad-nightblue)" left-icon="fa-solid fa-pen" @click="showEditPopup = true" txt-color="white"/>
      <Button btn-size="xs-btn" bg-color="var(--sad-red)" left-icon="mdi-delete-empty" @click="handleDelete" txt-color="white"/>
    </div>

    <q-dialog v-model="showEditPopup">
      <div class="edit-popup-form">
        <div class="edit-popup-form-header">
          <div class="text-h4 text-bold text-center q-mb-lg">Modifier une alerte</div>
        </div>
        <div class="form-body">
          <div v-if="errorMessage" class="text-warning text-bold text-center">{{ errorMessage }}</div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Type : </span>
            <Dropdown btn-bg-color="white" :selected-value="popupType" btn-size="sm-btn" :list="typesList" @update:selected="onTypeSelected" :style="{'width': 'max-content'}">
            </Dropdown>
          </div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Message : </span>
            <q-editor v-model="popupMessage" min-height="5rem" toolbar-color="primary"
              :content-style="{ 'color': 'var(--sad-nightblue)' }" :toolbar="toolbar"/>
          </div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Départements : </span>
            <q-option-group v-model="popupDpts" :options="departmentsOptions" color="secondary" type="checkbox" inline
              dark />
          </div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Visible : </span>
            <q-toggle v-model="visible" color="secondary" />
          </div>
          <Button :loading="loading" btn-text="Modifier" btn-type="submit" left-icon="fa-solid fa-pen"
            btn-size="md-btn" bg-color="var(--sad-orange)" txt-color="white" style="margin-top: auto;"
            @click="updatePopup" />
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
import { api } from 'src/boot/axios';


const props = defineProps({
  popup: Object,
  isSelected: Boolean,
  typesList: Array,
  departmentsOptions: Array,
  toolbar: Array
})

const emit = defineEmits(['toggleVisible', 'deletePopup', 'selectPopup', 'updatePopup']);

const loading = ref()

const visible = ref(props.popup.visible)
const selected = ref(props.isSelected)

const errorMessage = ref()

const popupId = ref(props.popup._id)
const popupType =ref(props.popup.type)
const popupDpts = ref(props.popup.dpts)
const popupMessage = ref(props.popup.message)


const onTypeSelected = (selected) => {
  popupType.value = selected
}

const showEditPopup = ref(false)

watch(() => props.isSelected, (newVal) => {
  selected.value = newVal;
});

const handleToggleVisible = () => {
  emit('toggleVisible', props.popup._id, visible.value);
}

const handleDelete = () => {
  showDialog({
    focus: "none",
    style: { width: "50%", },
    dark: true,
    message: "Êtes-vous sûr de vouloir supprimer cette alerte ?",
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
      emit('deletePopup', props.popup._id);
    });

}

const handleSelect = () => {
  emit('selectPopup', props.popup._id);
}

const updatePopup = async () => {
  loading.value = true
  const data = {
    _id: popupId.value,
    type: popupType.value,
    message: popupMessage.value,
    dpts: popupDpts.value,
    visible: visible.value
  }
  try {
    const response = await api.patch(`/admin/update-popup`, data);
    showEditPopup.value = false
    loading.value = false
    emit('updatePopup', response.data.popup)
  }
  catch (error) {
    errorMessage.value = error.response.data.message
    loading.value = false
  }
}


</script>

<style scoped>
.popup-card {
  flex: 1 1 auto;
  min-width: 300px;
  height: auto;
  flex-wrap: wrap;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  display: flex;
  color: var(--sad-nightblue);
}

.popup-card-header {
  position: relative;
  padding: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1em;
}

.popup-card-body {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  flex-wrap: wrap;

  gap: 1em;
  margin: auto;
}

.popup-card-message {
  background: #eee;
  border-radius: 5px;
  margin: 16px 0;
  padding: 10px;
  flex: 1;
  width: 100%;
}

.popup-card-footer {
  padding: 1em;
  display: flex;
  justify-content: center;
  margin-left: auto;
  gap: 1em;
  align-items: center;
}

.edit-popup-form {
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
</style>
