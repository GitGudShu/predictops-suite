<template>
  <div class="wrapper" :style="{ minHeight: height }">
    <div class="left-panel">
      <Vue3Lottie :animationData="SiriJSON" :height="siriHeight" :width="siriWidth" />
    </div>
    <div class="news-container">
      <p class="news-item" :style="{ fontSize: fontSize }">{{ currentBreakingNews }}</p>
    </div>
    <q-icon name="more_horiz" size="lg" @click="showAllBreakingNews"
      style="cursor: pointer; margin-right: 5px;"></q-icon>
  </div>
</template>


<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { api } from "boot/axios"
import { notifyUser } from "src/utils/notifyUser"
import { showDialog } from "src/utils/dialogUtil"
import { marked } from 'marked'
import SiriJSON from '/public/siri.json'
import { useRoute } from 'vue-router'

const location = useRoute()

const siriHeight = ref(75)
const siriWidth = ref(75)


const props = defineProps({
  page: String,
  height: String,
  fontSize: String,
  uuid: String,
})

const breakingNews = ref([])
const currentNewsIndex = ref(0)
const currentBreakingNews = ref()
const dpt = computed(() => { return localStorage.getItem("dpt") || location.params.dpt })

let newsCycleInterval, refreshInterval, newsCycleTimeout

function getFormattedNewsItem(newsItem) {
  // Check if the news item contains a category and a pipeline
  if (newsItem.includes(' | ')) {
    // Split the string and return the part after the pipeline
    return newsItem.split(' | ')[1];
  } else if (newsItem.trim() === "Rien à signaler") {
    // Return "Rien à signaler" directly
    return newsItem.trim();
  }
  // Return the original news item if no pipeline is found and it's not "Rien à signaler"
  return newsItem;
}

const formatNewsContentToMarkdown = (contentList) => {
  let formattedContent = [];
  let categories = {};
  let otherMessages = [];

  contentList.forEach(line => {
    if (line.includes(' | ')) {
      const [category, message] = line.split(' | ', 2);
      categories[category] = categories[category] || [];
      categories[category].push(message.trim()); // Add message to category
    } else {
      otherMessages.push(line.trim()); // Collect messages without categories
    }
  });

  Object.keys(categories).forEach(category => {
    formattedContent.push(`#### **${category}**`);
    formattedContent = [...formattedContent, ...categories[category].map(msg => `- ${msg}`)];
  });

  if (otherMessages.length) {
    formattedContent = [...formattedContent, ...otherMessages.map(msg => `- ${msg}`)];
  } else if (contentList.length === 0 || contentList.every(line => line.trim() === "Rien à signaler")) {
    formattedContent.push("### **Rien à signaler**");
  }

  return formattedContent.join("\n");
}

const showAllBreakingNews = () => {
  const markdownContent = formatNewsContentToMarkdown(breakingNews.value);
  const htmlContent = marked(markdownContent); // Convert Markdown to HTML

  showDialog({
    focus: "none",
    style: { width: "90%", maxWidth: "unset !important" },
    dark: true,
    message: htmlContent,
    html: true,
    ok: {
      label: 'OK',
      color: 'secondary',
    },
  });
};
const typeWriterEffect = (text, container, onComplete) => {
  let index = 0;
  const speed = 20;

  const type = () => {
    if (index < text.length) {
      container.innerHTML += text.charAt(index);
      index++;
      setTimeout(type, speed);
    } else if (onComplete) {
      onComplete(); // Callback when typing is complete
    }
  };

  container.innerHTML = ''; // Clear the container before starting
  type(); // Start typing
};

const displayNewsWithTypewriterEffect = (newsItem, container) => {
  typeWriterEffect(newsItem, container, () => {
    // Prepare for the next news item after a delay
    setTimeout(() => {
      currentNewsIndex.value = (currentNewsIndex.value + 1) % breakingNews.value.length;
      const nextNews = getFormattedNewsItem(breakingNews.value[currentNewsIndex.value]);
      displayNewsWithTypewriterEffect(nextNews, container);
    }, 10000); // Delay before the next news item
  });

}
const cycleNews = () => {
  const newsContainer = document.querySelector('.news-item'); // Adjust selector as needed
  if (breakingNews.value.length === 0) {
    // Handle the case where there are no news items
    currentBreakingNews.value = "Rien à signaler";
  }
  // Immediately display the first news item without animation
  if (breakingNews.value.length > 0) {
    let initialNews = getFormattedNewsItem(breakingNews.value[0]);
    newsContainer.innerHTML = initialNews;
    currentNewsIndex.value = 1; // Prepare for the next item
  }

  // Start the typewriter effect for subsequent items after a delay
  if (breakingNews.value.length > 1) {
    setTimeout(() => {
      const nextNews = getFormattedNewsItem(breakingNews.value[currentNewsIndex.value]);
      displayNewsWithTypewriterEffect(nextNews, newsContainer);
    }, 10000); // Delay before starting the typewriter effect
  }
}

const fetchData = async () => {
  try {
    const response = await api.get(`/data/news?dpt=${dpt.value}&page=${props.page}&uuid=${props.uuid}`)
    breakingNews.value = response.data

  } catch (error) {
    notifyUser({ icon: "error", message: "Erreur lors de la récupération des news.", color: "red", position: "bottom", timeout: 2500 })
  }
}


onMounted(() => {
  fetchData().then(() => {
    cycleNews()
  });
  refreshInterval = setInterval(fetchData, 180000)
});

onUnmounted(() => {
  clearInterval(newsCycleInterval)
  clearInterval(refreshInterval)
  clearTimeout(newsCycleTimeout)
});
</script>


<style scoped>
.wrapper {
  position: sticky;
  top: 5px;
  z-index: 1000;
  width: 100%;
  gap: 5px;
  color: var(--sad-nightblue);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  overflow-y: hidden;
  border-radius: 15px;
  background: white;
}

.news-container {
  display: flex;
  align-items: center;
  height: 100%;
  max-width: 100%;
  font-weight: bold;
  white-space: nowrap;
  flex: 1;
  background: white;
  padding: 10px;
}

.news-item {
  height: 100%;
  margin: 0;
  display: grid;
  place-items: center;
  overflow: hidden;
  white-space: pre-line;
  overflow-wrap: break-word;
}
</style>
