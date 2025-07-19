<script setup>
import { ref, watch, onMounted, onUnmounted } from "vue";
import InfoTooltip from "../ui/InfoTooltip.vue";
import { SymbolStore } from "../../stores/symbolStore";
import { useWebSocket } from "../../composables/useWebSocket";

// Use the websocket composable with 'raw-data' endpoint
const { data, isConnected, isLoading, error, connect, disconnect } =
  useWebSocket("wss://crypto-dashboard-975o.onrender.com/ws/data", "raw-data");
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
  console.log("Overview component unmounted, disconnecting WebSocket");
  disconnect();
});
</script>

<template>
  <div class="main">
    <h1>Overview: {{ currentSymbol }}</h1>

    <div v-if="error" class="error-container">
      <p class="error">Error: {{ error.message }}</p>
    </div>

    <div v-else-if="isLoading && !data.length" class="loading-container">
      <p>Loading raw price data...</p>
    </div>

    <div v-else-if="data.length >= 90" class="data-container">
      <p>{{ data[90].timestamp }}</p>
      <p><InfoTooltip message="The price at the beginning of the time period."/>Open: {{ parseFloat(data[90].Open).toFixed(2) }}</p>
      <p><InfoTooltip message="The highest price reached during the time period."/>High: {{ parseFloat(data[90].High).toFixed(2) }}</p>
      <p><InfoTooltip message="The lowest price reached during the time period."/>Low: {{ parseFloat(data[90].Low).toFixed(2) }}</p>
      <p><InfoTooltip message="The price at the end of the time period."/>Close: {{ parseFloat(data[90].Close).toFixed(2) }}</p>
      <p><InfoTooltip message="The total amount of the asset traded during the time period."/>Volume: {{ parseFloat(data[90].Volume).toFixed(2) }}</p>
    </div>

    <div v-else class="no-data-container">
      <p>No data available</p>
    </div>
  </div>
</template>

<style scoped>
.main {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #000;
  color: #00ff00;
  height: 100vh;
  width: 85vw;
  font-family: "Courier New", Courier, monospace;
  padding: 20px;
  overflow-y: auto;
}

h1 {
  margin-bottom: 30px;
}

.error {
  color: #ff0000;
}

.data-table {
  width: 90%;
  border-collapse: collapse;
  margin-top: 20px;
  color: #00ff00;
  border: 1px solid #00ff00;
}

.data-table th,
.data-table td {
  border: 1px solid #00ff00;
  padding: 8px;
  text-align: right;
}

.data-table th {
  background-color: #003300;
  text-align: center;
}

.data-table tr:nth-child(even) {
  background-color: #001100;
}

.note {
  font-size: 0.8em;
  color: #00aa00;
  margin-top: 10px;
}

.loading-container,
.error-container,
.no-data-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50vh;
}
</style>
