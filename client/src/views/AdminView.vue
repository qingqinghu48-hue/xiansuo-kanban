<template>
  <div>
    <div class="topbar">
      <div class="topbar-left">
        <div class="brand">
          <div class="brand-icon">招</div>
          <div class="brand-text">
            <h1>招商线索看板</h1>
            <span>管理后台</span>
          </div>
        </div>
      </div>
      <div class="topbar-right" style="display:flex;align-items:center;gap:12px">
        <router-link to="/dashboard" style="color:var(--primary);font-size:13px;font-weight:600;text-decoration:none">返回看板</router-link>
        <span>{{ userInfo.name || userInfo.username || '-' }}</span>
      </div>
    </div>
    <div class="main">
      <div class="section-title">管理操作</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px;margin-bottom:24px">
        <div class="chart-card" style="padding:20px">
          <h3 style="font-size:14px;font-weight:700;margin-bottom:12px">录入新线索</h3>
          <p style="font-size:12px;color:var(--text-3);margin-bottom:16px">手动录入单条招商线索信息</p>
          <button class="btn btn-pri" @click="showNewLead = true">打开录入表单</button>
        </div>
        <div class="chart-card" style="padding:20px">
          <h3 style="font-size:14px;font-weight:700;margin-bottom:12px">录入营销成本</h3>
          <p style="font-size:12px;color:var(--text-3);margin-bottom:16px">录入每日平台广告消耗</p>
          <button class="btn btn-pri" @click="showCost = true">打开成本录入</button>
        </div>
        <div class="chart-card" style="padding:20px">
          <h3 style="font-size:14px;font-weight:700;margin-bottom:12px">导入招商线索管理表</h3>
          <p style="font-size:12px;color:var(--text-3);margin-bottom:16px">批量导入招商线索数据</p>
          <button class="btn btn-pri" @click="importRef?.openZS()">开始导入</button>
        </div>
        <div class="chart-card" style="padding:20px">
          <h3 style="font-size:14px;font-weight:700;margin-bottom:12px">导入抖音渠道线索</h3>
          <p style="font-size:12px;color:var(--text-3);margin-bottom:16px">导入抖音广告渠道线索</p>
          <button class="btn btn-pri" @click="importRef?.openDY()">开始导入</button>
        </div>
        <div class="chart-card" style="padding:20px">
          <h3 style="font-size:14px;font-weight:700;margin-bottom:12px">导入小红书渠道线索</h3>
          <p style="font-size:12px;color:var(--text-3);margin-bottom:16px">导入小红书广告渠道线索</p>
          <button class="btn btn-pri" @click="importRef?.openXHS()">开始导入</button>
        </div>
      </div>
    </div>

    <CostModal :visible="showCost" @close="showCost = false" :costData="costData" @update="loadCost" />
    <ImportModals ref="importRef" />

    <!-- New lead modal -->
    <div class="modal" :class="{ show: showNewLead }" @click.self="showNewLead = false">
      <div class="modal-box" style="max-width:560px">
        <div class="modal-hd">
          <h3>录入新线索</h3>
          <button class="modal-x" @click="showNewLead = false">&#10005;</button>
        </div>
        <div class="modal-bd" style="padding:20px">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div class="cost-field" style="grid-column:1/-1">
              <label>手机号 *</label>
              <input type="text" v-model="newLead.phone" placeholder="请输入手机号">
            </div>
            <div class="cost-field">
              <label>线索平台 *</label>
              <select v-model="newLead.platform">
                <option value="">请选择</option>
                <option>400线索</option>
                <option>小红书</option>
                <option>转介绍</option>
                <option>豆包</option>
                <option>其他</option>
              </select>
            </div>
            <div class="cost-field">
              <label>录入日期 *</label>
              <input type="date" v-model="newLead.entry_date">
            </div>
            <div class="cost-field" style="grid-column:1/-1">
              <label>分配给 *</label>
              <select v-model="newLead.agent">
                <option value="">请选择招商员</option>
                <option v-for="a in agents" :key="a" :value="a">{{ a }}</option>
              </select>
            </div>
          </div>
          <div style="text-align:right;margin-top:16px">
            <button class="btn btn-ghost" @click="showNewLead = false">取消</button>
            <button class="btn btn-pri" style="margin-left:8px" @click="submitNewLead">录入线索</button>
          </div>
          <div :class="['cost-result', newResultType]">{{ newResult }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api.js'
import CostModal from '../components/CostModal.vue'
import ImportModals from '../components/ImportModals.vue'

const userInfo = ref({})
const showCost = ref(false)
const showNewLead = ref(false)
const importRef = ref(null)
const costData = ref([])
const router = useRouter()

const today = new Date().toISOString().slice(0,10)
const newLead = ref({ phone: '', platform: '', entry_date: today, agent: '' })
const newResult = ref('')
const newResultType = ref('')
const agents = ref([])

onMounted(async () => {
  try {
    const data = await api.getCurrentUser()
    const user = data.user || data
    if (user.role) userInfo.value = user
    else router.push('/login')
  } catch(e) { router.push('/login') }
  loadCost()
  loadAgents()
})

async function loadCost() {
  try { const data = await api.getCost(); costData.value = data || [] } catch(e) {}
}

async function loadAgents() {
  try {
    const res = await api.getLeads()
    const records = res.records || res
    const set = new Set()
    records.forEach(r => {
      const a = r['所属招商'] || r['跟进员工']
      if (a) set.add(a)
    })
    agents.value = Array.from(set).sort()
  } catch(e) {}
}

async function submitNewLead() {
  if (!newLead.value.phone || !newLead.value.platform || !newLead.value.agent) {
    newResult.value = '请填写完整信息'
    newResultType.value = 'err'
    return
  }
  try {
    const data = await api.addLead({
      phone: newLead.value.phone,
      platform: newLead.value.platform,
      agent: newLead.value.agent,
      entry_date: newLead.value.entry_date || today
    })
    if (data.success) {
      newResult.value = '线索录入成功'
      newResultType.value = 'ok'
      newLead.value = { phone: '', platform: '', entry_date: today, agent: '' }
    } else {
      newResult.value = data.message || '录入失败'
      newResultType.value = 'err'
    }
  } catch(e) { newResult.value = '网络错误'; newResultType.value = 'err' }
}
</script>
