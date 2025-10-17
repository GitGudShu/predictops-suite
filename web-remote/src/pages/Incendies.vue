<template>
  <q-page>
    <BreakingNews :page="location.path.replace('/', '')" height="80px" font-size="clamp(0.75rem, 1.75vw, 2rem)" ></BreakingNews>
    <q-banner inline-actions class="bg-warning text-white" style="border-radius: 15px;" v-show="showBanner">
      <span class="text-bold">
        Ces indices ne sont calculés que durant la période des feux.
      </span>
      <template v-slot:action>
        <q-btn flat color="white" label="ok" @click="showBanner = false"/>
      </template>
    </q-banner>
      <div class="cards-container">
        <Card icon="local_fire_department" header-text="Prévision risque de feux de forêt - Méthode Canadienne"
          body-height="85%" right-icon="question_mark" rightIconClickable @iconClicked="handleIconClickCanada">
          <template #body>
            <Map controls hover satellite-toggle type="fires" geometries="hexagones" fire-prediction-method="canada"
              horizon-dropdown opacity-slider legend />
          </template>
        </Card>
        <Card icon="local_fire_department" header-text="Prévision risque de feux d'espaces naturels - Méthode Predictops"
          body-height="85%" right-icon="question_mark" rightIconClickable @iconClicked="handleIconClickSAD">
          <template #body>
            <Map controls hover satellite-toggle type="fires" geometries="hexagones" fire-prediction-method="sad" horizon-dropdown
              opacity-slider legend />
          </template>
        </Card>
      </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import Card from 'src/components/Card.vue';
import BreakingNews from 'src/components/BreakingNews.vue';
import Map from "src/components/Map.vue";
import { showDialog } from "src/utils/dialogUtil";
import MarkdownIt from 'markdown-it';
import { api } from "src/boot/axios";
import { useRoute } from 'vue-router'
const location = useRoute();

const md = MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

const showBanner = ref(true)

const fetchMarkdown = async (markdown, ref) => {
  try {
    const response = await api.get(`/static/markdowns/${markdown}.md`);
    ref.value = md.render(response.data)
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération du markdown.", color: "red", position: "bottom", timeout: 2500 })
  }
};

const handleIconClickCanada = async () => {
  const canadaMarkdown = ref()
  await fetchMarkdown("incendie_canada", canadaMarkdown)

  showDialog({
    focus: "none",
    style: { width: "90%", maxWidth: "unset !important" },
    dark: true,
    message: canadaMarkdown.value,
    html: true,
    ok: {
      label: 'OK',
      color: 'secondary',
    },

  })
}
const handleIconClickSAD = async () => {
  const sadMarkdown = ref()
  await fetchMarkdown("incendie_sad", sadMarkdown)

  showDialog({
    focus: "none",
    style: { width: "90%", maxWidth: "unset !important" },
    dark: true,
    message: sadMarkdown.value,
    html: true,
    ok: {
      label: 'OK',
      color: 'secondary',
    },

  })
}


</script>

<style scoped>

.cards-container {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
  flex: 1;
}

</style>
