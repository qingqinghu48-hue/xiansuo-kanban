<template>
  <div class="filter-section">
    <div class="filter-row">
      <span class="filter-label">日期</span>
      <input type="date" class="filter-input" v-model="filter.ds">
      <span style="color:var(--text-3);font-size:12px">—</span>
      <input type="date" class="filter-input" v-model="filter.de">
      <span class="filter-label" style="margin-left:8px">平台</span>
      <select class="filter-select" v-model="filter.fp">
        <option value="">全部平台</option>
        <option v-for="p in platforms" :key="p" :value="p">{{ p }}</option>
      </select>
      <span class="filter-label">有效性</span>
      <select class="filter-select" v-model="filter.fv">
        <option value="">全部状态</option>
        <option>意向客户</option>
        <option>一般客户</option>
        <option>未联系上</option>
        <option>普通线索</option>
        <option>无意向客户</option>
        <option>无效线索</option>
      </select>
      <span class="filter-label">线索类型</span>
      <select class="filter-select" v-model="filter.flt">
        <option value="">全部类型</option>
        <option>广告线索</option>
        <option>自然流线索</option>
      </select>
      <span class="filter-label">大区</span>
      <select class="filter-select" v-model="filter.fr">
        <option value="">全部大区</option>
        <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
      </select>
      <span class="filter-label">招商员</span>
      <select class="filter-select" v-model="filter.fs">
        <option value="">全部招商</option>
        <option v-for="s in staffs" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>
    <div class="filter-row">
      <span class="filter-label">搜索</span>
      <input type="text" class="filter-search" v-model="filter.fk" placeholder="姓名 / 手机号">
      <div style="flex:1"></div>
      <button class="btn btn-pri" @click="apply">应用筛选</button>
      <button class="btn btn-ghost" @click="reset">重置</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch, onMounted } from 'vue'

const props = defineProps({
  allData: { type: Array, default: () => [] }
})
const emit = defineEmits(['filter'])

const platforms = reactive([])
const regions = reactive([])
const staffs = reactive([])

const filter = reactive({
  ds: '2026-03-01',
  de: '2026-04-30',
  fp: '',
  fv: '',
  flt: '',
  fr: '',
  fs: '',
  fk: ''
})

function extractOptions() {
  const regSet = new Set()
  const stfSet = new Set()
  const platSet = new Set()
  props.allData.forEach(r => {
    if (r['所属大区']) regSet.add(r['所属大区'])
    if (r['所属招商']) stfSet.add(r['所属招商'])
    if (r['平台']) platSet.add(r['平台'])
  })
  regions.splice(0, regions.length, ...Array.from(regSet).sort())
  staffs.splice(0, staffs.length, ...Array.from(stfSet).sort())
  platforms.splice(0, platforms.length, ...Array.from(platSet).sort())
}

function saveFilterState() {
  try { localStorage.setItem('kanban_filter', JSON.stringify(filter)) } catch(e) {}
}

function loadFilterState() {
  try {
    const raw = localStorage.getItem('kanban_filter')
    if (!raw) return
    const state = JSON.parse(raw)
    Object.assign(filter, state)
  } catch(e) {}
}

function apply() {
  saveFilterState()
  emit('filter', { ...filter })
}

function reset() {
  filter.ds = '2026-03-01'
  filter.de = '2026-04-30'
  filter.fp = ''
  filter.fv = ''
  filter.flt = ''
  filter.fr = ''
  filter.fs = ''
  filter.fk = ''
  saveFilterState()
  emit('filter', { ...filter })
}

watch(() => props.allData, extractOptions, { immediate: true })
watch(() => [filter.ds, filter.de], () => { saveFilterState(); emit('filter', { ...filter }) })

onMounted(() => {
  loadFilterState()
  emit('filter', { ...filter })
})
</script>
