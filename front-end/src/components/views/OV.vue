<script setup>
import { ref, watch, onMounted, onUnmounted } from "vue";
import InfoTooltip from "../ui/InfoTooltip.vue";
import { SymbolStore } from "../../stores/symbolStore";
import { useLivePrice } from "../../composables/useLivePrice";

const currentSymbol = ref(SymbolStore.value);
const todayStats = ref(null);
const isLoadingStats = ref(true);
const statsError = ref(null);

// Use live price WebSocket
const { price: livePrice, isConnected, error: priceError, connect, disconnect } = 
  useLivePrice("wss://crypto-dashboard-975o.onrender.com");

// Fetch today's stats from REST API
async function fetchTodayStats(symbol) {
  try {
    isLoadingStats.value = true;
    statsError.value = null;
    
    const response = await fetch(`https://crypto-dashboard-975o.onrender.com/api/today-stats/${symbol}USDT`);
    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }
    
    const data = await response.json();
    todayStats.value = data;
    isLoadingStats.value = false;
  } catch (err) {
    console.error('Error fetching today stats:', err);
    statsError.value = err;
    isLoadingStats.value = false;
  }
}

// Watch for symbol changes
watch(
  () => SymbolStore.value,
  (newSymbol) => {
    if (newSymbol !== currentSymbol.value) {
      currentSymbol.value = newSymbol;
      
      // Connect to live price and fetch today's stats
      connect(newSymbol);
      fetchTodayStats(newSymbol);
    }
  },
  { immediate: true }
);

onMounted(() => {
  connect(currentSymbol.value);
  fetchTodayStats(currentSymbol.value);
});

onUnmounted(() => {
  console.log("Overview component unmounted, disconnecting WebSocket");
  disconnect();
});
</script>

<template>
  <div class="main">
    <h1>Overview: {{ currentSymbol }}</h1>

    <div v-if="priceError || statsError" class="error-container">
      <p class="error" v-if="priceError">Price Error: {{ priceError.message }}</p>
      <p class="error" v-if="statsError">Stats Error: {{ statsError.message }}</p>
    </div>

    <div v-else-if="isLoadingStats" class="loading-container">
      <p>Loading market data...</p>
    </div>

    <div v-else-if="todayStats" class="data-container">
      <div class="live-price">
        <h2>Live Price</h2>
        <p class="price-display">
          <InfoTooltip message="Real-time price from Binance WebSocket"/>
          ${{ livePrice.toFixed(2) }}
          <span class="connection-status" :class="{ connected: isConnected }">
            {{ isConnected ? '🟢' : '🔴' }}
          </span>
        </p>
      </div>
      
      <div class="today-stats">
        <h2>Today's Statistics</h2>
        <p><InfoTooltip message="The price at the beginning of today's trading session"/>Open: ${{ todayStats.open.toFixed(2) }}</p>
        <p><InfoTooltip message="The highest price reached today"/>High: ${{ todayStats.high.toFixed(2) }}</p>
        <p><InfoTooltip message="The lowest price reached today"/>Low: ${{ todayStats.low.toFixed(2) }}</p>
        <p><InfoTooltip message="Total trading volume for today"/>Volume: {{ todayStats.volume.toFixed(2) }}</p>
        <p><InfoTooltip message="Price change from yesterday's close"/>Change: ${{ todayStats.price_change.toFixed(2) }} ({{ todayStats.price_change_percent.toFixed(2) }}%)</p>
        <p class="timestamp">Last updated: {{ todayStats.timestamp }}</p>
      </div>
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

.live-price {
  margin-bottom: 2rem;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
}

.price-display {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
}

.connection-status {
  font-size: 1rem;
  margin-left: 0.5rem;
}

.today-stats {
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.timestamp {
  font-size: 0.8rem;
  color: #666;
  margin-top: 1rem;
}
</style>
