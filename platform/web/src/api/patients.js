import request from './index'

export function listPatients(params) {
  return request.get('/patients', { params })
}

export function getPatient(id) {
  return request.get(`/patients/${id}`)
}

export function createPatient(data) {
  return request.post('/patients', data)
}

export function updatePatient(id, data) {
  return request.put(`/patients/${id}`, data)
}

export function deletePatient(id) {
  return request.delete(`/patients/${id}`)
}

export function getPatientConsultations(id) {
  return request.get(`/patients/${id}/consultations`)
}

export function getPatientFollowups(id) {
  return request.get(`/patients/${id}/followups`)
}
