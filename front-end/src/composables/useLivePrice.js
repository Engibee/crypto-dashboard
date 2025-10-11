import { ref, onUnmounted } from 'vue';

export function useLivePrice(baseUrl) {
  const price = ref(0);
  const isConnected = ref(false);
  const error = ref(null);
  
  let socket = null;
  let currentSymbol = null;
  let reconnectTimeout = null;

  function connect(symbol) {
    // If already connected to the same symbol, don't reconnect
    if (isConnected.value && symbol === currentSymbol) {
      return;
    }
    
    try {
      error.value = null;
      currentSymbol = symbol;
      
      // Close existing connection
      if (socket) {
        socket.close();
        socket = null;
      }
      
      console.log(`Connecting to live price WebSocket for ${symbol}...`);
      
      const url = `${baseUrl}/ws/live-price?ticker=${symbol}USDT`;

      console.log(`Connecting to ${url}`);
      socket = new WebSocket(url);

      socket.onopen = () => {
        console.log('Live price WebSocket connection established!');
        isConnected.value = true;
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.price) {
            price.value = data.price;
          }
        } catch (parseError) {
          console.error('Error parsing live price data:', parseError);
        }
      };

      socket.onerror = (err) => {
        console.error('Live price WebSocket error:', err);
        error.value = new Error("WebSocket connection error");
      };

      socket.onclose = (event) => {
        console.log(`Live price WebSocket closed: ${event.code}`);
        isConnected.value = false;
        
        // Clear any existing reconnect timeout
        if (reconnectTimeout) {
          clearTimeout(reconnectTimeout);
          reconnectTimeout = null;
        }
        
        // Reconnect if unexpected close
        if (event.code !== 1000 && event.code !== 1001 && symbol === currentSymbol) {
          reconnectTimeout = setTimeout(() => connect(symbol), 1000);
        }
      };
    } catch (err) {
      console.error('Live price WebSocket connection failure:', err);
      error.value = err;
    }
  }

  function disconnect() {
    console.log('Disconnecting from live price WebSocket...');
    
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout);
      reconnectTimeout = null;
    }
    
    if (socket) {
      if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
        socket.close(1000, "Component unmounted");
      }
      socket = null;
    }
    
    isConnected.value = false;
  }

  onUnmounted(() => {
    disconnect();
  });

  return {
    price,
    isConnected,
    error,
    connect,
    disconnect
  };
}