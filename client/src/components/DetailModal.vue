<template>
  <div class="modal" :class="{ show: visible }" @click.self="close">
    <div class="modal-box">
      <div class="modal-hd">
        <h3>线索详情</h3>
        <button class="modal-x" @click="close">&#10005;</button>
      </div>
      <div class="modal-bd">
        <div v-for="(k, idx) in displayKeys" :key="idx" class="detail-row">
          <div class="detail-l">{{ k }}</div>
          <div class="detail-v">{{ record[k] }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: Boolean,
  record: { type: Object, default: () => ({}) }
})
const emit = defineEmits(['close'])

const isXhs = computed(() => props.record['平台'] === '小红书')
const isAdChannel = computed(() => {
  const p = props.record['平台']
  return p === '抖音' || p === '小红书'
})

const displayKeys = computed(() => {
  const baseKeys = ['姓名','手机号','手机','平台','入库日期','创建时间','线索有效性','有效性','所属大区','所属招商','跟进员工','省份','城市','是否能加上微信','意向门店','线索阶段','线索标签','来源文件','备注','二次联系时间','二次联系备注','最近一次电联时间','到访时间','签约时间']
  if (isAdChannel.value) {
    baseKeys.push('流量类型')
  }
  if (isXhs.value) {
    baseKeys.push('小红书账号')
    baseKeys.push('用户小红书ID')
  }
  return baseKeys.filter(k => props.record[k] != null && String(props.record[k]).trim() !== '')
})

function close() { emit('close') }
</script>
