<script setup>
import { ref, watch, onMounted } from "vue";
import { SymbolStore } from "../stores/symbolStore";
import { useWebSocket } from "../composables/useWebSocket";

// Use the same composable with default 'data' endpoint
const { data, isConnected, isLoading, error, connect } = useWebSocket("wss://crypto-dashboard-975o.onrender.com/ws/data", "data");
const currentSymbol = ref(SymbolStore.value);

// Watch for symbol changes
watch(
  () => SymbolStore.value,
  (newSymbol) => {
    if (newSymbol !== currentSymbol.value) {
      currentSymbol.value = newSymbol;
      
      // Start a new connection after a small delay
      setTimeout(() => {
        connect(newSymbol, { days: 90 });
      }, 100);
    }
  },
  { immediate: true }
);

onMounted(() => {
  // Ensure initial connection is established
  connect(currentSymbol.value, { days: 90 });
});
</script>

<template>
  <div class="main">
    <div v-if="error">
      <p class="error">Error: {{ error.message }}</p>
    </div>
    <div v-else-if="isLoading && !data.length">
      <p>Loading data...</p>
    </div>
    <div v-else-if="data.length > 90">
      <p>Timestamp: {{ data[90]["timestamp"] }}</p>
      <p>Simple Moving Average: {{ data[90]["SMA"] }}</p>
      <p>Exponential Moving Average: {{ data[90]["EMA"] }}</p>
      <p>Relative Strength Index: {{ data[90]["RSI"] }}</p>
      <p>Moving Average Convergence Divergence: {{ data[90]["MACD"] }}</p>
      <p>MACD Signal: {{ data[90]["MACD_Signal"] }}</p>
      <p>Signal: {{ data[90]["Signal"] }}</p>
    </div>
    <div v-else>
      <p>Loading data...</p>
    </div>
  </div>
</template>

<style scoped>
.main {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #000;
  color: #00ff00;
  height: 100vh;
  width: 85vw;
  font-family: "Courier New", Courier, monospace;
}

.error {
  color: #ff0000;
}
</style>
