import request from './index'

export function listConsultations(params) {
  return request.get('/consultations', { params })
}

export function getConsultation(id) {
  return request.get(`/consultations/${id}`)
}

export function createConsultation(data) {
  return request.post('/consultations', data)
}

export function updateConsultation(id, data) {
  return request.put(`/consultations/${id}`, data)
}

export function triggerDiagnosis(id) {
  return request.post(`/consultations/${id}/diagnose`)
}

export function getConsultationImages(id) {
  return request.get(`/consultations/${id}/images`)
}

export function uploadConsultationImage(id, data) {
  return request.post(`/consultations/${id}/images`, data)
}

export function addFollowup(consultationId, data) {
  return request.post(`/consultations/${consultationId}/followups`, data)
}
