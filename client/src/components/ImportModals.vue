<template>
  <div>
    <!-- 招商线索管理表导入 -->
    <div class="modal" :class="{ show: showZS }" @click.self="closeZS">
      <div class="modal-box" style="max-width:520px">
        <div class="modal-hd">
          <h3>导入招商线索管理表</h3>
          <button class="modal-x" @click="closeZS">&#10005;</button>
        </div>
        <div class="modal-bd" style="padding:24px">
          <div class="cost-form" style="margin-bottom:16px">
            <div style="font-size:13px;color:var(--text-2);margin-bottom:12px;line-height:1.6">
              <p>请选择 Excel 文件（.xlsx / .xls）</p>
              <p style="margin-top:4px">支持增量更新：已存在手机号的线索会更新其他信息，抖音/小红书平台的入库日期不会修改。</p>
            </div>
            <div class="cost-field"><label>文件</label><input type="file" ref="zsFile" accept=".xlsx,.xls" @change="onFileChange('zs')"></div>
            <div style="text-align:right;margin-top:16px">
              <button v-if="!zsPending && !zsConfirm" class="btn btn-pri" @click="previewImport('zs')">预览导入</button>
              <button v-if="zsConfirm" class="btn btn-pri" @click="doImport('zs')">确认导入</button>
              <button v-if="zsConfirm" class="btn btn-ghost" @click="cancelConfirm('zs')" style="margin-left:8px">取消</button>
            </div>
          </div>
          <div v-if="zsPending" class="cost-result" style="color:var(--text-2)">正在解析...</div>
          <div v-else :class="['cost-result', zsResultType]">{{ zsResult }}</div>
        </div>
      </div>
    </div>

    <!-- 抖音渠道导入 -->
    <div class="modal" :class="{ show: showDY }" @click.self="closeDY">
      <div class="modal-box" style="max-width:520px">
        <div class="modal-hd">
          <h3>导入抖音渠道线索</h3>
          <button class="modal-x" @click="closeDY">&#10005;</button>
        </div>
        <div class="modal-bd" style="padding:24px">
          <div class="cost-form" style="margin-bottom:16px">
            <div style="font-size:13px;color:var(--text-2);margin-bottom:12px;line-height:1.6">
              <p>请选择 Excel 文件（.xlsx / .xls）</p>
              <p style="margin-top:4px">只导入新线索：已存在手机号的线索会跳过，不更新已有数据。</p>
            </div>
            <div class="cost-field"><label>文件</label><input type="file" ref="dyFile" accept=".xlsx,.xls" @change="onFileChange('dy')"></div>
            <div style="text-align:right;margin-top:16px">
              <button v-if="!dyPending && !dyConfirm" class="btn btn-pri" @click="previewImport('dy')">预览导入</button>
              <button v-if="dyConfirm" class="btn btn-pri" @click="doImport('dy')">确认导入</button>
              <button v-if="dyConfirm" class="btn btn-ghost" @click="cancelConfirm('dy')" style="margin-left:8px">取消</button>
            </div>
          </div>
          <div v-if="dyPending" class="cost-result" style="color:var(--text-2)">正在解析...</div>
          <div v-else :class="['cost-result', dyResultType]">{{ dyResult }}</div>
        </div>
      </div>
    </div>

    <!-- 小红书渠道导入 -->
    <div class="modal" :class="{ show: showXHS }" @click.self="closeXHS">
      <div class="modal-box" style="max-width:520px">
        <div class="modal-hd">
          <h3>导入小红书渠道线索</h3>
          <button class="modal-x" @click="closeXHS">&#10005;</button>
        </div>
        <div class="modal-bd" style="padding:24px">
          <div class="cost-form" style="margin-bottom:16px">
            <div style="font-size:13px;color:var(--text-2);margin-bottom:12px;line-height:1.6">
              <p>请选择 Excel 文件（.xlsx / .xls）</p>
              <p style="margin-top:4px">只导入新线索：已存在手机号的线索会跳过，不更新已有数据。</p>
            </div>
            <div class="cost-field"><label>文件</label><input type="file" ref="xhsFile" accept=".xlsx,.xls" @change="onFileChange('xhs')"></div>
            <div style="text-align:right;margin-top:16px">
              <button v-if="!xhsPending && !xhsConfirm" class="btn btn-pri" @click="previewImport('xhs')">预览导入</button>
              <button v-if="xhsConfirm" class="btn btn-pri" @click="doImport('xhs')">确认导入</button>
              <button v-if="xhsConfirm" class="btn btn-ghost" @click="cancelConfirm('xhs')" style="margin-left:8px">取消</button>
            </div>
          </div>
          <div v-if="xhsPending" class="cost-result" style="color:var(--text-2)">正在解析...</div>
          <div v-else :class="['cost-result', xhsResultType]">{{ xhsResult }}</div>
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

const zsPending = ref(false)
const dyPending = ref(false)
const xhsPending = ref(false)
const zsConfirm = ref(false)
const dyConfirm = ref(false)
const xhsConfirm = ref(false)

const zsFile = ref(null)
const dyFile = ref(null)
const xhsFile = ref(null)

const previewData = { zs: null, dy: null, xhs: null }

function openZS() { showZS.value = true; reset('zs') }
function openDY() { showDY.value = true; reset('dy') }
function openXHS() { showXHS.value = true; reset('xhs') }

function closeZS() { showZS.value = false; reset('zs') }
function closeDY() { showDY.value = false; reset('dy') }
function closeXHS() { showXHS.value = false; reset('xhs') }

function reset(type) {
  setResult(type, '', '')
  setPending(type, false)
  setConfirm(type, false)
  previewData[type] = null
}

function onFileChange(type) {
  setConfirm(type, false)
  setResult(type, '', '')
  previewData[type] = null
}

function getFileInput(type) {
  if (type === 'zs') return zsFile.value
  if (type === 'dy') return dyFile.value
  return xhsFile.value
}

async function previewImport(type) {
  const fileInput = getFileInput(type)
  const file = fileInput?.files?.[0]
  if (!file) { setResult(type, '请选择文件', 'err'); return }

  setPending(type, true)
  const fd = new FormData()
  fd.append('file', file)
  try {
    const data = await api.importFile(type, fd, true)
    setPending(type, false)
    if (data.success && data.preview) {
      previewData[type] = fd
      setConfirm(type, true)
      setResult(type, '【预览】' + data.message + '，确认后写入数据库', 'ok')
    } else {
      setResult(type, data.message || '预览失败', 'err')
    }
  } catch(e) {
    setPending(type, false)
    setResult(type, '网络错误', 'err')
  }
}

async function doImport(type) {
  const fileInput = getFileInput(type)
  const file = fileInput?.files?.[0]
  if (!file) { setResult(type, '文件已失效，请重新选择', 'err'); return }

  setPending(type, true)
  const fd = new FormData()
  fd.append('file', file)
  try {
    const data = await api.importFile(type, fd, false)
    setPending(type, false)
    setConfirm(type, false)
    if (data.success) {
      setResult(type, data.message || '导入成功', 'ok')
    } else {
      setResult(type, data.message || '导入失败', 'err')
    }
  } catch(e) {
    setPending(type, false)
    setResult(type, '网络错误', 'err')
  }
}

function cancelConfirm(type) {
  setConfirm(type, false)
  setResult(type, '', '')
  previewData[type] = null
}

function setResult(type, msg, rtype) {
  if (type === 'zs') { zsResult.value = msg; zsResultType.value = rtype }
  if (type === 'dy') { dyResult.value = msg; dyResultType.value = rtype }
  if (type === 'xhs') { xhsResult.value = msg; xhsResultType.value = rtype }
}

function setPending(type, v) {
  if (type === 'zs') zsPending.value = v
  if (type === 'dy') dyPending.value = v
  if (type === 'xhs') xhsPending.value = v
}

function setConfirm(type, v) {
  if (type === 'zs') zsConfirm.value = v
  if (type === 'dy') dyConfirm.value = v
  if (type === 'xhs') xhsConfirm.value = v
}

defineExpose({ openZS, openDY, openXHS })
</script>
