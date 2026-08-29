<template>
  <div class="page" v-loading="loading">
    <el-page-header @back="router.push('/surgery/diseases')" title="返回疾病库">
      <template #content>
        <span class="page-title">{{ disease.name }}</span>
      </template>
    </el-page-header>

    <el-card v-if="disease.id" class="detail-card">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="病名">{{ disease.name }}</el-descriptions-item>
        <el-descriptions-item label="分类">
          <el-tag>{{ disease.category }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="别名" :span="2">
          {{ (disease.aliases || []).join('、') || '—' }}
        </el-descriptions-item>
        <el-descriptions-item label="部位">{{ disease.location || '—' }}</el-descriptions-item>
        <el-descriptions-item label="阴阳">
          {{ disease.is_yang ? '阳证' : '阴证' }}
          <el-tag v-if="disease.is_dangerous" type="danger" size="small" style="margin-left:8px">危险</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="疮形">{{ disease.morphology || '—' }}</el-descriptions-item>
        <el-descriptions-item label="西医对应">{{ disease.western_equiv || '—' }}</el-descriptions-item>
        <el-descriptions-item label="辨证类型">{{ disease.differentiation || '消托补' }}</el-descriptions-item>
        <el-descriptions-item label="出处">{{ disease.source || '—' }}</el-descriptions-item>
        <el-descriptions-item label="疮形特点" :span="2">{{ disease.characteristics || '—' }}</el-descriptions-item>
        <el-descriptions-item label="鉴别要点" :span="2">{{ disease.differential || '—' }}</el-descriptions-item>
        <el-descriptions-item label="预后" :span="2">{{ disease.prognosis || '—' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 图版 -->
    <el-card v-if="(disease.images || []).length" class="section-card">
      <template #header><span>图版</span></template>
      <div class="image-grid">
        <div v-for="img in disease.images" :key="img.id" class="image-item">
          <el-image :src="img.path" fit="contain" :preview-src-list="[img.path]" preview-teleported class="book-img">
            <template #error><div class="img-fallback">图片缺失</div></template>
          </el-image>
          <div class="img-caption">{{ img.caption || img.category || img.image_type }}</div>
        </div>
      </div>
    </el-card>

    <!-- 论治规则 -->
    <el-card v-if="(disease.rules || []).length" class="section-card">
      <template #header><span>论治规则</span></template>
      <el-table :data="disease.rules" stripe>
        <el-table-column prop="stage" label="阶段" width="90" />
        <el-table-column label="证型" width="140">
          <template #default="{ row }">{{ row.syndrome?.name || '通用' }}</template>
        </el-table-column>
        <el-table-column label="内治方" width="160">
          <template #default="{ row }">{{ row.formula?.name || '—' }}</template>
        </el-table-column>
        <el-table-column label="外治" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ row.external_treatment || '—' }}</template>
        </el-table-column>
        <el-table-column label="调护" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ row.nursing || '—' }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-empty v-if="!loading && !disease.id" description="病种不存在" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDisease } from '../api'

const route = useRoute()
const router = useRouter()
const disease = ref({})
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    disease.value = (await getDisease(route.params.id)) || {}
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
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.image-item {
  text-align: center;
}

.book-img {
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

.img-caption {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}
</style>
