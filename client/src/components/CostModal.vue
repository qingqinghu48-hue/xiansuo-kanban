<template>
  <div class="modal" :class="{ show: visible }" @click.self="close">
    <div class="modal-box" style="max-width:680px">
      <div class="modal-hd">
        <h3>录入/管理营销成本</h3>
        <button class="modal-x" @click="close">&#10005;</button>
      </div>
      <div class="modal-bd" style="padding:24px">
        <!-- 录入每日消耗 -->
        <div class="cost-form" style="margin-bottom:20px;padding:16px;background:#f8fafc;border-radius:8px;border:1px solid var(--border)">
          <div style="font-weight:700;color:var(--primary);margin-bottom:14px;font-size:14px;display:flex;align-items:center;gap:6px">
            <span style="font-size:16px">💰</span> 录入每日总消耗
          </div>
          <div class="cost-form-grid" style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px">
            <div class="cost-field"><label>日期</label><input type="date" v-model="costForm.cost_date" @keyup.enter="submitCost"></div>
            <div class="cost-field">
              <label>平台</label>
              <select v-model="costForm.platform" @keyup.enter="submitCost">
                <option value="抖音">抖音</option>
                <option value="小红书">小红书</option>
              </select>
            </div>
            <div class="cost-field"><label>总消耗（元）</label><input type="number" v-model="costForm.amount" placeholder="输入金额" step="0.01" min="0" @keyup.enter="submitCost"></div>
            <div class="cost-field"><label>获得线索数</label><input type="number" v-model="costForm.lead_count" placeholder="输入数量" step="1" min="0" @keyup.enter="submitCost"></div>
          </div>
          <div style="text-align:right;margin-top:12px">
            <button class="btn btn-pri" @click="submitCost">确认录入</button>
          </div>
        </div>

        <!-- 批量导入 -->
        <div class="cost-form" style="margin-bottom:20px;padding:16px;background:#f0fdf4;border-radius:8px;border:1px solid #bbf7d0">
          <div style="font-weight:700;color:#15803d;margin-bottom:14px;font-size:14px;display:flex;align-items:center;gap:6px">
            <span style="font-size:16px">📥</span> 批量导入抖音线索消耗
          </div>
          <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px">
            <button class="btn btn-ghost" style="font-size:12px" @click="downloadTemplate">
              ⬇️ 下载模板（CSV）
            </button>
          </div>
          <div
            class="import-dropzone"
            :class="{ dragover: isDragOver }"
            @dragenter.prevent="isDragOver = true"
            @dragleave.prevent="isDragOver = false"
            @dragover.prevent
            @drop.prevent="onDrop"
            @click="fileInput?.click()"
            style="border:2px dashed #86efac;border-radius:8px;padding:20px;text-align:center;cursor:pointer;transition:border-color .2s;background:#fff"
          >
            <input ref="fileInput" type="file" accept=".csv,.xlsx,.xls" style="display:none" @change="onFileChange">
            <div style="font-size:24px;margin-bottom:6px">📁</div>
            <div style="font-size:13px;color:#15803d;font-weight:600">点击或拖拽文件到此处</div>
            <div v-if="pendingFile" style="font-size:12px;color:#15803d;margin-top:4px;font-weight:600">已选择：{{ pendingFile.name }}</div>
            <div v-else style="font-size:12px;color:#86a78f;margin-top:4px">支持 CSV、XLSX 格式</div>
          </div>
          <div style="text-align:right;margin-top:12px">
            <button v-if="!costImportPending && !costImportConfirm && pendingFile" class="btn btn-pri" @click="previewCostImport">预览导入</button>
            <button v-if="costImportConfirm" class="btn btn-pri" @click="doCostImport">确认导入</button>
            <button v-if="costImportConfirm" class="btn btn-ghost" @click="cancelCostConfirm" style="margin-left:8px">取消</button>
          </div>
          <div v-if="costImportPending" class="cost-result" style="margin-top:10px;color:var(--text-2)">正在解析...</div>
          <div v-else-if="importResult" :class="['cost-result', importResultType]" style="margin-top:10px">{{ importResult }}</div>
        </div>

        <!-- 历史记录 -->
        <div>
          <div style="font-weight:700;color:var(--text);margin-bottom:12px;font-size:14px">🗑 历史记录（点击编辑修改）</div>
          <div style="max-height:280px;overflow-y:auto;border:1px solid var(--border);border-radius:8px">
            <div v-if="!costData.length" style="color:var(--text-3);font-size:13px;text-align:center;padding:20px">暂无记录</div>
            <div v-for="c in costData" :key="c.id" style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid var(--border-2)">
              <template v-if="editingId === c.id">
                <div style="display:flex;align-items:center;gap:8px;flex:1;flex-wrap:wrap">
                  <span style="font-size:12px;color:var(--text-3)">{{ c.date }}</span>
                  <span style="font-size:12px;color:var(--text-3)">{{ c.platform }}</span>
                  <input v-model="editAmount" type="number" step="0.01" style="width:80px;font-size:12px;padding:2px 4px;border:1px solid var(--primary);border-radius:4px" placeholder="总消耗">
                  <input v-model="editLeadCount" type="number" step="1" style="width:80px;font-size:12px;padding:2px 4px;border:1px solid var(--primary);border-radius:4px" placeholder="线索数">
                </div>
                <div style="display:flex;gap:4px">
                  <button style="background:none;border:none;color:var(--success);cursor:pointer;font-size:13px" @click="saveEdit(c.id)">✓</button>
                  <button style="background:none;border:none;color:var(--text-3);cursor:pointer;font-size:13px" @click="cancelEdit">✕</button>
                </div>
              </template>
              <template v-else>
                <span style="font-size:13px">
                  {{ c.date }} {{ c.platform }}
                  <span style="color:var(--text-2)">总消耗 ¥{{ Number(c.amount||0).toFixed(2) }}</span>
                  <span style="color:var(--text-3)">线索 {{ Number(c.lead_count||0).toFixed(0) }} 条</span>
                  <span style="color:var(--primary)">单条 ¥{{ Number(c.unit_cost||0).toFixed(2) }}</span>
                </span>
                <div style="display:flex;gap:4px">
                  <button style="background:none;border:none;color:var(--primary);cursor:pointer;font-size:12px" @click="startEdit(c)">编辑</button>
                  <button style="background:none;border:none;color:var(--danger);cursor:pointer;font-size:12px" @click="delCost(c.id)">删除</button>
                </div>
              </template>
            </div>
          </div>
        </div>

        <div :class="['cost-result', resultType]" style="margin-top:12px">{{ result }}</div>
        <div style="margin-top:16px;text-align:right">
          <button class="btn btn-ghost" @click="close">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api.js'

const props = defineProps({
  visible: Boolean,
  costData: { type: Array, default: () => [] }
})
const emit = defineEmits(['close', 'update'])

const costForm = ref({ cost_date: today(), platform: '抖音', amount: '', lead_count: '' })
const result = ref('')
const resultType = ref('')

// 批量导入
const fileInput = ref(null)
const isDragOver = ref(false)
const importResult = ref('')
const importResultType = ref('')
const pendingFile = ref(null)
const costImportPending = ref(false)
const costImportConfirm = ref(false)

// 编辑状态
const editingId = ref(null)
const editAmount = ref('')
const editLeadCount = ref('')

function today() { return new Date().toISOString().slice(0,10) }

function close() { emit('close') }

function showMsg(msg, type) {
  result.value = msg
  resultType.value = type
}

function resetCostImport() {
  pendingFile.value = null
  costImportPending.value = false
  costImportConfirm.value = false
  importResult.value = ''
  importResultType.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

async function submitCost() {
  if (!costForm.value.cost_date || !costForm.value.amount) { showMsg('请填写完整', 'err'); return }
  try {
    const data = await api.submitCost({
      cost_date: costForm.value.cost_date,
      platform: costForm.value.platform,
      amount: parseFloat(costForm.value.amount) || 0,
      lead_count: parseFloat(costForm.value.lead_count) || 0
    })
    if (data.success) {
      showMsg('录入成功', 'ok')
      emit('update')
      costForm.value.amount = ''
      costForm.value.lead_count = ''
    } else { showMsg(data.message || '录入失败', 'err') }
  } catch(e) { showMsg('网络错误', 'err') }
}

function startEdit(c) {
  editingId.value = c.id
  editAmount.value = c.amount || 0
  editLeadCount.value = c.lead_count || 0
}

function cancelEdit() {
  editingId.value = null
  editAmount.value = ''
  editLeadCount.value = ''
}

async function saveEdit(id) {
  try {
    const data = await api.updateCost({
      id,
      amount: parseFloat(editAmount.value) || 0,
      lead_count: parseFloat(editLeadCount.value) || 0
    })
    if (data.success) {
      showMsg('更新成功', 'ok')
      editingId.value = null
      emit('update')
    } else {
      showMsg(data.message || '更新失败', 'err')
    }
  } catch(e) { showMsg('网络错误', 'err') }
}

async function delCost(id) {
  if (!confirm('确定删除这条记录？')) return
  try {
    const data = await api.deleteCost(id)
    if (data.success) { showMsg('删除成功', 'ok'); emit('update') }
    else { showMsg(data.message || '删除失败', 'err') }
  } catch(e) { showMsg('网络错误', 'err') }
}

// 下载模板（抖音线索消耗：日期、营销场景、消耗(元)、转化成本(元)、转化数）
function downloadTemplate() {
  const header = '日期,营销场景,消耗(元),转化成本(元),转化数\n'
  const sample = [
    '2026-04-20,短视频,2785.96,278.60,10',
    '2026-04-19,短视频,2533.68,281.52,9',
    '2026-04-18,短视频,2975.04,371.88,8',
  ].join('\n') + '\n'
  const blob = new Blob(['\uFEFF' + header + sample], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '抖音线索消耗导入模板.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// 文件选择
function onFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    pendingFile.value = file
    costImportConfirm.value = false
    importResult.value = ''
    importResultType.value = ''
  }
}

// 拖拽导入
function onDrop(e) {
  isDragOver.value = false
  const file = e.dataTransfer.files[0]
  if (file) {
    pendingFile.value = file
    costImportConfirm.value = false
    importResult.value = ''
    importResultType.value = ''
  }
}

// 预览导入
async function previewCostImport() {
  if (!pendingFile.value) { importResult.value = '请选择文件'; importResultType.value = 'err'; return }
  costImportPending.value = true
  importResult.value = ''
  const formData = new FormData()
  formData.append('file', pendingFile.value)
  try {
    const data = await api.importCost(formData, true)
    costImportPending.value = false
    if (data.success && data.preview) {
      costImportConfirm.value = true
      importResult.value = '【预览】' + data.message + '，确认后写入数据库'
      importResultType.value = 'ok'
    } else {
      importResult.value = data.message || '预览失败'
      importResultType.value = 'err'
    }
  } catch(e) {
    costImportPending.value = false
    importResult.value = '网络错误，请重试'
    importResultType.value = 'err'
  }
}

// 确认导入
async function doCostImport() {
  if (!pendingFile.value) { importResult.value = '文件已失效，请重新选择'; importResultType.value = 'err'; return }
  costImportPending.value = true
  const formData = new FormData()
  formData.append('file', pendingFile.value)
  try {
    const data = await api.importCost(formData, false)
    costImportPending.value = false
    costImportConfirm.value = false
    if (data.success) {
      importResult.value = data.message
      importResultType.value = 'ok'
      emit('update')
      pendingFile.value = null
      if (fileInput.value) fileInput.value.value = ''
    } else {
      importResult.value = data.message || '导入失败'
      importResultType.value = 'err'
    }
  } catch(e) {
    costImportPending.value = false
    importResult.value = '网络错误，请重试'
    importResultType.value = 'err'
  }
}

function cancelCostConfirm() {
  costImportConfirm.value = false
  importResult.value = ''
  importResultType.value = ''
}
</script>

<style scoped>
.import-dropzone:hover,
.import-dropzone.dragover {
  border-color: #15803d !important;
  background: #f0fdf4 !important;
}
@media(max-width:860px){
  .cost-form-grid{grid-template-columns:repeat(2,minmax(0,1fr)) !important}
}
@media(max-width:640px){
  .cost-form-grid{grid-template-columns:1fr !important}
}
</style>
