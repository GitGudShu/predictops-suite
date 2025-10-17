<template>
  <q-page>
    <BackButton />
    <div class="container">
      <h5>Changer le mot de passe</h5>
      <p class="text-italic text-bold">Les mots de passes robustes contiennent des chiffres, des lettres et des
        symboles.
      </p>
      <div class="form-body">
        <div v-if="errorMessage" class="text-negative text-bold ">{{ errorMessage }}</div>
        <div v-if="successMessage" class="text-positive text-bold ">{{ successMessage }}</div>
        <div class="input-wrapper">
          <div class="text-black text-h7 text-bold q-mb-sm">Adresse e-mail</div>
          <q-input v-model="email" label="Email utilisateur"
            label-color="var(--sad-lightgray)" type="email" outlined color="accent" disable
            ></q-input>
        </div>
        <div class="input-wrapper">
          <div class="text-black text-h7 text-bold q-mb-sm">Mot de passe actuel</div>
          <q-input :rules="passwordRules" v-model="actualPassword" label="Entrez votre mot de passe actuel"
            label-color="var(--sad-lightgray)" :type="showPassword ? 'text' : 'password'" outlined color="accent"
            @keyup.enter="updatePassword">
            <template v-slot:append>
              <q-icon :name="showPassword ? 'visibility_off' : 'visibility'" class="cursor-pointer"
                @click="showPassword = !showPassword" />
            </template></q-input>
        </div>
        <div class="input-wrapper">
          <div class="text-black text-h7 text-bold q-mb-sm">Nouveau mot de passe</div>
          <q-input :rules="passwordRules" v-model="password" label="Entrez votre nouveau mot de passe"
            label-color="var(--sad-lightgray)" :type="showPassword ? 'text' : 'password'" outlined color="accent"
            @keyup.enter="updatePassword">
            <template v-slot:append>
              <q-icon :name="showPassword ? 'visibility_off' : 'visibility'" class="cursor-pointer"
                @click="showPassword = !showPassword" />
            </template></q-input>
        </div>

        <Button :loading="loading" btn-text='Réinitialiser' btn-type="submit" txt-color="white"
          bg-color="var(--sad-nightblue)" style="width: 100%; font-weight: 400; margin-bottom: 3em;" btn-size="lg-btn"
          @click="updatePassword" />
      </div>
    </div>
  </q-page>
</template>

<script setup>
import Button from "src/components/Button.vue";
import BackButton from "src/components/BackButton.vue";
import { ref, onMounted } from "vue";
import { api } from "src/boot/axios";
import { notifyUser } from 'src/utils/notifyUser';
import { useRouter } from 'vue-router'
import { Base64 } from 'js-base64'
import { Cookies } from 'quasar'


const router = useRouter()

const decodedUser = JSON.parse(Base64.decode(Cookies.get('user')))

const email = ref(decodedUser.email)

const loading = ref()

const errorMessage = ref('')
const successMessage = ref('')

const showPassword = ref(false);

const actualPassword = ref()
const password = ref()


const passwordRules = [
  val => (val && val.length > 0) || 'Password is required',
];


const updatePassword = async () => {
  const isFormValid = passwordRules.every(rule => rule(password.value) === true)

  if (!isFormValid) {
    return
  }
  loading.value = true
  try {
    const response = await api.post('/password/update', {
      email: email.value,
      old_password: actualPassword.value,
      new_password: password.value,
    })
    loading.value = false
    successMessage.value = response.data.message
    errorMessage.value = ''
    setTimeout(() => {
      setTimeout(() => {
        router.push('/parametres')
      }, 1000)
    }, 1500)
  } catch (error) {
    loading.value = false
    successMessage.value = ''
    errorMessage.value = error.response.data.message
  }
}

</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  flex-direction: column;
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
