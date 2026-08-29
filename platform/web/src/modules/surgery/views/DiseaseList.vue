<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="title-side">
            <span>疾病库（疮疡图谱）</span>
            <el-button link type="primary" size="small" @click="router.push('/kb?module=surgery')">
              在知识总库检索该专科内容
            </el-button>
          </div>
          <el-input
            v-model="kw"
            placeholder="搜索病名 / 别名 / 部位 / 疮形特点"
            prefix-icon="Search"
            clearable
            style="width: 300px"
            @keyup.enter="doSearch"
            @clear="loadList"
          >
            <template #append>
              <el-button @click="doSearch">搜索</el-button>
            </template>
          </el-input>
        </div>
      </template>

      <div class="filter-bar">
        <el-radio-group v-model="category" @change="loadList">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button v-for="c in categories" :key="c" :value="c">{{ c }}</el-radio-button>
        </el-radio-group>
      </div>

      <div v-loading="loading">
        <el-row :gutter="16">
          <el-col v-for="d in diseases" :key="d.id" :xs="24" :sm="12" :md="8" :lg="6">
            <div class="disease-card" @click="router.push(`/surgery/diseases/${d.id}`)">
              <div class="thumb">
                <el-image v-if="d.thumbnail" :src="d.thumbnail" fit="cover" class="thumb-img">
                  <template #error><div class="thumb-placeholder">无图</div></template>
                </el-image>
                <div v-else class="thumb-placeholder">{{ d.name.charAt(0) }}</div>
                <el-tag v-if="d.is_dangerous" type="danger" size="small" class="danger-tag">危险</el-tag>
              </div>
              <div class="disease-info">
                <div class="disease-name">{{ d.name }}</div>
                <div class="disease-meta">
                  <el-tag size="small" type="info">{{ d.category }}</el-tag>
                  <span v-if="d.location" class="loc">{{ d.location }}</span>
                </div>
                <div class="aliases" v-if="(d.aliases || []).length">
                  别名：{{ (d.aliases || []).join('、') }}
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
        <el-empty v-if="!loading && !diseases.length" description="暂无病种数据" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listDiseaseCategories, listDiseases, searchDiseases } from '../api'

const router = useRouter()
const categories = ref([])
const diseases = ref([])
const category = ref('')
const kw = ref('')
const loading = ref(false)

async function loadList() {
  loading.value = true
  try {
    const res = await listDiseases({ category: category.value || undefined })
    diseases.value = res || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function doSearch() {
  if (!kw.value.trim()) {
    loadList()
    return
  }
  loading.value = true
  try {
    const res = await searchDiseases(kw.value.trim())
    diseases.value = res || []
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
  loadList()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.title-side {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-bar {
  margin-bottom: 16px;
}

.disease-card {
  border: 1px solid #e7e3da;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
  cursor: pointer;
  margin-bottom: 16px;
  transition: box-shadow 0.15s, transform 0.15s;
}

.disease-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.thumb {
  position: relative;
  height: 140px;
  background: #f5f3ec;
}

.thumb-img {
  width: 100%;
  height: 100%;
}

.thumb-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: #b9a87e;
  background: #f5f3ec;
}

.danger-tag {
  position: absolute;
  top: 8px;
  right: 8px;
}

.disease-info {
  padding: 12px 14px;
}

.disease-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e2227;
  margin-bottom: 6px;
}

.disease-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loc {
  font-size: 12px;
  color: #909399;
}

.aliases {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
