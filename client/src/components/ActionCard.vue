<template>
  <div class="chart-card action-card">
    <h3 class="action-card-title">{{ title }}</h3>
    <p class="action-card-desc">{{ description }}</p>
    <div class="action-card-action">
      <slot name="action"></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  description: String
})
</script>

<style scoped>
.action-card { padding: 20px; }
.action-card-title { font-size: 14px; font-weight: 700; margin-bottom: 12px; }
.action-card-desc { font-size: 12px; color: var(--text-3); margin-bottom: 16px; }
.action-card-action { margin-bottom: 16px; }
</style>
