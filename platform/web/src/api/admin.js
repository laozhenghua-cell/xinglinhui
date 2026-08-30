import request from './index'

// 词库管理(口语→证候标签映射)
export function listSynonyms(q = '') {
  return request.get('/admin/synonyms', { params: { q } })
}
export function upsertSynonym(keyword, labels) {
  return request.post('/admin/synonyms', { keyword, labels })
}
export function deleteSynonym(keyword) {
  return request.delete(`/admin/synonyms/${encodeURIComponent(keyword)}`)
}
