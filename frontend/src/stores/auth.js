import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')

  const isLoggedIn = computed(() => !!accessToken.value)

  async function login(username, password) {
    const res = await authAPI.post('/auth/login/', { username, password })
    setTokens(res.data.tokens)
    user.value = res.data.user
    localStorage.setItem('user', JSON.stringify(res.data.user))
    return res.data
  }

  async function register(username, email, password) {
    const res = await authAPI.post('/auth/register/', { username, email, password })
    setTokens(res.data.tokens)
    user.value = res.data.user
    localStorage.setItem('user', JSON.stringify(res.data.user))
    return res.data
  }

  function setTokens(tokens) {
    accessToken.value = tokens.access
    refreshToken.value = tokens.refresh
    localStorage.setItem('access_token', tokens.access)
    localStorage.setItem('refresh_token', tokens.refresh)
  }

  function logout() {
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    localStorage.clear()
  }

  return { user, accessToken, refreshToken, isLoggedIn, login, register, logout, setTokens }
})
