<template>
  <div class="ask-page">
    <div class="ask-body">
      <el-card shadow="never" style="margin-bottom:14px">
        <p style="color:#5c6b73;margin-top:0">学习中医有问题?向 AI 助教提问——它会结合知识总库内容作答;丹药相关问题必附毒性警示。</p>
        <div class="ask-samples">
          试试:
          <el-tag v-for="s in samples" :key="s" style="cursor:pointer;margin:0 6px 4px 0" @click="q = s">{{ s }}</el-tag>
        </div>
        <el-input v-model="q" type="textarea" :rows="3" placeholder="输入你的问题…" maxlength="2000" show-word-limit />
        <el-button type="primary" style="margin-top:10px" :loading="loading" @click="ask">提问</el-button>
      </el-card>

      <el-card v-if="answer" shadow="never">
        <template #header><b>🤖 助教回答</b></template>
        <div class="answer">{{ answer }}</div>
        <div class="answer-ops">
          <el-button size="small" @click="ask">追问</el-button>
          <el-button size="small" plain @click="copyAns">复制回答</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { aiAsk } from '@/api/learn'

const router = useRouter()
const q = ref('')
const answer = ref('')
const loading = ref(false)
const samples = [
  '八症六字是什么意思?',
  '为什么说"治疮疡忌挤压"?',
  '五味消毒饮和仙方活命饮怎么区分使用?',
  '毒龙丹为什么是剧毒药?',
  '儿科风热证为什么用平肝泻心法?',
  '痔疮便血和肠风下血怎么鉴别?'
]

async function ask() {
  if (!q.value.trim()) { ElMessage.warning('请输入问题'); return }
  loading.value = true
  try {
    const res = await aiAsk({ question: q.value.trim() })
    answer.value = res.answer
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || 'AI 服务暂时不可用')
  } finally {
    loading.value = false
  }
}
async function copyAns() {
  try {
    await navigator.clipboard.writeText(answer.value)
    ElMessage.success('已复制')
  } catch {
    ElMessage.warning('复制失败,请手动选择复制')
  }
}
</script>

<style scoped>
.ask-page { min-height: 100vh; background: #f5f7fa; }
.ask-topbar { display: flex; align-items: center; gap: 18px; padding: 12px 24px; background: #fff; border-bottom: 1px solid #e8e8e8; }
.ask-title { font-weight: 700; font-size: 16px; }
.ask-body { max-width: 820px; margin: 0 auto; padding: 20px 16px; }
.ask-samples { margin: 10px 0; color: #8a94a0; font-size: 13px; }
.answer { overflow-wrap: break-word; word-break: break-word; white-space: pre-wrap; line-height: 1.9; font-size: 14.5px; }
.answer-ops { margin-top: 12px; }
</style>
