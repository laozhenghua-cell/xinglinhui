import request from '@/api/index.js'

// ============ 疾病库 ============
export function listDiseaseCategories() {
  return request.get('/surgery/diseases/categories')
}

export function listDiseases(params) {
  return request.get('/surgery/diseases', { params })
}

export function searchDiseases(q) {
  return request.get('/surgery/diseases/search', { params: { q } })
}

export function getDisease(id) {
  return request.get(`/surgery/diseases/${id}`)
}

// ============ 方剂库 ============
export function listFormulas(params) {
  return request.get('/surgery/formulas', { params })
}

// ============ 医案 ============
export function listCases(params) {
  return request.get('/surgery/cases', { params })
}

export function getCase(id) {
  return request.get(`/surgery/cases/${id}`)
}

// ============ 名医经验 ============
export function getExpert(category) {
  return request.get(`/surgery/expert/${encodeURIComponent(category)}`)
}

// ============ 临床要诀 ============
export function listTips(params) {
  return request.get('/surgery/tips', { params })
}

// ============ 证型 ============
export function listSyndromes(params) {
  return request.get('/surgery/syndromes', { params })
}

// ============ 辨证诊断（AI） ============
// 旧版契约：analyze 接收表单字段 symptoms（Form）
export function analyzeSymptoms(symptoms) {
  const body = new URLSearchParams()
  body.append('symptoms', symptoms)
  return request.post('/surgery/diagnosis/analyze', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

// ============ 治法规则 ============
export function treatmentRecommend(body) {
  return request.post('/surgery/treatment/recommend', body)
}

export function treatmentDifferentiate(body) {
  return request.post('/surgery/treatment/differentiate', body)
}

// ============ 方证对应（按证选方） ============
export function matchOptions() {
  return request.get('/surgery/treatment/match-options')
}

export function matchSyndrome(body) {
  return request.post('/surgery/treatment/match-syndrome', body)
}

export function matchFormula(body) {
  return request.post('/surgery/treatment/match-formula', body)
}

// ============ 统计概览 ============
export function getStatsOverview() {
  return request.get('/surgery/stats/overview')
}
