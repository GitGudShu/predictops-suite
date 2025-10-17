<template>
  <q-page>
    <div class="actions-bar">
      <BackButton />
      <div class="right-buttons">
        <q-btn-toggle size="md" outline unelevated v-model="view" toggle-color="info" text-color="primary" :options="[
          { value: 'dense', slot: 'dense' },
          { value: 'detailed', slot: 'detailed' },
        ]" class="center">
          <template v-slot:dense>
            <q-icon name="fa-solid fa-list"></q-icon>
          </template>
          <template v-slot:detailed>
            <q-icon name="mdi-view-grid"></q-icon>
          </template>

        </q-btn-toggle>
        <Button left-icon="fa-solid fa-user-plus" btn-text="Nouvel utilisateur" bg-color="var(--sad-nightblue)"
          btn-size="sm-btn" @click="openAddUser" class="open-add-user" txt-color="white" />
        <q-input v-model="searchQuery" type="search" placeholder="Rechercher" bg-color="white" outlined dense clearable>
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
        <q-checkbox v-model="selectAll" @update:model-value="handleSelectAll" label="Tout séléctionner" dense
          class="text-black text-bold" />
        <Button v-if="selectedUsers.length" left-icon="fa-solid fa-trash" btn-text="Supprimer" btn-size="sm-btn"
          @click="deleteSelectedUsers" class="delete-selected" bg-color="var(--sad-red)" txt-color="white" />
      </div>
    </div>
    <div class="container">
      <UserCard :view="view" v-for="user in filteredUsers" :key="user.email" :user="user" @toggleActive="toggleActive"
        @updateRole="updateRole" @selectUser="selectUser" @deleteUser="deleteUser" @updateDpt="updateDpt"
        :is-selectable="user.email != decodedUser.email" :is-selected="selectedUsers.includes(user.email)" />
    </div>
    <q-dialog v-model="showAddUser">
      <div class="add-user-form text-white">
        <div class="add-user-form-header">
          <div class="text-h4 text-bold text-center q-mb-lg">Ajouter un utilisateur</div>
        </div>
        <div class="form-body">
          <div v-if="errorMessage" class="text-warning text-bold text-center">{{ errorMessage }}</div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Email : </span>
            <q-input input-class="text-black" v-model="newUserEmail" label="Email utilisateur" label-color="primary"
              bg-color="white" type="email" standout color="primary" dense style="width: 80%;"></q-input>
          </div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Role : </span>
            <Dropdown btn-bg-color="white" btn-size="sm-btn" :list="rolesList" @update:selected="onRoleSelected">
            </Dropdown>
          </div>
          <div class="input-wrapper">
            <span class="text-h7 text-bold q-mb-sm">Département : </span>
            <Dropdown btn-bg-color="white" btn-size="sm-btn" :list="departmentsList"
              @update:selected="onDepartmentSelected"></Dropdown>
          </div>
          <Button :loading="loading" btn-text="Ajouter" btn-type="submit" left-icon="fa-solid fa-plus"
            btn-size="md-btn" bg-color="var(--sad-orange)" txt-color="white" style="margin-top: auto;"
            @click="addUser" />
        </div>
      </div>
    </q-dialog>
  </q-page>
</template>

<script setup>
import Button from "src/components/Button.vue";
import BackButton from "src/components/BackButton.vue";
import Dropdown from "src/components/Dropdown.vue";
import UserCard from "src/components/UserCard.vue";
import { ref, onMounted, computed } from "vue";
import { api } from "src/boot/axios";
import { notifyUser } from 'src/utils/notifyUser';
import { showDialog } from "src/utils/dialogUtil";
import { useRouter } from 'vue-router'
import { Base64 } from 'js-base64'
import { Cookies } from 'quasar'


const decodedUser = JSON.parse(Base64.decode(Cookies.get('user')))

const rolesList = ["user", "admin", "admin-cta"]
const departmentsList = [decodedUser.dpt]

if (decodedUser.role === "maintainer") {
  rolesList.push("maintainer")
  departmentsList.push("01", "25", "31", "78")
  departmentsList.splice(departmentsList.indexOf(decodedUser.dpt), 1)
}

const view = ref("dense")

const searchQuery = ref(null)

const filteredUsers = computed(() => {
  const query = searchQuery.value ? searchQuery.value.toLowerCase() : '';
  return usersList.value.filter(user => user.email.toLowerCase().includes(query));
})

const newUserEmail = ref(null)
const newUserRole = ref(null)
const newUserDpt = ref(null)

const errorMessage = ref('')

const loading = ref()
const selectAll = ref(false)

const showAddUser = ref(false);

const usersList = ref([])
const selectedUsers = ref([])

const onRoleSelected = (selected) => {
  newUserRole.value = selected
}

const onDepartmentSelected = (selected) => {
  newUserDpt.value = selected
}

const handleSelectAll = (value) => {
  if (value) {
    selectedUsers.value = filteredUsers.value
      .filter(user => user.email !== decodedUser.email)
      .map(user => user.email);
  } else {
    selectedUsers.value = [];
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const response = await api.get(`/admin/users?dpt=${decodedUser.dpt}&role=${decodedUser.role}`);
    usersList.value = response.data
    loading.value = false
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des utilisateurs.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false
  }
})

const openAddUser = () => {
  showAddUser.value = true
}

const addUser = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await api.post(`/admin/create-user`, {
      email: newUserEmail.value,
      role: newUserRole.value,
      dpt: newUserDpt.value
    });
    usersList.value = [...usersList.value, response.data.user]
    showAddUser.value = false
    loading.value = false
    notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
  } catch (error) {
    errorMessage.value = error.response.data.message
    loading.value = false
  }
}

const toggleActive = async (email, active) => {
  try {
    const response = await api.patch(`/admin/toggle-user-active`, { email, active });
    const user = usersList.value.find(u => u.email === email);
    if (user) {
      user.active = active;
    }
    notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la modification de l'utilisateur.", color: "red", position: "bottom", timeout: 2500 });
  }
}

const updateRole = async (email, role) => {
  try {
    const response = await api.patch(`/admin/update-role`, { email, role });
    const user = usersList.value.find(u => u.email === email);
    if (user) {
      user.role = role;
    }
    notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la modification de l'utilisateur.", color: "red", position: "bottom", timeout: 2500 });
  }
}

const selectUser = (email) => {
  if (selectedUsers.value.includes(email)) {
    selectedUsers.value = selectedUsers.value.filter(e => e !== email);
  } else {
    selectedUsers.value.push(email);
  }
}

const deleteUser = async (email) => {
  try {
    const response = await api.delete(`/admin/delete-user`, { data: { email } });
    usersList.value = usersList.value.filter(user => user.email !== email);
    notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la suppression de l'utilisateur.", color: "red", position: "bottom", timeout: 2500 });
  }
}

const deleteSelectedUsers = () => {
  showDialog({
    focus: "none",
    style: { width: "50%", },
    dark: true,
    message: "Êtes-vous sûr de vouloir supprimer ce(s) utilisateur(s) ?",
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
        const response = await api.delete(`/admin/delete-users`, { data: { emails: selectedUsers.value } });
        usersList.value = usersList.value.filter(user => !selectedUsers.value.includes(user.email));
        selectedUsers.value = [];
        notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
      } catch (error) {
        notifyUser({ icon: "error", message: "Erreur lors de la suppression des utilisateurs.", color: "red", position: "bottom", timeout: 2500 });
      }
    });

}

const updateDpt = async (email, dpt) => {
  try {
    const response = await api.patch(`/admin/update-department`, { email, dpt });
    const user = usersList.value.find(u => u.email === email);
    if (user) {
      user.dpt = dpt;
    }
    notifyUser({ icon: "check", message: response.data.message, color: "green", position: "bottom", timeout: 2500 })
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la modification de l'utilisateur.", color: "red", position: "bottom", timeout: 2500 });
  }
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
  height: 10%;
}

.actions-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
  width: 100%;
}

.add-user-form {
  width: clamp(300px, 50vw, 650px);
  background: var(--sad-nightblue);
  display: flex;
  flex-direction: column;
  gap: 2em;
  padding: 1em;
  height: clamp(400px, 70vh, 550px);
}

.input-wrapper {
  display: flex;
  align-items: center;
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
