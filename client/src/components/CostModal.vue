<template>
  <div class="modal" :class="{ show: visible }" @click.self="close">
    <div class="modal-box" style="max-width:620px">
      <div class="modal-hd">
        <h3>录入/管理营销成本</h3>
        <button class="modal-x" @click="close">&#10005;</button>
      </div>
      <div class="modal-bd" style="padding:24px">
        <!-- 每日总消耗 -->
        <div class="cost-form" style="margin-bottom:20px;padding:16px;background:#f8fafc;border-radius:8px;border:1px solid var(--border)">
          <div style="font-weight:700;color:var(--primary);margin-bottom:14px;font-size:14px;display:flex;align-items:center;gap:6px">
            <span style="font-size:16px">💰</span> 录入每日总消耗
          </div>
          <div class="cost-form-grid" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
            <div class="cost-field"><label>日期</label><input type="date" v-model="costForm.cost_date"></div>
            <div class="cost-field">
              <label>平台</label>
              <select v-model="costForm.platform">
                <option value="抖音">抖音</option>
                <option value="小红书">小红书</option>
              </select>
            </div>
            <div class="cost-field"><label>总消耗（元）</label><input type="number" v-model="costForm.amount" placeholder="输入金额" step="0.01" min="0"></div>
          </div>
          <div style="text-align:right;margin-top:12px">
            <button class="btn btn-pri" @click="submitCost">确认录入</button>
          </div>
        </div>

        <!-- 单条线索成本 -->
        <div class="cost-form" style="margin-bottom:20px;padding:16px;background:#fff7ed;border-radius:8px;border:1px solid #fed7aa">
          <div style="font-weight:700;color:#c2410c;margin-bottom:14px;font-size:14px;display:flex;align-items:center;gap:6px">
            <span style="font-size:16px">📊</span> 录入单条线索成本
          </div>
          <div class="cost-form-grid" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
            <div class="cost-field"><label>日期</label><input type="date" v-model="unitForm.cost_date"></div>
            <div class="cost-field">
              <label>平台</label>
              <select v-model="unitForm.platform">
                <option value="抖音">抖音</option>
                <option value="小红书">小红书</option>
              </select>
            </div>
            <div class="cost-field"><label>单条成本（元/条）</label><input type="number" v-model="unitForm.unit_cost" placeholder="手动指定" step="0.01" min="0"></div>
          </div>
          <div style="text-align:right;margin-top:12px">
            <button class="btn" style="background:#c2410c;color:#fff;border-color:#c2410c" @click="submitUnitCost">录入单条成本</button>
          </div>
        </div>

        <!-- 历史记录 -->
        <div>
          <div style="font-weight:700;color:var(--text);margin-bottom:12px;font-size:14px">🗑 历史记录（点击编辑修改）</div>
          <div style="max-height:280px;overflow-y:auto;border:1px solid var(--border);border-radius:8px">
            <div v-if="!costData.length" style="color:var(--text-3);font-size:13px;text-align:center;padding:20px">暂无记录</div>
            <div v-for="c in costData" :key="c.id" style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid var(--border-2)">
              <template v-if="editingId === c.id">
                <div style="display:flex;align-items:center;gap:8px;flex:1">
                  <span style="font-size:12px;color:var(--text-3)">{{ c.date }}</span>
                  <span style="font-size:12px;color:var(--text-3)">{{ c.platform }}</span>
                  <input v-model="editAmount" type="number" step="0.01" style="width:80px;font-size:12px;padding:2px 4px;border:1px solid var(--primary);border-radius:4px" placeholder="总消耗">
                  <input v-model="editUnitCost" type="number" step="0.01" style="width:80px;font-size:12px;padding:2px 4px;border:1px solid var(--primary);border-radius:4px" placeholder="单条成本">
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
                  <span style="color:var(--text-3)">单条 ¥{{ Number(c.unit_cost||0).toFixed(2) }}</span>
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

const costForm = ref({ cost_date: today(), platform: '抖音', amount: '' })
const unitForm = ref({ cost_date: today(), platform: '抖音', unit_cost: '' })
const result = ref('')
const resultType = ref('')

// 编辑状态
const editingId = ref(null)
const editAmount = ref('')
const editUnitCost = ref('')

function today() { return new Date().toISOString().slice(0,10) }

function close() { emit('close') }

function showMsg(msg, type) {
  result.value = msg
  resultType.value = type
}

async function submitCost() {
  if (!costForm.value.cost_date || !costForm.value.amount) { showMsg('请填写完整', 'err'); return }
  try {
    const data = await api.submitCost({
      cost_date: costForm.value.cost_date,
      platform: costForm.value.platform,
      amount: parseFloat(costForm.value.amount) || 0
    })
    if (data.success) { showMsg('录入成功', 'ok'); emit('update'); costForm.value.amount = '' }
    else { showMsg(data.message || '录入失败', 'err') }
  } catch(e) { showMsg('网络错误', 'err') }
}

async function submitUnitCost() {
  if (!unitForm.value.cost_date || !unitForm.value.unit_cost) { showMsg('请填写完整', 'err'); return }
  try {
    const data = await api.submitUnitCost({
      cost_date: unitForm.value.cost_date,
      platform: unitForm.value.platform,
      unit_cost: parseFloat(unitForm.value.unit_cost) || 0
    })
    if (data.success) { showMsg('录入成功', 'ok'); emit('update'); unitForm.value.unit_cost = '' }
    else { showMsg(data.message || '录入失败', 'err') }
  } catch(e) { showMsg('网络错误', 'err') }
}

function startEdit(c) {
  editingId.value = c.id
  editAmount.value = c.amount || 0
  editUnitCost.value = c.unit_cost || 0
}

function cancelEdit() {
  editingId.value = null
  editAmount.value = ''
  editUnitCost.value = ''
}

async function saveEdit(id) {
  try {
    const data = await api.updateCost({
      id,
      amount: parseFloat(editAmount.value) || 0,
      unit_cost: parseFloat(editUnitCost.value) || 0
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
</script>

<style scoped>
@media(max-width:640px){
  .cost-form-grid{grid-template-columns:1fr !important}
}
</style>
