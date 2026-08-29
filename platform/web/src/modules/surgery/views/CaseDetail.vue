<template>
  <div class="page" v-loading="loading">
    <el-page-header @back="router.push('/surgery/cases')" title="返回医案库">
      <template #content>
        <span class="page-title">{{ data.patient_name || '医案' }}</span>
      </template>
    </el-page-header>

    <el-card v-if="data.id" class="detail-card">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="患者">{{ data.patient_name || '—' }}</el-descriptions-item>
        <el-descriptions-item label="基本信息">
          {{ data.gender || '' }} {{ data.age ? data.age + '岁' : '' }}
        </el-descriptions-item>
        <el-descriptions-item label="病种">{{ data.disease_id || '—' }}</el-descriptions-item>
        <el-descriptions-item label="证型">{{ data.syndrome || '—' }}</el-descriptions-item>
        <el-descriptions-item label="阶段">{{ data.stage || '—' }}</el-descriptions-item>
        <el-descriptions-item label="领域">{{ data.domain || '—' }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ data.source || '—' }}</el-descriptions-item>
        <el-descriptions-item label="疗效">
          <el-tag v-if="data.effect" type="success">{{ data.effect }}</el-tag>
          <span v-else>—</span>
        </el-descriptions-item>
        <el-descriptions-item label="主诉" :span="2">{{ data.chief_complaint || '—' }}</el-descriptions-item>
        <el-descriptions-item label="病史" :span="2">{{ data.history || '—' }}</el-descriptions-item>
        <el-descriptions-item label="治疗" :span="2">{{ data.treatment || '—' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 复诊照片时间线 -->
    <el-card v-if="(data.images || []).length" class="section-card">
      <template #header><span>复诊照片时间线</span></template>
      <div class="image-grid">
        <div v-for="img in data.images" :key="img.id" class="image-item">
          <el-image :src="img.path" fit="contain" :preview-src-list="[img.path]" preview-teleported class="case-img">
            <template #error><div class="img-fallback">图片缺失</div></template>
          </el-image>
          <div class="img-date">{{ img.taken_at ? img.taken_at.split('T')[0] : '' }}</div>
        </div>
      </div>
    </el-card>

    <!-- 诊疗记录 -->
    <el-card v-if="(data.records || []).length" class="section-card">
      <template #header><span>诊疗记录</span></template>
      <el-table :data="data.records" stripe>
        <el-table-column label="内治方" width="180">
          <template #default="{ row }">{{ row.formula?.name || '—' }}</template>
        </el-table-column>
        <el-table-column prop="external_treatment" label="外治" min-width="200" show-overflow-tooltip />
        <el-table-column prop="effect" label="疗效" width="110" />
        <el-table-column label="记录时间" width="180">
          <template #default="{ row }">{{ row.recorded_at }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-empty v-if="!loading && !data.id" description="医案不存在" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCase } from '../api'

const route = useRoute()
const router = useRouter()
const data = ref({})
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    data.value = (await getCase(route.params.id)) || {}
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-title {
  font-size: 18px;
  font-weight: 600;
}

.detail-card {
  margin-top: 20px;
}

.section-card {
  margin-top: 20px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.image-item {
  text-align: center;
}

.case-img {
  width: 100%;
  height: 200px;
  background: #f5f3ec;
  border-radius: 6px;
}

.img-fallback {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b9a87e;
  background: #f5f3ec;
}

.img-date {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}
</style>
