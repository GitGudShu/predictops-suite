<template>
  <div class="container">
    <div class="left-col">
      <div class="logo-container">
        <img class="predictops-logo" src="logo_predictops_black.svg" alt="Predictops logo">
        <div class="ai">
          <Vue3Lottie :animationData="SiriJSON" :height="50" :width="50" />
          <p>AI Powered solution</p>
        </div>
      </div>
      <div class="form-container">
        <div class="form-header">
          <h2>Bienvenue</h2>
          <h4>Entrez vos identifiants de connexion</h4>
        </div>
        <div class="form-body">
          <div v-if="errorMessage" class="text-negative text-bold ">{{ errorMessage }}</div>
          <div class="input-wrapper">
            <div class="text-black text-h7 text-bold q-mb-sm">Email</div>
            <q-input :rules="emailRules" v-model="email" label="Entrez votre adresse e-mail"
              label-color="var(--sad-lightgray)" outlined color="accent" @keyup.enter="login"></q-input>
          </div>
          <div class="input-wrapper">
            <div class="text-black text-h7 text-bold q-mb-sm">Mot de passe</div>
            <q-input :rules="passwordRules" v-model="password" label="Entrez votre mot de passe"
              label-color="var(--sad-lightgray)" :type="showPassword ? 'text' : 'password'" outlined color="accent"
              @keyup.enter="login">
              <template v-slot:append>
                <q-icon :name="showPassword ? 'visibility_off' : 'visibility'" class="cursor-pointer"
                  @click="showPassword = !showPassword" />
              </template></q-input>
          </div>
          <div class="form-footer">
            <q-checkbox v-model="keepSession" label="Garder ma session ouverte 14 jours" color="primary" />
            <router-link to="/password/forgotten">Mot de passe oublié ? </router-link>
          </div>
        </div>
        <Button :loading="loading" btn-text='Se connecter' btn-type="submit" txt-color="white"
          bg-color="var(--sad-nightblue)" style="width: 100%; font-weight: 400; margin-bottom: 3em;" btn-size="lg-btn"
          @click="login" :disabled="!email || !password" />
      </div>
    </div>
    <div class="right-col">
      <img class="background" src="background.jpg" alt="Predictops logo">
    </div>
  </div>
</template>

<script setup>
import Button from "src/components/Button.vue";
import { useRouter } from 'vue-router'
import { ref } from "vue";
import { api } from "src/boot/axios";
import { notifyUser } from 'src/utils/notifyUser';
import SiriJSON from '/public/siri.json'
import { Cookies } from 'quasar'
import { Base64 } from 'js-base64'
import { socket, connectSocket } from 'src/utils/socket'


const router = useRouter()


const loading = ref(false);

const errorMessage = ref('')

const showPassword = ref(false);

const email = ref();
const password = ref();
const keepSession = ref(false)

const emailRules = [
  val => (val && val.length > 0) || 'Email is required',
];
const passwordRules = [
  val => (val && val.length > 0) || 'Password is required',
];


const login = async () => {
  localStorage.clear()
  const isFormValid = emailRules.every(rule => rule(email.value) === true) &&
    passwordRules.every(rule => rule(password.value) === true)

  if (!isFormValid) {
    return
  }

  loading.value = true
  try {
    const response = await api.post('/auth/login', {
      email: email.value,
      password: password.value,
      keepSession: keepSession.value
    })


    const user = {
      email: response.data.email,
      role: response.data.role,
      dpt: response.data.dpt,
      token: response.data.token
    }


    localStorage.setItem("dpt", user.dpt)
    const encodedUser = Base64.encode(JSON.stringify(user))
    Cookies.set('user', encodedUser, { expires: '14d' })

    const boundsResponse = await api.get(`/data/bounds?dpt=${response.data.dpt}`)
    localStorage.setItem("dptBounds", JSON.stringify(boundsResponse.data[0].bounds))
    loading.value = false

    connectSocket();
    socket.once('connect', () => {
      socket.emit('login', user.email)
    })
    router.push('/')

  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la connexion.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false
    if (error.response.status === 403) {
      errorMessage.value = error.response.data.message
    } else {
      notifyUser({ icon: "error", message: "Erreur serveur ou de connectivité", color: "red", position: "bottom", timeout: 2500 });
    }
  }

}
</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  min-height: 100vh;
  overflow: hidden;
}

.background {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.right-col {
  width: 45%;
}

.left-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-container {
  width: 75%;
  max-height: 200px;
  display: flex;
  align-items: center;
}

.predictops-logo {
  height: 100%;
  flex: 0;
}

.ai {
  color: var(--sad-nightblue);
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-left: auto;
}

.ai p {
  margin: 0;
  font-weight: bold;
  font-size: 12px;
  text-align: center;
}


.form-container {
  width: 75%;
  display: flex;
  flex-direction: column;
  gap: 2em;
}

.form-header h2 {
  color: var(--sad-nightblue);
  font-weight: 500;
  font-size: 40px;
  margin-bottom: 0;
}

.form-header h4 {
  color: var(--sad-lightgray-2);
  font-weight: 500;
  font-size: 20px;
  margin-top: 0;
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

@media screen and (max-width: 1000px) {
  .right-col {
    display: none;
  }

  .logo-container {
    max-height: 150px;
  }

  .container {
    overflow: auto;
  }
}

@media screen and (max-width: 550px) {
  .ai {
    display: none;
  }

}
</style>
