import request from './index'

// 辨证诊断相关API

export function getSymptomDictionary(category = null) {
  return request.get('/diagnosis/symptoms', {
    params: category ? { category } : {}
  })
}

export function analyzeSyndrome(data) {
  return request.post('/diagnosis/analyze', data)
}

export function getSyndromesByDisease(diseaseType) {
  return request.get(`/diagnosis/syndromes/${diseaseType}`)
}

export function saveDiagnosisRecord(data) {
  return request.post('/diagnosis/records', data)
}

export function createPrescriptionDraft(recordId, data) {
  return request.post(`/diagnosis/records/${recordId}/prescription`, data)
}

export function updatePrescriptionStatus(prescriptionId, status) {
  return request.put(`/diagnosis/prescriptions/${prescriptionId}/status`, { status })
}

export function listTemplates(params) {
  return request.get('/diagnosis/templates', { params })
}

export function getTemplate(id) {
  return request.get(`/diagnosis/templates/${id}`)
}
