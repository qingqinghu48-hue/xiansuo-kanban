<template>
  <div class="table-card">
    <div class="table-card-head">
      <h2>线索明细</h2>
      <div class="table-head-actions" style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
        <span class="table-badge">{{ filtered.length }} 条</span>
        <button type="button" class="td-btn td-btn-success" @click="downloadExcel">📥 下载Excel</button>
        <button v-if="!isGuest" type="button" class="td-btn" @click="batchDelete" :style="batchStyle">🗑 批量删除</button>
      </div>
    </div>
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th v-if="!isGuest" class="th-check"><input type="checkbox" v-model="selectAll" @change="toggleSelectAll"></th>
            <th @click="sortBy('入库日期')">入库日期 {{ sortIcon('入库日期') }}</th>
            <th @click="sortBy('平台')">平台 {{ sortIcon('平台') }}</th>
            <th @click="sortBy('姓名')">姓名 {{ sortIcon('姓名') }}</th>
            <th>手机号</th>
            <th>城市</th>
            <th @click="sortBy('线索有效性')">有效性 {{ sortIcon('线索有效性') }}</th>
            <th @click="sortBy('所属大区')">大区 {{ sortIcon('所属大区') }}</th>
            <th @click="sortBy('所属招商')">招商员 {{ sortIcon('所属招商') }}</th>
            <th>能否加微</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, idx) in pageData" :key="idx">
            <td v-if="!isGuest" class="td-check"><input type="checkbox" :checked="selected.includes(r)" @change="e => toggleRow(r, e.target.checked)"></td>
            <td class="td-date">{{ fmtDate(r) }}</td>
            <td><span class="tag" :style="platStyle(r['平台'])">{{ r['平台'] || '-' }}</span></td>
            <td class="td-num">{{ r['姓名'] || '-' }}</td>
            <td class="td-num">{{ r['手机号'] || r['手机'] || '-' }}</td>
            <td>{{ r['省份'] || '-' }}</td>
            <td v-html="validTag(r['线索有效性'] || r['有效性'] || '')"></td>
            <td>{{ r['所属大区'] || '-' }}</td>
            <td>{{ r['所属招商'] || '-' }}</td>
            <td v-html="jmTag(r['是否能加上微信'])"></td>
            <td>
              <button class="td-btn td-btn-gap" @click="onDetail(r)">查看</button>
              <template v-if="!isGuest">
                <button class="td-btn td-btn-gap td-btn-edit" @click="onEdit(r)">编辑</button>
                <button class="td-btn td-btn-delete" @click="onDelete(r)">删除</button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="pager">
      <div class="pager-info">{{ pagerInfo }}</div>
      <div class="pager-btns">
        <button :disabled="page <= 1" @click="page--">&#8249;</button>
        <div class="page-nums">
          <template v-for="p in pageNums" :key="p">
            <button v-if="typeof p === 'number'" :class="['page-num', { active: p === page }]" @click="page = p">{{ p }}</button>
            <span v-else style="color:var(--text-3);line-height:32px">{{ p }}</span>
          </template>
        </div>
        <button :disabled="page >= totalPages" @click="page++">&#8250;</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { platColor, platStyle, esc } from '../utils.js'

const props = defineProps({
  filtered: { type: Array, default: () => [] },
  isGuest: { type: Boolean, default: false }
})
const emit = defineEmits(['detail', 'edit', 'delete', 'batchDelete'])

const page = ref(1)
const PS = 15
const sortK = ref('')
const sortAsc = ref(true)
const selected = ref([])
const selectAll = ref(false)

watch(() => props.filtered, () => { page.value = 1; selected.value = []; selectAll.value = false })

const sorted = computed(() => {
  if (!sortK.value) return props.filtered
  const arr = [...props.filtered]
  arr.sort((a, b) => {
    const va = a[sortK.value] || ''
    const vb = b[sortK.value] || ''
    const cmp = va < vb ? -1 : (va > vb ? 1 : 0)
    return sortAsc.value ? cmp : -cmp
  })
  return arr
})

const totalPages = computed(() => Math.max(1, Math.ceil(sorted.value.length / PS)))

const pageData = computed(() => {
  const start = (page.value - 1) * PS
  return sorted.value.slice(start, start + PS)
})

const pagerInfo = computed(() => `第 ${page.value} / ${totalPages.value} 页，共 ${sorted.value.length} 条`)

const pageNums = computed(() => {
  const total = totalPages.value
  if (total <= 1) return []
  const maxShow = 7
  const half = Math.floor(maxShow / 2)
  let start, end
  if (total <= maxShow) { start = 1; end = total }
  else {
    start = Math.max(1, page.value - half)
    end = Math.min(total, page.value + half)
    if (page.value <= half) end = maxShow
    if (page.value > total - half) start = total - maxShow + 1
  }
  const nums = []
  if (start > 1) { nums.push(1); if (start > 2) nums.push('…') }
  for (let i = start; i <= end; i++) nums.push(i)
  if (end < total) { if (end < total - 1) nums.push('…'); nums.push(total) }
  return nums
})

function sortBy(k) {
  if (sortK.value === k) sortAsc.value = !sortAsc.value
  else { sortK.value = k; sortAsc.value = true }
}
function sortIcon(k) {
  if (sortK.value !== k) return ''
  return sortAsc.value ? '▲' : '▼'
}

function validTag(v) {
  const cls = v === '意向客户' ? 'tag-yx' : v === '一般客户' ? 'tag-yb' : v === '无效线索' ? 'tag-wlx' : v === '普通线索' ? 'tag-pt' : ''
  return `<span class="tag ${cls}">${esc(v)}</span>`
}
function jmTag(jm) {
  if (jm === '是') return '<span style="color:#10b981;font-weight:700">是</span>'
  if (jm === '否') return '<span style="color:#94a3b8">否</span>'
  return '<span style="color:#94a3b8">—</span>'
}
function fmtDate(r) {
  return String(r['录入日期'] || r['入库日期'] || '-').slice(0, 10)
}

const batchStyle = computed(() => {
  return selected.value.length ? { display: 'inline-block', background: '#fff', color: 'var(--danger)', borderColor: 'var(--danger)', fontWeight: 600 } : { display: 'none' }
})
function toggleRow(row, checked) {
  if (checked) { if (!selected.value.includes(row)) selected.value.push(row) }
  else { const i = selected.value.indexOf(row); if (i > -1) selected.value.splice(i, 1) }
}
function toggleSelectAll() {
  if (selectAll.value) selected.value = [...pageData.value]
  else selected.value = []
}
function onDetail(r) { emit('detail', r) }
function onEdit(r) { emit('edit', r) }
function onDelete(r) { emit('delete', r) }
function batchDelete() {
  if (!selected.value.length) return
  emit('batchDelete', [...selected.value])
  selected.value = []
  selectAll.value = false
}
function downloadExcel() {
  const data = sorted.value
  if (!data.length) { alert('没有数据可下载'); return }

  const headers = [
    'ID','手机号','平台','所属招商','录入日期','姓名','省份','线索有效性','所属大区',
    '是否能加上微信','备注','入库时间','是否已读','二次联系时间','二次联系备注',
    '最近一次电联时间','到访时间','签约时间','小红书账号','线索类型','来源文件',
    '是否重复','用户小红书昵称','用户小红书ID','用户ID','来源笔记','创意名称',
    '创意ID','转化方式','微信号','详情','意向线索','意向门店','意向门店ID',
    '跟进户','最新跟进记录','线索阶段','线索标签','线索拨打次数','营销类型',
    '最近拨打时间','智能意向','互动场景','最近留资记录'
  ]

  const keys = [
    'id','手机号','平台','所属招商','录入日期','姓名','省份','线索有效性','所属大区',
    '是否能加上微信','备注','入库时间','是否已读','二次联系时间','二次联系备注',
    '最近一次电联时间','到访时间','签约时间','小红书账号','线索类型','来源文件',
    '是否重复','用户小红书昵称','用户小红书ID','用户ID','来源笔记','创意名称',
    '创意ID','转化方式','微信号','详情','意向线索','意向门店','意向门店ID',
    '跟进户','最新跟进记录','线索阶段','线索标签','线索拨打次数','营销类型',
    '最近拨打时间','智能意向','互动场景','最近留资记录'
  ]

  let csv = '\uFEFF' + headers.join(',') + '\n'
  data.forEach(r => {
    const row = keys.map(k => {
      const v = r[k]
      const s = v === undefined || v === null ? '' : String(v)
      return '"' + s.replace(/"/g,'""') + '"'
    })
    csv += row.join(',') + '\n'
  })
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = '线索明细_' + new Date().toISOString().slice(0,10) + '.csv'
  link.click()
}
</script>

<style scoped>
.th-check { width: 36px; text-align: center; }
.td-check { text-align: center; }
.td-btn-success { background: #10b981; }
.td-btn-gap { margin-right: 4px; }
.td-btn-edit { background: #fff; color: var(--primary); border-color: var(--primary); }
.td-btn-delete { background: #fff; color: var(--danger); border-color: var(--danger); }
</style>
