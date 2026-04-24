<template>
  <div class="modal" :class="{ show: visible }" @click.self="close">
    <div class="modal-box" style="max-width:580px">
      <div class="modal-hd">
        <h3>录入/管理营销成本</h3>
        <button class="modal-x" @click="close">&#10005;</button>
      </div>
      <div class="modal-bd" style="padding:24px">
        <div class="cost-form" style="margin-bottom:20px;padding:16px;background:#f8fafc;border-radius:8px;border:1px solid var(--border)">
          <div style="font-weight:700;color:var(--primary);margin-bottom:14px;font-size:14px;display:flex;align-items:center;gap:6px">
            <span style="font-size:16px">💰</span> 录入每日总消耗
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
            <div class="cost-field"><label>日期</label><input type="date" v-model="costForm.date"></div>
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

        <div class="cost-form" style="margin-bottom:20px;padding:16px;background:#fff7ed;border-radius:8px;border:1px solid #fed7aa">
          <div style="font-weight:700;color:#c2410c;margin-bottom:14px;font-size:14px;display:flex;align-items:center;gap:6px">
            <span style="font-size:16px">📊</span> 录入单条线索成本
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
            <div class="cost-field"><label>日期</label><input type="date" v-model="unitForm.date"></div>
            <div class="cost-field">
              <label>平台</label>
              <select v-model="unitForm.platform">
                <option value="抖音">抖音</option>
                <option value="小红书">小红书</option>
              </select>
            </div>
            <div class="cost-field"><label>单条成本（元/条）</label><input type="number" v-model="unitForm.amount" placeholder="手动指定" step="0.01" min="0"></div>
          </div>
          <div style="text-align:right;margin-top:12px">
            <button class="btn" style="background:#c2410c;color:#fff;border-color:#c2410c" @click="submitUnitCost">录入单条成本</button>
          </div>
        </div>

        <div>
          <div style="font-weight:700;color:var(--text);margin-bottom:12px;font-size:14px">🗑 删除历史记录</div>
          <div style="max-height:240px;overflow-y:auto;border:1px solid var(--border);border-radius:8px">
            <div v-if="!costData.length" style="color:var(--text-3);font-size:13px;text-align:center;padding:20px">暂无记录</div>
            <div v-for="c in costData" :key="c.id" style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid var(--border-2)">
              <span style="font-size:13px">{{ c.date }} {{ c.platform }} ¥{{ c.amount }}</span>
              <button class="td-btn" style="color:var(--danger);border-color:var(--danger)" @click="delCost(c.id)">删除</button>
            </div>
          </div>
        </div>

        <div :class="['cost-result', resultType]">{{ result }}</div>
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

const costForm = ref({ date: today(), platform: '抖音', amount: '' })
const unitForm = ref({ date: today(), platform: '抖音', amount: '' })
const result = ref('')
const resultType = ref('')

function today() { return new Date().toISOString().slice(0,10) }

function close() { emit('close') }

async function submitCost() {
  if (!costForm.value.date || !costForm.value.amount) { result.value = '请填写完整'; resultType.value = 'err'; return }
  try {
    const data = await api.submitCost(costForm.value)
    if (data.success) { result.value = '录入成功'; resultType.value = 'ok'; emit('update'); costForm.value.amount = '' }
    else { result.value = data.message || '录入失败'; resultType.value = 'err' }
  } catch(e) { result.value = '网络错误'; resultType.value = 'err' }
}

async function submitUnitCost() {
  if (!unitForm.value.date || !unitForm.value.amount) { result.value = '请填写完整'; resultType.value = 'err'; return }
  try {
    const data = await api.submitUnitCost(unitForm.value)
    if (data.success) { result.value = '录入成功'; resultType.value = 'ok'; emit('update'); unitForm.value.amount = '' }
    else { result.value = data.message || '录入失败'; resultType.value = 'err' }
  } catch(e) { result.value = '网络错误'; resultType.value = 'err' }
}

async function delCost(id) {
  if (!confirm('确定删除这条记录？')) return
  try {
    const data = await api.deleteCost(id)
    if (data.success) { result.value = '删除成功'; resultType.value = 'ok'; emit('update') }
    else { result.value = data.message || '删除失败'; resultType.value = 'err' }
  } catch(e) { result.value = '网络错误'; resultType.value = 'err' }
}
</script>
