<template>
  <q-page>
    <BreakingNews :page="location.path.replace('/', '')" height="80px" font-size="clamp(0.75rem, 1.75vw, 2rem)" ></BreakingNews>

    <div class="container">
      <Card icon="fmd_bad" header-text-size="fs-md" header-text="Prévisions des inondations" >
        <template #body>
          <Map contour click legend hover type="vigicrues" />
        </template>
      </Card>
      <Card icon="mdi-water-alert" header-text-size="fs-md" header-text="Nappes phréatiques" >
        <template #body>
          <Map contour click legend hover type="groundwater" />
        </template>
      </Card>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from "vue";
import Card from 'src/components/Card.vue';
import BreakingNews from 'src/components/BreakingNews.vue';
import Map from "src/components/Map.vue";
import { notifyUser } from "src/utils/notifyUser";
import { useRoute } from 'vue-router'
const location = useRoute();


</script>

<style scoped>
.container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-wrap: wrap;
  flex: 1;
  gap: 1em;
}



</style>
