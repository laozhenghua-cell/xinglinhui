<template>
  <div>
    <h1 class="page-title">毒龙丹引药全书</h1>
    <div class="page-sub">玄门四大丹之一 · 一药多引 · 共 {{ total }} 条（内科 {{ counts.internal }} · 妇科 {{ counts.gynecology }} · 儿科 {{ counts.pediatrics }} · 外科 {{ counts.surgery }}）</div>

    <div class="safety-banner">
      <strong>⚠️</strong> 毒龙丹主药为马钱子（番木鳖），含士的宁，为剧毒神经毒物。原书自诫：每服0.9克、每次最多不超过0.15克，服后避风一时，忌鱼腥海味、辛辣、菜菔，孕妇慎用；「病愈后必不可再用」。本品属毒性药品管理品种，<strong>仅供专业学术研究参考，严禁自行配制与服用</strong>。
    </div>

    <div class="card" style="padding:14px">
      <el-input v-model="kw" placeholder="检索病证或引药，如：咳嗽 / 生姜 / 疳积 / 梅毒…" clearable size="large" />
      <div class="pill-row" style="margin-top:10px">
        <span class="filter-pill" :class="{ active: sec === '' }" @click="sec = ''">全部（{{ total }}）</span>
        <span v-for="s in sections" :key="s.id" class="filter-pill" :class="{ active: sec === s.id }" @click="sec = s.id">
          {{ s.name }}（{{ s.entries.length }}）
        </span>
      </div>
    </div>

    <div class="card">
      <h3 style="margin-top:0">📖 方剂概况</h3>
      <p style="font-size:0.9rem;color:#5c5240;margin:0 0 6px">
        处方：马钱子，不拘多少。制法：以童便、五石（丹砂、雄黄、曾青、白矾、磁石）、五豆（扁豆、赤豆、绿豆、黄豆、黑豆，须发芽约三分）浸泡
        （春秋二十日，夏十四日，冬四十九日），刮去皮毛，入甘草水煮三小时，晒干研末，制为菜菔子大丸子。每服0.9克，早晚各服一次，按症用引药送服。
      </p>
      <p style="font-size:0.9rem;color:#5c5240;margin:0">
        功能：钻筋透骨，活络搜风，兴奋补脑。原书：「丹头药力都是霸道而不王道的，因此，病愈后就应停止使用」；赵学敏《串雅内编》：「药有最验者曰丹头，即劫药是也，病愈后必不可再用」。
      </p>
      <div style="margin-top:10px">
        <el-button type="danger" plain size="small" @click="$router.push('/alchemy/formula/F30')">查看方剂详情（F30）→</el-button>
        <el-button size="small" @click="$router.push('/alchemy/assist/professional')">去专业问诊选引药 →</el-button>
      </div>
    </div>

    <div v-for="s in filteredSections" :key="s.id" class="card">
      <h3 style="margin-top:0">{{ s.name }} <span style="font-size:0.78rem;color:#9a8a6c">· {{ s.pages }}</span></h3>
      <table style="width:100%;border-collapse:collapse;font-size:0.85rem">
        <thead>
          <tr style="background:var(--dan-paper-deep)">
            <th style="padding:6px;text-align:left;width:44px">序</th>
            <th style="padding:6px;text-align:left">病证</th>
            <th style="padding:6px;text-align:left">引药（煎汤送服）</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in s.entries" :key="e.n" style="border-top:1px solid #f0e9d8">
            <td style="padding:6px;color:#9a8a6c">{{ e.n }}</td>
            <td style="padding:6px">{{ e.d }}</td>
            <td style="padding:6px;color:#8a6a1c">{{ e.g }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="!filteredSections.length" class="card" style="text-align:center;color:#9a8a6c">未找到匹配条目</div>

    <div class="safety-banner">
      <strong>⚠️</strong> 本页 245 条引药忠实转录自原书第 110–122 页，仅为文献研究资料。马钱子制剂现代按毒性药品管理，严禁按此自行配制、服用。
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import dulong from '../data/dulong.json'

const kw = ref('')
const sec = ref('')
const sections = dulong.meta.sections
const counts = Object.fromEntries(sections.map((s) => [s.id, s.entries.length]))
const total = computed(() => sections.reduce((n, s) => n + s.entries.length, 0))

const filteredSections = computed(() => {
  const k = kw.value.trim()
  return sections
    .filter((s) => !sec.value || s.id === sec.value)
    .map((s) => ({
      ...s,
      entries: k
        ? s.entries.filter((e) => e.d.includes(k) || e.g.includes(k))
        : s.entries,
    }))
    .filter((s) => s.entries.length)
})
</script>
