<template>
  <span class="relative group inline-block cursor-pointer">
    <!-- Ícone -->
    <span class="text-blue-500 hover:text-blue-600 transition-colors">ℹ️</span>

    <!-- Tooltip to the LEFT -->
    <div
      class="tooltip-override border bg-[#000000] absolute z-50 right-full top-1/2 -translate-y-1/2 mr-3 px-4 py-3 text-sm rounded-lg shadow-xl
             min-w-[20vw] max-w-[25vw] opacity-0 invisible group-hover:opacity-100 group-hover:visible
             pointer-events-none group-hover:pointer-events-auto
             transition-all duration-300 ease-in-out
             transform -translate-x-2 group-hover:translate-x-0"
    >
      <div class="tooltip-text-override m-[2%]">
        {{ message }}
      </div>
      <!-- Arrow pointing right (toward the icon) -->
      <div class="tooltip-arrow-override absolute left-full top-1/2 -translate-y-1/2"></div>
    </div>
  </span>
</template>

<script setup>
defineProps({
  message: String,
});
</script>

