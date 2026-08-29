import request from './index'

export function listChargeItems(params) {
  return request.get('/billing/charge-items', { params })
}

export function createChargeItem(data) {
  return request.post('/billing/charge-items', data)
}

export function updateChargeItem(id, data) {
  return request.put(`/billing/charge-items/${id}`, data)
}

export function deleteChargeItem(id) {
  return request.delete(`/billing/charge-items/${id}`)
}

export function listBills(params) {
  return request.get('/billing/bills', { params })
}

export function getBill(id) {
  return request.get(`/billing/bills/${id}`)
}

export function createBill(data) {
  return request.post('/billing/bills', data)
}

// 收款：后端接口为 POST /billing/payments
export function payBill(billId, data) {
  return request.post('/billing/payments', { bill_id: billId, ...data })
}

// 收入统计：后端统一为 GET /billing/revenue，返回 { summary, daily }
export function getRevenue(params) {
  return request.get('/billing/revenue', { params })
}

// 工作台用：汇总为 月收入 / 今日收入
export async function getRevenueStats() {
  const today = new Date().toISOString().slice(0, 10)
  const monthAgo = new Date(Date.now() - 30 * 86400000).toISOString().slice(0, 10)
  const data = await request.get('/billing/revenue', { params: { date_from: monthAgo, date_to: today } })
  const daily = data.daily || []
  const todayRow = daily.find(d => (d.date || '').slice(0, 10) === today)
  return {
    monthly_total: data.summary?.total_revenue || 0,
    today_total: todayRow ? Number(todayRow.total_revenue || 0) : 0,
  }
}
