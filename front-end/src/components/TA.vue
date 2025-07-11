<script setup>
import { ref, onMounted, watch, onUnmounted } from "vue";
import { SymbolStore } from "../stores/symbolStore";

const data = ref([]);
let socket = null;
let isConnecting = false;

watch(SymbolStore, (newSymbol) => {
  if (!isConnecting) {
    connectWebSocket(newSymbol);
  }
}, { immediate: true });

async function connectWebSocket(symbol) {
  try {
    isConnecting = true;
    
    // Close existing connection if any
    if (socket) {
      socket.close();
      socket = null;
    }

    console.log(`Connecting to WebSocket for ${symbol}USDT...`);
    
    // Create new WebSocket connection
    socket = new WebSocket(
      `wss://crypto-dashboard-975o.onrender.com/ws/data?ticker=${symbol}USDT&days=90`
    );

    // Set up event handlers
    socket.onopen = () => {
      console.log("WebSocket connection established successfully");
      isConnecting = false;
    };

    socket.onmessage = (event) => {
      try {
        const json = JSON.parse(event.data);
        data.value = json;
      } catch (parseError) {
        console.error("Error parsing WebSocket data:", parseError);
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    socket.onclose = (event) => {
      console.log(`WebSocket closed: ${event.code} ${event.reason}`);
      isConnecting = false;
      
      // If connection was closed unexpectedly and not during component cleanup
      if (event.code !== 1000 && event.code !== 1001) {
        fallbackToREST(symbol);
      }
    };

    // Wait for connection with timeout
    const connectionTimeout = 8000; // 8 seconds
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        if (socket && socket.readyState !== WebSocket.OPEN) {
          reject(new Error("WebSocket connection timeout"));
        }
      }, connectionTimeout);

      socket.addEventListener('open', () => {
        clearTimeout(timer);
        resolve();
      });

      socket.addEventListener('error', () => {
        clearTimeout(timer);
        reject(new Error("Failed to connect to WebSocket"));
      });
    });
  } catch (error) {
    console.error("WebSocket connection failed:", error);
    isConnecting = false;
    fallbackToREST(symbol);
  }
}

async function fallbackToREST(symbol) {
  console.log("Falling back to REST API...");
  try {
    const response = await fetch(`https://crypto-dashboard-975o.onrender.com/api/data/${symbol}USDT?days=90`);
    const json = await response.json();
    data.value = json;
  } catch (fallbackError) {
    console.error("Fallback API request also failed:", fallbackError);
  }
}

onMounted(async () => {
  await connectWebSocket(SymbolStore.value);
});

// Clean up WebSocket connection when component is unmounted
onUnmounted(() => {
  if (socket) {
    socket.close();
    socket = null;
  }
});
</script>

<template>
  <div class="main">
    <div v-if="data.length > 90">
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
</style>
