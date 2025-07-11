import { ref, onUnmounted } from 'vue';

export function useWebSocket(baseUrl) {
  const data = ref([]);
  const isConnected = ref(false);
  const isLoading = ref(true);
  const error = ref(null);
  
  let socket = null;
  let isConnecting = false;
  let connectionAttempts = 0;
  const MAX_ATTEMPTS = 3;
  let currentSymbol = null;
  let reconnectTimeout = null;

  async function connect(symbol, options = { days: 90 }) {
    // Avoid multiple simultaneous connection attempts
    if (isConnecting) return;
    
    // If already connected to the same symbol, don't reconnect
    if (isConnected.value && symbol === currentSymbol) {
      return;
    }
    
    try {
      isConnecting = true;
      isLoading.value = true;
      error.value = null;
      connectionAttempts++;
      currentSymbol = symbol;
      
      // Close existing connection
      if (socket) {
        socket.close();
        socket = null;
      }
      
      console.log(`Attempt ${connectionAttempts}: Connecting to WebSocket for ${symbol}USDT...`);
      
      // Create new WebSocket connection
      const url = `${baseUrl}?ticker=${symbol}USDT&days=${options.days}`;
      socket = new WebSocket(url);

      // Configure event handlers
      socket.onopen = () => {
        console.log("WebSocket connection established successfully!");
        isConnecting = false;
        isConnected.value = true;
        
        // Don't disable isLoading here - wait for data
        connectionAttempts = 0; // Reset counter after success
      };

      socket.onmessage = (event) => {
        try {
          const json = JSON.parse(event.data);
          
          // Check if data is valid
          if (Array.isArray(json) && json.length > 0) {
            console.log(`Received ${json.length} data records via WebSocket`);
            data.value = json;
            isLoading.value = false; // Only disable loading when data arrives
          } else {
            console.warn("Received unexpected WebSocket data format:", json);
          }
        } catch (parseError) {
          console.error("Error parsing WebSocket data:", parseError);
          error.value = parseError;
        }
      };

      socket.onerror = (err) => {
        console.error("WebSocket error:", err);
        error.value = new Error("WebSocket connection error");
        
        // If error occurs, try fallback
        if (connectionAttempts >= MAX_ATTEMPTS) {
          fallbackToREST(symbol, options);
        }
      };

      socket.onclose = (event) => {
        console.log(`WebSocket closed: ${event.code} ${event.reason}`);
        isConnecting = false;
        isConnected.value = false;
        
        // Clear any existing reconnect timeout
        if (reconnectTimeout) {
          clearTimeout(reconnectTimeout);
          reconnectTimeout = null;
        }
        
        // If connection was closed unexpectedly and we're on the current symbol
        if (event.code !== 1000 && event.code !== 1001 && symbol === currentSymbol) {
          if (connectionAttempts < MAX_ATTEMPTS) {
            console.log(`Attempting to reconnect (${connectionAttempts}/${MAX_ATTEMPTS})...`);
            reconnectTimeout = setTimeout(() => connect(symbol, options), 1000); // Wait 1 second before trying again
          } else {
            console.log("Maximum number of attempts reached, using REST API as fallback");
            fallbackToREST(symbol, options);
          }
        }
      };

      // Add data timeout
      setTimeout(() => {
        if (isLoading.value && symbol === currentSymbol) {
          console.log("Timeout waiting for WebSocket data, trying REST fallback");
          fallbackToREST(symbol, options);
        }
      }, 5000); // 5 second timeout for receiving data
    } catch (err) {
      console.error("WebSocket connection failure:", err);
      isConnecting = false;
      isLoading.value = false;
      error.value = err;
      
      // Only try to reconnect if we're still on the same symbol
      if (connectionAttempts < MAX_ATTEMPTS && symbol === currentSymbol) {
        console.log(`Attempting to reconnect (${connectionAttempts}/${MAX_ATTEMPTS})...`);
        reconnectTimeout = setTimeout(() => connect(symbol, options), 1000); // Wait 1 second before trying again
      } else if (symbol === currentSymbol) {
        fallbackToREST(symbol, options);
      }
    }
  }

  async function fallbackToREST(symbol, options = { days: 90 }) {
    console.log("Usando API REST como fallback...");
    try {
      isLoading.value = true;
      error.value = null;
      
      const apiUrl = baseUrl.replace('ws', 'api').replace('wss', 'https');
      const response = await fetch(`${apiUrl.split('/ws')[0]}/api/data/${symbol}USDT?days=${options.days}`, {
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
      if (Array.isArray(json) && json.length > 0) {
        console.log(`Recebidos ${json.length} registros de dados via REST`);
        data.value = json;
        isLoading.value = false;
      } else {
        console.warn("Recebidos dados REST em formato inesperado:", json);
        error.value = new Error("Formato de dados inesperado");
      }
    } catch (fallbackError) {
      console.error("Requisição de fallback para API também falhou:", fallbackError);
      error.value = fallbackError;
      isLoading.value = false;
    }
  }

  function disconnect() {
    if (socket) {
      socket.close();
      socket = null;
      isConnected.value = false;
    }
  }

  // Limpar conexão quando o componente for desmontado
  onUnmounted(() => {
    disconnect();
  });

  return {
    data,
    isConnected,
    isLoading,
    error,
    connect,
    disconnect
  };
}

