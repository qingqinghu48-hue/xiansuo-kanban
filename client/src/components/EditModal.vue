<template>
  <div class="modal" :class="{ show: visible }" @click.self="close">
    <div class="modal-box" style="max-width:560px">
      <div class="modal-hd">
        <h3>编辑线索</h3>
        <button class="modal-x" @click="close">&#10005;</button>
      </div>
      <div class="modal-bd" style="padding:20px">
        <div class="modal-form-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <div class="cost-field"><label>客户姓名</label><input type="text" v-model="form['姓名']"></div>
          <div class="cost-field"><label>客户电话</label><input type="text" v-model="form['手机号']"></div>
          <div class="cost-field">
            <label>线索平台</label>
            <select v-model="form['平台']" :disabled="!isAdmin" :style="!isAdmin?roStyle:{}">
              <option value="">请选择</option>
              <option v-for="p in platforms" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>
          <div class="cost-field"><label>入库日期</label><input type="date" v-model="form['入库日期']" :readonly="!isAdmin" :style="!isAdmin?roStyle:{}" ></div>
          <div v-if="isXhs" class="cost-field"><label>用户小红书ID</label><input type="text" v-model="form['用户小红书ID']" placeholder="请输入用户小红书ID"></div>
          <div class="cost-field">
            <label>线索类型</label>
            <select v-model="form['线索类型']">
              <option value="">请选择</option>
              <option value="广告线索">广告线索</option>
              <option value="自然流线索">自然流线索</option>
            </select>
          </div>
          <div class="cost-field">
            <label>所属大区</label>
            <div class="multi-select-wrap" ref="regionWrap" style="display:block">
              <button type="button" class="filter-select multi-select-trigger" style="width:100%" @click.stop="regionOpen = !regionOpen">
                <span v-if="selectedRegions.length === 0">请选择大区</span>
                <span v-else-if="selectedRegions.length === 1">{{ selectedRegions[0] }}</span>
                <span v-else>已选 {{ selectedRegions.length }} 个大区</span>
                <span class="multi-caret" :class="{ open: regionOpen }">▼</span>
              </button>
              <div v-show="regionOpen" class="multi-select-dropdown" style="max-height:200px" @click.stop>
                <div class="multi-select-bd">
                  <label v-for="r in regions" :key="r" class="multi-select-item">
                    <input type="checkbox" :value="r" v-model="selectedRegions">
                    <span>{{ r }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
          <div class="cost-field"><label>所属城市</label><input type="text" v-model="form['城市']"></div>
          <div v-if="isAdmin" class="cost-field">
            <label>所属招商</label>
            <select v-model="form['所属招商']">
              <option value="">请选择</option>
              <option v-for="a in agents" :key="a" :value="a">{{ a }}</option>
            </select>
          </div>
          <div class="cost-field" style="grid-column:1/-1">
            <label>线索有效性</label>
            <select v-model="form['线索有效性']">
              <option value="">请选择</option>
              <option>意向客户</option>
              <option>一般客户</option>
              <option>未联系上</option>
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
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import api from '../api.js'
import { splitRegions } from '../utils.js'

const props = defineProps({
  visible: Boolean,
  record: { type: Object, default: () => ({}) },
  isAdmin: Boolean,
  regions: { type: Array, default: () => [] },
  platforms: { type: Array, default: () => [] },
  agents: { type: Array, default: () => [] }
})
const emit = defineEmits(['close', 'saved'])

const form = ref({})
const result = ref('')
const resultType = ref('')
const roStyle = { background: 'var(--surface2)', color: 'var(--text-3)' }

const regionOpen = ref(false)
const regionWrap = ref(null)
const selectedRegions = ref([])

const isXhs = computed(() => form.value['平台'] === '小红书')

watch(() => props.visible, (v) => {
  if (v) {
    result.value = ''
    selectedRegions.value = splitRegions(props.record['所属大区'])
    form.value = {
      '姓名': props.record['姓名'] || '',
      '手机号': props.record['手机号'] || props.record['手机'] || '',
      '平台': props.record['平台'] || '',
      '入库日期': String(props.record['入库日期'] || '').slice(0,10),
      '所属大区': props.record['所属大区'] || '',
      '城市': props.record['省份'] || props.record['城市'] || '',
      '用户小红书ID': props.record['用户小红书ID'] || '',
      '线索类型': props.record['线索类型'] || '',
      '线索有效性': props.record['线索有效性'] || props.record['有效性'] || '',
      '是否能加上微信': props.record['是否能加上微信'] || '',
      '备注': props.record['备注'] || '',
      '二次联系时间': props.record['二次联系时间'] || '',
      '二次联系备注': props.record['二次联系备注'] || '',
      '最近一次电联时间': props.record['最近一次电联时间'] || '',
      '到访时间': props.record['到访时间'] || '',
      '签约时间': props.record['签约时间'] || '',
      '所属招商': props.record['所属招商'] || ''
    }
  }
})

function onDocClick(e) {
  if (regionWrap.value && !regionWrap.value.contains(e.target)) {
    regionOpen.value = false
  }
}

onMounted(() => { document.addEventListener('click', onDocClick) })
onUnmounted(() => { document.removeEventListener('click', onDocClick) })

function close() { emit('close') }

async function save() {
  form.value['所属大区'] = selectedRegions.value.join('、')
  const payload = { phone: form.value['手机号'] }
  const fields = ['姓名','平台','入库日期','所属大区','城市','用户小红书ID','线索类型','线索有效性','是否能加上微信','备注','二次联系时间','二次联系备注','最近一次电联时间','到访时间','签约时间']
  fields.forEach(f => { payload[f] = form.value[f] })
  if (props.isAdmin) {
    payload['agent'] = form.value['所属招商']
  }
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

<style scoped>
@media(max-width:480px){
  .modal-form-grid{grid-template-columns:1fr !important}
}
</style>
