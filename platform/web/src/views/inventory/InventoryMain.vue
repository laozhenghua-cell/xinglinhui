<template>
  <div class="inventory-page">
    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="药品管理" name="medicines">
          <div class="tab-header">
            <el-input
              v-model="medicineSearch"
              placeholder="搜索药品名称"
              prefix-icon="Search"
              clearable
              style="width: 200px"
              @input="loadMedicines"
            />
            <el-button type="primary" @click="showMedicineDialog()">
              <el-icon><Plus /></el-icon>
              新增药品
            </el-button>
          </div>

          <el-table :data="medicines" v-loading="loadingMedicines" stripe>
            <el-table-column prop="name" label="药品名称" width="140" />
            <el-table-column prop="category" label="分类" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="specification" label="规格" width="100" />
            <el-table-column prop="unit" label="单位" width="60" />
            <el-table-column prop="stock_quantity" label="库存" width="80">
              <template #default="{ row }">
                <el-tag :type="getStockType(row)" size="small">{{ row.stock_quantity }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="min_stock" label="最低库存" width="80" />
            <el-table-column prop="selling_price" label="售价" width="80">
              <template #default="{ row }">
                ¥{{ Number(row.selling_price || 0).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="supplier" label="供应商" width="120" show-overflow-tooltip />
            <el-table-column label="操作" width="140">
              <template #default="{ row }">
                <el-button type="primary" link @click="showMedicineDialog(row)">编辑</el-button>
                <el-popconfirm title="确定删除？" @confirm="handleDeleteMedicine(row.id)">
                  <template #reference>
                    <el-button type="danger" link>删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="入库" name="stockin">
          <el-form ref="stockInFormRef" :model="stockInForm" :rules="stockInRules" label-width="80px" class="stock-form">
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12">
                <el-form-item label="选择药品" prop="medicine_id">
                  <el-select v-model="stockInForm.medicine_id" filterable placeholder="搜索药品" style="width: 100%">
                    <el-option
                      v-for="m in medicines"
                      :key="m.id"
                      :label="`${m.name} (${m.specification || ''})`"
                      :value="m.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item label="数量" prop="quantity">
                  <el-input-number v-model="stockInForm.quantity" :min="1" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12">
                <el-form-item label="批号" prop="batch_no">
                  <el-input v-model="stockInForm.batch_no" placeholder="生产批号" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item label="有效期" prop="expiry_date">
                  <el-date-picker
                    v-model="stockInForm.expiry_date"
                    type="date"
                    placeholder="选择有效期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12">
                <el-form-item label="进价" prop="purchase_price">
                  <el-input-number v-model="stockInForm.purchase_price" :min="0" :precision="2" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item label="供应商">
                  <el-input v-model="stockInForm.supplier" placeholder="供应商名称" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="备注">
              <el-input v-model="stockInForm.notes" type="textarea" :rows="2" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="stockingIn" @click="handleStockIn">确认入库</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="出库" name="stockout">
          <el-form ref="stockOutFormRef" :model="stockOutForm" :rules="stockOutRules" label-width="80px" class="stock-form">
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12">
                <el-form-item label="选择药品" prop="medicine_id">
                  <el-select v-model="stockOutForm.medicine_id" filterable placeholder="搜索药品" style="width: 100%">
                    <el-option
                      v-for="m in medicines"
                      :key="m.id"
                      :label="`${m.name} (库存: ${m.stock_quantity})`"
                      :value="m.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item label="数量" prop="quantity">
                  <el-input-number v-model="stockOutForm.quantity" :min="1" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12">
                <el-form-item label="出库原因" prop="reason">
                  <el-select v-model="stockOutForm.reason" placeholder="选择原因" style="width: 100%">
                    <el-option label="处方配药" value="prescription" />
                    <el-option label="报损" value="damage" />
                    <el-option label="过期销毁" value="expired" />
                    <el-option label="盘亏" value="inventory_loss" />
                    <el-option label="其他" value="other" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12">
                <el-form-item label="备注">
                  <el-input v-model="stockOutForm.notes" placeholder="出库备注" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item>
              <el-button type="warning" :loading="stockingOut" @click="handleStockOut">确认出库</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="库存预警" name="alerts">
          <el-table :data="alerts" v-loading="loadingAlerts" stripe>
            <el-table-column prop="alert_type" label="预警类型" width="110">
              <template #default="{ row }">
                <el-tag :type="getAlertType(row.alert_type)" size="small">{{ getAlertLabel(row.alert_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="预警说明" min-width="300" show-overflow-tooltip />
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.is_resolved ? 'success' : 'danger'" size="small">{{ row.is_resolved ? '已处理' : '待处理' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="时间" width="160">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="medicineDialogVisible" :title="editingMedicine ? '编辑药品' : '新增药品'" width="500px">
      <el-form ref="medicineFormRef" :model="medicineForm" :rules="medicineRules" label-width="80px">
        <el-form-item label="药品名称" prop="name">
          <el-input v-model="medicineForm.name" placeholder="如：槐花散" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="medicineForm.category" placeholder="选择分类">
            <el-option label="中药饮片" value="中药饮片" />
            <el-option label="中成药" value="中成药" />
            <el-option label="外用药" value="外用药" />
            <el-option label="西药" value="西药" />
            <el-option label="耗材" value="耗材" />
          </el-select>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="规格">
              <el-input v-model="medicineForm.specification" placeholder="如：10g/包" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="medicineForm.unit" placeholder="如：包、瓶、盒" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="售价">
              <el-input-number v-model="medicineForm.selling_price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最低库存">
              <el-input-number v-model="medicineForm.min_stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="供应商">
          <el-input v-model="medicineForm.supplier" placeholder="供应商名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="medicineDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingMedicine" @click="handleSaveMedicine">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import {
  listMedicines, createMedicine, updateMedicine, deleteMedicine,
  stockIn, stockOut, getStockAlerts
} from '@/api/inventory'
import { ElMessage } from 'element-plus'

const activeTab = ref('medicines')
const medicines = ref([])
const loadingMedicines = ref(false)
const medicineSearch = ref('')

const medicineDialogVisible = ref(false)
const editingMedicine = ref(null)
const savingMedicine = ref(false)
const medicineFormRef = ref(null)
const medicineForm = reactive({
  name: '', category: '', specification: '', unit: '',
  selling_price: 0, min_stock: 10, supplier: ''
})
const medicineRules = {
  name: [{ required: true, message: '请输入药品名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

const stockInFormRef = ref(null)
const stockInForm = reactive({
  medicine_id: null, quantity: 1, batch_no: '',
  expiry_date: '', purchase_price: 0, supplier: '', notes: ''
})
const stockInRules = {
  medicine_id: [{ required: true, message: '请选择药品', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  batch_no: [{ required: true, message: '请输入批号', trigger: 'blur' }]
}
const stockingIn = ref(false)

const stockOutFormRef = ref(null)
const stockOutForm = reactive({
  medicine_id: null, quantity: 1, reason: '', notes: ''
})
const stockOutRules = {
  medicine_id: [{ required: true, message: '请选择药品', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  reason: [{ required: true, message: '请选择出库原因', trigger: 'change' }]
}
const stockingOut = ref(false)

const alerts = ref([])
const loadingAlerts = ref(false)

function getStockType(row) {
  if (row.stock_quantity <= 0) return 'danger'
  if (row.stock_quantity <= (row.min_stock || 10)) return 'warning'
  return 'success'
}

function getAlertType(type) {
  if (type === 'low_stock') return 'warning'
  if (type === 'expired') return 'danger'
  if (type === 'expiring') return 'warning'
  return 'info'
}

function getAlertLabel(type) {
  const labels = { low_stock: '库存不足', expired: '已过期', expiring: '即将过期' }
  return labels[type] || type
}

function formatTime(str) {
  if (!str) return '-'
  const d = new Date(str)
  return d.toLocaleString('zh-CN', { hour12: false })
}

async function loadMedicines() {
  loadingMedicines.value = true
  try {
    const res = await listMedicines({ search: medicineSearch.value || undefined })
    medicines.value = res.items || res || []
  } catch (e) {
    console.error(e)
  } finally {
    loadingMedicines.value = false
  }
}

function showMedicineDialog(item) {
  editingMedicine.value = item || null
  if (item) {
    Object.assign(medicineForm, {
      name: item.name, category: item.category, specification: item.specification,
      unit: item.unit, selling_price: Number(item.selling_price || 0), min_stock: item.min_stock, supplier: item.supplier
    })
  } else {
    Object.assign(medicineForm, { name: '', category: '', specification: '', unit: '', selling_price: 0, min_stock: 10, supplier: '' })
  }
  medicineDialogVisible.value = true
}

async function handleSaveMedicine() {
  const valid = await medicineFormRef.value.validate().catch(() => false)
  if (!valid) return
  savingMedicine.value = true
  try {
    if (editingMedicine.value) {
      await updateMedicine(editingMedicine.value.id, medicineForm)
      ElMessage.success('更新成功')
    } else {
      await createMedicine(medicineForm)
      ElMessage.success('新增成功')
    }
    medicineDialogVisible.value = false
    loadMedicines()
  } catch (e) {
    // handled
  } finally {
    savingMedicine.value = false
  }
}

async function handleDeleteMedicine(id) {
  try {
    await deleteMedicine(id)
    ElMessage.success('删除成功')
    loadMedicines()
  } catch (e) {
    // handled
  }
}

async function handleStockIn() {
  const valid = await stockInFormRef.value.validate().catch(() => false)
  if (!valid) return
  stockingIn.value = true
  try {
    await stockIn(stockInForm)
    ElMessage.success('入库成功')
    Object.assign(stockInForm, { medicine_id: null, quantity: 1, batch_no: '', expiry_date: '', purchase_price: 0, supplier: '', notes: '' })
    loadMedicines()
  } catch (e) {
    // handled
  } finally {
    stockingIn.value = false
  }
}

async function handleStockOut() {
  const valid = await stockOutFormRef.value.validate().catch(() => false)
  if (!valid) return
  stockingOut.value = true
  try {
    await stockOut(stockOutForm)
    ElMessage.success('出库成功')
    Object.assign(stockOutForm, { medicine_id: null, quantity: 1, reason: '', notes: '' })
    loadMedicines()
  } catch (e) {
    // handled
  } finally {
    stockingOut.value = false
  }
}

async function loadAlerts() {
  loadingAlerts.value = true
  try {
    const res = await getStockAlerts()
    alerts.value = Array.isArray(res) ? res : res.items || []
  } catch (e) {
    console.error(e)
  } finally {
    loadingAlerts.value = false
  }
}

watch(activeTab, (val) => {
  if (val === 'alerts') loadAlerts()
})

onMounted(() => {
  loadMedicines()
})
</script>

<style scoped>
.inventory-page {
  max-width: 1200px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stock-form {
  max-width: 700px;
  margin-top: 8px;
}
</style>
