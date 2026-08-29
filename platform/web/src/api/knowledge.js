import request from './index'

export function listHerbs(params) {
  return request.get('/knowledge/herbs', { params })
}

export function getHerb(id) {
  return request.get(`/knowledge/herbs/${id}`)
}

export function listFormulas(params) {
  return request.get('/knowledge/formulas', { params })
}

export function getFormula(id) {
  return request.get(`/knowledge/formulas/${id}`)
}

export function listCases(params) {
  return request.get('/knowledge/cases', { params })
}

export function getCase(id) {
  return request.get(`/knowledge/cases/${id}`)
}

export function listPrevention(params) {
  return request.get('/knowledge/prevention', { params })
}

export function getPrevention(id) {
  return request.get(`/knowledge/prevention/${id}`)
}

export function searchKnowledge(keyword) {
  return request.get('/knowledge/search', { params: { q: keyword } })
}

export function getZhouCoverage() {
  return request.get('/knowledge/zhou-coverage')
}

export function listMedicalCases(params) {
  return request.get('/medical-cases/', { params })
}

export function getMedicalCase(id) {
  return request.get(`/medical-cases/${id}`)
}

export function findSimilarCases(data) {
  return request.post('/medical-cases/similar', data)
}

export function getDifferentials(diseaseType) {
  return request.get(`/knowledge/differentials/${encodeURIComponent(diseaseType)}`)
}

export function getAcupuncture(diseaseType) {
  return request.get(`/knowledge/acupuncture/${encodeURIComponent(diseaseType)}`)
}

export function getSurgicalTechniques(diseaseType) {
  return request.get(`/knowledge/surgical-techniques/${encodeURIComponent(diseaseType)}`)
}
