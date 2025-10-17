<template>
  <q-inner-loading :showing="initialLoading">
    <q-spinner-tail size="10vw" color="secondary"/>
  </q-inner-loading>
  <div v-if="!tokenIsValid && !initialLoading" class="container text-subtitle1">
    <p>Lien invalide ou expiré.</p>
    <p>Veuillez demander un nouveau lien <router-link to="/password/forgotten"
        class="text-bold">ici.</router-link></p>
  </div>
  <div class="container" v-else v-show="tokenIsValid && !initialLoading">
    <h5>Réinitialiser le mot de passe</h5>
    <p class="text-italic text-bold">Les mots de passes robustes contiennent des chiffres, des lettres et des symboles.
    </p>
    <div class="form-body">
      <div v-if="errorMessage" class="text-negative text-bold ">{{ errorMessage }}</div>
      <div v-if="successMessage" class="text-positive text-bold ">{{ successMessage }}</div>
      <div v-if="redirectionMessage" class="text-black text-bold ">{{ redirectionMessage }}</div>
      <div class="input-wrapper">
        <div class="text-black text-h7 text-bold q-mb-sm">Nouveau mot de passe</div>
        <q-input :rules="passwordRules" v-model="password" label="Entrez votre nouveau mot de passe"
          label-color="var(--sad-lightgray)" :type="showPassword ? 'text' : 'password'" outlined color="accent"
          @keyup.enter="resetPassword">
          <template v-slot:append>
            <q-icon :name="showPassword ? 'visibility_off' : 'visibility'" class="cursor-pointer"
              @click="showPassword = !showPassword" />
          </template></q-input>
      </div>

      <Button :loading="loading" btn-text='Réinitialiser' btn-type="submit" txt-color="white"
        bg-color="var(--sad-nightblue)" style="width: 100%; font-weight: 400; margin-bottom: 3em;" btn-size="lg-btn"
        @click="resetPassword" />
    </div>
  </div>
</template>

<script setup>
import Button from "src/components/Button.vue";
import { useRouter, useRoute } from 'vue-router'
import { ref, onMounted } from "vue";
import { api } from "src/boot/axios";
import { notifyUser } from 'src/utils/notifyUser';

const router = useRouter()
const route = useRoute()

const token = route.query.token

const loading = ref()
const initialLoading = ref(true)

const errorMessage = ref('')
const successMessage = ref('')
const redirectionMessage = ref('')

const tokenIsValid = ref()

const showPassword = ref(false);

const password = ref();


const passwordRules = [
  val => (val && val.length > 0) || 'Password is required',
];

const checkToken = async () => {
  initialLoading.value = true
  try {
    const response = await api.post(`/password/check-password-reset-token`, {
      token: token
    })
    if (response.status === 200) {
      initialLoading.value = false
      tokenIsValid.value = true
    }
    else if (response.status === 403) {
      initialLoading.value = false
      tokenIsValid.value = false
    }
    else {
      initialLoading.value = false
      notifyUser({ icon: "error", message: "Erreur serveur ou de connectivité", color: "red", position: "bottom", timeout: 2500 })
    }
  } catch (error) {
    initialLoading.value = false
  }
}

const resetPassword = async () => {
  const isFormValid = passwordRules.every(rule => rule(password.value) === true)

  if (!isFormValid) {
    return
  }
  loading.value = true
  try {
    const response = await api.post('/password/reset', {
      token: token,
      new_password: password.value,
    })
    loading.value = false
    successMessage.value = response.data.message
    errorMessage.value = ''
    setTimeout(() => {
      redirectionMessage.value = "Vous allez être redirigé vers la page de connexion..."
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    }, 1500)
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la reinitialisation.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false
    errorMessage.value = error.response.data.message
  }
}

onMounted(async () => {
  await checkToken()

})
</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  flex-direction: column;
  width: 75%;
  max-width: 400px;
  min-height: 50vh;
  color: var(--sad-nightblue);
  margin: auto;
}


.form-body {
  display: flex;
  flex-direction: column;
  gap: 2em;
}
</style>
