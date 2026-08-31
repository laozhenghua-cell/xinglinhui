<template>
  <el-dialog
    v-model="visible"
    title="处方打印预览"
    width="min(680px, 94vw)"
    :close-on-click-modal="false"
    class="prescription-print-dialog"
  >
    <div class="print-toolbar">
      <el-alert
        title="本处方为辅助决策参考，须经执业医师审核后使用。"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 12px"
      />
      <div class="toolbar-btns">
        <el-button type="primary" :icon="Printer" @click="print">打印 / 存为 PDF</el-button>
        <el-button @click="visible = false">关闭</el-button>
      </div>
    </div>

    <!-- 可打印的处方笺 -->
    <div class="prescription-sheet">
      <div class="sheet-header">
        <h2>中医处方笺</h2>
        <span class="clinic-name">{{ clinicName }}</span>
      </div>

      <div class="patient-row">
        <span>姓名：<strong>{{ patient?.name || '—' }}</strong></span>
        <span>性别：{{ patient?.gender || '—' }}</span>
        <span>年龄：{{ patient?.age ?? '—' }}</span>
        <span v-if="patient?.phone">电话：{{ patient.phone }}</span>
      </div>

      <div class="diagnosis-row">
        <div><label>中医诊断</label><span>{{ syndrome?.syndrome_name || '—' }}</span></div>
        <div v-if="syndrome?.treatment_principle"><label>治则</label><span>{{ syndrome.treatment_principle }}</span></div>
      </div>

      <div class="formula-row">
        <div class="formula-title">
          <span class="rx">R</span>
          <strong>{{ formulaName || '—' }}</strong>
        </div>
        <div class="formula-composition">
          <template v-if="Array.isArray(composition)">
            <span v-for="(h, i) in composition" :key="i" class="herb">
              {{ h.name }}{{ h.dosage }}{{ h.unit }}<span v-if="h.note">（{{ h.note }}）</span>
            </span>
          </template>
          <span v-else>{{ composition || '（方剂组成见系统方剂库）' }}</span>
        </div>
      </div>

      <div class="usage-row">
        <div><label>用法</label><span>{{ usage || '水煎服，日服一剂' }}</span></div>
        <div><label>剂数</label><span>{{ durationDays || 7 }} 剂</span></div>
      </div>

      <div v-if="notes" class="notes-row">
        <label>加减 / 医嘱</label>
        <p>{{ notes }}</p>
      </div>

      <div class="sheet-footer">
        <div class="doctor-sign">
          <span>医师：{{ doctorName || '—' }}</span>
        </div>
        <div class="date">
          <span>日期：{{ today }}</span>
        </div>
      </div>

      <div class="sheet-disclaimer">
        本处方依据中医临床经验辨证生成，仅供执业医师临床决策参考，用药须结合患者年龄、妊娠哺乳、肝肾功能、过敏史及合并用药复核。
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Printer } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  patient: { type: Object, default: () => ({}) },
  syndrome: { type: Object, default: () => ({}) },
  formulaName: { type: String, default: '' },
  composition: { type: [Array, String], default: '' },
  usage: { type: String, default: '' },
  durationDays: { type: Number, default: 7 },
  notes: { type: String, default: '' },
  doctorName: { type: String, default: '' },
  clinicName: { type: String, default: '中医肛肠专科门诊' },
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const today = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })

function print() {
  window.print()
}
</script>

<style scoped>
.print-toolbar {
  margin-bottom: 16px;
}
.toolbar-btns {
  display: flex;
  gap: 12px;
}

.prescription-sheet {
  border: 1px solid #333;
  padding: 28px 32px;
  background: #fff;
  font-family: 'Songti SC', 'SimSun', serif;
  color: #111;
  line-height: 1.7;
}

.sheet-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  border-bottom: 2px solid #333;
  padding-bottom: 12px;
  margin-bottom: 16px;
}
.sheet-header h2 {
  margin: 0;
  font-size: 22px;
  letter-spacing: 4px;
}
.clinic-name {
  font-size: 14px;
  color: #333;
}

.patient-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  font-size: 15px;
  margin-bottom: 14px;
}

.diagnosis-row {
  border: 1px solid #999;
  border-radius: 4px;
  padding: 10px 14px;
  margin-bottom: 14px;
  font-size: 15px;
}
.diagnosis-row div {
  margin: 2px 0;
}
.diagnosis-row label,
.usage-row label,
.notes-row label {
  color: #555;
  margin-right: 8px;
}

.formula-row {
  margin-bottom: 14px;
}
.formula-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 17px;
  margin-bottom: 8px;
}
.formula-title .rx {
  font-size: 20px;
  font-weight: 700;
}
.formula-composition {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 14px;
  font-size: 15px;
}
.formula-composition .herb {
  white-space: nowrap;
}

.usage-row {
  display: flex;
  gap: 28px;
  font-size: 15px;
  margin-bottom: 12px;
}

.notes-row {
  border-top: 1px dashed #999;
  padding-top: 10px;
  font-size: 14px;
}
.notes-row p {
  margin: 4px 0 0;
}

.sheet-footer { flex-wrap: wrap; gap: 8px;
  display: flex;
  justify-content: space-between;
  margin-top: 28px;
  font-size: 15px;
}
.doctor-sign {
  min-width: 180px;
}
@media (max-width: 480px) {
  .doctor-sign { min-width: 0; }
}

.sheet-disclaimer {
  margin-top: 18px;
  padding-top: 10px;
  border-top: 1px solid #ccc;
  font-size: 11px;
  color: #777;
}
</style>

<style>
/* 打印时只显示处方笺，隐藏其余界面 */
@media print {
  body * {
    visibility: hidden;
  }
  .prescription-sheet,
  .prescription-sheet * {
    visibility: visible;
  }
  .prescription-sheet {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    border: none;
  }
}
</style>
