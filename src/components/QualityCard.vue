<template>
  <div class="container" :style="{ borderTop: `solid 5px var(--sad-${color})` }">
    <div class="title">
      <q-icon class="title-icon" v-if="titleIcon" :name="titleIcon" size="sm"></q-icon>
      <p class="title-text">{{ title }}</p>
    </div>
    <!-- <span class="color-badge" :class="color"></span> -->
    <div class="content">
      <!-- <p v-if="text" class="text">{{ text }}</p> -->
      <FitText v-if="text" :text="text" :min-font-size="14" :step="1" :grow="true" class="text" />
      <q-icon class="icon" v-if="icon" :name="icon"></q-icon>
    </div>
    <q-icon class="description-icon" v-if="description" name="info" size="xs">
      <q-tooltip anchor="center right" self="center left" :offset="[10, 10]" class="tooltip">
        {{ description }}
      </q-tooltip>
    </q-icon>

  </div>
</template>

<script setup>
import FitText from './FitText.vue';

const props = defineProps({
  titleIcon: String,
  title: String,
  color: String,
  text: [String, Number],
  icon: String,
  description: String,
})
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 5px;
  /* border: var(--sad-nightblue) 1px solid; */
  box-shadow: 0px 3px 24px 0px var(--sad-lightgray);
  /* min-width: 150px; */
  flex: 1 0 20%;
  padding: 5px;
  height: 100px;
  background: white;
  color: var(--sad-nightblue);
  position: relative;
}

.title {
  display: flex;
  align-items: center;
  gap: 3px;
}

.title-text {
  margin: 0;
  white-space: nowrap;
  width: fit-content;
  text-overflow: ellipsis;
}

.color-badge {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  position: absolute;
  right: 0;
  margin-right: 2px;
}

.text {
  width: 100%;
  height: 90%;
}

.content {
  flex: 1;
  display: grid;
  place-items: center;
}

.content i {
  font-size: clamp(1.5rem, 5vw, 3.5rem);
}

.description-icon {
  position: absolute;
  right: 0;
  bottom: 0;
}

.green {
  background: var(--sad-green);
}

.yellow {
  background: var(--sad-yellow);
}

.orange {
  background: var(--sad-orange);
}

.red {
  background: var(--sad-red);
}
</style>
