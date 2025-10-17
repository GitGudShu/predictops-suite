<template>
  <button :style="{ backgroundColor: bgColor, color: txtColor }" :class="btnSize" :type="btnType">
    <q-icon :name="leftIcon" :rotation="leftIconRotation ? leftIconRotation : null" :size="leftIconSize"
      v-if="leftIcon && !loading" />
    <span v-if="!loading" v-show="btnText">{{ btnText }}</span>
    <q-spinner v-if="loading" color="white" />
    <q-icon :name="rightIcon" :class="rightIconRotation ? rightIconRotation : ''" :size="rightIconSize"
      v-if="rightIcon && !loading" />
  </button>
</template>

<script setup>
const props = defineProps({
  loading: Boolean,
  leftIcon: String,
  rightIcon: String,
  leftIconSize: String,
  rightIconSize: String,
  leftIconRotation: String,
  rightIconRotation: String,
  btnText: String,
  bgColor: String,
  txtColor: String,
  btnSize: String,
  btnType: String,
})

</script>

<style scoped>
.xs-btn {
  min-width: 40px;
  gap: 5px;
}

.sm-btn {
  min-width: 100px;
  gap: 8px;
}

.md-btn {
  min-width: 150px;
  height: 40px;
  font-size: 1rem;
  gap: 12px;

}

.lg-btn {
  min-width: 200px;
  height: 50px;
  font-size: 1.2rem;
  gap: 16px;
}

.xl-btn {
  min-width: 250px;
  height: 60px;
  font-size: 1.4rem;
  gap: 24px;
}

button {
  padding: 0.5rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  outline: none;
  border: none;
  margin: auto;
  min-width: fit-content;
  white-space: nowrap;
  text-overflow: ellipsis;
  text-align: center;
  line-height: 15px;
  border-radius: 4px;
  font-family: 'Roboto', sans-serif;
}

button i {
  -webkit-transition: all .4s;
  /* Safari */
  transition: all .4s;
}
</style>
