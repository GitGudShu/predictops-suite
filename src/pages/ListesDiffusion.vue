<template>
  <q-page>
    <div class="actions-bar">
      <BackButton />
    </div>
    <div class="container">
      <q-inner-loading :showing="loading" style="z-index: 0;">
        <q-spinner-tail size="50px" color="primary" />
      </q-inner-loading>
      <div class="header">
        <q-icon name="fa-solid fa-share-nodes" size="2em" />
        <h4>Listes de diffusion</h4>
        <q-icon name="fa-solid fa-plus" class="q-ml-auto cursor-pointer" @click="openAddList" size="sm" />
      </div>
      <div class="cards-container" v-if="!loading">
        <div class="diffusion-list-card" v-for="(list, index) in diffusionLists"
          :class="{ 'hidden': editing && editingList._id !== list._id && index > 2 }">
          <div class="dlc-header">
            <q-icon :name="iconsMap[list.type]" :size="list.type === 'hybrid' ? '2.5em' : '1.5em'" />
            <p>{{ list.name }}</p>
            <q-badge rounded floating :label="list.recipients.length + '/' + list.limit"
              :style="{ background: '#778beb', padding: '5px 7px', fontWeight: 'bold' }"></q-badge>
          </div>
          <div class="footer">
            <Button left-icon="fa-solid fa-pen" class="btn edit-btn" @click="toggleEditList(list)"
              :class="{ 'active': editing && editingList._id === list._id }" />
            <Button left-icon="fa-solid fa-clone" class="btn duplicate-btn" @click="duplicateList(list)" />
            <Button left-icon="fa-solid fa-trash" class="btn delete-btn" @click="deleteList(list)" />
          </div>
        </div>
      </div>

      <q-form v-if="editing && editingList" class="edit-list-form" @submit="confirmEditList(editingList)"
        @reset="cancelEditList(editingList)">
        <h4 class="edit-list-form-header">Modifier la liste</h4>
        <div class="edit-list-form-body">
          <div class="input-wrapper">
            <div class="text-black text-h7 text-bold q-mb-sm">Nom</div>
            <q-input :rules="[val => val && val.length > 0 && val !== '' || 'Champ obligatoire']"
              v-model="editingList.name" outlined color="accent" hide-bottom-space></q-input>
          </div>
          <div class="input-wrapper">
            <div class="text-black text-h7 text-bold q-mb-sm">Type</div>
            <q-select v-model="editingList.type" emit-value map-options bg-color="white" :options="listTypes" outlined
              @update:model-value="filterRecipients(editingList)" option-disable="disabled">
              <template v-slot:option="scope">
                <q-item v-bind="scope.itemProps">
                  <q-item-section>
                    {{ scope.opt.label }}
                  </q-item-section>
                  <q-item-section side v-if="scope.opt.disabled">
                    <q-chip label="Bientôt disponible" no-ripple />
                  </q-item-section>
                </q-item>
              </template>
            </q-select>

          </div>
          <!-- Replace your recipients section in the edit form with this -->
          <div class="input-wrapper recipients">
            <div class="text-black text-h7 text-bold">
              Destinataires ({{ editingList.recipients.length }}{{ editingList.limit ? '/' + editingList.limit : '' }})
            </div>

            <div class="recipients-list" style="max-height: 300px; overflow-y: auto;">
              <q-list bordered separator v-if="editingList.recipients.length > 0">
                <q-item v-for="(recipient, index) in editingList.recipients" :key="index">
                  <q-item-section>
                    <q-item-label>{{ recipient }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div>
                      <q-icon name="fa-solid fa-pen" color="primary" size="12px" class="cursor-pointer"
                        @click="editRecipient(recipient, index)" />
                      <q-icon name="fa-solid fa-trash" color="warning" size="12px" class="cursor-pointer q-ml-sm"
                        @click="removeRecipient(recipient)" />
                    </div>
                  </q-item-section>
                </q-item>
              </q-list>

              <div v-else class="text-center q-pa-lg text-grey">
                Aucun destinataire ajouté pour le moment
              </div>
            </div>

            <!-- Add recipient input -->
            <div class="row items-center" v-if="addingRecipient">
              <div class="col-12">
                <q-input v-model="newRecipient"
                  :label="editingList.type === 'email' ? 'Adresse email' : editingList.type === 'sms' ? 'Numéro de téléphone' : 'Email ou téléphone'"
                  outlined hide-bottom-space :rules="[
                    val => !!val || 'Champ obligatoire',
                    val => validateRecipient(val, editingList.type) || getValidationMessage(editingList.type),
                    val => !val || !editingList.recipients.includes(val) || 'Ce destinataire existe déjà'
                  ]" ref="recipientInput" @keyup.enter="confirmAddRecipient(editingList)">
                  <template v-slot:append>
                    <q-icon name="fa-solid fa-check" @click="confirmAddRecipient(editingList)" size="14px"
                      color="positive" class="cursor-pointer" />
                    &nbsp;
                    <q-icon name="fa-solid fa-times" @click="discardAddRecipient" size="14px" color="warning"
                      class="cursor-pointer" />
                  </template>
                </q-input>
              </div>
            </div>

            <!-- Add recipient button -->
            <Button v-if="!addingRecipient" left-icon="mdi-plus" left-icon-size="md" bg-color="transparent"
              btn-type="button" txt-color="var(--sad-nightblue)" class="add-recipient-btn q-mt-sm"
              :disabled="editingList.limit && editingList.recipients.length >= editingList.limit"
              @click="addRecipient(editingList)" />
          </div>

        </div>
        <div class="edit-list-actions">
          <Button left-icon="mdi-close" bg-color="transparent" btn-type="reset" txt-color="var(--sad-red)"
            btn-text="Annuler" class="btn cancel-btn" />
          <Button left-icon="mdi-check" bg-color="transparent" btn-type="submit" txt-color="var(--sad-nightblue)"
            btn-text="Valider" class="btn submit-btn" />
        </div>
      </q-form>

      <!-- Stepper Dialog -->
      <q-dialog v-model="creatingList" persistent>
        <q-card>
          <q-bar class="bg-primary text-white q-pt-lg q-pb-lg">
            <div class="text-weight-bold">Nouvelle liste de diffusion</div>
            <q-space />
            <q-btn dense flat icon="close" @click="cancelAddList" />
          </q-bar>

          <q-stepper v-model="step" ref="stepper" color="primary" animated class="q-pa-md">
            <!-- Step 1: Basic Information -->
            <q-step :name="1" title="Informations" icon="fa-solid fa-info" :done="step > 1">
              <div class="q-pa-md q-gutter-md" style="max-width: 500px; margin: 0 auto;">
                <div class="text-h6 q-mb-lg">Informations de base</div>

                <q-input v-model="newList.name" label="Nom de la liste *" outlined
                  :rules="[val => !!val || 'Le nom est obligatoire']" ref="nameInput" />

                <q-select v-model="newList.type" :options="listTypes" label="Type de liste *" emit-value map-options
                  outlined option-disable="disabled">
                  <template v-slot:option="scope">
                    <q-item v-bind="scope.itemProps">
                      <q-item-section>
                        {{ scope.opt.label }}
                      </q-item-section>
                      <q-item-section side v-if="scope.opt.disabled">
                        <q-chip label="Bientôt disponible" no-ripple />
                      </q-item-section>
                    </q-item>
                  </template>
                </q-select>

                <div class="text-caption q-mt-sm">* Champs obligatoires</div>
              </div>

              <q-stepper-navigation class="q-mt-lg flex" style="justify-content: space-between;">
                <Button left-icon="fa-solid fa-times" @click="cancelAddList" btn-text="Annuler"
                  txt-color="var(--sad-red)" class="btn cancel-btn" />
                <Button right-icon="trending_flat" @click="validateStep1" btn-text="Continuer"
                  class="btn submit-btn" />
              </q-stepper-navigation>
            </q-step>

            <!-- Step 2: Add Recipients -->
            <q-step :name="2" title="Destinataires" icon="fa-solid fa-users" :done="step > 2">
              <div class="q-pa-md" style="max-width: 700px; margin: 0 auto;">
                <div class="text-h6 q-mb-lg">Ajouter des destinataires</div>

                <div class="q-mb-md">
                  <div class="row items-center justify-between q-mb-sm">
                    <div class="text-subtitle1 text-weight-medium">
                      Destinataires ({{ newList.recipients.length }})
                    </div>
                    <div class="text-caption text-grey-8">
                      Vous pouvez ajouter jusqu'à {{ recipientLimit }} destinataires
                    </div>
                  </div>

                  <!-- List of recipients -->
                  <div class="recipients-list q-mb-lg" style="max-height: 300px; overflow-y: auto;">
                    <q-list bordered separator v-if="newList.recipients.length > 0">
                      <q-item v-for="(recipient, index) in newList.recipients" :key="index">
                        <q-item-section>
                          <q-item-label>{{ recipient }}</q-item-label>
                        </q-item-section>
                        <q-item-section side>
                          <div>
                            <q-icon name="fa-solid fa-pen" color="primary" size="12px" class="cursor-pointer"
                              @click="editNewRecipient(recipient, index)" />
                            <q-icon name="fa-solid fa-trash" color="warning" size="12px" class="cursor-pointer q-ml-sm"
                              @click="removeNewRecipient(recipient)" />
                          </div>
                        </q-item-section>
                      </q-item>
                    </q-list>

                    <div v-else class="text-center q-pa-lg text-grey">
                      Aucun destinataire ajouté pour le moment
                    </div>
                  </div>

                  <!-- Add recipient form -->
                  <div class="add-recipient-form">
                    <div class="row items-center q-col-gutter-md">
                      <div class="col-12">
                        <q-input v-model="newRecipient"
                          :label="newList.type === 'email' ? 'Adresse email' : newList.type === 'sms' ? 'Numéro de téléphone' : 'Email ou téléphone'"
                          outlined hide-bottom-space :rules="[
                            val => !val || validateRecipient(val, newList.type) || getValidationMessage(newList.type),
                            val => !val || !newList.recipients.includes(val) || 'Ce destinataire existe déjà'
                          ]" ref="newRecipientInput" @keyup.enter="addRecipientToList"
                          :disable="newList.recipients.length >= recipientLimit">
                          <template v-slot:append>
                            <q-icon name="fa-solid fa-plus" color="primary" size="16px" @click="addRecipientToList"
                              class="cursor-pointer" />
                          </template>
                        </q-input>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <q-stepper-navigation class="q-mt-lg flex" style="justify-content: space-between;">
                <Button left-icon="fa-solid fa-times" @click="cancelAddList" btn-text="Annuler"
                  txt-color="var(--sad-red)" class="btn cancel-btn" />
                <div class="flex" style="gap: 1em;">
                  <Button left-icon="trending_flat"  @click="step = 1" btn-text="Retour"
                    txt-color="var(--sad-nightblue)" class="btn submit-btn" left-icon-class="rotate-180" />
                  <Button right-icon="trending_flat" @click="step = 3" btn-text="Continuer"
                    txt-color="var(--sad-nightblue)" class="btn submit-btn" />
                </div>
              </q-stepper-navigation>
            </q-step>

            <!-- Step 3: Review and Confirm -->
            <q-step :name="3" title="Confirmation" icon="fa-solid fa-check">
              <div class="q-pa-md" style="max-width: 700px; margin: 0 auto;">
                <div class="text-h6 q-mb-lg">Vérifiez les informations</div>

                <q-card flat bordered class="q-mb-md">
                  <q-card-section>
                    <div class="text-h6">{{ newList.name }}</div>
                    <div class="text-subtitle2 text-primary">
                      {{ getTypeLabel(newList.type) }}
                    </div>
                  </q-card-section>

                  <q-separator />

                  <q-card-section>
                    <div class="text-subtitle2 q-mb-sm">
                      Destinataires ({{ newList.recipients.length }})
                    </div>

                    <q-list dense>
                      <q-item v-for="(recipient, index) in newList.recipients" :key="index">
                        <q-item-section>
                          <q-item-label>{{ recipient }}</q-item-label>
                        </q-item-section>
                      </q-item>

                      <q-item v-if="newList.recipients.length === 0">
                        <q-item-section>
                          <q-item-label class="text-grey">Aucun destinataire</q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-card-section>
                </q-card>

                <div class="text-caption q-mb-xl">
                  Vous pourrez ajouter ou modifier des destinataires après la création de la liste.
                </div>
              </div>

              <q-stepper-navigation class="q-mt-lg flex" style="justify-content: space-between;">
                <Button left-icon="fa-solid fa-times" @click="cancelAddList" btn-text="Annuler"
                  txt-color="var(--sad-red)" class="btn cancel-btn" />
                <div class="flex" style="gap: 1em;">
                  <Button left-icon="trending_flat" left-icon-class="rotate-180" @click="step = 2" btn-text="Retour"
                    txt-color="var(--sad-nightblue)" class="btn submit-btn" />
                  <Button right-icon="fa-solid fa-check" @click="createList" btn-text="Créer la liste"
                    txt-color="var(--sad-nightblue)" class="btn submit-btn" />
                </div>
              </q-stepper-navigation>
            </q-step>
          </q-stepper>
        </q-card>
      </q-dialog>
    </div>
  </q-page>
</template>

<script setup>
import Button from "src/components/Button.vue";
import BackButton from "src/components/BackButton.vue";
import { ref, onMounted, computed, watch, nextTick } from "vue";
import { api } from "src/boot/axios";
import { notifyUser } from 'src/utils/notifyUser';
import { showDialog } from "src/utils/dialogUtil";
import { Base64 } from 'js-base64'
import { Cookies } from 'quasar'

const decodedUser = JSON.parse(Base64.decode(Cookies.get('user')))

const publicPath = process.env.PUBLIC_PATH || '/predictops/'

const loading = ref(true)

const diffusionLists = ref([])

const originalList = ref(null);

const creatingList = ref(false)
const newList = ref({
  name: "",
  type: "email",
  recipients: []
})

const editing = ref(false)
const editingList = ref({})

const addingRecipient = ref(false)
const newRecipient = ref("")

const editingRecipientIndex = ref(null);
const recipientInput = ref(null);

const listTypes = [
  { label: "Email", value: "email" },
  { label: "SMS", value: "sms", disabled: true },
  { label: "Hybride", value: "hybrid", disabled: true }
]

const iconsMap = {
  "email": "fa-solid fa-at",
  "sms": "fa-solid fa-comment-sms",
  "hybrid": `img:${publicPath}hybrid-black.svg`
}

const step = ref(1);
const stepper = ref(null);
const nameInput = ref(null);
const newRecipientInput = ref(null);
const creating = ref(false);
const editingNewRecipientIndex = ref(null);

// Constants for validation
const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const phoneRegex = /^\+[0-9]{10,15}$/;

// Computed property for recipient limit
const recipientLimit = computed(() => {
  switch (newList.value.type) {
    case 'email': return 15;
    case 'sms': return 15;
    case 'hybrid': return 30;
    default: return 15;
  }
});

const openAddList = () => {
  creatingList.value = true;
  editing.value = false;
  editingList.value = {};
};
// Methods for the stepper
const validateStep1 = () => {
  if (!newList.value.name) {
    notifyUser({
      icon: "error",
      message: "Le nom de la liste est obligatoire",
      color: "red",
      position: "bottom"
    });
    return;
  }

  step.value = 2;

  // Focus on recipient input in next tick
  nextTick(() => {
    if (newRecipientInput.value) {
      newRecipientInput.value.focus();
    }
  });
};

const cancelAddList = () => {
  creatingList.value = false;
  step.value = 1;
  newList.value = {
    name: "",
    type: "email",
    recipients: []
  };
  newRecipient.value = "";
  editingNewRecipientIndex.value = null;
};

const validateRecipient = (value, type) => {
  if (!value) return false;

  if (type === 'email') {
    return emailRegex.test(value);
  } else if (type === 'sms') {
    return phoneRegex.test(value);
  } else if (type === 'hybrid') {
    return emailRegex.test(value) || phoneRegex.test(value);
  }

  return true;
};

const getValidationMessage = (type) => {
  if (type === 'email') {
    return 'Veuillez entrer une adresse email valide';
  } else if (type === 'sms') {
    return 'Veuillez entrer un numéro de téléphone au format international (+33...)';
  } else if (type === 'hybrid') {
    return 'Veuillez entrer une adresse email ou un numéro de téléphone valide';
  }
};

const getTypeLabel = (type) => {
  return listTypes.find(item => item.value === type)?.label || type;
};

const addRecipientToList = () => {
  if (!newRecipient.value ||
    !validateRecipient(newRecipient.value, newList.value.type) ||
    newList.value.recipients.includes(newRecipient.value) ||
    newList.value.recipients.length >= recipientLimit.value) {
    return;
  }

  if (editingNewRecipientIndex.value !== null) {
    // Edit existing recipient
    newList.value.recipients[editingNewRecipientIndex.value] = newRecipient.value;
    editingNewRecipientIndex.value = null;
  } else {
    // Add new recipient
    newList.value.recipients.push(newRecipient.value);
  }

  newRecipient.value = "";
  newRecipientInput.value.focus();
};

const editRecipient = (recipient, index) => {
  newRecipient.value = recipient;
  editingRecipientIndex.value = index;
  addingRecipient.value = true;

  // Focus on the input field
  nextTick(() => {
    if (recipientInput.value) {
      recipientInput.value.focus();
    }
  });
};

const removeRecipient = (recipient) => {

  editingList.value.recipients = editingList.value.recipients.filter(r => r !== recipient);


  if (newRecipient.value === recipient) {
    newRecipient.value = "";
    editingRecipientIndex.value = null;
  }

};



const editNewRecipient = (recipient, index) => {
  newRecipient.value = recipient;
  editingNewRecipientIndex.value = index;

  nextTick(() => {
    newRecipientInput.value.focus();
  });
};

const removeNewRecipient = (recipient) => {
  newList.value.recipients = newList.value.recipients.filter(r => r !== recipient);

  if (newRecipient.value === recipient) {
    newRecipient.value = "";
    editingNewRecipientIndex.value = null;
  }
};

const createList = async () => {
  creating.value = true;

  try {
    let listData = {
      name: newList.value.name,
      type: newList.value.type,
      dpt: decodedUser.dpt,
      recipients: [...newList.value.recipients],
    };


    const response = await api.post('/admin/create-diffusion-list', listData);
    diffusionLists.value.push(response.data.list);

    notifyUser({
      icon: "check_circle",
      message: "Liste de diffusion créée avec succès",
      color: "green",
      position: "bottom"
    });

    cancelAddList();
  } catch (error) {
    console.error("Create list error:", error);
    notifyUser({
      icon: "error",
      message: error.response.data.message,
      color: "warning",
      position: "bottom"
    });
  } finally {
    creating.value = false;
  }
};

watch(creatingList, (newVal) => {
  if (newVal) {
    step.value = 1;
    nextTick(() => {
      if (nameInput.value) {
        nameInput.value.focus();
      }
    });
  }
});

const toggleEditList = (list) => {
  addingRecipient.value = false;

  if (editing.value) {
    if (editingList.value && editingList.value._id === list._id) {
      // Cancel editing this list
      editing.value = false;
      editingList.value = null;
      originalList.value = null;
    } else {
      // Switch to editing a different list
      originalList.value = JSON.parse(JSON.stringify(list));
      editingList.value = JSON.parse(JSON.stringify(list));
    }
  } else {
    // Start editing this list
    editing.value = true;
    originalList.value = JSON.parse(JSON.stringify(list));
    editingList.value = JSON.parse(JSON.stringify(list));
  }
};

const confirmEditList = async (list) => {
  editing.value = false

  try {
    await api.put(`/admin/update-diffusion-list/${list._id}`, list)
    diffusionLists.value = diffusionLists.value.map(l => l._id === list._id ? list : l)
    notifyUser({ icon: "check_circle", message: "Liste de diffusion modifiée avec succès.", color: "green", position: "bottom", timeout: 2500 })
  }
  catch (error) {
    console.error("Edit list error:", error)
    notifyUser({ icon: "error", message: "Erreur lors de la modification de la liste de diffusion.", color: "red", position: "bottom", timeout: 2500 })
  }
  finally {
    editingList.value = {}
  }
}

const cancelEditList = (list) => {
  editing.value = false
  editingList.value = list
}

const duplicateList = async (list) => {
  try {
    const response = await api.post(`/admin/duplicate-diffusion-list/${list._id}`)
    diffusionLists.value.push(response.data.list)
    notifyUser({ icon: "check_circle", message: "Liste de diffusion dupliquée avec succès.", color: "green", position: "bottom", timeout: 2500 })

  }
  catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la duplication de la liste de diffusion.", color: "red", position: "bottom", timeout: 2500 })
  }
}

const deleteList = (list) => {
  showDialog({
    title: 'Confirmer la suppression',
    message: `Voulez-vous vraiment supprimer la liste de diffusion "${list.name}" ?`,
    cancel: true,
    dark: true,
    ok: {
      label: 'OK',
      color: 'secondary'
    },
    cancel: {
      label: 'Annuler',
      color: 'negative'
    }
  },
    async () => {
      await api.delete(`/admin/delete-diffusion-list/${list._id}`)
      diffusionLists.value = diffusionLists.value.filter(l => l._id !== list._id)
      notifyUser({ icon: "check_circle", message: "Liste de diffusion supprimée avec succès.", color: "green", position: "bottom", timeout: 2500 })
    })
}

const filterRecipients = (list) => {
  console.log(list)
}

const addRecipient = (list) => {
  if (list.recipients.length >= list.limit) {
    notifyUser({
      icon: "error",
      message: `Limite de ${list.limit} destinataires atteinte`,
      color: "warning",
      position: "bottom",
      timeout: 2500
    });
    return;
  }

  // Reset state for adding new recipient
  newRecipient.value = "";
  editingRecipientIndex.value = null;
  addingRecipient.value = true;

  // Focus on the input field
  nextTick(() => {
    if (recipientInput.value) {
      recipientInput.value.focus();
    }
  });
};

const confirmAddRecipient = (list) => {
  if (!newRecipient.value || !validateRecipient(newRecipient.value, list.type)) {
    notifyUser({
      icon: "error",
      message: getValidationMessage(list.type),
      color: "negative",
      position: "bottom",
      timeout: 2500
    });
    return;
  }

  // Check for duplicates only if not editing an existing recipient
  if (editingRecipientIndex.value === null && list.recipients.includes(newRecipient.value)) {
    notifyUser({
      icon: "error",
      message: "Ce destinataire existe déjà dans la liste",
      color: "warning",
      position: "bottom",
      timeout: 2500
    });
    return;
  }

  // If editing existing recipient
  if (editingRecipientIndex.value !== null) {
    // Check if trying to change to a duplicate
    const otherRecipients = [...list.recipients];
    otherRecipients.splice(editingRecipientIndex.value, 1);

    if (otherRecipients.includes(newRecipient.value)) {
      notifyUser({
        icon: "error",
        message: "Ce destinataire existe déjà dans la liste",
        color: "warning",
        position: "bottom",
        timeout: 2500
      });
      return;
    }

    // Update the recipient
    list.recipients[editingRecipientIndex.value] = newRecipient.value;
    notifyUser({
      icon: "check_circle",
      message: "Destinataire modifié",
      color: "green",
      position: "bottom",
      timeout: 1500
    });
  } else {
    // Add new recipient
    list.recipients.push(newRecipient.value);
    notifyUser({
      icon: "check_circle",
      message: "Destinataire ajouté",
      color: "green",
      position: "bottom",
      timeout: 1500
    });
  }

  // Reset state
  newRecipient.value = "";
  editingRecipientIndex.value = null;
  addingRecipient.value = false;
}

const discardAddRecipient = () => {
  newRecipient.value = "";
  editingRecipientIndex.value = null;
  addingRecipient.value = false;
}

onMounted(async () => {
  loading.value = true
  try {
    const response = await api.get(`/admin/diffusion-lists?dpt=${decodedUser.dpt}`);
    diffusionLists.value = response.data
    loading.value = false
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des listes de diffusion.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false
  }
})


</script>

<style scoped>
.container {
  width: 80%;
  margin: 1em auto;
  display: flex;
  flex-direction: column;
  gap: 2em;
}

.header {
  display: flex;
  align-items: center;
  gap: 1em;
  color: var(--sad-nightblue);
  z-index: 1;
}

.header h4 {
  margin: 0;
  font-size: clamp(1.5em, 3vw, 2em);
  font-weight: 600;
}

.actions-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
  width: 100%;
}

.cards-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
}

.diffusion-list-card {
  display: flex;
  flex-direction: column;
  gap: 1em;
  background: white;
  padding: 1em;
  border-radius: 1em;
  color: white;
  flex: 1;
  min-width: 250px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);

  transition: all 0.15s ease;
}

.diffusion-list-card:hover {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}

.hidden {
  display: none;
}

.dlc-header {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1em;
  color: var(--sad-nightblue);
  white-space: nowrap;
  text-wrap: nowrap;
}

.dlc-header p {
  text-wrap: none;
  font-size: clamp(1em, 2vw, 1.5em);
  font-weight: 600;
  width: 80%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin: 0;
}

.footer {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 1em;
}

.btn {
  background-color: white;
  color: var(--sad-nightblue);
  border: 1px solid var(--sad-nightblue);
  margin: 0;
  transition: background-color .4s ease;
}

.edit-btn:hover {
  background-color: var(--sad-nightblue);
  color: white;
}

.edit-btn.active {
  background-color: var(--sad-nightblue);
  color: white;
}

.delete-btn:hover {
  background-color: var(--sad-red);
  color: white;
  border: 1px solid var(--sad-red);
}

.duplicate-btn:hover {
  background-color: var(--sad-nightblue);
  color: white;
}

.cancel-btn {
  gap: 0.5em;
  border-color: var(--sad-red);
}

.cancel-btn:hover {
  background-color: var(--sad-red) !important;
  color: white !important;
}

.submit-btn {
  gap: 0.5em;
  border-color: var(--sad-nightblue);
}

.submit-btn:hover {
  background-color: var(--sad-nightblue) !important;
  color: white !important;
}

.new-list-form,
.edit-list-form {
  position: relative;
  display: flex;
  align-items: flex-start;
  flex-direction: column;
  gap: 1em;
  width: 100%;
  background-color: white;
  padding: 0 2em;
  max-height: 500px;
  overflow-y: auto;
  border-radius: 1em;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
  margin: 1em 0;
}


.edit-list-form-header {
  position: sticky;
  top: 0;
  font-size: clamp(1.5em, 3vw, 1.75em);
  font-weight: 600;
  margin: 0.75em 0;
}

.edit-list-form-body {
  display: flex;
  flex-direction: column;
  gap: 2em;
  width: 100%;
}

.recipients {
  display: flex;
  flex-direction: column;
  gap: 1em;
}

.edit-list-actions {
  position: sticky;
  bottom: 0;
  left: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5em;
  background-color: white;
  width: 100%;
  gap: 1em;
}

</style>
