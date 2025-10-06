<template>
  <span class="relative group inline-block cursor-pointer">
    <!-- Ícone -->
    <span class="text-blue-500 hover:text-blue-600 transition-colors">ℹ️</span>

    <!-- Tooltip to the LEFT -->
    <div
      class="tooltip-override absolute z-50 right-full top-1/2 -translate-y-1/2 mr-3 px-4 py-3 text-sm rounded-lg shadow-xl
             opacity-0 invisible group-hover:opacity-100 group-hover:visible
             pointer-events-none group-hover:pointer-events-auto
             transition-all duration-300 ease-in-out
             transform -translate-x-2 group-hover:translate-x-0"
    >
      <div class="tooltip-text-override">
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

<style scoped>
/* Use very high specificity to override everything */
.tooltip-override.tooltip-override.tooltip-override {
  background-color: #000000 !important;
  border: 1px solid #00ff00 !important;
  color: #00ff00 !important;
  text-align: left !important;
  width: 320px !important;
  min-width: 320px !important;
  max-width: 400px !important;
  white-space: normal !important;
  word-wrap: break-word !important;
  line-height: 1.5 !important;
  font-family: system-ui, sans-serif !important;
  font-size: 14px !important;
  font-weight: normal !important;
}

.tooltip-text-override.tooltip-text-override.tooltip-text-override {
  color: #00ff00 !important;
  text-align: left !important;
  white-space: normal !important;
  word-wrap: break-word !important;
  line-height: 1.5 !important;
}

.tooltip-arrow-override.tooltip-arrow-override.tooltip-arrow-override {
  border-left: 8px solid #00ff00 !important;
  border-top: 8px solid transparent !important;
  border-bottom: 8px solid transparent !important;
  width: 0 !important;
  height: 0 !important;
}
</style>


