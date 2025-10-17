<template>
  <div class="container">
    <h5>Mot de passe oublié ?</h5>
    <p class="text-italic text-bold">Pas de panique, nous vous envoyons un email pour réinitialiser votre mot de passe.
    </p>
    <div class="form-body">
      <div v-if="errorMessage" class="text-negative text-bold ">{{ errorMessage }}</div>
      <div v-if="successMessage" class="text-positive text-bold ">{{ successMessage }}</div>
      <div class="input-wrapper">
        <div class="text-black text-h7 text-bold q-mb-sm">Email</div>
        <q-input :rules="emailRules" v-model="email" label="Entrez votre adresse e-mail"
          label-color="var(--sad-lightgray)" outlined color="accent" @keyup.enter="resetPassword"></q-input>
      </div>

      <Button :loading="loading" :btn-text='btnText' btn-type="submit" txt-color="white"
        bg-color="var(--sad-nightblue)" style="width: 100%; font-weight: 400; margin-bottom: 3em;" btn-size="lg-btn"
        @click="resetPassword" :disabled="!email || disabled"/>
    </div>
  </div>
</template>

<script setup>
import Button from "src/components/Button.vue";
import { useRouter, useRoute } from 'vue-router'
import { ref, computed } from "vue";
import { api } from "src/boot/axios";
import { notifyUser } from 'src/utils/notifyUser';

const router = useRouter()
const route = useRoute()

const loading = ref(false);

const errorMessage = ref('')
const successMessage = ref('')

const btnText = ref('Réinitialiser')
const disabled = ref()

const showPassword = ref(false);

const email = ref();

const emailRules = [
  val => (val && val.length > 0) || 'Email is required',
];


const resetPassword = async () => {
  const isFormValid = emailRules.every(rule => rule(email.value) === true)

  if (!isFormValid) {
    return
  }
  loading.value = true
  try {
    const response = await api.post('/password/forgotten', {
      email: email.value,
    })
    loading.value = false
    errorMessage.value = ''
    successMessage.value = response.data.message

    disabled.value = true
    btnText.value = 'Réessayez dans 60s'

    let countdown = 60
    const countdownInterval = setInterval(() => {
      if (countdown === 0) {
        clearInterval(countdownInterval)
        disabled.value = false
        btnText.value = 'Réinitialiser'
      } else {
        btnText.value = `Réessayez dans ${countdown}s`
      }
      countdown--
    }, 1000)
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
  width: 75%;
  max-width: 500px;
  min-height: 50vh;
  color: var(--sad-nightblue);
  margin: auto;
  overflow: hidden;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}


.form-body {
  display: flex;
  flex-direction: column;
  gap: 2em;
}

.form-footer {
  color: var(--sad-nightblue);
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5em;
}

</style>
