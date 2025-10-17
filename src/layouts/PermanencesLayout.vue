<template>
  <q-layout view="hHh lpR fFf">
    <q-header>
      <Nav />
    </q-header>

    <q-drawer side="left" show-if-above :width="75" style="max-height: calc(100vh - 72px);">
      <q-scroll-area class="fit">
        <q-list class="sidebar">
          <div v-for="page in pages" :key="page.path">
            <router-link v-if="!(page.path == 'fiabilite' && (decodedUser.role == 'user' && decodedUser.dpt == '01'))"
              :to="'/' + page.path" class="sidebar-link" active-class="sidebar-active" exact>
              <q-tooltip anchor="center right" self="center left" :offset="[10, 10]" class="tooltip">
                {{ page.name }}
              </q-tooltip>
              <q-item>
                <q-item-section>
                  <q-badge v-if="pagesWithAlert[page.path]" color="orange" rounded floating
                    :style="{ width: '7px', height: '7px', minHeight: 'unset', padding: '0', top: '4px', right: '4px' }"></q-badge>
                  <q-icon :name="page.icon" size="20px"></q-icon>
                </q-item-section>
              </q-item>
            </router-link>
          </div>

        </q-list>
      </q-scroll-area>
      <div class="sdis-logo-container">
        <img :src="`${publicPath}logo-${dpt}.png`" class="sdis-logo" />
      </div>
    </q-drawer>

    <q-page-container>
      <div class="page-navigation">
        <template v-for="page in pages" :key="page.path">
          <router-link v-for="subpage in page.subpages" v-if="page.subpages" :key="subpage.path"
            :to="'/permanences/' + subpage.path" class="page-navigation-link" active-class="page-navigation-active" exact> {{
              subpage.name }}</router-link>
        </template>
      </div>
      <router-view v-slot="{ Component }">
        <transition :name="transitionName" @before-enter="addNoScrollbarStyle" @after-enter="removeNoScrollbarStyle"
          @before-leave="addNoScrollbarStyle" @after-leave="removeNoScrollbarStyle">
          <component :is="Component" />
        </transition>
      </router-view>
    </q-page-container>

    <q-footer v-if="isMobile">
      <BottomBar />
    </q-footer>
  </q-layout>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount, onUnmounted, provide } from 'vue';
import Nav from 'src/components/Nav.vue';
import { api } from 'boot/axios';
import BottomBar from 'src/components/BottomBar.vue';
import { useRouter, useRoute } from 'vue-router';
import { Cookies } from 'quasar';
import { Base64 } from 'js-base64';

const location = useRoute();

const publicPath = process.env.PUBLIC_PATH || '/predictops/';

const decodedUser = JSON.parse(Base64.decode(Cookies.get('user')));

const dpt = computed(() => localStorage.getItem("dpt") || location.params.dpt);
const pages = ref([]);
const windowWidth = ref(window.innerWidth);
const isMobile = computed(() => windowWidth.value <= 1015);

const subpageMenus = ref({});
const pagesWithAlert = ref({});
let refreshInterval;

const updateWindowWidth = () => {
  windowWidth.value = window.innerWidth;
};

onMounted(async () => {
  window.addEventListener('resize', updateWindowWidth);
  clearInterval(refreshInterval);
  await getPages();
  await fetchAlertsForAllPages();
  refreshInterval = setInterval(async () => {
    await getPages();
    await fetchAlertsForAllPages();
  }, 300000);
});

onUnmounted(() => {
  clearInterval(refreshInterval);
});
onBeforeUnmount(() => {
  window.removeEventListener('resize', updateWindowWidth);
});

const fetchAlertsForAllPages = async () => {
  try {
    const response = await api.get(`/data/pages-alerts?dpt=${dpt.value}`);
    const alertsData = response.data;
    const alerts = {};

    alertsData.forEach(alert => {
      alerts[alert.page] = alert.has_alert;
    });

    pagesWithAlert.value = alerts;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des alertes de pages.", color: "red", position: "bottom", timeout: 2500 })
  }
};

const getPages = async () => {
  const response = await api.get(`/data/pages?dpt=${dpt.value}`);
  pages.value = response.data[0].pages;
};

provide('getPages', getPages);

function addNoScrollbarStyle() {
  const style = document.createElement('style');
  style.id = 'no-scrollbar-style';
  style.innerHTML = `
    ::-webkit-scrollbar {
      display: none;
    }
    * {
      -ms-overflow-style: none;  /* IE and Edge */
      scrollbar-width: none;  /* Firefox */
    }
  `;
  document.head.appendChild(style);
}

function removeNoScrollbarStyle() {
  const style = document.getElementById('no-scrollbar-style');
  if (style) {
    document.head.removeChild(style);
  }
}

const router = useRouter();
const transitionName = ref('');

router.beforeEach((to, from, next) => {
  if (to.path.startsWith('/parametres') && from.path === '/parametres') {
    transitionName.value = 'swipe-right';
  } else if (from.path.startsWith('/parametres') && to.path === '/parametres') {
    transitionName.value = 'swipe-left';
  } else if (!to.path.includes('/parametres') && from.path.includes('/parametres')) {
    transitionName.value = '';
  } else {
    transitionName.value = '';
  }
  next();
});

const handleMouseOver = (page) => {
  if (page.subpages) {
    subpageMenus.value[page.path] = true;
  }
};

const handleSubMenuMouseOver = (page) => {
  subpageMenus.value[page.path] = true;
};

const handleSubMenuMouseLeave = (page) => {
  subpageMenus.value[page.path] = false;
};
</script>

<style scoped>
.sidebar {
  display: flex;
  position: fixed;
  height: calc(100% - 70px);
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  overflow: auto;
  width: 100%;
}

.sidebar-link {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.3s ease-in, color 0.3s ease-in;
  color: #181632;
  margin-top: 5px;
  border-radius: 15px;
  text-align: center;
  width: fit-content;
  position: relative;
}

.sidebar-link:hover,
.sidebar-active {
  background-color: #181632;
  color: white;
  border-radius: 15px;
  width: fit-content;
}

.sidebar-link p {
  margin: 0;
  pointer-events: none;
  font-size: 16px;
  font-weight: 500;
  white-space: pre-line;
}

.page-navigation {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: center;
  overflow: auto;
  min-width: 30%;
  margin: auto;
}

.page-navigation-link {
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  font-weight: bold;
  padding: 15px;
  cursor: pointer;
  transition: background-color 0.3s ease-in, color 0.3s ease-in;
  color: #181632;
  margin-top: 5px;
  border-radius: 15px;
  text-align: center;
  width: fit-content;
  position: relative;
}

.page-navigation-link:hover,
.page-navigation-active {
  background-color: #181632;
  color: white;
  border-radius: 15px;
  width: fit-content;
}


.open-subpages-icon {
  position: absolute;
  right: -2px;
}

.subpages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-top: 10px;
  width: 100%;
}

.sdis-logo-container {
  position: absolute;
  bottom: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 10px;
}

.sdis-logo {
  width: clamp(30px, 75%, 60px);
}

.swipe-left-enter-active,
.swipe-left-leave-active {
  transition: transform 0.3s ease;
}

.swipe-left-enter,
.swipe-left-leave-to {
  transform: translateX(100%);
}

.swipe-right-enter-active,
.swipe-right-leave-active {
  transition: transform 0.3s ease;
}

.swipe-right-enter,
.swipe-right-leave-to {
  transform: translateX(-100%);
}

.disabled-router-link {
  pointer-events: none;
}
</style>
