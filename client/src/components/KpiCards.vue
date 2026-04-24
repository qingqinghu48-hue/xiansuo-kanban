<template>
  <div class="kpi-grid">
    <div class="kpi-card blue">
      <div class="kpi-top">
        <div class="kpi-icon">📊</div>
        <span class="kpi-badge">全部渠道</span>
      </div>
      <div class="kpi-label">总线索数</div>
      <div class="kpi-value">{{ total }}</div>
    </div>
    <div class="kpi-card red">
      <div class="kpi-top">
        <div class="kpi-icon">🎵</div>
        <span class="kpi-badge">{{ dyPct }}</span>
      </div>
      <div class="kpi-label">抖音线索</div>
      <div class="kpi-value">{{ dyCount }}</div>
      <div class="kpi-sub">占比 {{ dyPct }}</div>
    </div>
    <div class="kpi-card amber">
      <div class="kpi-top">
        <div class="kpi-icon">📕</div>
        <span class="kpi-badge">{{ xhsPct }}</span>
      </div>
      <div class="kpi-label">小红书线索</div>
      <div class="kpi-value">{{ xhsCount }}</div>
      <div class="kpi-sub">占比 {{ xhsPct }}</div>
    </div>
    <div v-if="isAdmin" class="kpi-card green">
      <div class="kpi-top">
        <div class="kpi-icon">💰</div>
        <span class="kpi-badge">累计</span>
      </div>
      <div class="kpi-label">累计消耗</div>
      <div class="kpi-value">¥{{ totalSpend }}</div>
    </div>
    <div v-if="isAdmin" class="kpi-card indigo">
      <div class="kpi-top">
        <div class="kpi-icon">📈</div>
        <span class="kpi-badge">平均</span>
      </div>
      <div class="kpi-label">单条平均成本</div>
      <div class="kpi-value">¥{{ avgCost }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  filtered: { type: Array, default: () => [] },
  isAdmin: { type: Boolean, default: false },
  costData: { type: Array, default: () => [] }
})

const total = computed(() => props.filtered.length)

const dyCount = computed(() => props.filtered.filter(r => r['平台'] === '抖音').length)
const xhsCount = computed(() => props.filtered.filter(r => r['平台'] === '小红书').length)

const dyPct = computed(() => {
  if (!total.value) return '0%'
  return Math.round((dyCount.value / total.value) * 100) + '%'
})
const xhsPct = computed(() => {
  if (!total.value) return '0%'
  return Math.round((xhsCount.value / total.value) * 100) + '%'
})

const totalSpend = computed(() => {
  let sum = 0
  props.costData.forEach(c => { sum += Number(c.amount || 0) })
  return sum.toFixed(2)
})

const avgCost = computed(() => {
  const adLeads = props.filtered.filter(r => r['平台'] === '抖音' || r['平台'] === '小红书')
  if (!adLeads.length) return '0.00'
  const sum = props.costData.reduce((a, c) => a + Number(c.amount || 0), 0)
  return (sum / adLeads.length).toFixed(2)
})
</script>
