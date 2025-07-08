<script setup>
import { ref, onMounted, watch } from 'vue';

const data = ref([]);
const selectedCoin = ref('BTC');
let intervalId = null;

watch(selectedCoin, (newSymbol) => {
  fetchData(newSymbol);
});

async function fetchData(symbol) {
  const response = await fetch(`https://crypto-dashboard-975o.onrender.com/api/data/${symbol}USDT?days=90`);
  const json = await response.json();
  data.value = json;
}

onMounted(async () => {
  await fetchData(selectedCoin.value);

  intervalId = setInterval(() => {
    fetchData(selectedCoin.value);
  }, 1000);

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
