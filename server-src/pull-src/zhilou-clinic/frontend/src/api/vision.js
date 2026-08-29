import request from './index'

export function analyzeImage(base64, type, symptoms) {
  return request.post('/vision/analyze-image', {
    image: base64,
    image_type: type,
    symptoms: symptoms || ''
  })
}

export function getAnalysisHistory(params) {
  return request.get('/vision/history', { params })
}

export function getAnalysisDetail(id) {
  return request.get(`/vision/history/${id}`)
}

export function saveToConsultation(analysisId, consultationId) {
  return request.post('/vision/save-to-consultation', {
    analysis_id: analysisId,
    consultation_id: consultationId
  })
}
