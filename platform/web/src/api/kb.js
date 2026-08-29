import request from './index'

// ============ 知识总库（后端契约 /api/v1/kb，全免鉴权） ============

// GET /kb/stats → { counts:{...}, by_module:{ module:{...} } }
export function getKbStats() {
  return request.get('/kb/stats')
}

// GET /kb/{type}?q=&module=&category=&page=&size=
export function listKbItems(type, params) {
  return request.get(`/kb/${type}`, { params })
}

// GET /kb/{type}/{id}
export function getKbItem(type, id) {
  return request.get(`/kb/${type}/${id}`)
}

// GET /kb/search?q=&type=
export function searchKb(params) {
  return request.get('/kb/search', { params })
}

// GET /kb/linked?type=&id=
export function getKbLinked(params) {
  return request.get('/kb/linked', { params })
}
