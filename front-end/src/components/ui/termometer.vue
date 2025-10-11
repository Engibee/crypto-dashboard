<template>
  <div class="flex flex-col items-center">
    <div class="w-[5vw] h-[50vh] border-5 border-gray-700 rounded-full overflow-hidden flex flex-col-reverse">
      <div
        v-for="(level, index) in levels"
        :key="index"
        :class="[
          'flex-1 transition-colors duration-300',
          isActive(level) ? levelColors[level] : 'bg-gray-200'
        ]"
      ></div>
    </div>
    <span class="mt-2 text-sm font-medium">{{ signal }}</span>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  signal: {
    type: String,
    default: "Neutro",
    validator: (value) =>
      ["Forte Venda", "Venda", "Neutro", "Compra", "Forte Compra"].includes(
        value
      ),
  },
});

// Ordem dos níveis do termômetro de baixo para cima
const levels = ["Forte Venda", "Venda", "Neutro", "Compra", "Forte Compra"];

// Cores para cada nível ativo
const levelColors = {
  "Forte Venda": "[#ff0000]",
  Venda: "bg-[#ff0000]",
  Neutro: "bg-[#999999]",
  Compra: "bg-[#00ff00]",
  "Forte Compra": "bg-[#00ff00]",
};

// Determina se o nível deve ser preenchido
const isActive = (level) => {
  const signalIndex = levels.indexOf(props.signal);
  const levelIndex = levels.indexOf(level);
  return levelIndex <= signalIndex;
};
</script>

<style scoped>
/* Opcional: adiciona sombra interna para dar profundidade */
div > div.flex-1 {
  box-shadow: inset 0 -1px 2px rgba(0, 0, 0, 0.2);
}
</style>
