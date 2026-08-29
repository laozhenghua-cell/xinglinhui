import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const login = async (email, password) => {
    const formData = new FormData()
    formData.append('email', email)
    formData.append('password', password)

    const response = await api.post('/auth/login', formData)
    token.value = response.data.access_token
    user.value = response.data.user

    localStorage.setItem('token', token.value)
    localStorage.setItem('user', JSON.stringify(user.value))

    return response.data
  }

  const register = async (email, password, name, role = 'doctor') => {
    const formData = new FormData()
    formData.append('email', email)
    formData.append('password', password)
    formData.append('name', name)
    formData.append('role', role)

    const response = await api.post('/auth/register', formData)
    token.value = response.data.access_token
    user.value = response.data.user

    localStorage.setItem('token', token.value)
    localStorage.setItem('user', JSON.stringify(user.value))

    return response.data
  }

  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    token,
    user,
    login,
    register,
    logout
  }
})
