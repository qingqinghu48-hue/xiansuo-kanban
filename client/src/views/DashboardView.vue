<template>
  <div>
    <div class="topbar">
      <div class="topbar-left">
        <div class="brand">
          <div class="brand-icon">招</div>
          <div class="brand-text">
            <h1>招商线索看板</h1>
            <span>全渠道线索数据总览</span>
          </div>
        </div>
      </div>
      <div class="topbar-right" style="display:flex;align-items:center;gap:12px">
        <router-link to="/admin" class="admin-link" style="color:var(--primary);font-size:13px;font-weight:600;text-decoration:none">⚙️ {{ isAdmin ? '管理后台' : '个人设置' }}</router-link>
        <span class="user-name">{{ userInfo.name || userInfo.username || '-' }}</span>
        <button class="btn btn-ghost btn-sm logout-btn" @click="doLogout">退出登录</button>
      </div>
    </div>

    <div class="main">
      <FilterBar :allData="allData" @filter="onFilter" />
      <KpiCards :filtered="filtered" :isAdmin="isAdmin" :costData="filteredCostData" :dateRange="{ ds: filterState.ds, de: filterState.de }" />
      <ChartSection :filtered="filtered" :costData="costData" :isAdmin="isAdmin" />
      <DataTable
        :filtered="filtered"
        :isGuest="isGuest"
        :canDelete="isAdmin"
        @detail="openDetail"
        @edit="openEdit"
        @delete="doDelete"
        @batchDelete="doBatchDelete"
      />
    </div>

    <DetailModal :visible="detailVisible" :record="detailRecord" @close="detailVisible = false" />
    <EditModal :visible="editVisible" :record="editRecord" :isAdmin="isAdmin" :regions="allRegions" :platforms="platformList" :agents="agentList" @close="editVisible = false" @saved="onEditSaved" />

    <!-- Toast -->
    <div v-if="toastMsg" :class="['toast', toastType === 'ok' ? 'toast-ok' : 'toast-err']">{{ toastMsg }}</div>

    <!-- Notify -->
    <div v-if="notifyVisible" class="notify-bar">
      <div class="notify-title">🎉 您有 {{ unreadCount }} 条新线索</div>
      <div class="notify-text">请及时跟进处理</div>
      <div class="notify-close" @click="closeNotify">我知道了</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api.js'
import { checkAuth } from '../auth.js'
import { splitRegions } from '../utils.js'
import FilterBar from '../components/FilterBar.vue'
import KpiCards from '../components/KpiCards.vue'
import ChartSection from '../components/ChartSection.vue'
import DataTable from '../components/DataTable.vue'
import DetailModal from '../components/DetailModal.vue'
import EditModal from '../components/EditModal.vue'

const allData = ref([])
const filtered = ref([])
const costData = ref([])
const filteredCostData = ref([])
const filterState = ref({ ds: '2026-03-01', de: '2026-04-30' })
const userInfo = ref({})
const loading = ref(true)
const router = useRouter()

const detailVisible = ref(false)
const detailRecord = ref({})
const editVisible = ref(false)
const editRecord = ref({})

const toastMsg = ref('')
const toastType = ref('ok')

const notifyVisible = ref(false)
const unreadCount = ref(0)

const isAdmin = computed(() => userInfo.value.role === 'admin')
const isGuest = computed(() => userInfo.value.role === 'guest')

const platformList = ref([])
const agentList = ref([])

const allRegions = computed(() => {
  const set = new Set()
  allData.value.forEach(r => {
    if (r['所属大区']) {
      splitRegions(r['所属大区']).forEach(region => set.add(region))
    }
  })
  return Array.from(set).sort()
})

onMounted(async () => {
  const user = await checkAuth(router)
  if (!user) {
    loading.value = false
    return
  }
  userInfo.value = user

  try {
    const leadsRes = await api.getLeads()
    const records = leadsRes.records || leadsRes.data || (Array.isArray(leadsRes) ? leadsRes : [])
    allData.value = dedup(records)

    if (isAdmin.value) {
      try {
        const c = await api.getCost()
        costData.value = Array.isArray(c) ? c : (c.cost_data || [])
      } catch(e) { costData.value = [] }
      // 初始筛选
      onFilter(filterState.value)
    }
    // 检查未读新线索
    if (!isAdmin.value && (leadsRes.new_leads_count || leadsRes.new_count)) {
      unreadCount.value = leadsRes.new_leads_count || leadsRes.new_count || 0
      notifyVisible.value = true
    }

    // 加载平台列表
    try {
      const p = await api.getPlatforms()
      if (p.success) platformList.value = p.platforms || []
    } catch(e) {}

    // 加载启用状态的招商员列表
    try {
      const a = await api.getActiveAgents()
      if (a.success) agentList.value = a.agents || []
    } catch(e) {}
  } catch(e) {
    console.error(e)
  }
  loading.value = false
})

function dedup(arr) {
  const seen = {}
  const res = []
  arr.forEach(r => {
    const phone = String(r['手机号'] || r['手机'] || '').trim()
    if (!phone || phone === 'undefined') { res.push(r); return }
    if (!seen[phone]) { seen[phone] = true; res.push(r) }
  })
  return res
}

function onFilter(f) {
  const ds = f.ds, de = f.de, fp = f.fp, fv = f.fv, flt = f.flt, fr = f.fr || [], fs = f.fs, fk = (f.fk || '').trim().toLowerCase()
  filterState.value = { ds, de }
  const frSet = new Set(fr)
  const res = []
  allData.value.forEach(r => {
    const dt = String(r['入库日期'] || '').slice(0, 10)
    if (dt && dt < ds) return
    if (dt && dt > de) return
    if (fp && r['平台'] !== fp) return
    if (fv && r['线索有效性'] !== fv && r['有效性'] !== fv) return
    if (flt && r['流量类型'] !== flt) return
    if (frSet.size) {
      const recordRegions = splitRegions(r['所属大区'])
      if (!recordRegions.some(region => frSet.has(region))) return
    }
    if (fs && r['所属招商'] !== fs) return
    if (fk) {
      const hay = (r['姓名'] || '') + (r['手机号'] || '') + (r['手机'] || '') + (r['所属大区'] || '') + (r['所属招商'] || '')
      if (hay.toLowerCase().indexOf(fk) === -1) return
    }
    res.push(r)
  })
  filtered.value = res

  // 同步筛选营销成本数据（按日期范围）
  const cres = []
  costData.value.forEach(c => {
    const dt = String(c.date || c.cost_date || '').slice(0, 10)
    if (dt && dt < ds) return
    if (dt && dt > de) return
    cres.push(c)
  })
  filteredCostData.value = cres
}

function showToast(msg, type) {
  toastMsg.value = msg
  toastType.value = type
  setTimeout(() => { toastMsg.value = '' }, 2500)
}

function openDetail(r) { detailRecord.value = r; detailVisible.value = true }
function openEdit(r) { editRecord.value = r; editVisible.value = true }

function getPhone(r) { return String(r['手机号'] || r['手机'] || '').trim() }

async function doLogout() {
  try { await api.logout() } catch(e) {}
  router.push('/login')
}

async function doDelete(r) {
  const phone = getPhone(r)
  if (!phone || phone === '-') { showToast('该记录缺少手机号，无法删除', 'err'); return }
  if (!confirm('确定删除 ' + (r['姓名'] || '') + ' (' + phone + ') 的线索记录？')) return
  try {
    const data = await api.deleteLead(phone)
    if (data.success) {
      allData.value = allData.value.filter(x => getPhone(x) !== phone)
      filtered.value = filtered.value.filter(x => getPhone(x) !== phone)
      showToast('删除成功', 'ok')
    } else { showToast(data.message || '删除失败', 'err') }
  } catch(e) { showToast('网络错误', 'err') }
}

async function doBatchDelete(rows) {
  const phones = rows.map(r => getPhone(r)).filter(p => p && p !== '-')
  if (!phones.length) { showToast('请先选择要删除的线索', 'err'); return }
  if (!confirm('确定删除选中的 ' + phones.length + ' 条线索？')) return
  try {
    const data = await api.batchDelete({ phones })
    if (data.success) {
      const set = new Set(phones)
      allData.value = allData.value.filter(x => !set.has(getPhone(x)))
      filtered.value = filtered.value.filter(x => !set.has(getPhone(x)))
      showToast(data.message || '删除成功', 'ok')
    } else { showToast(data.message || '删除失败', 'err') }
  } catch(e) { showToast('删除失败', 'err') }
}

function onEditSaved(payload) {
  const phoneStr = String(payload.phone || '').trim()

  const idx = allData.value.findIndex(x => getPhone(x) === phoneStr)
  if (idx >= 0) {
    Object.keys(payload).forEach(k => { if (k !== 'phone') allData.value[idx][k] = payload[k] })
    // 如果手机号改了，同步更新
    if (payload['手机号'] !== undefined) allData.value[idx]['手机号'] = payload['手机号']
    // 如果 admin 修改了招商员，同步更新
    if (payload['agent'] !== undefined) allData.value[idx]['所属招商'] = payload['agent']
    allData.value = [...allData.value]
  }

  const fIdx = filtered.value.findIndex(x => getPhone(x) === phoneStr)
  if (fIdx >= 0) {
    Object.keys(payload).forEach(k => { if (k !== 'phone') filtered.value[fIdx][k] = payload[k] })
    if (payload['手机号'] !== undefined) filtered.value[fIdx]['手机号'] = payload['手机号']
    if (payload['agent'] !== undefined) filtered.value[fIdx]['所属招商'] = payload['agent']
    filtered.value = [...filtered.value]
  }
}

async function closeNotify() {
  notifyVisible.value = false
  try { await api.markRead() } catch(e) {}
}
</script>
