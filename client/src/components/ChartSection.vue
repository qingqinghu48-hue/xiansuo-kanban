<template>
  <div v-if="isAdmin">
    <div class="charts-pies">
      <div class="chart-card">
        <div class="chart-card-head"><h3>平台来源分布</h3><span class="chart-tag">渠道占比</span></div>
        <div class="chart-card-body"><canvas ref="cvPlat" style="height:280px"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-card-head"><h3>有效性分布</h3><span class="chart-tag">线索质量</span></div>
        <div class="chart-card-body"><canvas ref="cvValid" style="height:280px"></canvas></div>
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
          <div class="chart-card-body" style="overflow-x:auto"><canvas ref="cvDySpend" style="height:200px"></canvas></div>
        </div>
        <div class="chart-card" style="border:1px solid var(--border-2)">
          <div class="chart-card-head"><h3>单条线索成本</h3><span class="chart-tag" style="background:#fee2e2;color:#dc2626">抖音</span></div>
          <div class="chart-card-body" style="overflow-x:auto"><canvas ref="cvDyUnit" style="height:200px"></canvas></div>
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
          <div class="chart-card-body" style="overflow-x:auto"><canvas ref="cvXhsSpend" style="height:200px"></canvas></div>
        </div>
        <div class="chart-card" style="border:1px solid var(--border-2)">
          <div class="chart-card-head"><h3>单条线索成本</h3><span class="chart-tag" style="background:#fce7f3;color:#be185d">小红书</span></div>
          <div class="chart-card-body" style="overflow-x:auto"><canvas ref="cvXhsUnit" style="height:200px"></canvas></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { platColor } from '../utils.js'

const props = defineProps({
  filtered: { type: Array, default: () => [] },
  costData: { type: Array, default: () => [] },
  isAdmin: { type: Boolean, default: false }
})

const cvPlat = ref(null)
const cvValid = ref(null)
const cvDySpend = ref(null)
const cvDyUnit = ref(null)
const cvXhsSpend = ref(null)
const cvXhsUnit = ref(null)

const VALID_COLORS = {
  '意向客户': '#10b981', '一般客户': '#3b82f6', '无效线索': '#94a3b8',
  '无意向客户': '#f59e0b', '未联系上': '#f43f5e', '未知': '#cbd5e1'
}

function getCanvasCtx(refEl) {
  if (!refEl) return null
  const canvas = refEl
  const rect = canvas.getBoundingClientRect()
  const dpr = window.devicePixelRatio || 1
  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr
  const ctx = canvas.getContext('2d')
  ctx.scale(dpr, dpr)
  return { ctx, width: rect.width, height: rect.height }
}

function drawPie(canvasRef, dataDict, colorMap) {
  const info = getCanvasCtx(canvasRef)
  if (!info) return
  const { ctx, width, height } = info
  const total = Object.values(dataDict).reduce((a, b) => a + b, 0)
  if (!total) { ctx.clearRect(0, 0, width, height); return }
  const cx = width / 2, cy = height / 2, radius = Math.min(width, height) / 2 - 30
  let start = -Math.PI / 2
  const entries = Object.entries(dataDict)
  entries.forEach(([k, v]) => {
    const angle = (v / total) * Math.PI * 2
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.arc(cx, cy, radius, start, start + angle)
    ctx.closePath()
    ctx.fillStyle = colorMap[k] || '#94a3b8'
    ctx.fill()
    start += angle
  })
  // legend
  let ly = 10
  entries.forEach(([k, v]) => {
    const pct = ((v / total) * 100).toFixed(1) + '%'
    ctx.fillStyle = colorMap[k] || '#94a3b8'
    ctx.fillRect(10, ly, 10, 10)
    ctx.fillStyle = '#475569'
    ctx.font = '11px sans-serif'
    ctx.fillText(`${k} ${v} (${pct})`, 24, ly + 9)
    ly += 18
  })
}

function drawBarChart(canvasRef, dataDict, colorStart, colorEnd) {
  const info = getCanvasCtx(canvasRef)
  if (!info) return
  const { ctx, width, height } = info
  ctx.clearRect(0, 0, width, height)
  const keys = Object.keys(dataDict).sort()
  if (!keys.length) return
  const max = Math.max(...Object.values(dataDict), 1)
  const pad = 30, bottom = 20, barW = Math.max(10, (width - pad * 2) / keys.length - 6)
  const chartH = height - pad - bottom
  keys.forEach((k, i) => {
    const v = dataDict[k]
    const barH = (v / max) * chartH
    const x = pad + i * (barW + 6)
    const y = pad + chartH - barH
    const grad = ctx.createLinearGradient(x, y, x, y + barH)
    grad.addColorStop(0, colorStart)
    grad.addColorStop(1, colorEnd)
    ctx.fillStyle = grad
    ctx.fillRect(x, y, barW, barH)
    ctx.fillStyle = '#475569'
    ctx.font = '10px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(String(k).slice(5), x + barW / 2, pad + chartH + 12)
    ctx.fillStyle = '#0f172a'
    ctx.fillText('¥' + Number(v).toFixed(0), x + barW / 2, y - 4)
  })
}

function drawLineChart(canvasRef, dataDict, lineColor, fillColors) {
  const info = getCanvasCtx(canvasRef)
  if (!info) return
  const { ctx, width, height } = info
  ctx.clearRect(0, 0, width, height)
  const keys = Object.keys(dataDict).sort()
  if (!keys.length) return
  const values = keys.map(k => dataDict[k])
  const max = Math.max(...values, 1)
  const pad = 30, bottom = 20
  const chartW = width - pad * 2
  const chartH = height - pad - bottom
  const step = keys.length > 1 ? chartW / (keys.length - 1) : chartW

  const points = keys.map((k, i) => ({
    x: pad + (keys.length > 1 ? i * step : chartW / 2),
    y: pad + chartH - (dataDict[k] / max) * chartH
  }))

  // fill
  if (points.length) {
    ctx.beginPath()
    ctx.moveTo(points[0].x, pad + chartH)
    points.forEach(p => ctx.lineTo(p.x, p.y))
    ctx.lineTo(points[points.length - 1].x, pad + chartH)
    ctx.closePath()
    const grad = ctx.createLinearGradient(0, pad, 0, pad + chartH)
    grad.addColorStop(0, fillColors[0] || 'rgba(59,130,246,0.25)')
    grad.addColorStop(1, fillColors[1] || 'rgba(59,130,246,0.02)')
    ctx.fillStyle = grad
    ctx.fill()
  }

  // line
  ctx.beginPath()
  points.forEach((p, i) => { if (i === 0) ctx.moveTo(p.x, p.y); else ctx.lineTo(p.x, p.y) })
  ctx.strokeStyle = lineColor
  ctx.lineWidth = 2
  ctx.stroke()

  // points
  points.forEach(p => {
    ctx.beginPath()
    ctx.arc(p.x, p.y, 3, 0, Math.PI * 2)
    ctx.fillStyle = lineColor
    ctx.fill()
  })

  // labels
  keys.forEach((k, i) => {
    ctx.fillStyle = '#475569'
    ctx.font = '10px sans-serif'
    ctx.textAlign = 'center'
    const x = points[i].x
    ctx.fillText(String(k).slice(5), x, pad + chartH + 12)
    ctx.fillStyle = '#0f172a'
    ctx.fillText('¥' + Number(dataDict[k]).toFixed(2), x, points[i].y - 8)
  })
}

function autoCanvasWidth(canvasRef, keys, type) {
  if (!canvasRef) return
  const parent = canvasRef.parentElement
  const parentW = parent ? parent.clientWidth : 300
  let dataW = 300
  const n = keys.length
  if (type === 'bar') {
    dataW = Math.max(300, n * 40 + 60)
  } else {
    dataW = Math.max(300, (n - 1) * 50 + 60)
  }
  canvasRef.style.width = `${Math.max(parentW, dataW)}px`
}

function renderAll() {
  nextTick(() => {
    // platform pie
    const platDict = {}
    props.filtered.forEach(r => { const p = r['平台'] || '未知'; platDict[p] = (platDict[p] || 0) + 1 })
    const platColors = {}
    Object.keys(platDict).forEach(p => platColors[p] = platColor(p))
    drawPie(cvPlat.value, platDict, platColors)

    // validity pie
    const validDict = {}
    props.filtered.forEach(r => { const v = r['线索有效性'] || r['有效性'] || '未知'; validDict[v] = (validDict[v] || 0) + 1 })
    const validColors = {}
    Object.keys(validDict).forEach(v => validColors[v] = VALID_COLORS[v] || '#cbd5e1')
    drawPie(cvValid.value, validDict, validColors)

    // cost data: amount (每日总消耗) + unit_cost (单条线索成本)
    const COST_BY_PLAT = { '抖音': {}, '小红书': {} }
    const UNIT_COST_BY_PLAT = { '抖音': {}, '小红书': {} }
    props.costData.forEach(c => {
      const plat = c.platform
      if (COST_BY_PLAT[plat]) {
        COST_BY_PLAT[plat][c.date] = Number(c.amount || 0)
        UNIT_COST_BY_PLAT[plat][c.date] = Number(c.unit_cost || 0)
      }
    })

    // 每日线索数按平台
    const leadsByDayPlat = { '抖音': {}, '小红书': {} }
    props.filtered.forEach(r => {
      const dt = String(r['入库时间'] || r['入库日期'] || '').slice(0, 10)
      const plat = r['平台']
      if (leadsByDayPlat[plat] && dt) {
        leadsByDayPlat[plat][dt] = (leadsByDayPlat[plat][dt] || 0) + 1
      }
    })

    // unit cost: 优先使用录入的 unit_cost，未录入则自动计算（amount/线索数）
    const unitByPlat = { '抖音': {}, '小红书': {} }
    Object.keys(COST_BY_PLAT).forEach(plat => {
      Object.keys(COST_BY_PLAT[plat]).forEach(dt => {
        const enteredUnit = UNIT_COST_BY_PLAT[plat][dt]
        if (enteredUnit > 0) {
          unitByPlat[plat][dt] = enteredUnit
        } else {
          const spend = COST_BY_PLAT[plat][dt]
          const leads = leadsByDayPlat[plat][dt] || 0
          unitByPlat[plat][dt] = leads > 0 ? spend / leads : 0
        }
      })
    })

    const dySpendKeys = Object.keys(COST_BY_PLAT['抖音'] || {}).sort()
    autoCanvasWidth(cvDySpend.value, dySpendKeys, 'bar')
    drawBarChart(cvDySpend.value, COST_BY_PLAT['抖音'] || {}, '#3b82f6', '#93c5fd')

    const dyUnitKeys = Object.keys(unitByPlat['抖音'] || {}).sort()
    autoCanvasWidth(cvDyUnit.value, dyUnitKeys, 'line')
    drawLineChart(cvDyUnit.value, unitByPlat['抖音'] || {}, '#f59e0b', ['rgba(245,158,11,0.25)', 'rgba(245,158,11,0.02)'])

    const xhsSpendKeys = Object.keys(COST_BY_PLAT['小红书'] || {}).sort()
    autoCanvasWidth(cvXhsSpend.value, xhsSpendKeys, 'bar')
    drawBarChart(cvXhsSpend.value, COST_BY_PLAT['小红书'] || {}, '#ec4899', '#fbcfe8')

    const xhsUnitKeys = Object.keys(unitByPlat['小红书'] || {}).sort()
    autoCanvasWidth(cvXhsUnit.value, xhsUnitKeys, 'line')
    drawLineChart(cvXhsUnit.value, unitByPlat['小红书'] || {}, '#be185d', ['rgba(190,24,93,0.25)', 'rgba(190,24,93,0.02)'])
  })
}

watch(() => [props.filtered, props.costData], renderAll, { deep: true })
</script>
