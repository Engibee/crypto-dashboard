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
  <div class="bg-[#000000] text-[#00ff00] flex flex-col justify-center items-center text-center w-full h-full">
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
          ${{ livePrice.toLocaleString() }}
          <span class="connection-status" :class="{ connected: isConnected }">
            {{ isConnected ? '🟢' : '🔴' }}
          </span>
        </p>
      </div>
      
      <div class="today-stats">
        <h2>Today's Statistics</h2>
        <p><InfoTooltip message="The price at the beginning of today's trading session"/>Open: ${{ todayStats.open.toLocaleString() }}</p>
        <p><InfoTooltip message="The highest price reached today"/>High: ${{ todayStats.high.toLocaleString() }}</p>
        <p><InfoTooltip message="The lowest price reached today"/>Low: ${{ todayStats.low.toLocaleString() }}</p>
        <p><InfoTooltip message="Total trading volume for today"/>Volume: {{ todayStats.volume.toLocaleString() }}</p>
        <p><InfoTooltip message="Price change from yesterday's close"/>Change: ${{ todayStats.price_change.toLocaleString() }} ({{ todayStats.price_change_percent.toLocaleString() }}%)</p>
        <p class="timestamp">Last updated: {{ todayStats.timestamp }}</p>
      </div>
    </div>
  </div>
</template>