<template>
  <q-layout view="hHh lpR fFf">

    <q-header class="bg-transparent">
      <router-link to="/login" class="logo-link" exact>
        <img :src="`${publicPath}logo_predictops_black.svg`" alt="Predictops logo" class="logo">
      </router-link>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>


  </q-layout>
</template>

<script setup>
import { computed } from 'vue';

const publicPath = process.env.PUBLIC_PATH || '/predictops/'


</script>

<style scoped>
.logo {
  max-width: 175px;
  min-width: 100px;
  margin-left: 15px;
  max-height: 100%;
  width: clamp(100px, 10vw, 175px);
}
</style>
