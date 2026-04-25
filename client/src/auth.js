import api from './api.js'

export async function checkAuth(router) {
  try {
    const data = await api.getCurrentUser()
    const user = data.user || data
    if (user.role) {
      return user
    } else {
      router.push('/login')
      return null
    }
  } catch (e) {
    router.push('/login')
    return null
  }
}
