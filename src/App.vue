<template>

  <router-view></router-view>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router'
import { Cookies } from 'quasar';
import { Base64 } from 'js-base64'
import { socket, connectSocket } from 'src/utils/socket';

const router = useRouter()


window.addEventListener('storage', (event) => {
  if (event.key === 'logoutEvent') {
    router.push("/login")
  }
}
)

onMounted(() => {

  if (Cookies.has('user')) {
    const decodedUser = JSON.parse(Base64.decode(Cookies.get('user')));

    connectSocket();

    socket.once('connect', () => {
      console.log("Socket connected (App.vue onMounted).");
      socket.emit('login', decodedUser.email);
    });
  }
});


</script>
