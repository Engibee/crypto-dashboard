<script setup>
import { ref, watch, onMounted, onUnmounted } from "vue";
import InfoTooltip from "../ui/InfoTooltip.vue";
import { SymbolStore } from "../../stores/symbolStore";
import { useWebSocket } from "../../composables/useWebSocket";

// Use the same composable with default 'data' endpoint
const { data, isConnected, isLoading, error, connect, disconnect } = useWebSocket("wss://crypto-dashboard-975o.onrender.com/ws/data", "data");
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

// Properly disconnect when component is unmounted
onUnmounted(() => {
  console.log("Technical Analysis component unmounted, disconnecting WebSocket");
  disconnect();
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
      <p>{{ data[90]["timestamp"] }}</p>
      <p><InfoTooltip message="The average price of the asset over a specific period of time."/>Simple Moving Average: {{ data[90]["SMA"] }}</p>
      <p><InfoTooltip message="The average price of the asset over a specific period of time, but with more weight given to recent prices."/>Exponential Moving Average: {{ data[90]["EMA"] }}</p>
      <p><InfoTooltip message="A momentum oscillator that measures the speed and change of price movements."/>Relative Strength Index: {{ data[90]["RSI"] }}</p>
      <p><InfoTooltip message="A trend-following momentum indicator that shows the relationship between two moving averages of prices."/>Moving Average Convergence Divergence: {{ data[90]["MACD"] }}</p>
      <p><InfoTooltip message="A moving average of the MACD, used to identify crossovers and divergences."/>MACD Signal: {{ data[90]["MACD_Signal"] }}</p>
      <p><InfoTooltip message="A binary signal (1 or 0) indicating whether the SMA is above the EMA (1) or below (0)." />Signal: {{ data[90]["Signal"] }}</p>
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
