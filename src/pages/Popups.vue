<template>
  <q-page>
    <div class="actions-bar">
      <BackButton />
      <div class="right-buttons">
        <Button left-icon="mdi-bell-plus-outline" btn-text="Nouvelle alerte" bg-color="var(--sad-nightblue)"
          btn-size="sm-btn" @click="openAddPopup" txt-color="white"/>
        <q-checkbox v-model="selectAll" @update:model-value="handleSelectAll" label="Tout séléctionner" dense
          class="text-black text-bold" />
        <Button v-if="selectedPopups.length" left-icon="fa-solid fa-trash" btn-text="Supprimer" btn-size="sm-btn"
          @click="deleteSelectedPopups" class="delete-selected" bg-color="var(--sad-red)" txt-color="white" />
      </div>
    </div>
    <div class="container">
      <PopupCard v-for="popup in popupsList" :key="popup._id" :popup="popup" @toggleVisible="toggleVisible" @updatePopup="updatePopup"
        :types-list="typesList" :toolbar="toolbar" :departments-options="departmentsOptions" @selectPopup="selectPopup"
        @deletePopup="deletePopup" :is-selected="selectedPopups.includes(popup._id)" />
      <div class="q-mt-xl empty-popups" v-if="popupsList.length === 0">
        <div class="text-bold text-h5 text-center text-black q-mb-lg">Aucune alerte</div>
        <div class="text-h6 text-center text-black q-mb-lg">Ajouter une alerte pour commencer</div>
        <Button left-icon="mdi-bell-plus-outline" btn-text="Nouvelle alerte" bg-color="var(--sad-nightblue)"
          btn-size="sm-btn" @click="openAddPopup" txt-color="white"/>
      </div>
    </div>
    <q-dialog v-model="showAddPopup">
      <div class="add-popup-form">
        <div class="add-popup-form-header">
          <div class="text-h4 text-bold text-center q-mb-lg">Ajouter une alerte</div>
        </div>
        <div class="form-body">
          <div v-if="errorMessage" class="text-warning text-bold text-center">{{ errorMessage }}</div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Type : </span>
            <Dropdown btn-bg-color="white" btn-size="sm-btn" :list="typesList" @update:selected="onTypeSelected"
              :style="{ 'width': 'max-content' }">
            </Dropdown>
          </div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Message : </span>
            <q-editor v-model="popupMessage" min-height="5rem" toolbar-color="primary"
              :content-style="{ 'color': 'var(--sad-nightblue)' }" :toolbar="toolbar" />
          </div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Départements : </span>
            <q-option-group v-model="popupDpts" :options="departmentsOptions" color="secondary" type="checkbox" inline
              dark />
          </div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Visible : </span>
            <q-toggle v-model="popupVisible" color="secondary" />
          </div>
          <Button :loading="loading" btn-text="Ajouter" btn-type="submit" left-icon="fa-solid fa-plus"
            btn-size="md-btn" bg-color="var(--sad-orange)" style="margin-top: auto;"
            @click="addPopup" txt-color="white" />
        </div>
      </div>
    </q-dialog>

  </q-page>
</template>

<script setup>
import Button from "src/components/Button.vue";
import BackButton from "src/components/BackButton.vue";
import Dropdown from "src/components/Dropdown.vue";
import PopupCard from "src/components/PopupCard.vue";
import { ref, onMounted, computed } from "vue";
import { api } from "src/boot/axios";
import { notifyUser } from 'src/utils/notifyUser';
import { showDialog } from "src/utils/dialogUtil";
import { useRouter } from 'vue-router'
import { Base64 } from 'js-base64'
import { Cookies } from 'quasar'
import { useQuasar } from 'quasar'

const $q = useQuasar()

const toolbar = [
  ['left', 'center', 'right', 'justify'],
  ['bold', 'italic', 'underline', 'strike', 'subscript', 'superscript', 'removeFormat'],
  ['unordered', 'ordered'],
  [{
    label: $q.lang.editor.fontSize,
    icon: $q.iconSet.editor.fontSize,
    fixedLabel: true,
    fixedIcon: true,
    list: 'no-icons',
    options: [
      'size-1',
      'size-2',
      'size-3',
      'size-4',
      'size-5',
      'size-6',
      'size-7'
    ]
  }],
];

const decodedUser = JSON.parse(Base64.decode(Cookies.get('user')))

const typesList = ["warning", "info"]
const departmentsOptions = [
  {
    label: '01',
    value: '01'
  },
  {
    label: '25',
    value: '25'
  },
  {
    label: '31',
    value: '31'
  },
  {
    label: '78',
    value: '78'
  },
]


const popupTitle = ref('')
const popupType = ref()
const popupDpts = ref(["25"])
const popupMessage = ref('')
const popupVisible = ref(true)

const errorMessage = ref('')

const loading = ref()
const selectAll = ref(false)

const showAddPopup = ref(false)

const popupsList = ref([])
const selectedPopups = ref([])

const onTypeSelected = (selected) => {
  popupType.value = selected
}

const handleSelectAll = (value) => {
  if (value) {
    selectedPopups.value = popupsList.value
      .map(popup => popup._id);
  } else {
    selectedPopups.value = [];
  }
}

const selectPopup = (_id) => {
  if (selectedPopups.value.includes(_id)) {
    selectedPopups.value = selectedPopups.value.filter(e => e !== _id);
  } else {
    selectedPopups.value.push(_id);
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const response = await api.get(`/admin/popups`);
    popupsList.value = response.data
    loading.value = false
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des utilisateurs.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false
  }
})

const openAddPopup = () => {
  showAddPopup.value = true
}

const addPopup = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await api.post(`/admin/create-popup`, {
      title: popupTitle.value,
      type: popupType.value,
      visible: popupVisible.value,
      message: popupMessage.value,
      dpts: popupDpts.value
    });
    popupsList.value = [...popupsList.value, response.data.popup]
    showAddPopup.value = false
    loading.value = false
    notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
  } catch (error) {
    errorMessage.value = error.response.data.message
    loading.value = false
  }
}

const updatePopup = (updatedPopup) => {
  const index = popupsList.value.findIndex(popup => popup._id === updatedPopup._id)
  if (index !== -1) {
    popupsList.value.splice(index, 1, updatedPopup)
  }
}

const toggleVisible = async (_id, visible) => {
  try {
    const response = await api.patch(`/admin/toggle-popup-visible`, { _id, visible });
    const popup = popupsList.value.find(u => u._id === _id);
    if (popup) {
      popup.visible = visible;
    }
    notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la modification de l'alerte.", color: "red", position: "bottom", timeout: 2500 });
  }
}


const deletePopup = async (_id) => {
  try {
    const response = await api.delete(`/admin/delete-popup`, { data: { _id } });
    popupsList.value = popupsList.value.filter(popup => popup._id !== _id);
    notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la suppression de l'alerte.", color: "red", position: "bottom", timeout: 2500 });
  }
}

const deleteSelectedPopups = () => {
  showDialog({
    focus: "none",
    style: { width: "50%", },
    dark: true,
    message: "Êtes-vous sûr de vouloir supprimer ce(s) alerte(s) ?",
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
        const response = await api.delete(`/admin/delete-popups`, { data: { _ids: selectedPopups.value } });
        popupsList.value = popupsList.value.filter(popup => !selectedPopups.value.includes(popup._id));
        selectedPopups.value = [];
        notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
      } catch (error) {
        notifyUser({ icon: "error", message: "Erreur lors de la suppression des alertes.", color: "red", position: "bottom", timeout: 2500 });
      }
    });

}



</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  width: 90%;
  margin: 0 auto;
  gap: 1em;
}

.actions-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
  width: 100%;
}

.add-popup-form {
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



.empty-popups {
  width: 50%;
  height: 100%;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  padding: 20px;
}
</style>
