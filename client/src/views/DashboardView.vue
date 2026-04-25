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
        <router-link v-if="isAdmin" to="/admin" class="admin-link" style="color:var(--primary);font-size:13px;font-weight:600;text-decoration:none">⚙️ 管理后台</router-link>
        <span class="user-name">{{ userInfo.name || userInfo.username || '-' }}</span>
        <button class="btn btn-ghost btn-sm logout-btn" @click="doLogout">退出登录</button>
      </div>
    </div>

    <div class="main">
      <FilterBar :allData="allData" @filter="onFilter" />
      <KpiCards :filtered="filtered" :isAdmin="isAdmin" :costData="costData" />
      <ChartSection :filtered="filtered" :costData="costData" />
      <DataTable
        :filtered="filtered"
        :isGuest="isGuest"
        @detail="openDetail"
        @edit="openEdit"
        @delete="doDelete"
        @batchDelete="doBatchDelete"
      />
    </div>

    <DetailModal :visible="detailVisible" :record="detailRecord" @close="detailVisible = false" />
    <EditModal :visible="editVisible" :record="editRecord" :isAdmin="isAdmin" @close="editVisible = false" @saved="onEditSaved" />

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
    }
    // 检查未读新线索
    if (!isAdmin.value && (leadsRes.new_leads_count || leadsRes.new_count)) {
      unreadCount.value = leadsRes.new_leads_count || leadsRes.new_count || 0
      notifyVisible.value = true
    }
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
  const frSet = new Set(fr)
  const res = []
  allData.value.forEach(r => {
    const dt = String(r['入库时间'] || r['入库日期'] || '').slice(0, 10)
    if (dt && dt < ds) return
    if (dt && dt > de) return
    if (fp && r['平台'] !== fp) return
    if (fv && r['线索有效性'] !== fv && r['有效性'] !== fv) return
    if (flt && r['线索类型'] !== flt) return
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
    allData.value = [...allData.value]
  }

  const fIdx = filtered.value.findIndex(x => getPhone(x) === phoneStr)
  if (fIdx >= 0) {
    filtered.value = [...filtered.value]
  }
}

async function closeNotify() {
  notifyVisible.value = false
  try { await api.markRead() } catch(e) {}
}
</script>
