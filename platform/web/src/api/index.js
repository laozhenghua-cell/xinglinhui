import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      // 全开放模式：后端 OPEN_ACCESS 不要求 token，401 不再强制跳转登录
      if (status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        ElMessage.error(data?.detail || '未授权访问')
      } else if (status === 402) {
        ElMessage.warning('试用期已过期，请升级订阅')
      } else if (status === 403) {
        ElMessage.error('无权限执行此操作')
      } else if (status === 422) {
        const detail = data.detail
        if (Array.isArray(detail)) {
          ElMessage.error(detail.map(d => d.msg).join('; '))
        } else {
          ElMessage.error(detail || '请求参数错误')
        }
      } else {
        ElMessage.error(data.detail || data.message || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查连接')
    }
    return Promise.reject(error)
  }
)

export default request
