<template>
  <q-page>
    <BreakingNews :page="location.path.replace('/', '')" height="80px" font-size="clamp(0.75rem, 1.75vw, 2rem)">
    </BreakingNews>
    <div class="cards-container">
      <Card icon="fmd_bad" header-text-size="fs-md" header-text="Historique des interventions" v-show="dpt != '78'" :flex="flex" style="min-width: 350px;">
        <template #body>
          <Map controls legend contour quality hover click horizon-dropdown type="delays" geometries="hexagones"/>
        </template>
      </Card>
      <Card icon="mdi-binoculars" header-text-size="fs-md" header-text="Prévisions interventions" style="min-width: 350px;">
        <template #body>
          <Map controls legend alerts hover click type="interventions_predictions" geometries-dropdown horizon-dropdown
            geometries="Tous" :polar-bars="dpt != '01'"/>
        </template>
      </Card>
    </div>
  </q-page>
</template>

<script setup>

import { computed, ref } from "vue"
import BreakingNews from 'src/components/BreakingNews.vue';
import Card from 'src/components/Card.vue';
import Map from "src/components/Map.vue";
import { useRoute } from 'vue-router'

const location = useRoute();
const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value <= 1050)

const updateWindowWidth = () => {
  windowWidth.value = window.innerWidth;
}
const flex = computed(() => isMobile.value ? '1' : '0')

const dpt = computed(() => {
  return localStorage.getItem("dpt") || location.params.dpt
})

window.addEventListener('resize', updateWindowWidth)

</script>

<style scoped>
.cards-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-wrap: wrap;
  flex: 1;
  gap: 1em;
}
</style>
