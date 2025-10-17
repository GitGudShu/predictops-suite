<template>
  <q-page>
    <div class="actions-bar">
      <BackButton />
      <div class="right-buttons">
        <q-input v-model="searchQuery" type="search" placeholder="Rechercher" bg-color="white" outlined dense clearable>
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>
    </div>
    <div class="wrapper">
      <div class="header-skeleton" v-if="loading">
        <q-skeleton type="circle" />
        <q-skeleton type="text" :style="{ width: '75px' }"/>
        <q-skeleton type="text" :style="{ flex: '1' }"/>
      </div>
      <div class="skeletons-container" v-if="loading">
        <q-skeleton type="rect" v-for="i in 15" :key="i"
          :style="{ width: '300px', height: '75px', borderRadius: '15px' }"></q-skeleton>
      </div>
      <div v-for="(collections, dpt) in filteredCollectionsByDpt" :key="dpt" v-if="!loading">
        <div class="header">
          <q-icon name="fire_truck" size="lg"></q-icon>
          <h3>SDIS {{ dpt }}</h3>
          <q-separator size="3px" />
        </div>

        <div class="container" v-if="!loading">
          <div class="health-card" v-for="collection in collections" :key="collection.name">
            <div class="health-color" :style="{ 'background-color': collection.color }"></div>
            <div class="health-card-body">
              <div class="health-card-title">{{ collection.name }}</div>
              <div class="health-card-latest-timestamp text-italic text-weight-regular">Dernière actualisation : {{
                collection.latest_added_at
                }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>

import BackButton from "src/components/BackButton.vue";
import { ref, onMounted, onUnmounted, computed } from "vue";
import { api } from "src/boot/axios";
import { notifyUser } from 'src/utils/notifyUser';

const searchQuery = ref(null)

const collectionsByDpt = ref({})

const filteredCollectionsByDpt = computed(() => {
  const query = searchQuery.value ? searchQuery.value.toLowerCase() : '';
  const filtered = {};
  for (const [dpt, collections] of Object.entries(collectionsByDpt.value)) {
    filtered[dpt] = collections.filter(collection => collection.name.toLowerCase().includes(query));
  }
  return filtered;
})

const loading = ref()

let refreshInterval;

const fetchData = async () => {
  loading.value = true
  try {
    const response = await api.get(`/admin/health`);
    collectionsByDpt.value = response.data
    loading.value = false
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des états des collections.", color: "red", position: "bottom", timeout: 2500 })
    loading.value = false
  }
}

onMounted(async () => {
  fetchData()
  clearInterval(refreshInterval)
  refreshInterval = setInterval(() => {
    fetchData()
  }, 90000)
})

onUnmounted(() => {
  clearInterval(refreshInterval);
});

</script>

<style scoped>
.wrapper {
  display: flex;
  justify-content: center;
  flex-direction: column;
  gap: 1em;
  width: 70%;
  margin: 0 auto;
  height: 100%;
}

.skeletons-container {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  margin: 0 auto;
  gap: 1em;
  height: 10%;
}

.container {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  margin: 10px auto;
  gap: 1em;
  height: 10%;
}

.header-skeleton {
  display: flex;
  align-items: center;
  gap: 1em;
  /* padding: 0 2em; */
}

.header {
  display: flex;
  align-items: center;
  gap: 1em;
  padding: 0 2em;
  color: var(--sad-nightblue);
}

.header h3 {
  margin: 5px;
  font-size: clamp(1.5em, 3vw, 2em);
  font-weight: 500;
}

.actions-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1em;
  width: 100%;
}

.health-card {
  flex: 0 1 auto;
  width: 300px;
  height: 75px;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--sad-nightblue);

}

.health-card-body {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  height: 100%;
  flex: 1;
}

.health-color {
  width: 15px;
  height: 100%;
  border-top-left-radius: 15px;
  border-bottom-left-radius: 15px;
}



.q-separator {
  flex: 1;
  background: var(--sad-nightblue);
}

@media screen and (max-width: 1200px) {
  .wrapper {
    width: 80%;
  }
}

@media screen and (max-width: 750px) {
  .wrapper {
    width: 100%;
  }
}
</style>
