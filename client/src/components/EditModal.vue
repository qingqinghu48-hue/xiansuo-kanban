<template>
  <div class="modal" :class="{ show: visible }" @click.self="close">
    <div class="modal-box" style="max-width:560px">
      <div class="modal-hd">
        <h3>编辑线索</h3>
        <button class="modal-x" @click="close">&#10005;</button>
      </div>
      <div class="modal-bd" style="padding:20px">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <div class="cost-field"><label>客户姓名</label><input type="text" v-model="form['姓名']"></div>
          <div class="cost-field"><label>客户电话</label><input type="text" v-model="form['手机号']" readonly style="background:var(--surface2);color:var(--text-3)"></div>
          <div class="cost-field"><label>线索平台</label><input type="text" v-model="form['平台']" :readonly="!isAdmin" :style="!isAdmin?roStyle:{}" ></div>
          <div class="cost-field"><label>入库日期</label><input type="date" v-model="form['入库日期']" :readonly="!isAdmin" :style="!isAdmin?roStyle:{}" ></div>
          <div class="cost-field"><label>小红书账号</label><input type="text" v-model="form['小红书账号']" placeholder="请输入小红书账号"></div>
          <div class="cost-field">
            <label>线索类型</label>
            <select v-model="form['线索类型']">
              <option value="">请选择</option>
              <option value="广告线索">广告线索</option>
              <option value="自然流线索">自然流线索</option>
            </select>
          </div>
          <div class="cost-field"><label>所属大区</label><input type="text" v-model="form['所属大区']"></div>
          <div class="cost-field"><label>所属城市</label><input type="text" v-model="form['城市']"></div>
          <div class="cost-field" style="grid-column:1/-1">
            <label>线索有效性</label>
            <select v-model="form['线索有效性']">
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
            <select v-model="form['是否能加上微信']">
              <option value="">请选择</option>
              <option>是</option>
              <option>否</option>
            </select>
          </div>
          <div class="cost-field"><label>二次联系时间</label><input type="date" v-model="form['二次联系时间']"></div>
          <div class="cost-field"><label>二次联系备注</label><input type="text" v-model="form['二次联系备注']"></div>
          <div class="cost-field"><label>最近一次电联时间</label><input type="date" v-model="form['最近一次电联时间']"></div>
          <div class="cost-field"><label>到访时间</label><input type="date" v-model="form['到访时间']"></div>
          <div class="cost-field"><label>签约时间</label><input type="date" v-model="form['签约时间']"></div>
          <div class="cost-field" style="grid-column:1/-1">
            <label>客户情况备注</label>
            <textarea v-model="form['备注']" rows="3" style="width:100%;padding:8px 12px;border:1px solid var(--border);border-radius:var(--radius-xs);font-family:inherit;font-size:13px;resize:vertical"></textarea>
          </div>
        </div>
        <div style="text-align:right;margin-top:16px">
          <button class="btn btn-ghost" @click="close">取消</button>
          <button class="btn btn-pri" style="margin-left:8px" @click="save">保存</button>
        </div>
        <div :class="['cost-result', resultType]">{{ result }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '../api.js'

const props = defineProps({
  visible: Boolean,
  record: { type: Object, default: () => ({}) },
  isAdmin: Boolean
})
const emit = defineEmits(['close', 'saved'])

const form = ref({})
const result = ref('')
const resultType = ref('')
const roStyle = { background: 'var(--surface2)', color: 'var(--text-3)' }

watch(() => props.visible, (v) => {
  if (v) {
    result.value = ''
    form.value = {
      '姓名': props.record['姓名'] || '',
      '手机号': props.record['手机号'] || props.record['手机'] || '',
      '平台': props.record['平台'] || '',
      '入库日期': String(props.record['入库时间'] || props.record['入库日期'] || '').slice(0,10),
      '所属大区': props.record['所属大区'] || '',
      '城市': props.record['省份'] || props.record['城市'] || '',
      '小红书账号': props.record['小红书账号'] || '',
      '线索类型': props.record['线索类型'] || '',
      '线索有效性': props.record['线索有效性'] || props.record['有效性'] || '',
      '是否能加上微信': props.record['是否能加上微信'] || '',
      '备注': props.record['备注'] || '',
      '二次联系时间': props.record['二次联系时间'] || '',
      '二次联系备注': props.record['二次联系备注'] || '',
      '最近一次电联时间': props.record['最近一次电联时间'] || '',
      '到访时间': props.record['到访时间'] || '',
      '签约时间': props.record['签约时间'] || ''
    }
  }
})

function close() { emit('close') }

async function save() {
  const payload = { phone: form.value['手机号'] }
  const fields = ['姓名','平台','入库日期','所属大区','城市','小红书账号','线索类型','线索有效性','是否能加上微信','备注','二次联系时间','二次联系备注','最近一次电联时间','到访时间','签约时间']
  fields.forEach(f => { payload[f] = form.value[f] })
  try {
    const data = await api.updateLead(payload)
    if (data.success) {
      result.value = '保存成功'
      resultType.value = 'ok'
      emit('saved', payload)
      setTimeout(() => { close() }, 800)
    } else {
      result.value = data.message || '保存失败'
      resultType.value = 'err'
    }
  } catch(e) {
    result.value = '网络错误'
    resultType.value = 'err'
  }
}
</script>
