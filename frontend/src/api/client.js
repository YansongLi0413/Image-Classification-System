import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器 — 自动附加 JWT
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 — 自动刷新 Token
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const res = await axios.post('/api/auth/refresh/', { refresh })
          localStorage.setItem('access_token', res.data.access)
          localStorage.setItem('refresh_token', res.data.refresh)
          original.headers.Authorization = `Bearer ${res.data.access}`
          return apiClient(original)
        } catch (e) {
          const auth = useAuthStore()
          auth.logout()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

// 便捷方法
export const authAPI = apiClient
export const predictAPI = apiClient

export default apiClient
