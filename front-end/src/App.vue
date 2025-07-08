<script setup>
import TechnicalAnalysis from './components/TA.vue'
</script>

<template>
  <div class="sidebar"><button class="technical analysis">Technical Analysis</button></div>
  <div class="content"><TechnicalAnalysis></TechnicalAnalysis></div>
</template>

<style scoped>
.sidebar {
  width: 15vw;
  height: 100vh;
  background-color: #f0f0f0;
  position: fixed;
  top: 0;
  left: 0;
}

.content {
  width: 85vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 15vw;
}
</style>
