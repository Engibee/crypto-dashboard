<script setup>
import { ref, onMounted, watch, onUnmounted } from "vue";
import { SymbolStore } from "../stores/symbolStore";

const data = ref([]);
let socket = null;
let isConnecting = false;
let connectionAttempts = 0;
const MAX_ATTEMPTS = 3;
const currentSymbol = ref(SymbolStore.value);

// Usar um único watcher com debounce para evitar múltiplas chamadas
watch(
  () => SymbolStore.value,
  (newSymbol) => {
    if (newSymbol !== currentSymbol.value) {
      console.log(`Símbolo alterado de ${currentSymbol.value} para ${newSymbol}`);
      currentSymbol.value = newSymbol;
      connectionAttempts = 0;
      
      // Cancelar qualquer tentativa de conexão pendente
      isConnecting = false;
      
      // Fechar conexão existente
      if (socket) {
        socket.close();
        socket = null;
      }
      
      // Iniciar nova conexão após um pequeno delay
      setTimeout(() => {
        connectWebSocket(newSymbol);
      }, 100);
    }
  },
  { immediate: true }
);

async function connectWebSocket(symbol) {
  // Evitar múltiplas tentativas simultâneas
  if (isConnecting) return;
  
  try {
    isConnecting = true;
    connectionAttempts++;
    
    console.log(`Tentativa ${connectionAttempts}: Conectando ao WebSocket para ${symbol}USDT...`);
    
    // Criar nova conexão WebSocket
    socket = new WebSocket(
      `wss://crypto-dashboard-975o.onrender.com/ws/data?ticker=${symbol}USDT&days=90`
    );

    // Configurar handlers de eventos
    socket.onopen = () => {
      console.log("Conexão WebSocket estabelecida com sucesso!");
      isConnecting = false;
      connectionAttempts = 0; // Resetar contagem após sucesso
    };

    socket.onmessage = (event) => {
      try {
        const json = JSON.parse(event.data);
        data.value = json;
      } catch (parseError) {
        console.error("Erro ao analisar dados do WebSocket:", parseError);
      }
    };

    socket.onerror = (error) => {
      console.error("Erro no WebSocket:", error);
    };

    socket.onclose = (event) => {
      console.log(`WebSocket fechado: ${event.code} ${event.reason}`);
      isConnecting = false;
      
      // Se a conexão foi fechada inesperadamente e estamos no símbolo atual
      if (event.code !== 1000 && event.code !== 1001 && symbol === currentSymbol.value) {
        if (connectionAttempts < MAX_ATTEMPTS) {
          console.log(`Tentando reconectar (${connectionAttempts}/${MAX_ATTEMPTS})...`);
          setTimeout(() => connectWebSocket(symbol), 1000); // Esperar 1 segundo antes de tentar novamente
        } else {
          console.log("Número máximo de tentativas atingido, usando API REST como fallback");
          fallbackToREST(symbol);
        }
      }
    };

    // Aguardar conexão com timeout
    const connectionTimeout = 5000; // 5 segundos
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        if (socket && socket.readyState !== WebSocket.OPEN) {
          reject(new Error("Timeout na conexão WebSocket"));
        }
      }, connectionTimeout);

      socket.addEventListener('open', () => {
        clearTimeout(timer);
        resolve();
      });

      socket.addEventListener('error', () => {
        clearTimeout(timer);
        reject(new Error("Falha ao conectar ao WebSocket"));
      });
    });
  } catch (error) {
    console.error("Falha na conexão WebSocket:", error);
    isConnecting = false;
    
    // Só tentar reconectar se ainda estivermos no mesmo símbolo
    if (connectionAttempts < MAX_ATTEMPTS && symbol === currentSymbol.value) {
      console.log(`Tentando reconectar (${connectionAttempts}/${MAX_ATTEMPTS})...`);
      setTimeout(() => connectWebSocket(symbol), 1000); // Esperar 1 segundo antes de tentar novamente
    } else if (symbol === currentSymbol.value) {
      fallbackToREST(symbol);
    }
  }
}

async function fallbackToREST(symbol) {
  console.log("Usando API REST como fallback...");
  try {
    const response = await fetch(`https://crypto-dashboard-975o.onrender.com/api/data/${symbol}USDT?days=90`, {
      mode: 'cors',
      credentials: 'omit',
      headers: {
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Erro HTTP: ${response.status}`);
    }
    
    const json = await response.json();
    data.value = json;
  } catch (fallbackError) {
    console.error("Requisição de fallback para API também falhou:", fallbackError);
  }
}

onMounted(() => {
  // A conexão inicial já é tratada pelo watcher com immediate: true
});

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
