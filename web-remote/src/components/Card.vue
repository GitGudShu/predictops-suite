<template>
  <div class="card" :style="{ height: height, flex: ` ${flex} 0 40%` }">
    <div class="card-header">
      <q-icon :name="icon" :rotation="iconRotation ? iconRotation : null"></q-icon>
      <h2 class="header-text">{{ headerText }}</h2>
      <q-icon :name="rightIcon" class="additional-icon" :style="{cursor : rightIconClickable ? 'pointer' : 'auto'}" size="xs" @click="handleIconClick"></q-icon>
    </div>
    <div class="card-body" :style="{ height: bodyHeight }">
      <slot name="body"></slot>
    </div>

  </div>
</template>

<script setup>
import { onMounted, nextTick } from 'vue';
import { adjustFontSize } from 'src/utils/textUtils'
const props = defineProps({
  headerText: String,
  icon: String,
  iconRotation: String,
  rightIcon: String,
  height: String,
  bodyHeight: String,
  rightIconClickable: Boolean,
  flex: {
    type: String,
    default: '1'
  }
})

const emit = defineEmits(['iconClicked']);



const handleIconClick = () => {
  emit('iconClicked')
}

onMounted(() => {
  const headerTexts = document.querySelectorAll('.header-text');
  if (headerTexts) {
    headerTexts.forEach(element => {
      adjustFontSize(element)
    })
  }
})

</script>


<style>
.card {
  background-color: white;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 100%;
  gap: 5px;
  min-height: 220px;
  box-shadow: 0px 3px 24px 0px var(--sad-lightgray);
  /* min-width: 300px; */
  /* flex: 0 0 40%; */
  border-radius: 15px;
}

.card-header {
  /* color: white; */
  background: #e9eaeb72;
  color: var(--sad-nightblue);
  padding: 0 0.75rem;
  display: flex;
  align-items: center;
  gap: 1em;
  border-top-right-radius: inherit;
  border-top-left-radius: inherit;
}

.card-header h2,
.card-header .header-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
  font-weight: 500;
  font-size: clamp(1rem, 2vw, 1.35rem);
}

.card-header i {
  font-weight: 500;
  font-size: clamp(1rem, 2vw, 2rem);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
}

.card-header .additional-icon {
  flex-shrink: 0;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1em;
  position: relative;
}

@media screen and (min-width: 2000px) {
  .card-header {
    height: 150px;
  }
  .card-header h2, .card-header .header-text {
    font-size: clamp(0.75rem, 15vw, 10rem);
  }
  .card-header i {
    font-size: clamp(0.75rem, 10vw, 5rem);
  }

}

</style>
