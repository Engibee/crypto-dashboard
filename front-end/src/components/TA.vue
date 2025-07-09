<script setup>
import { ref, onMounted, watch } from 'vue';

const data = ref([]);
const selectedCoin = ref('BTC');
let socket = null;

watch(selectedCoin, (newSymbol) => {
  connectWebSocket(newSymbol);
});

async function connectWebSocket(symbol) {
  if (socket) {
    socket.close(); // Fecha conexão anterior se houver
  }

  socket = new WebSocket(`ws://https://crypto-dashboard-975o.onrender.com/ws/data?ticker=${symbol}USDT&days=90`);

  socket.onopen = () => {
    console.log("Conectado via WebSocket");
  };

  socket.onmessage = (event) => {
    const json = JSON.parse(event.data);
    data.value = json;
  };

  socket.onerror = (error) => {
    console.error("Erro no WebSocket:", error);
  };

  socket.onclose = () => {
    console.log("WebSocket fechado");
  };
}

onMounted(async () => {
  await connectWebSocket(selectedCoin.value);
});
</script>

<template>
  <div class="main">
    <select v-model="selectedCoin">
      <option value="BTC">Bitcoin</option>
      <option value="ETH">Ethereum</option>
    </select>
    <div v-if="data.length > 90">
      <p>Timestamp: {{ data[90]['timestamp'] }}</p>
      <p>Simple Moving Average: {{ data[90]['SMA'] }}</p>
      <p>Exponential Moving Average: {{ data[90]['EMA'] }}</p>
      <p>Relative Strength Index: {{ data[90]['RSI'] }}</p>
      <p>Moving Average Convergence Divergence: {{ data[90]['MACD'] }}</p>
      <p>MACD Signal: {{ data[90]['MACD_Signal'] }}</p>
      <p>Signal: {{ data[90]['Signal'] }}</p>
    </div>
    <div v-else>
      <p>Loading data...</p>
    </div>
  </div>
</template>

<style scoped>
.main {
  display: flex;
  flex-direction:column;
  align-items: center;
  justify-content: center;
  background-color: #000;
  color: #00FF00;
  height: 100vh;
  width: 85vw;
  font-family: 'Courier New', Courier, monospace;
}
</style>
