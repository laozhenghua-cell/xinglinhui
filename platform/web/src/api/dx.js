import request from './index'

// ============ 统一辨证中心(后端 /api/v1/dx,免鉴权) ============

// POST /dx/analyze
export function dxAnalyze(data) {
  return request.post('/dx/analyze', data)
}

// GET /dx/records?limit=
export function dxRecords(params) {
  return request.get('/dx/records', { params })
}

// GET /dx/records/{id}
export function dxRecord(id) {
  return request.get(`/dx/records/${id}`)
}

// GET /dx/quick?q=
export function dxQuick(q) {
  return request.get('/dx/quick', { params: { q } })
}

// POST /dx/tongue (multipart 舌象照片 → 标签)
export function dxTongue(file) {
  const fd = new FormData()
  fd.append('image', file)
  return request.post('/dx/tongue', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
}
