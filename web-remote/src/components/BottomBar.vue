<template>
  <div class="bottom-bar">
    <div v-for="page in pages" :key="page.path" class="bottom-bar-link">
      <router-link v-if="!(page.path == 'fiabilite' && (decodedUser.role == 'user' && decodedUser.dpt == '01'))" :to="'/' + page.path" active-class="bottom-bar-active" exact>
        <q-item>
          <q-item-section>
            <div class="bottom-bar-icon">
              <q-badge v-if="pagesWithAlert[page.path]" color="orange" rounded floating
                :style="{ width: '5px', height: '5px', minHeight: 'unset', padding: '0', top: '4px', right: '4px' }"></q-badge>
              <q-icon :name="page.icon" size="18px"></q-icon>
            </div>
            <!-- <span class="bottom-bar-text">{{ page.name }}</span> -->
          </q-item-section>
        </q-item>
      </router-link>

    </div>
    <q-icon name="fa-solid fa-caret-left" class="bottom-bar-link scroll-left" size="14px" v-if="showScrollLeftArrow"
      @click="scrollLeft"></q-icon>
    <q-icon name="fa-solid fa-caret-right" class="bottom-bar-link scroll-right" size="14px" v-if="showScrollRightArrow"
      @click="scrollRight"></q-icon>
  </div>
</template>


<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { api } from 'boot/axios'
import { notifyUser } from "src/utils/notifyUser";
import { useRoute } from 'vue-router';
import { Cookies } from "quasar";
import { Base64 } from 'js-base64';

const decodedUser = computed(() => {
  return JSON.parse(Base64.decode(Cookies.get('user')))
})
const location = useRoute();

const dpt = computed(() => { return localStorage.getItem("dpt") || location.params.dpt })
const pages = ref([])

const subpageMenus = ref({})
const pagesWithAlert = ref({})

const showScrollRightArrow = ref();
const showScrollLeftArrow = ref();

let refreshInterval;
const fetchAlertsForAllPages = async () => {
  try {
    const response = await api.get(`/data/pages-alerts?dpt=${dpt.value}`);
    const alertsData = response.data;
    const alerts = {};

    // Assuming response.data is an array of alert objects
    alertsData.forEach(alert => {
      alerts[alert.page] = alert.has_alert;
    });

    // Update pagesWithAlert with the new alerts
    pagesWithAlert.value = alerts;
  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des alertes de pages.", color: "red", position: "bottom", timeout: 2500 })
  }
};

const getPages = async () => {
  const response = await api.get(`/data/pages?dpt=${dpt.value}`);
  pages.value = response.data[0].pages;
}

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

const checkScrollArrows = () => {
  const element = document.querySelector('.bottom-bar');
  if (!element) return;
  const scrollPosition = element.scrollLeft;
  const scrollEnd = element.scrollWidth - element.clientWidth;

  showScrollRightArrow.value = scrollPosition < scrollEnd;
  showScrollLeftArrow.value = scrollPosition > 0;
};

const scrollRight = () => {
  const element = document.querySelector('.bottom-bar');
  const scrollEnd = element.scrollWidth - element.clientWidth;
  const scrollAmount = Math.min(scrollEnd - element.scrollLeft, element.clientWidth * 0.7); // Dynamic scroll value

  element.scrollBy({ left: scrollAmount, behavior: 'smooth' });

  // After scrolling, recheck if the arrows should be displayed
  setTimeout(checkScrollArrows, 300); // Delay to account for smooth scroll behavior
};

const scrollLeft = () => {
  const element = document.querySelector('.bottom-bar');
  const scrollAmount = Math.min(element.scrollLeft, element.clientWidth * 0.7); // Dynamic scroll value

  element.scrollBy({ left: -scrollAmount, behavior: 'smooth' });

  // After scrolling, recheck if the arrows should be displayed
  setTimeout(checkScrollArrows, 300); // Delay to account for smooth scroll behavior
};

const handleScroll = () => {
  checkScrollArrows();
};

const isOverflown = (element) => {
  return element.scrollHeight > element.clientHeight || element.scrollWidth > element.clientWidth;
};

onMounted(async () => {
  clearInterval(refreshInterval)
  await getPages()
  await fetchAlertsForAllPages()
  const element = document.querySelector('.bottom-bar');

  refreshInterval = setInterval(async () => {
    await getPages()
    await fetchAlertsForAllPages()
  }, 300000)

  if (isOverflown(element)) {
    checkScrollArrows();
  }
  element.addEventListener('scroll', handleScroll);
  window.addEventListener('resize', checkScrollArrows);
})

onUnmounted(() => {
  // const element = document.querySelector('.bottom-bar');
  // element.removeEventListener('scroll', handleScroll);
  // window.removeEventListener('resize', checkScrollArrows);
  clearInterval(refreshInterval);
});
</script>

<style scoped>
.bottom-bar {
  height: 50px;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  padding: 0;
  overflow-x: scroll;
  overflow-y: hidden;
  -ms-overflow-style: none;
  /* Internet Explorer 10+ */
  scrollbar-width: none;
}

.bottom-bar-link {
  position: relative;
  font-size: clamp(1rem, 2vw, 1rem);
  width: 100%;
  height: 100%;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1 0 15px;
  white-space: nowrap;
  cursor: pointer;
  transition: color 0.3s ease-in;
  color: var(--sad-nightblue);
  text-align: center;
}

.bottom-bar-text {
  white-space: nowrap;
  pointer-events: none;
  text-overflow: ellipsis;
  text-align: center;
  font-size: 9px;
}

.open-subpages-icon {
  position: absolute;
  top: 0px;
  transform: translateX(-6px);
  transition: color 0.3s ease-in;
}

.subpages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-top: 10px;
  width: 100%;
}

.bottom-bar-link i {
  font-size: clamp(1rem, 5vw, 1.75rem);
}

.scroll-right {
  position: absolute;
  width: 20px;
  height: 80%;
  right: 0;
  background: #ffffffa2;
  backdrop-filter: blur(2px);
}

.scroll-left {
  position: absolute;
  width: 20px;
  height: 80%;
  left: 0;
  background: #ffffffa2;
  backdrop-filter: blur(2px);
}

.bottom-bar-active {
  color: var(--sad-orange);
  border-radius: 0;
}

.bottom-bar-link:hover,
.bottom-bar-active {
  color: var(--sad-orange);
  border-radius: 0;
}

.bottom-bar-link p {
  margin: 0;
  pointer-events: none;
  font-size: 10px;
  font-weight: 500;
  white-space: wrap;
}
</style>
