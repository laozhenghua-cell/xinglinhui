import request from './index'

export function listMedicines(params) {
  return request.get('/inventory/medicines', { params })
}

export function getMedicine(id) {
  return request.get(`/inventory/medicines/${id}`)
}

export function createMedicine(data) {
  return request.post('/inventory/medicines', data)
}

export function updateMedicine(id, data) {
  return request.put(`/inventory/medicines/${id}`, data)
}

export function deleteMedicine(id) {
  return request.delete(`/inventory/medicines/${id}`)
}

export function stockIn(data) {
  return request.post('/inventory/stock-in', data)
}

export function stockOut(data) {
  return request.post('/inventory/stock-out', data)
}

export function getStockAlerts() {
  return request.get('/inventory/alerts')
}

export function listBatches(medicineId) {
  return request.get(`/inventory/batches/${medicineId}`)
}
