<template>
<router-link :to="path" class="cta-card">
  <div class="cta-card-header">
    <q-icon :name="icon" size="sm" />
    <h3 class="cta-card-title">{{ title }}</h3>
  </div>
  <div class="cta-card-body">
    <slot name="body"></slot>
  </div>
  <div class="cta-card-footer">
    <q-icon :name="arrowIcon" size="lg" />
  </div>
</router-link>
</template>

<script setup>
const props = defineProps({
  path: String,
  icon: String,
  title: String,
  arrowIcon: String
})
</script>

<style scoped>
.cta-card {
  display: flex;
  flex-direction: column;
  padding: 1em;
  height: 200px;
  border-radius: 15px;
  flex: 1 1 fit-content;
  min-width: 200px;
  max-width: 600px;
  color: var(--sad-nightblue);
  overflow: hidden;
  transition: all 0.15s ease;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
  cursor: pointer;
}

.cta-card:hover {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
  transform: translateY(-3px);

}

.cta-card-header {
  display: flex;
  align-items: center;
  gap: 1.5em;
  padding: 0.5em;
}

.cta-card-title {
  font-size: clamp(1em, 1.75vw, 1.5em);
  font-weight: 700;
  margin: 0;

}

.cta-card-body {
  flex: 1;
  padding: 0.5em;
  font-weight: 600;
}

.cta-card-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0.25em;
}
</style>
