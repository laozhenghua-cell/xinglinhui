<template>
  <div class="billing-page">
    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="收费项目" name="items">
          <div class="tab-header">
            <el-input
              v-model="itemSearch"
              placeholder="搜索收费项目"
              prefix-icon="Search"
              clearable
              style="width: 200px"
              @input="loadChargeItems"
            />
            <el-button type="primary" @click="showItemDialog()">
              <el-icon><Plus /></el-icon>
              新增项目
            </el-button>
          </div>

          <el-table :data="chargeItems" v-loading="loadingItems" stripe>
            <el-table-column prop="name" label="项目名称" width="160" />
            <el-table-column v-if="!isMobile" prop="category" label="分类" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="单价(元)" width="100">
              <template #default="{ row }">
                ¥{{ Number(row.price || 0).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column v-if="!isMobile" prop="unit" label="单位" width="80" />
            <el-table-column v-if="!isMobile" prop="description" label="说明" show-overflow-tooltip />
            <el-table-column label="操作" width="140">
              <template #default="{ row }">
                <el-button type="primary" link @click="showItemDialog(row)">编辑</el-button>
                <el-popconfirm title="确定删除？" @confirm="handleDeleteItem(row.id)">
                  <template #reference>
                    <el-button type="danger" link>删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="开单收费" name="billing">
          <el-form label-width="80px" class="bill-form">
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12">
                <el-form-item label="选择患者">
                  <el-select
                    v-model="billForm.patient_id"
                    filterable
                    remote
                    :remote-method="searchBillPatients"
                    placeholder="搜索患者"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="p in billPatientOptions"
                      :key="p.id"
                      :label="`${p.name} (${p.phone || ''})`"
                      :value="p.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item label="备注">
                  <el-input v-model="billForm.notes" placeholder="账单备注" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">收费明细</el-divider>

            <div v-for="(item, index) in billForm.items" :key="index" class="bill-item-row">
              <el-row :gutter="12" align="middle">
                <el-col :xs="10" :sm="8">
                  <el-select v-model="item.charge_item_id" placeholder="选择项目" @change="onItemSelect(index)">
                    <el-option
                      v-for="ci in chargeItems"
                      :key="ci.id"
                      :label="ci.name"
                      :value="ci.id"
                    />
                  </el-select>
                </el-col>
                <el-col :xs="4" :sm="3">
                  <el-input-number v-model="item.quantity" :min="1" size="small" @change="calcTotal" />
                </el-col>
                <el-col :xs="4" :sm="3">
                  <span class="item-price">¥{{ (item.price * item.quantity).toFixed(2) }}</span>
                </el-col>
                <el-col :xs="2" :sm="2">
                  <el-button type="danger" circle size="small" @click="removeBillItem(index)">
                    <el-icon><Minus /></el-icon>
                  </el-button>
                </el-col>
              </el-row>
            </div>

            <el-button type="primary" link @click="addBillItem" class="add-item-btn">
              <el-icon><Plus /></el-icon>
              添加项目
            </el-button>

            <el-divider />

            <div class="bill-total">
              <span>合计金额：</span>
              <span class="total-amount">¥{{ billTotal.toFixed(2) }}</span>
            </div>

            <div class="bill-actions">
              <el-select v-model="billForm.payment_method" placeholder="支付方式" style="width: 140px">
                <el-option label="现金" value="cash" />
                <el-option label="微信" value="wechat" />
                <el-option label="支付宝" value="alipay" />
                <el-option label="银行卡" value="card" />
                <el-option label="医保" value="insurance" />
              </el-select>
              <el-button type="primary" size="large" :loading="creatingBill" @click="handleCreateBill">
                收费确认
              </el-button>
            </div>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="收入统计" name="revenue">
          <div class="revenue-header">
            <el-radio-group v-model="revenueType" @change="loadRevenue">
              <el-radio-button value="daily">按日</el-radio-button>
              <el-radio-button value="monthly">按月</el-radio-button>
            </el-radio-group>
            <el-date-picker
              v-model="revenueDateRange"
              type="daterange"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="loadRevenue"
            />
          </div>
          <div ref="chartRef" class="revenue-chart"></div>
          <el-row :gutter="20" class="revenue-summary">
            <el-col :span="8">
              <el-statistic title="总收入" :value="revenueSummary.total" prefix="¥" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="账单数" :value="revenueSummary.count" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="平均单价" :value="revenueSummary.average" prefix="¥" />
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="itemDialogVisible" :title="editingItem ? '编辑收费项目' : '新增收费项目'" width="450px">
      <el-form ref="itemFormRef" :model="itemForm" :rules="itemRules" label-width="80px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="itemForm.name" placeholder="如：肛门镜检查" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="itemForm.category" placeholder="选择分类">
            <el-option label="诊查" value="诊查" />
            <el-option label="治疗" value="治疗" />
            <el-option label="手术" value="手术" />
            <el-option label="检查" value="检查" />
            <el-option label="药品" value="药品" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="单价" prop="price">
          <el-input-number v-model="itemForm.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="itemForm.unit" placeholder="如：次、剂、盒" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="itemForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="itemDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingItem" @click="handleSaveItem">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { useWindowSize } from '@vueuse/core'
import * as echarts from 'echarts'
import {
  listChargeItems, createChargeItem, updateChargeItem, deleteChargeItem,
  createBill, payBill, getRevenue
} from '@/api/billing'
import { listPatients } from '@/api/patients'
import { ElMessage } from 'element-plus'

const activeTab = ref('items')
const { width } = useWindowSize()
const isMobile = computed(() => width.value < 768)
const loadingItems = ref(false)
const chargeItems = ref([])
const itemSearch = ref('')

const itemDialogVisible = ref(false)
const editingItem = ref(null)
const savingItem = ref(false)
const itemFormRef = ref(null)
const itemForm = reactive({ name: '', category: '', price: 0, unit: '', description: '' })
const itemRules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  price: [{ required: true, message: '请输入单价', trigger: 'blur' }]
}

const billForm = reactive({
  patient_id: null,
  notes: '',
  items: [{ charge_item_id: null, quantity: 1, price: 0 }],
  payment_method: 'cash'
})
const billPatientOptions = ref([])
const creatingBill = ref(false)

const billTotal = computed(() => {
  return billForm.items.reduce((sum, item) => sum + (item.price || 0) * (item.quantity || 0), 0)
})

const revenueType = ref('daily')
const revenueDateRange = ref([])
const chartRef = ref(null)
const revenueSummary = ref({ total: 0, count: 0, average: 0 })
let chartInstance = null

async function loadChargeItems() {
  loadingItems.value = true
  try {
    const res = await listChargeItems({ search: itemSearch.value || undefined })
    chargeItems.value = res.items || res || []
  } catch (e) {
    console.error(e)
  } finally {
    loadingItems.value = false
  }
}

function showItemDialog(item) {
  editingItem.value = item || null
  if (item) {
    Object.assign(itemForm, { name: item.name, category: item.category, price: Number(item.price), unit: item.unit, description: item.description })
  } else {
    Object.assign(itemForm, { name: '', category: '', price: 0, unit: '', description: '' })
  }
  itemDialogVisible.value = true
}

async function handleSaveItem() {
  const valid = await itemFormRef.value.validate().catch(() => false)
  if (!valid) return
  savingItem.value = true
  try {
    if (editingItem.value) {
      await updateChargeItem(editingItem.value.id, itemForm)
      ElMessage.success('更新成功')
    } else {
      await createChargeItem(itemForm)
      ElMessage.success('新增成功')
    }
    itemDialogVisible.value = false
    loadChargeItems()
  } catch (e) {
    // handled
  } finally {
    savingItem.value = false
  }
}

async function handleDeleteItem(id) {
  try {
    await deleteChargeItem(id)
    ElMessage.success('删除成功')
    loadChargeItems()
  } catch (e) {
    // handled
  }
}

function onItemSelect(index) {
  const selected = chargeItems.value.find(ci => ci.id === billForm.items[index].charge_item_id)
  if (selected) {
    billForm.items[index].price = Number(selected.price)
  }
  calcTotal()
}

function addBillItem() {
  billForm.items.push({ charge_item_id: null, quantity: 1, price: 0 })
}

function removeBillItem(index) {
  if (billForm.items.length <= 1) return
  billForm.items.splice(index, 1)
}

function calcTotal() {
  // computed handles this
}

async function searchBillPatients(query) {
  if (!query) return
  try {
    const res = await listPatients({ search: query, size: 20 })
    billPatientOptions.value = res.items || res || []
  } catch (e) {
    console.error(e)
  }
}

async function handleCreateBill() {
  if (!billForm.patient_id) {
    ElMessage.warning('请选择患者')
    return
  }
  const validItems = billForm.items.filter(i => i.charge_item_id)
  if (!validItems.length) {
    ElMessage.warning('请添加收费项目')
    return
  }
  creatingBill.value = true
  try {
    // 按后端契约构造明细：name/category/unit/unit_price
    const items = validItems.map(i => {
      const ci = chargeItems.value.find(c => c.id === i.charge_item_id)
      return {
        charge_item_id: i.charge_item_id,
        name: ci?.name || '',
        category: ci?.category || '',
        unit: ci?.unit || '次',
        quantity: i.quantity || 1,
        unit_price: Number(i.price ?? ci?.price ?? 0),
      }
    })
    const bill = await createBill({
      patient_id: billForm.patient_id,
      notes: billForm.notes,
      items,
    })
    await payBill(bill.id, { amount: billTotal.value, payment_method: billForm.payment_method })
    ElMessage.success('收费成功')
    billForm.patient_id = null
    billForm.notes = ''
    billForm.items = [{ charge_item_id: null, quantity: 1, price: 0 }]
  } catch (e) {
    // handled
  } finally {
    creatingBill.value = false
  }
}

async function loadRevenue() {
  try {
    const params = {}
    if (revenueDateRange.value && revenueDateRange.value.length === 2) {
      params.date_from = revenueDateRange.value[0]
      params.date_to = revenueDateRange.value[1]
    }

    const data = await getRevenue(params)
    const summary = data.summary || {}
    revenueSummary.value.total = summary.total_revenue || 0
    revenueSummary.value.count = summary.total_bills || 0
    revenueSummary.value.average = summary.total_bills > 0
      ? Math.round(summary.total_revenue / summary.total_bills * 100) / 100
      : 0

    let daily = data.daily || []
    // 按月汇总
    let items = daily.map(d => ({ label: d.date, amount: Number(d.total_revenue || 0) }))
    if (revenueType.value === 'monthly') {
      const map = {}
      daily.forEach(d => {
        const month = (d.date || '').slice(0, 7)
        map[month] = (map[month] || 0) + Number(d.total_revenue || 0)
      })
      items = Object.entries(map).map(([month, amount]) => ({ label: month, amount }))
    }
    renderChart(items)
  } catch (e) {
    console.error(e)
  }
}

function renderChart(data) {
  if (!chartRef.value) return
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: data.map(d => d.label || '')
    },
    yAxis: { type: 'value', name: '金额(元)' },
    series: [{
      name: '收入',
      type: 'bar',
      data: data.map(d => d.amount || 0),
      itemStyle: { color: '#409EFF' }
    }]
  }
  chartInstance.setOption(option)
}

watch(activeTab, (val) => {
  if (val === 'revenue') {
    nextTick(() => loadRevenue())
  }
})

onMounted(() => {
  loadChargeItems()
})
</script>

<style scoped>
.billing-page {
  max-width: 1200px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.bill-form {
  max-width: 800px;
}

.bill-item-row {
  margin-bottom: 12px;
}

.item-price {
  font-weight: 600;
  color: #F56C6C;
}

.add-item-btn {
  margin: 8px 0 16px;
}

.bill-total {
  font-size: 18px;
  text-align: right;
  margin-bottom: 16px;
}

.total-amount {
  font-weight: 700;
  color: #F56C6C;
  font-size: 24px;
}

.bill-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  align-items: center;
}

.revenue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.revenue-chart {
  width: 100%;
  height: 350px;
}

.revenue-summary {
  margin-top: 20px;
  text-align: center;
}
</style>
