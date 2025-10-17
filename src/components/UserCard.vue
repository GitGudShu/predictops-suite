<template>
  <div class="user-card-detailed" v-show="view == 'detailed'" :class="selected ? 'selected' : ''">
    <div class="user-card-header-detailed">
      <q-badge v-if="user.email == decodedUser.email" color="primary" label="C'est vous !" rounded floating></q-badge>
      <div class="checkbox-container-detailed" v-show="isSelectable">
        <q-checkbox v-model="selected" @update:model-value="handleSelect" />
      </div>
      <img :src="bannerSrc" alt="banner" class="banner">
      <img :src="'data:image/png;base64,' + user.profile_image" alt="profile" class="profile-detailed">
    </div>
    <div class="user-card-body-detailed">
      <div class="user-card-email-detailed">{{ user.email }}</div>
      <div class="user-card-role-detailed" v-show="user.email != decodedUser.email">Role :
        <Dropdown btn-size="sm-btn" :list="rolesList" :selected-value="user.role" @update:selected="onRoleSelected" />
      </div>
      <div class="user-card-dpt-detailed" v-if="decodedUser.role == 'maintainer'">Département :
        <Dropdown btn-size="sm-btn" :list="departmentsList" :selected-value="user.dpt"
          @update:selected="onDptSelected" />
      </div>
    </div>
    <div class="user-card-footer-detailed" v-show="user.email != decodedUser.email">
      <Button btn-size="xs-btn"  bg-color="var(--sad-red)" txt-color="white" left-icon="fa-solid fa-user-times" @click="handleDelete" />
      <q-toggle v-model="active" left-label label="Actif" color="primary"
        @update:model-value="handleToggleActive"></q-toggle>
    </div>
  </div>
  <div class="user-card-dense" v-show="view == 'dense'" :class="selected ? 'selected' : ''">
    <div class="user-card-header-dense">
      <div class="checkbox-container-dense" v-show="isSelectable">
        <q-checkbox v-model="selected" @update:model-value="handleSelect" />
      </div>
      <img :src="'data:image/png;base64,' + user.profile_image" alt="profile" class="profile-dense">
      <q-badge v-if="user.email == decodedUser.email" color="primary" label="C'est vous !" rounded style="position: absolute; top: 0; left: 0;"></q-badge>
    </div>
    <div class="user-card-body-dense">
      <div class="user-card-email-dense">{{ user.email }}</div>
      <div class="user-card-role-dense" v-show="user.email != decodedUser.email">
        <Dropdown btn-size="xs-btn" :list="rolesList" :selected-value="user.role" @update:selected="onRoleSelected" />
      </div>
      <div class="user-card-dpt-dense" v-if="decodedUser.role == 'maintainer'">
        <Dropdown btn-size="xs-btn" :list="departmentsList" :selected-value="user.dpt"
          @update:selected="onDptSelected" />
      </div>
    </div>
    <div class="user-card-footer-dense">
      <q-toggle v-model="active" left-label label="Actif" color="primary"
        @update:model-value="handleToggleActive" v-show="user.email != decodedUser.email"></q-toggle>
      <Button btn-size="xs-btn" bg-color="var(--sad-red)" txt-color="white" left-icon="fa-solid fa-user-times" @click="handleDelete" v-show="user.email != decodedUser.email"/>
      <q-icon name="fa-solid fa-ellipsis-vertical" size="16px" @click="showUserDetails" style="cursor: pointer;"></q-icon>
    </div>
  </div>
</template>

<script setup>
import { computed, watch, ref, h } from 'vue';
import Dropdown from "src/components/Dropdown.vue";
import Button from './Button.vue';
import { showDialog } from 'src/utils/dialogUtil';
import { Base64 } from 'js-base64'
import { Cookies } from 'quasar'

const props = defineProps({
  user: Object,
  isSelectable: Boolean,
  isSelected: Boolean,
  view: String
})

const emit = defineEmits(['toggleActive', 'deleteUser', 'selectUser', 'updateRole', 'updateDpt']);

const publicPath = process.env.PUBLIC_PATH || '/predictops/'


const decodedUser = JSON.parse(Base64.decode(Cookies.get('user')))

const rolesList = ["user", "admin", "admin-cta"]
const departmentsList = ["01", "25", "31", "78"]

if (decodedUser.role === "maintainer") rolesList.push("maintainer")

const active = ref(props.user.active)
const selected = ref(props.isSelected)

watch(() => props.isSelected, (newVal) => {
  selected.value = newVal;
});

const handleToggleActive = () => {
  emit('toggleActive', props.user.email, active.value);
}

function toTime(seconds) {
  var date = new Date(null);
  if(seconds) {
    date.setSeconds(seconds);
    return date.toISOString().substr(11, 8);
  }
  return "N/A"
}

const handleDelete = () => {
  showDialog({
    focus: "none",
    style: { width: "50%", },
    dark: true,
    message: "Êtes-vous sûr de vouloir supprimer cet utilisateur ?",
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
      emit('deleteUser', props.user.email);
    });

}

const handleSelect = () => {
  emit('selectUser', props.user.email);
}

const showUserDetails = () => {
  showDialog({
    focus: "none",
    style: { width: "50%", },
    dark: true,
    html: true,
    message: `
      <div style="font-size: 14px; color: white; display: flex; flex-direction: column; gap: 8px;">
        <span>Dernière connexion: ${props.user.last_login ? new Intl.DateTimeFormat('fr-FR', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }).format(new Date(props.user.last_login)) : 'N/A'}</span>
        <span>Nombre de connexions: ${props.user.number_of_logins || 'N/A'}</span>
        <span>Temps total d'activité: ${toTime(props.user.total_activity)}</span>
      </div>`,
    ok: {
      label: 'OK',
      color: 'secondary',
    },
  })
}

const onRoleSelected = (selected) => {
  if (props.user.role && selected != props.user.role) emit('updateRole', props.user.email, selected);
  else emit('updateRole', props.user.email, "user");
}

const onDptSelected = (selected) => {
  if (props.user.dpt && selected != props.user.dpt) emit('updateDpt', props.user.email, selected);
  else emit('updateDpt', props.user.email, "25");
}

const bannerSrc = computed(() => {
  return `${publicPath}banner_${props.user.dpt}.svg`
})

</script>

<style scoped>
.user-card-detailed {
  flex: 1 1 auto;
  min-width: 225px;
  max-width: 300px;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  color: var(--sad-nightblue);
  gap: 0.5em;
}

.user-card-dense {
  flex: 1 1 33%;
  min-width: 300px;
  max-height: 250px;
  height: auto;
  flex-wrap: wrap;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  display: flex;
  color: var(--sad-nightblue);
}

.user-card-header-detailed {
  position: relative;
}

.user-card-header-dense {
  position: relative;
  padding: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1em;
}

.banner {
  width: 100%;
  height: 100px;
  border-top-left-radius: 15px;
  border-top-right-radius: 15px;
  object-fit: cover;
}

.profile-detailed {
  width: 75px;
  height: 75px;
  border-radius: 50%;
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
}

.profile-dense {
  width: 35px;
  height: 35px;
  border-radius: 50%;
}

.user-card-body-detailed {
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  gap: 1em;
  padding: 1em;
  flex: 1;
}

.user-card-body-dense {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  flex-wrap: wrap;
  flex: 1;
  gap: 1em;
  padding: 1em;
}

.user-card-email-detailed {
  font-size: clamp(0.9rem, 3vw, 1rem);
  font-weight: 800;
  word-wrap: break-word;
  text-overflow: ellipsis;
  text-align: center;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-card-email-dense {
  font-size: clamp(0.9rem, 3vw, 1rem);
  font-weight: 800;
  word-wrap: break-word;
  text-overflow: ellipsis;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-card-role-detailed,
.user-card-dpt-detailed {
  margin-top: auto;
  font-weight: 800;
}

.user-card-role-dense,
.user-card-dpt-dense {
  font-weight: 800;
}

.user-card-footer-detailed {
  padding: 1em;
  display: flex;
  justify-content: flex-start;
  gap: 1em;
  align-items: center;
}

.user-card-footer-dense {
  padding: 1em;
  display: flex;
  justify-content: center;
  margin-left: auto;
  gap: 1em;
  align-items: center;
}


button {
  margin: 0;
}

.checkbox-container-detailed {
  position: absolute;
  opacity: 0;
  transition: all 0.3s ease;
}


.user-card-detailed:hover .checkbox-container-detailed {
  opacity: 1;
}

.user-card-detailed.selected .checkbox-container-detailed {
  opacity: 1;
}

.user-card-detailed.selected {
  transform: translateY(-10px);
}
</style>
