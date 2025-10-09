<script setup>
import { ref, watch, onMounted, onUnmounted } from "vue";
import InfoTooltip from "../ui/InfoTooltip.vue";
import { SymbolStore } from "../../stores/symbolStore";
import { useWebSocket } from "../../composables/useWebSocket";

// Use the same composable with default 'data' endpoint
const { data, isConnected, isLoading, error, connect, disconnect } = useWebSocket(import.meta.env.VITE_API_URL, "data");
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
  <div class="bg-[#000000] text-[#00ff00] flex flex-col justify-center items-center w-full h-full">
    <h1>Technical Analysis: {{ currentSymbol }}</h1>
    <div v-if="error">
      <p class="text-[#ff0000]">Error: {{ error.message }}</p>
    </div>
    <div v-else-if="isLoading && !data.length">
      <p>Loading data...</p>
    </div>
    <div v-else-if="data.length > 0" class="text-center">
      <p>{{ data[0]["timestamp"] }}</p>
      <p><InfoTooltip message="The average price of the asset over a specific period of time."/>Simple Moving Average: {{ data[0]["SMA"].toLocaleString() }}</p>
      <p><InfoTooltip message="The average price of the asset over a specific period of time, but with more weight given to recent prices."/>Exponential Moving Average: {{ data[0]["EMA"].toLocaleString() }}</p>
      <p><InfoTooltip message="A momentum oscillator that measures the speed and change of price movements."/>Relative Strength Index: {{ data[0]["RSI"].toLocaleString() }}</p>
      <p><InfoTooltip message="A trend-following momentum indicator that shows the relationship between two moving averages of prices."/>Moving Average Convergence Divergence: {{ data[0]["MACD"].toLocaleString() }}</p>
      <p><InfoTooltip message="A moving average of the MACD, used to identify crossovers and divergences."/>MACD Signal: {{ data[0]["MACD_Signal"].toLocaleString() }}</p>
      <p><InfoTooltip message="A binary signal (1 or 0) indicating whether the SMA is above the EMA (1) or below (0)." />Signal: {{ data[0]["Signal"] }}</p>
    </div>
    <div v-else>
      <p>Loading data...</p>
    </div>
  </div>
</template>