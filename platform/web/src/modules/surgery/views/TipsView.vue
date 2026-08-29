<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>临床要诀</span>
          <el-select v-model="category" placeholder="分类筛选" clearable style="width:160px" @change="load">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
        </div>
      </template>

      <el-table :data="tips" v-loading="loading" stripe>
        <el-table-column prop="category" label="分类" width="150">
          <template #default="{ row }"><el-tag size="small">{{ row.category }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="content" label="要诀内容" min-width="400" show-overflow-tooltip />
        <el-table-column prop="source" label="出处" width="200" show-overflow-tooltip />
      </el-table>
      <el-empty v-if="!loading && !tips.length" description="暂无要诀数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listTips } from '../api'

const tips = ref([])
const categories = ref([])
const category = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = (await listTips({ category: category.value || undefined })) || []
    tips.value = res
    const set = new Set(res.map((t) => t.category).filter(Boolean))
    categories.value = [...set]
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
