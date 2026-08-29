<template>
  <div class="knowledge">
    <el-card>
      <template #header>
        <div class="header">
          <span><el-icon><Reading /></el-icon> 疮疡知识库</span>
          <div class="header-filters">
            <el-select v-model="selectedCategory" placeholder="选择分类" style="width: 150px; margin-right: 10px" @change="loadKnowledge">
              <el-option label="全部" value="" />
              <el-option label="痈" value="痈" />
              <el-option label="疽" value="疽" />
              <el-option label="疖" value="疖" />
              <el-option label="疔" value="疔" />
              <el-option label="疮" value="疮" />
            </el-select>
            <el-select v-model="selectedLocation" placeholder="选择部位" style="width: 150px; margin-right: 10px" @change="loadKnowledge">
              <el-option label="全部" value="" />
              <el-option label="头面部" value="头面部" />
              <el-option label="上肢" value="上肢" />
              <el-option label="下肢" value="下肢" />
              <el-option label="躯干" value="躯干" />
            </el-select>
            <el-input
              v-model="searchText"
              placeholder="搜索疮疡名称"
              style="width: 200px"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
      </template>

      <div v-loading="loading">
        <el-row :gutter="20">
          <el-col :span="8" v-for="item in knowledgeList" :key="item.id">
            <el-card class="knowledge-card" shadow="hover" @click="handleView(item)">
              <div class="card-header">
                <h3>{{ item.chinese_name }}</h3>
                <el-tag size="small">{{ item.category }}</el-tag>
              </div>
              <div class="card-body">
                <p class="location">
                  <el-icon><Location /></el-icon>
                  {{ item.location }}
                </p>
                <p class="features" v-if="item.morphology">
                  <strong>形态特征：</strong>
                  {{ item.morphology.color }}，{{ item.morphology.size }}
                </p>
                <p class="treatment" v-if="item.treatment_principle">
                  <strong>治则：</strong>{{ item.treatment_principle }}
                </p>
              </div>
              <div class="card-footer">
                <el-text type="info" size="small">
                  来源：疮疡图谱 p{{ item.page_number }}
                </el-text>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-empty v-if="knowledgeList.length === 0 && !loading" description="暂无数据" />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="currentItem?.chinese_name"
      width="80%"
      top="5vh"
    >
      <div v-if="currentItem" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="中文名称">
            {{ currentItem.chinese_name }}
          </el-descriptions-item>
          <el-descriptions-item label="分类">
            <el-tag>{{ currentItem.category }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="好发部位" :span="2">
            {{ currentItem.location }} - {{ currentItem.location_detail }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">病因病机</el-divider>
        <el-descriptions :column="1" border v-if="currentItem.etiology || currentItem.pathogenesis">
          <el-descriptions-item label="病因" v-if="currentItem.etiology">
            {{ currentItem.etiology }}
          </el-descriptions-item>
          <el-descriptions-item label="病机" v-if="currentItem.pathogenesis">
            {{ currentItem.pathogenesis }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">临床表现</el-divider>
        <el-descriptions :column="1" border v-if="currentItem.morphology">
          <el-descriptions-item label="形态特征">
            <el-tag style="margin: 3px">颜色：{{ currentItem.morphology.color }}</el-tag>
            <el-tag style="margin: 3px">大小：{{ currentItem.morphology.size }}</el-tag>
            <el-tag style="margin: 3px" v-if="currentItem.morphology.shape">形状：{{ currentItem.morphology.shape }}</el-tag>
            <el-tag style="margin: 3px" v-if="currentItem.morphology.texture">质地：{{ currentItem.morphology.texture }}</el-tag>
            <el-tag style="margin: 3px" v-if="currentItem.morphology.pain">疼痛：{{ currentItem.morphology.pain }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="临床特征" v-if="currentItem.clinical_features">
            {{ currentItem.clinical_features }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">治疗方案</el-divider>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="治则" v-if="currentItem.treatment_principle">
            {{ currentItem.treatment_principle }}
          </el-descriptions-item>
        </el-descriptions>

        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="12">
            <el-card header="内治法" v-if="currentItem.internal_treatment">
              <div v-if="currentItem.internal_treatment.formulas">
                <div v-for="(formula, index) in currentItem.internal_treatment.formulas" :key="index" style="margin-bottom: 15px">
                  <h4>{{ formula.name }}</h4>
                  <p><strong>组成：</strong>{{ formula.composition }}</p>
                  <p v-if="formula.modifications"><strong>加减：</strong>{{ formula.modifications }}</p>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card header="外治法" v-if="currentItem.external_treatment">
              <div v-if="currentItem.external_treatment.topical">
                <div v-for="(item, index) in currentItem.external_treatment.topical" :key="index" style="margin-bottom: 10px">
                  <el-tag type="success">{{ item.name }}</el-tag>
                  <span style="margin-left: 10px">{{ item.usage }}</span>
                </div>
              </div>
              <p v-if="currentItem.external_treatment.wash">
                <strong>熏洗：</strong>{{ currentItem.external_treatment.wash }}
              </p>
            </el-card>
          </el-col>
        </el-row>

        <el-divider content-position="left">预防与护理</el-divider>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="预防" v-if="currentItem.prevention">
            {{ currentItem.prevention }}
          </el-descriptions-item>
          <el-descriptions-item label="护理" v-if="currentItem.nursing">
            {{ currentItem.nursing }}
          </el-descriptions-item>
          <el-descriptions-item label="饮食建议" v-if="currentItem.diet_advice">
            {{ currentItem.diet_advice }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Reading, Search, Location } from '@element-plus/icons-vue'
import api from '../api'

const loading = ref(false)
const knowledgeList = ref([])
const selectedCategory = ref('')
const selectedLocation = ref('')
const searchText = ref('')

const showDetailDialog = ref(false)
const currentItem = ref(null)

const loadKnowledge = async () => {
  loading.value = true
  try {
    const response = await api.get('/ulcers/knowledge/ulcers', {
      params: {
        category: selectedCategory.value,
        location: selectedLocation.value,
        search: searchText.value
      }
    })
    knowledgeList.value = response.data
  } catch (error) {
    ElMessage.error('加载知识库失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadKnowledge()
}

const handleView = async (item) => {
  try {
    const response = await api.get(`/ulcers/knowledge/ulcers/${item.ulcer_type}`)
    currentItem.value = response.data
    showDetailDialog.value = true
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

onMounted(() => {
  loadKnowledge()
})
</script>

<style scoped>
.knowledge {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-filters {
  display: flex;
  align-items: center;
}

.knowledge-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.knowledge-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.card-body {
  min-height: 120px;
}

.location {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
}

.features,
.treatment {
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
  margin-bottom: 8px;
}

.card-footer {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.detail-content {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
