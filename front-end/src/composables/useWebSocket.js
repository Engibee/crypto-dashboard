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

  async function connect(symbol, options = { days: 90 }) {
    // Evitar múltiplas tentativas simultâneas
    if (isConnecting) return;
    
    // Se já estamos conectados ao mesmo símbolo, não reconectar
    if (isConnected.value && symbol === currentSymbol) {
      return;
    }
    
    try {
      isConnecting = true;
      isLoading.value = true;
      error.value = null;
      connectionAttempts++;
      currentSymbol = symbol;
      
      // Fechar conexão existente
      if (socket) {
        socket.close();
        socket = null;
      }
      
      console.log(`Tentativa ${connectionAttempts}: Conectando ao WebSocket para ${symbol}USDT...`);
      
      // Criar nova conexão WebSocket
      const url = `${baseUrl}?ticker=${symbol}USDT&days=${options.days}`;
      socket = new WebSocket(url);

      // Configurar handlers de eventos
      socket.onopen = () => {
        console.log("Conexão WebSocket estabelecida com sucesso!");
        isConnecting = false;
        isConnected.value = true;
        
        // Não desativar isLoading aqui - esperar pelos dados
        connectionAttempts = 0; // Resetar contagem após sucesso
      };

      socket.onmessage = (event) => {
        try {
          const json = JSON.parse(event.data);
          
          // Verificar se os dados são válidos
          if (Array.isArray(json) && json.length > 0) {
            console.log(`Recebidos ${json.length} registros de dados via WebSocket`);
            data.value = json;
            isLoading.value = false; // Só desativar loading quando dados chegarem
          } else {
            console.warn("Recebidos dados WebSocket em formato inesperado:", json);
          }
        } catch (parseError) {
          console.error("Erro ao analisar dados do WebSocket:", parseError);
          error.value = parseError;
        }
      };

      socket.onerror = (err) => {
        console.error("Erro no WebSocket:", err);
        error.value = new Error("Erro na conexão WebSocket");
        
        // Se ocorrer erro, tentar fallback
        if (connectionAttempts >= MAX_ATTEMPTS) {
          fallbackToREST(symbol, options);
        }
      };

      socket.onclose = (event) => {
        console.log(`WebSocket fechado: ${event.code} ${event.reason}`);
        isConnecting = false;
        isConnected.value = false;
        
        // Se a conexão foi fechada inesperadamente e estamos no símbolo atual
        if (event.code !== 1000 && event.code !== 1001 && symbol === currentSymbol) {
          if (connectionAttempts < MAX_ATTEMPTS) {
            console.log(`Tentando reconectar (${connectionAttempts}/${MAX_ATTEMPTS})...`);
            setTimeout(() => connect(symbol, options), 1000); // Esperar 1 segundo antes de tentar novamente
          } else {
            console.log("Número máximo de tentativas atingido, usando API REST como fallback");
            fallbackToREST(symbol, options);
          }
        }
      };

      // Adicionar timeout para dados
      setTimeout(() => {
        if (isLoading.value && symbol === currentSymbol) {
          console.log("Timeout esperando dados do WebSocket, tentando fallback REST");
          fallbackToREST(symbol, options);
        }
      }, 5000); // 5 segundos de timeout para receber dados
    } catch (err) {
      console.error("Falha na conexão WebSocket:", err);
      isConnecting = false;
      isLoading.value = false;
      error.value = err;
      
      // Só tentar reconectar se ainda estivermos no mesmo símbolo
      if (connectionAttempts < MAX_ATTEMPTS && symbol === currentSymbol) {
        console.log(`Tentando reconectar (${connectionAttempts}/${MAX_ATTEMPTS})...`);
        setTimeout(() => connect(symbol, options), 1000); // Esperar 1 segundo antes de tentar novamente
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
