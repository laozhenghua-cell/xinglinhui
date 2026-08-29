import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, getMe } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const userName = computed(() => user.value?.name || user.value?.email || '')

  async function login(credentials) {
    const res = await apiLogin(credentials)
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)
    await fetchUser()
    router.push('/anorectal/dashboard')
  }

  async function fetchUser() {
    try {
      const res = await getMe()
      user.value = res
      localStorage.setItem('user', JSON.stringify(res))
    } catch (e) {
      console.error('Failed to fetch user:', e)
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/')
  }

  function setToken(t) {
    token.value = t
    localStorage.setItem('token', t)
  }

  // 注册后直接写入登录态（后端 register 已返回 token + user）
  function setAuth(accessToken, userInfo) {
    token.value = accessToken
    user.value = userInfo
    localStorage.setItem('token', accessToken)
    localStorage.setItem('user', JSON.stringify(userInfo))
  }

  return {
    token,
    user,
    isLoggedIn,
    userName,
    login,
    fetchUser,
    logout,
    setToken,
    setAuth
  }
})
