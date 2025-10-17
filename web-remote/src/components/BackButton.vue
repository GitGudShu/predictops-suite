<template>
  <button @click="goBack" class="btn-back"><q-icon name="trending_flat" class="rotate-180"
    size="xl"></q-icon></button>
</template>

<script setup>
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();

const goBack = () => {
  if (router) {
        router.back();
      }
}
</script>


<style scoped>
.btn-back {
  width: 75px;
  background-color: transparent;
  outline: none;
  border: none;
  color: var(--sad-nightblue);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-back:hover {
  transform: scale(1.1);
}
</style>
