<script setup>
import TechnicalAnalysis from "./components/TA.vue";
import Overview from "./components/OV.vue";
import { SymbolStore } from "./stores/symbolStore";
import { ref } from "vue";

const selectedSymbol = ref("BTC");
const selectedView = ref("ta");

function onSymbolChange() {
  SymbolStore.value = selectedSymbol.value;
}
</script>

<template>
  <div class="sidebar">
    <select
      class="symbol-select"
      @change="onSymbolChange"
      v-model="selectedSymbol"
    >
      <option value="BTC">Bitcoin</option>
      <option value="ETH">Ethereum</option>
    </select>
    <div class="views">
      <button class="overview" @click="selectedView = 'ov'">Overview</button>
      <button class="technical-analysis" @click="selectedView = 'ta'">Technical Analysis</button>
    </div>
  </div>
  <div class="content">
    <TechnicalAnalysis v-if="selectedView === 'ta'" />
    <Overview v-if="selectedView === 'ov'" />
    <RawData v-if="selectedView === 'raw'" />
  </div>
</template>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
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

.symbol-select {
  height: 7vh;
  width: 100%;
  border-radius: 0;
}

.views {
  margin: 1vh 0 0 0;
}

.button {
  width: 1%;
}

.overview {
  height: 7vh;
  width: 100%;
  border-radius: 0;
}

.technical-analysis {
  height: 7vh;
  width: 100%;
  border-radius: 0;
  margin: 1vh 0 0 0;
}
</style>


