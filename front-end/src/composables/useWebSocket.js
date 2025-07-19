import { ref, onUnmounted } from 'vue';

export function useWebSocket(baseUrl, endpoint = 'data') {
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
      currentSymbol = symbol;
      
      // Close existing connection
      if (socket) {
        socket.close();
        socket = null;
      }
      
      console.log(`Attempt ${connectionAttempts}: Connecting to ${endpoint} WebSocket for ${symbol}USDT...`);
      
      // Create new WebSocket connection
      // Use the provided endpoint (data or raw-data)
      const url = `${baseUrl.replace('/data', `/${endpoint}`)}?ticker=${symbol}USDT&days=${options.days}`;
      socket = new WebSocket(url);

      // Configure event handlers
      socket.onopen = () => {
        console.log(`${endpoint} WebSocket connection established successfully!`);
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
            console.log(`Received ${json.length} ${endpoint} records via WebSocket`);
            data.value = json;
            isLoading.value = false; // Only disable loading when data arrives
          } else {
            console.warn(`Received unexpected ${endpoint} WebSocket data format:`, json);
          }
        } catch (parseError) {
          console.error(`Error parsing ${endpoint} WebSocket data:`, parseError);
          error.value = parseError;
        }
      };

      socket.onerror = (err) => {
        console.error(`${endpoint} WebSocket error:`, err);
        error.value = new Error("WebSocket connection error");
        isConnecting = false;
        connectionAttempts++;
        
        
        // If error occurs, try fallback
        if (connectionAttempts >= MAX_ATTEMPTS) {
          fallbackToREST(symbol, options);
        }
      };

      socket.onclose = (event) => {
        console.log(`${endpoint} WebSocket closed: ${event.code} ${event.reason}`);
        isConnecting = false;
        isConnected.value = false;
        connectionAttempts++;
        
        // Clear any existing reconnect timeout
        if (reconnectTimeout) {
          clearTimeout(reconnectTimeout);
          reconnectTimeout = null;
        }
        
        // If connection was closed unexpectedly and we're on the current symbol
        if (event.code !== 1000 && event.code !== 1001 && symbol === currentSymbol) {
            console.log(`Attempting to reconnect (Attempt number: ${connectionAttempts}...)`);
            reconnectTimeout = setTimeout(() => connect(symbol, options), 1000); // Wait 1 second before trying again
        }
      };

      // Add data timeout
      setTimeout(() => {
        if (isLoading.value && symbol === currentSymbol) {
          console.log(`Timeout waiting for ${endpoint} WebSocket data, trying REST fallback`);
          fallbackToREST(symbol, options);
        }
      }, 5000); // 5 second timeout for receiving data
    } catch (err) {
      console.error(`${endpoint} WebSocket connection failure:`, err);
      isConnecting = false;
      isLoading.value = false;
      connectionAttempts++;
      error.value = err;
      
      // Only try to reconnect if we're still on the same symbol
      if (symbol === currentSymbol) {
        console.log(`Attempting to reconnect (Attempt number: ${connectionAttempts})...`);
        reconnectTimeout = setTimeout(() => connect(symbol, options), 1000); // Wait 1 second before trying again
      } else if (symbol === currentSymbol) {
        fallbackToREST(symbol, options);
      }
    }
  }

  async function fallbackToREST(symbol, options = { days: 90 }) {
    console.log(`Using REST API as fallback for ${endpoint}...`);
    try {
      isLoading.value = true;
      error.value = null;
      
      // Fix URL construction for REST API fallback
      const baseApiUrl = baseUrl.replace('wss://', 'https://').replace('ws://', 'http://').split('/ws')[0];
      const apiUrl = `${baseApiUrl}/api/${endpoint}/${symbol}USDT?days=${options.days}`;
      
      console.log(`Calling REST API: ${apiUrl}`);
      
      const response = await fetch(apiUrl, {
        mode: 'cors',
        credentials: 'omit',
        headers: {
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
      }
      
      const json = await response.json();
      if (Array.isArray(json) && json.length > 0) {
        console.log(`Received ${json.length} ${endpoint} records via REST`);
        data.value = json;
        isLoading.value = false;
      } else {
        console.warn(`Received unexpected ${endpoint} REST data format:`, json);
        error.value = new Error("Unexpected data format");
      }
    } catch (fallbackError) {
      console.error(`Fallback API request for ${endpoint} also failed:`, fallbackError);
      error.value = fallbackError;
      isLoading.value = false;
    }
  }

  function disconnect() {
    console.log(`Disconnecting from ${endpoint} WebSocket...`);
    
    // Clear any pending reconnect timeout
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout);
      reconnectTimeout = null;
    }
    
    // Close the socket if it exists
    if (socket) {
      // Only try to close if the socket is open
      if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
        socket.close(1000, "Component unmounted");
      }
      socket = null;
    }
    
    isConnected.value = false;
    isConnecting = false;
    connectionAttempts = 0;
    
    console.log(`Disconnected from ${endpoint} WebSocket`);
  }

  // Clean up connection when component is unmounted
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




