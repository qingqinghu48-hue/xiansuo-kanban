<template>
  <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg)">
    <!-- 登录表单 -->
    <div v-if="!showChangePwd" style="background:var(--surface);padding:40px;border-radius:var(--radius);box-shadow:var(--shadow-lg);width:92%;max-width:360px;border:1px solid var(--border-2)">
      <div style="text-align:center;margin-bottom:28px">
        <div style="width:48px;height:48px;background:linear-gradient(135deg,var(--primary),var(--accent));color:#fff;border-radius:12px;display:inline-flex;align-items:center;justify-content:center;font-weight:800;font-size:20px;margin-bottom:12px">招</div>
        <h2 style="font-size:18px;font-weight:700">招商线索看板</h2>
        <p style="font-size:13px;color:var(--text-3);margin-top:4px">请登录以继续使用</p>
      </div>
      <div class="cost-field" style="margin-bottom:14px">
        <label>用户名</label>
        <input type="text" v-model="username" placeholder="请输入用户名" style="width:100%">
      </div>
      <div class="cost-field" style="margin-bottom:20px">
        <label>密码</label>
        <input type="password" v-model="password" placeholder="请输入密码" style="width:100%">
      </div>
      <button class="btn btn-pri" style="width:100%;padding:10px" @click="doLogin">登录</button>
      <div v-if="error" style="margin-top:12px;color:var(--danger);font-size:13px;text-align:center">{{ error }}</div>
    </div>

    <!-- 首次登录强制修改密码 -->
    <div v-else style="background:var(--surface);padding:40px;border-radius:var(--radius);box-shadow:var(--shadow-lg);width:92%;max-width:360px;border:1px solid var(--border-2)">
      <div style="text-align:center;margin-bottom:28px">
        <div style="width:48px;height:48px;background:linear-gradient(135deg,var(--primary),var(--accent));color:#fff;border-radius:12px;display:inline-flex;align-items:center;justify-content:center;font-weight:800;font-size:20px;margin-bottom:12px">🔐</div>
        <h2 style="font-size:18px;font-weight:700">首次登录，请修改密码</h2>
        <p style="font-size:13px;color:var(--text-3);margin-top:4px">密码必须为 6 位</p>
      </div>
      <div class="cost-field" style="margin-bottom:14px">
        <label>新密码</label>
        <input type="password" v-model="newPassword" placeholder="请输入6位新密码" style="width:100%" maxlength="6">
      </div>
      <div class="cost-field" style="margin-bottom:20px">
        <label>确认密码</label>
        <input type="password" v-model="confirmPassword" placeholder="请再次输入新密码" style="width:100%" maxlength="6">
      </div>
      <button class="btn btn-pri" style="width:100%;padding:10px" @click="submitChangePwd">确认修改</button>
      <div v-if="pwdError" style="margin-top:12px;color:var(--danger);font-size:13px;text-align:center">{{ pwdError }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api.js'

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

const showChangePwd = ref(false)
const newPassword = ref('')
const confirmPassword = ref('')
const pwdError = ref('')

async function doLogin() {
  error.value = ''
  try {
    const data = await api.login({ username: username.value, password: password.value })
    if (data.success) {
      if (data.must_change_password) {
        showChangePwd.value = true
      } else {
        router.push('/dashboard')
      }
    } else {
      error.value = data.message || '登录失败'
    }
  } catch(e) {
    error.value = '网络错误'
  }
}

async function submitChangePwd() {
  pwdError.value = ''
  if (!newPassword.value || newPassword.value.length !== 6) {
    pwdError.value = '密码必须为6位'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    pwdError.value = '两次输入的密码不一致'
    return
  }
  try {
    const data = await api.changePassword({ old_password: '', new_password: newPassword.value })
    if (data.success) {
      showChangePwd.value = false
      newPassword.value = ''
      confirmPassword.value = ''
      router.push('/dashboard')
    } else {
      pwdError.value = data.message || '修改失败'
    }
  } catch(e) {
    pwdError.value = '网络错误'
  }
}
</script>
