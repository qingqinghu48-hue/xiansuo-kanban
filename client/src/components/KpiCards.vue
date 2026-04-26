<template>
  <div class="kpi-grid">
    <!-- 1. 总线索数 -->
    <div class="kpi-card blue">
      <div class="kpi-top">
        <div class="kpi-icon">📊</div>
        <span class="kpi-badge">全部渠道</span>
      </div>
      <div class="kpi-label">总线索数</div>
      <div class="kpi-value">{{ total }}</div>
    </div>

    <!-- 2. 抖音线索数 -->
    <div class="kpi-card red">
      <div class="kpi-top">
        <div class="kpi-icon">🎵</div>
        <span class="kpi-badge">{{ dyPct }}</span>
      </div>
      <div class="kpi-label">抖音线索数</div>
      <div class="kpi-value">{{ dyCount }}</div>
      <div class="kpi-sub">占比 {{ dyPct }}</div>
    </div>

    <!-- 3. 小红书线索数 -->
    <div class="kpi-card amber">
      <div class="kpi-top">
        <div class="kpi-icon">📕</div>
        <span class="kpi-badge">{{ xhsPct }}</span>
      </div>
      <div class="kpi-label">小红书线索数</div>
      <div class="kpi-value">{{ xhsCount }}</div>
      <div class="kpi-sub">占比 {{ xhsPct }}</div>
    </div>

    <!-- 4. 其他平台线索数 -->
    <div class="kpi-card teal">
      <div class="kpi-top">
        <div class="kpi-icon">🌐</div>
        <span class="kpi-badge">{{ otherPct }}</span>
      </div>
      <div class="kpi-label">其他平台线索数</div>
      <div class="kpi-value">{{ otherCount }}</div>
      <div class="kpi-sub">占比 {{ otherPct }}</div>
      <div v-if="otherPlatforms.length" class="kpi-note" :title="otherPlatforms.join('、')">
        含 {{ otherPlatforms.join('、') }}
      </div>
    </div>

    <!-- 5. 累计营销费用消耗 -->
    <div v-if="isAdmin" class="kpi-card green">
      <div class="kpi-top">
        <div class="kpi-icon">💰</div>
        <span class="kpi-badge">累计</span>
      </div>
      <div class="kpi-label">累计营销费用消耗</div>
      <div class="kpi-value">¥{{ totalSpend }}</div>
      <div v-if="dateRange.ds && dateRange.de" class="kpi-note">
        {{ dateRange.ds }} 至 {{ dateRange.de }}
      </div>
    </div>

    <!-- 6. 单条线索平均成本 -->
    <div v-if="isAdmin" class="kpi-card indigo">
      <div class="kpi-top">
        <div class="kpi-icon">📈</div>
        <span class="kpi-badge">平均</span>
      </div>
      <div class="kpi-label">单条线索平均成本</div>
      <div class="kpi-value">¥{{ avgCost }}</div>
      <div class="kpi-note">线索指全部营销线索，不区分有效性</div>
      <div v-if="dateRange.ds && dateRange.de" class="kpi-note">
        {{ dateRange.ds }} 至 {{ dateRange.de }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  filtered: { type: Array, default: () => [] },
  isAdmin: { type: Boolean, default: false },
  costData: { type: Array, default: () => [] },
  dateRange: { type: Object, default: () => ({}) }
})

const total = computed(() => props.filtered.length)

const dyCount = computed(() => props.filtered.filter(r => r['平台'] === '抖音').length)
const xhsCount = computed(() => props.filtered.filter(r => r['平台'] === '小红书').length)
const otherCount = computed(() => props.filtered.filter(r => {
  const p = r['平台']
  return p && p !== '抖音' && p !== '小红书'
}).length)

const dyPct = computed(() => {
  if (!total.value) return '0%'
  return Math.round((dyCount.value / total.value) * 100) + '%'
})
const xhsPct = computed(() => {
  if (!total.value) return '0%'
  return Math.round((xhsCount.value / total.value) * 100) + '%'
})
const otherPct = computed(() => {
  if (!total.value) return '0%'
  return Math.round((otherCount.value / total.value) * 100) + '%'
})

const otherPlatforms = computed(() => {
  const set = new Set()
  props.filtered.forEach(r => {
    const plat = r['平台']
    if (plat && plat !== '抖音' && plat !== '小红书') {
      set.add(plat)
    }
  })
  return Array.from(set).sort()
})

const totalSpend = computed(() => {
  const arr = Array.isArray(props.costData) ? props.costData : []
  let sum = 0
  arr.forEach(c => { sum += Number(c.amount || 0) })
  return sum.toFixed(2)
})

const avgCost = computed(() => {
  const arr = Array.isArray(props.costData) ? props.costData : []
  const totalAmount = arr.reduce((a, c) => a + Number(c.amount || 0), 0)
  const totalLeads = arr.reduce((a, c) => a + Number(c.lead_count || 0), 0)
  if (!totalLeads) return '0.00'
  return (totalAmount / totalLeads).toFixed(2)
})
</script>

<style scoped>
.kpi-note {
  font-size: 11px;
  color: var(--text-3);
  margin-top: 4px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.kpi-card.teal::after {
  background: linear-gradient(90deg, #14b8a6, #2dd4bf);
}
.kpi-card.teal .kpi-icon {
  background: #ccfbf1;
  color: #14b8a6;
}
</style>
