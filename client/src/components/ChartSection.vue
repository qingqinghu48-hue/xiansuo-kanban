<template>
  <div v-if="isAdmin">
    <div class="charts-pies">
      <div class="chart-card">
        <div class="chart-card-head"><h3>平台来源分布</h3><span class="chart-tag">渠道占比</span></div>
        <div class="chart-card-body"><div ref="elPlat" style="height:280px"></div></div>
      </div>
      <div class="chart-card">
        <div class="chart-card-head"><h3>有效性分布</h3><span class="chart-tag">线索质量</span></div>
        <div class="chart-card-body"><div ref="elValid" style="height:280px"></div></div>
      </div>
    </div>

    <div class="chart-row-full cost-section" style="background:#fff;border:1px solid var(--border);border-radius:16px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.04)">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;padding-bottom:14px;border-bottom:1px solid var(--border-2)">
        <div>
          <div style="font-size:16px;font-weight:700;color:var(--text)">抖音营销成本</div>
          <div style="font-size:12px;color:var(--text-3);margin-top:2px">每日消耗与单条成本追踪</div>
        </div>
        <span style="display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;background:linear-gradient(135deg,#ff6b6b,#ee5a5a);color:#fff;border-radius:8px;font-size:14px;font-weight:700">抖</span>
      </div>
      <div class="cost-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
        <div class="chart-card" style="border:1px solid var(--border-2)">
          <div class="chart-card-head"><h3>每日总消耗</h3><span class="chart-tag" style="background:#fee2e2;color:#dc2626">抖音</span></div>
          <div class="chart-card-body" style="overflow-x:auto"><div ref="elDySpend" style="height:220px;min-width:300px"></div></div>
        </div>
        <div class="chart-card" style="border:1px solid var(--border-2)">
          <div class="chart-card-head"><h3>单条线索成本</h3><span class="chart-tag" style="background:#fee2e2;color:#dc2626">抖音</span></div>
          <div class="chart-card-body" style="overflow-x:auto"><div ref="elDyUnit" style="height:220px;min-width:300px"></div></div>
        </div>
      </div>
    </div>

    <div class="chart-row-full cost-section" style="background:#fff;border:1px solid var(--border);border-radius:16px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.04)">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;padding-bottom:14px;border-bottom:1px solid var(--border-2)">
        <div>
          <div style="font-size:16px;font-weight:700;color:var(--text)">小红书营销成本</div>
          <div style="font-size:12px;color:var(--text-3);margin-top:2px">每日消耗与单条成本追踪</div>
        </div>
        <span style="display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;background:linear-gradient(135deg,#ec4899,#be185d);color:#fff;border-radius:8px;font-size:14px;font-weight:700">红</span>
      </div>
      <div class="cost-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
        <div class="chart-card" style="border:1px solid var(--border-2)">
          <div class="chart-card-head"><h3>每日总消耗</h3><span class="chart-tag" style="background:#fce7f3;color:#be185d">小红书</span></div>
          <div class="chart-card-body" style="overflow-x:auto"><div ref="elXhsSpend" style="height:220px;min-width:300px"></div></div>
        </div>
        <div class="chart-card" style="border:1px solid var(--border-2)">
          <div class="chart-card-head"><h3>单条线索成本</h3><span class="chart-tag" style="background:#fce7f3;color:#be185d">小红书</span></div>
          <div class="chart-card-body" style="overflow-x:auto"><div ref="elXhsUnit" style="height:220px;min-width:300px"></div></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { platColor } from '../utils.js'

const props = defineProps({
  filtered: { type: Array, default: () => [] },
  costData: { type: Array, default: () => [] },
  isAdmin: { type: Boolean, default: false }
})

const elPlat = ref(null)
const elValid = ref(null)
const elDySpend = ref(null)
const elDyUnit = ref(null)
const elXhsSpend = ref(null)
const elXhsUnit = ref(null)

const charts = {}

const VALID_COLORS = {
  '意向客户': '#10b981', '一般客户': '#3b82f6', '无效线索': '#94a3b8',
  '无意向客户': '#f59e0b', '未联系上': '#f43f5e', '未知': '#cbd5e1'
}

function initChart(el) {
  if (!el) return null
  const c = echarts.init(el)
  return c
}

function setPieChart(chart, dataDict, colorMap) {
  if (!chart) return
  const data = Object.entries(dataDict)
    .map(([name, value]) => ({ name, value, itemStyle: { color: colorMap[name] || '#94a3b8' } }))
    .sort((a, b) => b.value - a.value)

  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
      textStyle: { fontSize: 13 }
    },
    series: [{
      type: 'pie',
      radius: '60%',
      center: ['35%', '50%'],
      data,
      label: {
        show: true,
        position: 'outside',
        formatter: '{b}\n{c} ({d}%)',
        fontSize: 13,
        fontWeight: 'bold',
        color: '#1e293b'
      },
      labelLine: {
        show: true,
        length: 15,
        length2: 25,
        smooth: true
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.2)'
        }
      }
    }]
  }, true)
}

function setBarChart(chart, dataDict, colorStart, colorEnd) {
  if (!chart) return
  const keys = Object.keys(dataDict).sort()
  const values = keys.map(k => dataDict[k])
  const pointCount = keys.length
  const needZoom = pointCount > 12
  // 数据点多时：每个柱子至少 28px，图表撑开可横向滚动
  const minBarPx = 28
  const barGapPx = 12
  const chartWidth = needZoom ? Math.max(300, pointCount * (minBarPx + barGapPx)) : undefined

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: params => `${params[0].axisValue}<br/>¥${Number(params[0].value).toFixed(2)}`,
      textStyle: { fontSize: 13 }
    },
    grid: { left: 50, right: 20, top: 30, bottom: needZoom ? 50 : 30 },
    xAxis: {
      type: 'category',
      data: keys.map(k => String(k).slice(5)),
      axisLabel: { fontSize: 12, color: '#475569', interval: needZoom ? 'auto' : 0 },
      axisLine: { lineStyle: { color: '#e2e8f0' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 12,
        color: '#475569',
        formatter: v => '¥' + (v >= 1000 ? (v / 1000).toFixed(1) + 'k' : v)
      },
      splitLine: { lineStyle: { color: '#f1f5f9' } }
    },
    dataZoom: needZoom ? [
      { type: 'inside', start: Math.max(0, 100 - Math.round(12 / pointCount * 100)), end: 100 },
      { type: 'slider', start: Math.max(0, 100 - Math.round(12 / pointCount * 100)), end: 100, height: 18, bottom: 8, borderColor: 'transparent', fillerColor: 'rgba(148,163,184,0.15)', handleStyle: { color: '#94a3b8' } }
    ] : undefined,
    series: [{
      type: 'bar',
      data: values,
      barWidth: needZoom ? minBarPx : '50%',
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: colorStart },
          { offset: 1, color: colorEnd }
        ])
      },
      label: {
        show: true,
        position: 'top',
        formatter: p => '¥' + Number(p.value).toFixed(0),
        fontSize: 12,
        fontWeight: 'bold',
        color: '#0f172a'
      }
    }]
  }, true)

  // 动态设置容器宽度以撑开滚动
  if (needZoom && chart.getDom) {
    const dom = chart.getDom()
    if (dom) dom.style.width = chartWidth + 'px'
    chart.resize()
  }
}

function setLineChart(chart, dataDict, lineColor, fillColors) {
  if (!chart) return
  const keys = Object.keys(dataDict).sort()
  const values = keys.map(k => dataDict[k])
  const pointCount = keys.length
  const needZoom = pointCount > 12
  // 数据点多时：每个点至少 36px 间距，图表撑开可横向滚动
  const minPointPx = 36
  const chartWidth = needZoom ? Math.max(300, pointCount * minPointPx) : undefined

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: params => `${params[0].axisValue}<br/>¥${Number(params[0].value).toFixed(2)}`,
      textStyle: { fontSize: 13 }
    },
    grid: { left: 50, right: 20, top: 30, bottom: needZoom ? 50 : 30 },
    xAxis: {
      type: 'category',
      data: keys.map(k => String(k).slice(5)),
      axisLabel: { fontSize: 12, color: '#475569', interval: needZoom ? 'auto' : 0 },
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 12,
        color: '#475569',
        formatter: v => '¥' + (v >= 1000 ? (v / 1000).toFixed(1) + 'k' : v)
      },
      splitLine: { lineStyle: { color: '#f1f5f9' } }
    },
    dataZoom: needZoom ? [
      { type: 'inside', start: Math.max(0, 100 - Math.round(12 / pointCount * 100)), end: 100 },
      { type: 'slider', start: Math.max(0, 100 - Math.round(12 / pointCount * 100)), end: 100, height: 18, bottom: 8, borderColor: 'transparent', fillerColor: 'rgba(148,163,184,0.15)', handleStyle: { color: '#94a3b8' } }
    ] : undefined,
    series: [{
      type: 'line',
      data: values,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 2.5, color: lineColor },
      itemStyle: { color: lineColor, borderWidth: 2, borderColor: '#fff' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: fillColors[0] || 'rgba(59,130,246,0.25)' },
          { offset: 1, color: fillColors[1] || 'rgba(59,130,246,0.02)' }
        ])
      },
      label: {
        show: true,
        position: 'top',
        formatter: p => '¥' + Number(p.value).toFixed(2),
        fontSize: 12,
        fontWeight: 'bold',
        color: '#0f172a'
      }
    }]
  }, true)

  // 动态设置容器宽度以撑开滚动
  if (needZoom && chart.getDom) {
    const dom = chart.getDom()
    if (dom) dom.style.width = chartWidth + 'px'
    chart.resize()
  }
}

function renderAll() {
  nextTick(() => {
    // platform pie
    const platDict = {}
    props.filtered.forEach(r => { const p = r['平台'] || '未知'; platDict[p] = (platDict[p] || 0) + 1 })
    const platColors = {}
    Object.keys(platDict).forEach(p => platColors[p] = platColor(p))
    if (!charts.plat) charts.plat = initChart(elPlat.value)
    setPieChart(charts.plat, platDict, platColors)

    // validity pie
    const validDict = {}
    props.filtered.forEach(r => { const v = r['线索有效性'] || r['有效性'] || '未知'; validDict[v] = (validDict[v] || 0) + 1 })
    const validColors = {}
    Object.keys(validDict).forEach(v => validColors[v] = VALID_COLORS[v] || '#cbd5e1')
    if (!charts.valid) charts.valid = initChart(elValid.value)
    setPieChart(charts.valid, validDict, validColors)

    // cost data — 直接从后端 unit_cost 获取
    const COST_BY_PLAT = { '抖音': {}, '小红书': {} }
    const unitByPlat = { '抖音': {}, '小红书': {} }
    props.costData.forEach(c => {
      const plat = c.platform
      if (COST_BY_PLAT[plat]) {
        COST_BY_PLAT[plat][c.date] = Number(c.amount || 0)
        unitByPlat[plat][c.date] = Number(c.unit_cost || 0)
      }
    })

    if (!charts.dySpend) charts.dySpend = initChart(elDySpend.value)
    setBarChart(charts.dySpend, COST_BY_PLAT['抖音'] || {}, '#3b82f6', '#93c5fd')

    if (!charts.dyUnit) charts.dyUnit = initChart(elDyUnit.value)
    setLineChart(charts.dyUnit, unitByPlat['抖音'] || {}, '#f59e0b', ['rgba(245,158,11,0.25)', 'rgba(245,158,11,0.02)'])

    if (!charts.xhsSpend) charts.xhsSpend = initChart(elXhsSpend.value)
    setBarChart(charts.xhsSpend, COST_BY_PLAT['小红书'] || {}, '#ec4899', '#fbcfe8')

    if (!charts.xhsUnit) charts.xhsUnit = initChart(elXhsUnit.value)
    setLineChart(charts.xhsUnit, unitByPlat['小红书'] || {}, '#be185d', ['rgba(190,24,93,0.25)', 'rgba(190,24,93,0.02)'])
  })
}

function onResize() {
  Object.values(charts).forEach(c => c && c.resize())
}

onMounted(() => {
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  Object.values(charts).forEach(c => c && c.dispose())
})

watch(() => [props.filtered, props.costData], renderAll, { deep: true })
</script>
