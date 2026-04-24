<template>
  <div>
    <!-- 招商线索管理表导入 -->
    <div class="modal" :class="{ show: showZS }" @click.self="showZS = false">
      <div class="modal-box" style="max-width:520px">
        <div class="modal-hd">
          <h3>导入招商线索管理表</h3>
          <button class="modal-x" @click="showZS = false">&#10005;</button>
        </div>
        <div class="modal-bd" style="padding:24px">
          <div class="cost-form" style="margin-bottom:16px">
            <div style="font-size:13px;color:var(--text-2);margin-bottom:12px;line-height:1.6">
              <p>请选择 Excel 文件（.xlsx / .xls）</p>
              <p style="margin-top:4px">支持增量更新：已存在手机号的线索会更新其他信息，抖音/小红书平台的入库日期不会修改。</p>
            </div>
            <div class="cost-field"><label>文件</label><input type="file" ref="zsFile" accept=".xlsx,.xls"></div>
            <div style="text-align:right;margin-top:16px">
              <button class="btn btn-pri" @click="importFile('zs', $refs.zsFile)">开始导入</button>
            </div>
          </div>
          <div :class="['cost-result', zsResultType]">{{ zsResult }}</div>
        </div>
      </div>
    </div>

    <!-- 抖音渠道导入 -->
    <div class="modal" :class="{ show: showDY }" @click.self="showDY = false">
      <div class="modal-box" style="max-width:520px">
        <div class="modal-hd">
          <h3>导入抖音渠道线索</h3>
          <button class="modal-x" @click="showDY = false">&#10005;</button>
        </div>
        <div class="modal-bd" style="padding:24px">
          <div class="cost-form" style="margin-bottom:16px">
            <div style="font-size:13px;color:var(--text-2);margin-bottom:12px;line-height:1.6">
              <p>请选择 Excel 文件（.xlsx / .xls）</p>
              <p style="margin-top:4px">只导入新线索：已存在手机号的线索会跳过，不更新已有数据。</p>
            </div>
            <div class="cost-field"><label>文件</label><input type="file" ref="dyFile" accept=".xlsx,.xls"></div>
            <div style="text-align:right;margin-top:16px">
              <button class="btn btn-pri" @click="importFile('dy', $refs.dyFile)">开始导入</button>
            </div>
          </div>
          <div :class="['cost-result', dyResultType]">{{ dyResult }}</div>
        </div>
      </div>
    </div>

    <!-- 小红书渠道导入 -->
    <div class="modal" :class="{ show: showXHS }" @click.self="showXHS = false">
      <div class="modal-box" style="max-width:520px">
        <div class="modal-hd">
          <h3>导入小红书渠道线索</h3>
          <button class="modal-x" @click="showXHS = false">&#10005;</button>
        </div>
        <div class="modal-bd" style="padding:24px">
          <div class="cost-form" style="margin-bottom:16px">
            <div style="font-size:13px;color:var(--text-2);margin-bottom:12px;line-height:1.6">
              <p>请选择 Excel 文件（.xlsx / .xls）</p>
              <p style="margin-top:4px">只导入新线索：已存在手机号的线索会跳过，不更新已有数据。</p>
            </div>
            <div class="cost-field"><label>文件</label><input type="file" ref="xhsFile" accept=".xlsx,.xls"></div>
            <div style="text-align:right;margin-top:16px">
              <button class="btn btn-pri" @click="importFile('xhs', $refs.xhsFile)">开始导入</button>
            </div>
          </div>
          <div :class="['cost-result', xhsResultType]">{{ xhsResult }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api.js'

const showZS = ref(false)
const showDY = ref(false)
const showXHS = ref(false)

const zsResult = ref('')
const zsResultType = ref('')
const dyResult = ref('')
const dyResultType = ref('')
const xhsResult = ref('')
const xhsResultType = ref('')

function openZS() { showZS.value = true; zsResult.value = '' }
function openDY() { showDY.value = true; dyResult.value = '' }
function openXHS() { showXHS.value = true; xhsResult.value = '' }

async function importFile(type, fileInput) {
  const file = fileInput?.files?.[0]
  if (!file) { setResult(type, '请选择文件', 'err'); return }
  const fd = new FormData()
  fd.append('file', file)
  try {
    const data = await api.importFile(type, fd)
    if (data.success) { setResult(type, data.message || '导入成功', 'ok') }
    else { setResult(type, data.message || '导入失败', 'err') }
  } catch(e) { setResult(type, '网络错误', 'err') }
}

function setResult(type, msg, rtype) {
  if (type === 'zs') { zsResult.value = msg; zsResultType.value = rtype }
  if (type === 'dy') { dyResult.value = msg; dyResultType.value = rtype }
  if (type === 'xhs') { xhsResult.value = msg; xhsResultType.value = rtype }
}

defineExpose({ openZS, openDY, openXHS })
</script>
