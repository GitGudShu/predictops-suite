<template>
  <div class="alert-card" :class="`alert-${alertLevel}`">
    <h6 class="alert-header">{{ alertTitle }}</h6>
    <div class="alert-body" :class="`highlight-${alertLevel}`">
      <slot name="alert-body"></slot>
    </div>
  </div>
</template>

<script setup>

const props = defineProps({
  alertLevel: Number,
  alertTitle: String,
  date: String,
  start: String,
  end: String
})
</script>

<style scoped>
.alert-card {
  color: black;
  border-top: solid 1rem;
  min-height: 100px;
  padding: 1rem;
  display: flex;
  margin: 1em;
  flex-direction: column;
  flex: 1 0 30%;
  gap: 1rem;
  box-shadow: 0px 3px 24px 0px var(--sad-lightgray);
  border-radius: 4px;
}

.alert-card h6 {
  margin: 0;
}

.alert-body {
  width: fit-content;
  padding: 0.25rem;
  font-size: 1rem;
}


.alert-0 {
  border-top-color: var(--sad-green);
}

.alert-1 {
  border-top-color: var(--sad-yellow);
}

.alert-2 {
  border-top-color: var(--sad-orange);
}

.alert-3 {
  border-top-color: var(--sad-red);
}

.highlight-1 {
  background: var(--sad-yellow);
}

.highlight-2 {
  background: var(--sad-orange);
}

.highlight-3 {
  background: var(--sad-red);
  color: white;
}
</style>
