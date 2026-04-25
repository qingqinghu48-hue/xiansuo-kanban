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
      <!-- Tab 切换 -->
      <div style="display:flex;gap:8px;margin-bottom:20px;border-bottom:1px solid var(--border);padding-bottom:8px">
        <button class="tab-btn" :class="{ active: activeTab === 'ops' }" @click="activeTab = 'ops'">管理操作</button>
        <button class="tab-btn" :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">账号管理</button>
        <button class="tab-btn" :class="{ active: activeTab === 'platforms' }" @click="activeTab = 'platforms'">平台来源管理</button>
      </div>

      <!-- 管理操作 -->
      <div v-if="activeTab === 'ops'">
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

      <!-- 账号管理 -->
      <div v-if="activeTab === 'users'">
        <div class="chart-card" style="padding:20px;margin-bottom:16px">
          <h3 style="font-size:14px;font-weight:700;margin-bottom:12px">添加新账号</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr 120px;gap:12px;align-items:end">
            <div class="cost-field">
              <label>用户名（英文/数字）</label>
              <input type="text" v-model="newUser.username" placeholder="例如：zhangsan">
            </div>
            <div class="cost-field">
              <label>姓名</label>
              <input type="text" v-model="newUser.name" placeholder="例如：张三">
            </div>
            <button class="btn btn-pri" @click="createUser">创建账号</button>
          </div>
          <div :class="['cost-result', userResultType]" style="margin-top:8px">{{ userResult }}</div>
        </div>

        <div class="chart-card" style="padding:0;overflow:hidden">
          <table class="data-table">
            <thead>
              <tr>
                <th>用户名</th>
                <th>姓名</th>
                <th>角色</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in userList" :key="u.id">
                <td>{{ u.username }}</td>
                <td>{{ u.name }}</td>
                <td>{{ u.role === 'admin' ? '管理员' : u.role === 'agent' ? '招商员' : '游客' }}</td>
                <td>
                  <span :style="{ color: u.active ? 'var(--success)' : 'var(--danger)', fontSize: '12px', fontWeight: 600 }">
                    {{ u.active ? '正常' : '已停用' }}
                  </span>
                </td>
                <td>
                  <button v-if="u.role !== 'admin'" class="td-btn" @click="toggleUser(u)" style="margin-right:4px">
                    {{ u.active ? '停用' : '启用' }}
                  </button>
                  <button v-if="u.role !== 'admin'" class="td-btn" @click="deleteUser(u)" style="background:#fff;color:var(--danger);border-color:var(--danger)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 平台来源管理 -->
      <div v-if="activeTab === 'platforms'">
        <div class="chart-card" style="padding:20px;margin-bottom:16px">
          <h3 style="font-size:14px;font-weight:700;margin-bottom:12px">添加平台来源</h3>
          <div style="display:grid;grid-template-columns:1fr 120px;gap:12px;align-items:end">
            <div class="cost-field">
              <label>平台名称</label>
              <input type="text" v-model="newPlatformName" placeholder="例如：百度推广">
            </div>
            <button class="btn btn-pri" @click="addPlatform">添加</button>
          </div>
          <div :class="['cost-result', platformResultType]" style="margin-top:8px">{{ platformResult }}</div>
        </div>

        <div class="chart-card" style="padding:20px">
          <h3 style="font-size:14px;font-weight:700;margin-bottom:12px">现有平台来源</h3>
          <div style="display:flex;flex-wrap:wrap;gap:8px">
            <div v-for="p in platformList" :key="p" style="display:flex;align-items:center;gap:6px;padding:6px 12px;border-radius:var(--radius-xs);border:1px solid var(--border);background:#fff">
              <span style="font-size:13px">{{ p }}</span>
              <button @click="deletePlatform(p)" style="background:none;border:none;color:var(--danger);cursor:pointer;font-size:14px;line-height:1">&times;</button>
            </div>
          </div>
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
                <option v-for="p in platformList" :key="p" :value="p">{{ p }}</option>
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
const platformList = ref([])

// Tab
const activeTab = ref('ops')

// 账号管理
const userList = ref([])
const newUser = ref({ username: '', name: '' })
const userResult = ref('')
const userResultType = ref('')

// 平台管理
const newPlatformName = ref('')
const platformResult = ref('')
const platformResultType = ref('')

onMounted(async () => {
  try {
    const data = await api.getCurrentUser()
    const user = data.user || data
    if (user.role) userInfo.value = user
    else router.push('/login')
  } catch(e) { router.push('/login') }
  loadCost()
  loadAgents()
  loadPlatforms()
  loadUsers()
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

async function loadPlatforms() {
  try {
    const data = await api.getPlatforms()
    if (data.success) platformList.value = data.platforms || []
  } catch(e) {}
}

async function loadUsers() {
  try {
    const data = await api.getUsers()
    if (data.success) userList.value = data.users || []
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

// 账号管理
async function createUser() {
  userResult.value = ''
  const u = (newUser.value.username || '').trim()
  const n = (newUser.value.name || '').trim()
  if (!u || !n) {
    userResult.value = '用户名和姓名不能为空'
    userResultType.value = 'err'
    return
  }
  if (!/^[a-zA-Z0-9]+$/.test(u)) {
    userResult.value = '用户名只能包含英文和数字'
    userResultType.value = 'err'
    return
  }
  try {
    const data = await api.createUser({ username: u, name: n, role: 'agent' })
    userResult.value = data.message
    userResultType.value = data.success ? 'ok' : 'err'
    if (data.success) {
      newUser.value = { username: '', name: '' }
      loadUsers()
    }
  } catch(e) {
    userResult.value = '网络错误'
    userResultType.value = 'err'
  }
}

async function toggleUser(u) {
  if (!confirm(`确定${u.active ? '停用' : '启用'}账号 "${u.name}" 吗？`)) return
  try {
    const data = await api.toggleUser({ id: u.id })
    if (data.success) loadUsers()
    else alert(data.message)
  } catch(e) { alert('操作失败') }
}

async function deleteUser(u) {
  if (!confirm(`确定删除账号 "${u.name}" 吗？此操作不可恢复。`)) return
  try {
    const data = await api.deleteUser({ id: u.id })
    if (data.success) loadUsers()
    else alert(data.message)
  } catch(e) { alert('删除失败') }
}

// 平台管理
async function addPlatform() {
  platformResult.value = ''
  const n = (newPlatformName.value || '').trim()
  if (!n) {
    platformResult.value = '平台名称不能为空'
    platformResultType.value = 'err'
    return
  }
  try {
    const data = await api.addPlatform({ name: n })
    platformResult.value = data.message
    platformResultType.value = data.success ? 'ok' : 'err'
    if (data.success) {
      newPlatformName.value = ''
      loadPlatforms()
    }
  } catch(e) {
    platformResult.value = '网络错误'
    platformResultType.value = 'err'
  }
}

async function deletePlatform(name) {
  if (!confirm(`确定删除平台来源 "${name}" 吗？`)) return
  try {
    const data = await api.deletePlatform({ name })
    if (data.success) loadPlatforms()
    else alert(data.message)
  } catch(e) { alert('删除失败') }
}
</script>

<style scoped>
.tab-btn {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-2);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border-radius: var(--radius-xs);
  transition: all .15s;
}
.tab-btn:hover { color: var(--primary); }
.tab-btn.active { background: var(--primary); color: #fff; }
</style>
