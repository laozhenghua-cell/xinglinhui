import request from './index'

// ============ 统一门诊(后端 /api/v1/clinic,免登录设备级) ============
export function clinicDashboard() {
  return request.get('/clinic/dashboard')
}
export function clinicVisits(params) {
  return request.get('/clinic/visits', { params })
}
export function clinicVisit(id) {
  return request.get(`/clinic/visits/${id}`)
}
export function createVisit(data) {
  return request.post('/clinic/visits', data)
}
export function updateVisit(id, data) {
  return request.put(`/clinic/visits/${id}`, data)
}

export function clinicFollowups(params) {
  return request.get('/clinic/followups', { params })
}
export function visitPdfUrl(id) {
  return `/api/v1/clinic/visits/${id}/pdf`
}
export function exportVisitsUrl(format) {
  return `/api/v1/clinic/export?format=${format}`
}
