import request from './index'

export function login(data) {
  return request.post('/auth/login', data)
}

export function register(data) {
  return request.post('/auth/register', data)
}

export function getMe() {
  return request.get('/auth/me')
}

export function changePassword(data) {
  return request.put('/auth/password', data)
}

export function updateProfile(data) {
  return request.put('/auth/profile', data)
}
