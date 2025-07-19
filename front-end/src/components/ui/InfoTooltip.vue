<template>
  <span class="relative group inline-block cursor-pointer">
    <!-- Ícone -->
    <span class="text-blue-500">ℹ️</span>

    <!-- Tooltip flutuante -->
    <span
      class="absolute z-10 right-full top-1/2 -translate-y-1/2 mr-2 w-64 px-3 py-2 text-sm text-white bg-gray-800 border border-gray-300 rounded shadow-lg 
             opacity-0 group-hover:opacity-100 
             pointer-events-none group-hover:pointer-events-auto 
             transition-opacity duration-200"
    >
      {{ message }}
      <!-- Seta -->
      <span
        class="absolute left-[-6px] top-1/2 -translate-y-1/2 w-3 h-3 bg-gray-800 rotate-45 border-l border-t border-gray-300"
      ></span>
    </span>
  </span>
</template>

<script setup>
defineProps({
  message: String,
});
</script>
