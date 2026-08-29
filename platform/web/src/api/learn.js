import request from './index'

// ============ 学苑(后端 /api/v1/learn,免登录,设备级) ============
export function learnPaths() {
  return request.get('/learn/paths')
}
export function saveProgress(data) {
  return request.post('/learn/progress', data)
}
export function getProgress(params) {
  return request.get('/learn/progress', { params })
}
export function getCard(params) {
  return request.get('/learn/card', { params })
}
export function addNote(data) {
  return request.post('/learn/notes', data)
}
export function listNotes() {
  return request.get('/learn/notes')
}
export function delNote(id) {
  return request.delete(`/learn/notes/${id}`)
}
export function toggleFav(data) {
  return request.post('/learn/favorites/toggle', data)
}
export function listFavs() {
  return request.get('/learn/favorites')
}
export function getQuiz(params) {
  return request.get('/learn/quiz', { params })
}
export function submitQuiz(data) {
  return request.post('/learn/quiz/submit', data)
}
export function quizHistory(params) {
  return request.get('/learn/quiz/history', { params })
}
export function aiAsk(data) {
  return request.post('/learn/ask', data)
}
