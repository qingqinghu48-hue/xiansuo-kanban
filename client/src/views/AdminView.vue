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
            <div class="cost-field"><label>客户姓名</label><input type="text" v-model="newLead['姓名']"></div>
            <div class="cost-field"><label>客户电话</label><input type="text" v-model="newLead['手机号']"></div>
            <div class="cost-field"><label>线索平台</label><input type="text" v-model="newLead['平台']"></div>
            <div class="cost-field"><label>入库日期</label><input type="date" v-model="newLead['入库日期']" :value="today"></div>
            <div class="cost-field"><label>所属大区</label><input type="text" v-model="newLead['所属大区']"></div>
            <div class="cost-field"><label>所属城市</label><input type="text" v-model="newLead['省份']"></div>
            <div class="cost-field" style="grid-column:1/-1">
              <label>线索有效性</label>
              <select v-model="newLead['线索有效性']">
                <option value="">请选择</option>
                <option>意向客户</option>
                <option>一般客户</option>
                <option>未联系上</option>
                <option>普通线索</option>
                <option>无意向客户</option>
                <option>无效线索</option>
              </select>
            </div>
            <div class="cost-field" style="grid-column:1/-1">
              <label>能否加上微信</label>
              <select v-model="newLead['是否能加上微信']">
                <option value="">请选择</option>
                <option>是</option>
                <option>否</option>
              </select>
            </div>
            <div class="cost-field" style="grid-column:1/-1">
              <label>客户情况备注</label>
              <textarea v-model="newLead['备注']" rows="3" style="width:100%;padding:8px 12px;border:1px solid var(--border);border-radius:var(--radius-xs);font-family:inherit;font-size:13px;resize:vertical"></textarea>
            </div>
          </div>
          <div style="text-align:right;margin-top:16px">
            <button class="btn btn-ghost" @click="showNewLead = false">取消</button>
            <button class="btn btn-pri" style="margin-left:8px" @click="submitNewLead">保存</button>
          </div>
          <div :class="['cost-result', newResultType]">{{ newResult }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api.js'
import CostModal from '../components/CostModal.vue'
import ImportModals from '../components/ImportModals.vue'

const userInfo = ref({})
const showCost = ref(false)
const showNewLead = ref(false)
const importRef = ref(null)
const costData = ref([])

const newLead = ref({})
const newResult = ref('')
const newResultType = ref('')
const today = new Date().toISOString().slice(0,10)

onMounted(async () => {
  try {
    const data = await api.getCurrentUser()
    if (data.role) userInfo.value = data
    else window.location.href = '/login'
  } catch(e) { window.location.href = '/login' }
  loadCost()
})

async function loadCost() {
  try { const data = await api.getCost(); costData.value = data || [] } catch(e) {}
}

async function submitNewLead() {
  try {
    const data = await api.updateLead({ ...newLead.value, action: 'create' })
    if (data.success) { newResult.value = '录入成功'; newResultType.value = 'ok'; newLead.value = {} }
    else { newResult.value = data.message || '录入失败'; newResultType.value = 'err' }
  } catch(e) { newResult.value = '网络错误'; newResultType.value = 'err' }
}
</script>
