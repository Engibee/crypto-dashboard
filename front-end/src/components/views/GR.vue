<script setup>
import { ref, watch, onMounted, onUnmounted } from "vue";
import { SymbolStore } from "../../stores/symbolStore";
import termometer from "../ui/termometer.vue";

const currentSymbol = ref(SymbolStore.value);
</script>

<template>
  <div class="bg-[#000000] text-[#00ff00] flex flex-col justify-center items-center w-full h-full">
    <h1>Indicators Graphs: {{ currentSymbol }}</h1>
    <termometer :signal="Compra" />
  </div>
</template>
