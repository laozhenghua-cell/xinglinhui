<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>名医经验</span>
          <el-select v-model="category" placeholder="选择病种大类" style="width:180px" @change="load">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
        </div>
      </template>

      <el-empty v-if="!category" description="请先选择病种大类查看名家经验与医案" />

      <div v-else v-loading="loading">
        <h3 class="sec-title">名家经验</h3>
        <div v-if="data.experiences?.length">
          <div v-for="e in data.experiences" :key="e.id" class="exp-card">
            <div class="exp-head">
              <span class="exp-name">{{ e.expert_name }}</span>
              <el-tag size="small" type="info">{{ e.category }}</el-tag>
            </div>
            <div v-if="e.syndrome_points" class="exp-block"><b>辨证要点：</b>{{ e.syndrome_points }}</div>
            <div v-if="e.internal_treatment" class="exp-block"><b>内治：</b>{{ e.internal_treatment }}</div>
            <div v-if="e.external_treatment" class="exp-block"><b>外治：</b>{{ e.external_treatment }}</div>
            <div v-if="e.source" class="exp-src">{{ e.source }}</div>
          </div>
        </div>
        <el-empty v-else description="暂无经验" :image-size="70" />

        <h3 class="sec-title">名家医案</h3>
        <div v-if="data.cases?.length">
          <div v-for="c in data.cases" :key="c.id" class="exp-card">
            <div class="exp-head">
              <span class="exp-name">{{ c.expert_name }}</span>
              <el-tag v-if="c.diagnosis" size="small">{{ c.diagnosis }}</el-tag>
            </div>
            <div v-if="c.history" class="exp-block"><b>病史：</b>{{ c.history }}</div>
            <div v-if="c.syndrome" class="exp-block"><b>辨证：</b>{{ c.syndrome }}</div>
            <div v-if="c.treatment" class="exp-block"><b>治疗：</b>{{ c.treatment }}</div>
            <div v-if="c.effect" class="exp-block"><b>疗效：</b>{{ c.effect }}</div>
          </div>
        </div>
        <el-empty v-else description="暂无医案" :image-size="70" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listDiseaseCategories, getExpert } from '../api'

const categories = ref([])
const category = ref('')
const data = ref({})
const loading = ref(false)

async function load() {
  if (!category.value) return
  loading.value = true
  try {
    data.value = (await getExpert(category.value)) || {}
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    categories.value = (await listDiseaseCategories()) || []
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sec-title {
  margin: 8px 0 12px;
  color: #2e4760;
  font-size: 15px;
}

.exp-card {
  border: 1px solid #e7e3da;
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 12px;
  background: #faf8f3;
}

.exp-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.exp-name {
  font-weight: 700;
  color: #1e2227;
}

.exp-block {
  font-size: 13.5px;
  line-height: 1.8;
  color: #333;
}

.exp-src {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
</style>
