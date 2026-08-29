<template>
  <div class="qz-page">
    <div class="qz-body">
      <div v-if="!result" class="qz-setup">
        <el-card shadow="never">
          <el-form label-position="top">
            <el-form-item label="出题范围">
              <el-radio-group v-model="scope">
                <el-radio-button value="all">全部四科</el-radio-button>
                <el-radio-button value="surgery">外科疮疡</el-radio-button>
                <el-radio-button value="anorectal">肛肠痔漏</el-radio-button>
                <el-radio-button value="pediatrics">儿科</el-radio-button>
                <el-radio-button value="alchemy">丹药研究</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="题量">
              <el-slider v-model="n" :min="5" :max="20" :step="5" show-stops style="max-width:320px" />
            </el-form-item>
            <el-button type="primary" @click="start">开始自测({{ n }} 题)</el-button>
          </el-form>
        </el-card>
      </div>

      <div v-else-if="!submitted" class="qz-paper">
        <el-card v-for="(q, i) in questions" :key="q.id" shadow="never" class="q-card">
          <div class="q-head">{{ i + 1 }}. {{ q.q }}</div>
          <el-radio-group v-model="answers[q.id]" class="q-opts">
            <el-radio v-for="o in q.options" :key="o" :value="o" style="display:block;margin:6px 0">{{ o }}</el-radio>
          </el-radio-group>
        </el-card>
        <el-button type="primary" size="large" style="width:100%" @click="submit">交卷</el-button>
      </div>

      <div v-else class="qz-result">
        <el-card shadow="never">
          <div class="score-big">{{ result.score }}<span style="font-size:16px"> 分</span></div>
          <div style="color:#666">{{ result.correct }}/{{ result.total }} 答对</div>
          <el-button style="margin-top:12px" @click="again">再来一组</el-button>
          <el-button type="primary" plain @click="router.push('/learn')">返回学苑</el-button>
        </el-card>
        <el-card v-for="d in result.detail" :key="d.id" shadow="never" class="q-card" :class="d.ok ? 'ok' : 'bad'">
          <div class="q-head">{{ d.q }}</div>
          <div class="ans-line">你的答案:<b :class="d.ok ? 'g' : 'r'">{{ d.chosen }}</b>
            <template v-if="!d.ok"> · 正确答案:<b class="g">{{ d.answer }}</b></template>
            <el-tag size="small" :type="d.ok ? 'success' : 'danger'" style="margin-left:8px">{{ d.ok ? '正确' : '错误' }}</el-tag>
          </div>
          <div class="explain">{{ d.explain }}</div>
          <el-button link type="primary" size="small" @click="router.push('/kb/' + d.item_type + '/' + d.item_id)">查看总库详情 →</el-button>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getQuiz, submitQuiz } from '@/api/learn'

const router = useRouter()
const scope = ref('all')
const n = ref(10)
const questions = ref([])
const answers = reactive({})
const result = ref(null)
const submitted = ref(false)

async function start() {
  const res = await getQuiz({ scope: scope.value, n: n.value })
  questions.value = res.questions || []
  for (const k of Object.keys(answers)) delete answers[k]
  submitted.value = false
  result.value = null
}
async function submit() {
  const payload = (questions.value || []).map(q => ({
    id: q.id, q: q.q, item_type: q.item_type, item_id: q.item_id,
    chosen: answers[q.id] || '',
  }))
  result.value = await submitQuiz({ scope: scope.value, answers: payload })
  submitted.value = true
  window.scrollTo(0, 0)
}
function again() { result.value = null; start() }
</script>

<style scoped>
.qz-page { min-height: 100vh; background: #f5f7fa; }
.qz-topbar { display: flex; align-items: center; gap: 18px; padding: 12px 24px; background: #fff; border-bottom: 1px solid #e8e8e8; }
.qz-title { font-weight: 700; font-size: 16px; }
.qz-body { max-width: 760px; margin: 0 auto; padding: 20px 16px; }
.qz-paper .q-card { margin-bottom: 12px; }
.q-card { margin-bottom: 12px; }
.q-card.ok { border-left: 4px solid #67c23a; }
.q-card.bad { border-left: 4px solid #f56c6c; }
.q-head { font-weight: 600; margin-bottom: 8px; }
.q-opts { width: 100%; }
.ans-line { font-size: 13.5px; }
.g { color: #67c23a; } .r { color: #f56c6c; }
.explain { color: #7a8494; font-size: 12.5px; margin-top: 6px; background: #f8f9fa; padding: 6px 8px; border-radius: 6px; }
.score-big { font-size: 44px; font-weight: 800; color: #1f6e8c; }
</style>
