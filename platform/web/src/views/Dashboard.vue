<template>
  <div class="xl-page">
    <!-- 品牌横幅 -->
    <div class="dash-hero">
      <div>
        <h2>杏林汇 · 智能诊疗工作台</h2>
        <p class="hero-sub">四科合参 · 知识总库 · AI 辨证 —— 一个系统,完成从学习到诊疗的全部工作</p>
      </div>
      <el-button type="primary" size="large" @click="router.push('/clinic/new')">
        <el-icon><Plus /></el-icon>&nbsp;新建就诊
      </el-button>
    </div>

    <el-row :gutter="14" style="margin-bottom:14px">
      <el-col :span="6"><div class="xl-card stat"><div class="xl-num">{{ fmt(pv) }}</div><div class="xl-label">平台总访问(PV)</div></div></el-col>
      <el-col :span="6"><div class="xl-card stat"><div class="xl-num">{{ fmt(uv) }}</div><div class="xl-label">独立访客(UV)</div></div></el-col>
      <el-col :span="6"><div class="xl-card stat"><div class="xl-num">{{ fmt(myTotal) }}</div><div class="xl-label">我的就诊记录</div></div></el-col>
      <el-col :span="6"><div class="xl-card stat"><div class="xl-num">{{ fmt(myToday) }}</div><div class="xl-label">今日新增就诊</div></div></el-col>
    </el-row>

    <div class="xl-card" style="margin-bottom:14px">
      <h3>快捷入口</h3>
      <div class="quick-grid">
        <div class="quick" @click="router.push('/clinic/new')"><span class="q-ico">🩺</span><b>门诊接诊</b><i>四诊录入 → AI 辨证 → 处方</i></div>
        <div class="quick" @click="router.push('/dx')"><span class="q-ico">🔮</span><b>智能辨证</b><i>跨专科证型病种方剂推荐</i></div>
        <div class="quick" @click="router.push('/kb')"><span class="q-ico">📚</span><b>知识总库</b><i>3,500+ 方药病证案诀</i></div>
        <div class="quick" @click="router.push('/learn')"><span class="q-ico">🎓</span><b>学苑</b><i>学习路径 · 自测 · AI 助教</i></div>
      </div>
    </div>

    <div class="xl-card" v-if="followups.length" style="margin-bottom:14px">
      <div class="card-head">
        <h3>🔔 随访提醒</h3>
        <span class="fu-count">{{ overdueCount }} 例逾期 · {{ followups.length - overdueCount }} 例近期</span>
      </div>
      <div class="fu-grid">
        <div v-for="f in followups" :key="f.visit_id" class="fu-item" :class="{ od: f.overdue }" @click="router.push('/clinic/' + f.visit_id)">
          <b>{{ f.patient_name }}</b>
          <el-tag size="small" :type="TAG2[f.specialty]">{{ SPEC[f.specialty] }}</el-tag>
          <span class="fu-date">{{ f.overdue ? '逾期 ' : '' }}{{ f.days_left < 0 ? -f.days_left : f.days_left }} 天 · {{ f.followup_date }}</span>
          <i>{{ f.chief_complaint || f.note }}</i>
        </div>
      </div>
    </div>

    <el-row :gutter="14">
      <el-col :span="15">
        <div class="xl-card">
          <div class="card-head"><h3>最近就诊</h3><el-button text size="small" @click="router.push('/clinic')">全部 →</el-button></div>
          <el-table :data="recent" size="small" style="width:100%">
            <el-table-column prop="patient_name" label="患者" width="110" />
            <el-table-column label="专科" width="90">
              <template #default="{ row }"><el-tag size="small" :type="SPEC_TAG[row.specialty]">{{ SPEC[row.specialty] }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="chief_complaint" label="主诉" show-overflow-tooltip />
            <el-table-column label="时间" width="130">
              <template #default="{ row }">{{ fmtTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="" width="60">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="router.push('/clinic/' + row.id)">查看</el-button>
              </template>
            </el-table-column>
            <template #empty><div class="xl-empty">暂无就诊记录,点右上角"新建就诊"开始</div></template>
          </el-table>
        </div>
      </el-col>
      <el-col :span="9">
        <div class="xl-card">
          <h3>四科专科知识</h3>
          <div v-for="m in MODULES" :key="m.key" class="spec-row" @click="router.push('/kb?module=' + m.key)">
            <span class="spec-ico">{{ m.icon }}</span>
            <div class="spec-txt"><b>{{ m.name }}</b><i>{{ m.desc }}</i></div>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, ArrowRight } from '@element-plus/icons-vue'
import { clinicDashboard, clinicFollowups } from '@/api/clinic'

const router = useRouter()
const SPEC = { surgery: '外科疮疡', anorectal: '肛肠痔漏', pediatrics: '儿科', alchemy: '丹药研究' }
const SPEC_TAG = { surgery: 'danger', anorectal: 'warning', pediatrics: 'success', alchemy: 'info' }
const TAG2 = SPEC_TAG
const MODULES = [
  { key: 'surgery', icon: '🩹', name: '外科疮疡', desc: '疔痈疽 · 消托补' },
  { key: 'anorectal', icon: '🩺', name: '肛肠痔漏', desc: '痔瘘裂脱 · 凉血利湿' },
  { key: 'pediatrics', icon: '👶', name: '儿科', desc: '八症六字' },
  { key: 'alchemy', icon: '⚗️', name: '丹药研究', desc: '三大汞类 · 安全第一' },
]

const pv = ref(0)
const uv = ref(0)
const myTotal = ref(0)
const myToday = ref(0)
const recent = ref([])
const followups = ref([])

onMounted(async () => {
  try {
    const d = await clinicDashboard()
    pv.value = d.platform?.pv || 0
    uv.value = d.platform?.uv || 0
    myTotal.value = d.my_visits_total || 0
    myToday.value = d.my_visits_today || 0
    recent.value = d.recent || []
    const fu = await clinicFollowups({ days: 14 })
    followups.value = fu.items || []
  } catch (e) { console.error(e) }
})
const overdueCount = computed(() => followups.value.filter(f => f.overdue).length)
const fmt = (n) => (n ?? 0).toLocaleString()
const fmtTime = (t) => (t ? String(t).replace('T', ' ').slice(5, 16) : '')
</script>

<style scoped>
.dash-hero {
  background: linear-gradient(115deg, #17332E 0%, #1F4E46 55%, #2E7D6B 100%);
  border-radius: 14px; padding: 26px 28px; color: #fff;
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;
}
.dash-hero h2 { color: #fff; font-size: 22px; margin-bottom: 6px; }
.hero-sub { color: #C6DAD2; font-size: 13px; }
.stat { text-align: center; padding: 16px 10px; }
.quick-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.quick { border: 1px solid var(--xl-line); border-radius: 10px; padding: 14px; cursor: pointer; transition: all .15s; }
.quick:hover { border-color: var(--xl-teal); box-shadow: var(--xl-shadow); transform: translateY(-2px); }
.q-ico { font-size: 22px; }
.quick b { display: block; margin: 6px 0 2px; color: var(--xl-ink); }
.quick i { font-style: normal; font-size: 12px; color: #8A94A0; }
.card-head { display: flex; align-items: center; justify-content: space-between; }
.card-head h3 { margin: 0; }
.spec-row {
  display: flex; align-items: center; gap: 12px; padding: 10px 8px; border-radius: 10px; cursor: pointer;
}
.spec-row:hover { background: var(--xl-mint); }
.spec-ico { font-size: 20px; }
.spec-txt { flex: 1; display: flex; flex-direction: column; }
.spec-txt b { color: var(--xl-ink); }
.spec-txt i { font-style: normal; font-size: 12px; color: #8A94A0; }
.fu-count { color: var(--xl-cinnabar); font-size: 12.5px; }
.fu-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 10px; }
.fu-item { border: 1px solid var(--xl-line); border-radius: 10px; padding: 10px 12px; cursor: pointer; display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.fu-item.od { border-color: #E8B4AE; background: #FBF2F1; }
.fu-item b { color: var(--xl-ink); }
.fu-date { color: var(--xl-cinnabar); font-size: 12px; margin-left: auto; }
.fu-item i { font-style: normal; width: 100%; font-size: 12px; color: #8A94A0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
