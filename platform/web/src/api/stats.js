import request from './index'

// 平台级公开统计（免鉴权）
export function getPublicStats() {
  return request.get('/stats/public')
}

// 访问埋点（免鉴权）
export function reportVisit(data) {
  return request.post('/visits', data)
}
