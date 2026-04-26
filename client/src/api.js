const API_BASE = import.meta.env.PROD ? '/LeadKanBan' : ''

class ApiError extends Error {
  constructor(message, status, data) {
    super(message)
    this.status = status
    this.data = data
    this.name = 'ApiError'
  }
}

async function request(url, options = {}) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 10000)
  const isFormData = options.body instanceof FormData

  try {
    const res = await fetch(API_BASE + url, {
      ...options,
      signal: controller.signal,
      credentials: 'include',
      headers: isFormData
        ? { ...options.headers }
        : {
            'Content-Type': 'application/json',
            ...options.headers
          }
    })

    clearTimeout(timeoutId)

    if (res.status === 401) {
      window.location.href = API_BASE + '/login'
      throw new ApiError('未授权，请重新登录', 401, null)
    }

    if (!res.ok) {
      throw new ApiError(`请求失败: ${res.status}`, res.status, null)
    }

    return res.json()
  } catch (e) {
    clearTimeout(timeoutId)
    if (e.name === 'AbortError') {
      throw new ApiError('请求超时，请稍后重试', 0, null)
    }
    if (e instanceof ApiError) throw e
    throw new ApiError(e.message || '网络错误', 0, null)
  }
}

export default {
  getLeads() {
    return request('/api/leads')
  },
  getCurrentUser() {
    return request('/api/current_user')
  },
  getCost() {
    return request('/api/cost')
  },
  deleteLead(phone) {
    return request('/api/leads/delete', {
      method: 'POST',
      body: JSON.stringify({ phone })
    })
  },
  batchDelete(payload) {
    return request('/api/leads/batch-delete', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },
  updateLead(data) {
    return request('/api/leads/update', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  markRead() {
    return request('/api/leads/mark_read', { method: 'POST' })
  },
  submitCost(data) {
    return request('/api/cost/add', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  updateCost(data) {
    return request('/api/cost/update', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  deleteCost(id) {
    return request('/api/cost/delete', {
      method: 'POST',
      body: JSON.stringify({ id })
    })
  },
  importCost(formData) {
    return request('/api/cost/import', {
      method: 'POST',
      body: formData
    })
  },
  importFile(type, formData) {
    const map = { zs: 'zhaoshang', dy: 'douyin', xhs: 'xiaohongshu' }
    const endpoint = type === 'dy' ? '/api/leads/import-douyin' : '/api/leads/import'
    if (type !== 'dy') formData.append('type', map[type] || type)
    return request(endpoint, {
      method: 'POST',
      body: formData
    })
  },
  addLead(data) {
    return request('/api/leads/add', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  logout() {
    return request('/api/logout', { method: 'POST' })
  },
  login(data) {
    return request('/api/login', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  changePassword(data) {
    return request('/api/change-password', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  updateSelf(data) {
    return request('/api/users/update-self', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  getUsers() {
    return request('/api/users')
  },
  createUser(data) {
    return request('/api/users', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  toggleUser(data) {
    return request('/api/users/toggle', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  deleteUser(data) {
    return request('/api/users/delete', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  getAgents() {
    return request('/api/agents')
  },
  getActiveAgents() {
    return request('/api/agents-active')
  },
  getPlatforms() {
    return request('/api/platforms')
  },
  addPlatform(data) {
    return request('/api/platforms', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  deletePlatform(data) {
    return request('/api/platforms/delete', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  updatePlatform(data) {
    return request('/api/platforms/update', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  getRegions() {
    return request('/api/regions')
  },
  addRegion(data) {
    return request('/api/regions', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  deleteRegion(data) {
    return request('/api/regions/delete', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  updateRegion(data) {
    return request('/api/regions/update', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }
}
