<template>
  <div>
    <div class="safety-banner">
      <strong>⚠️ 安全声明：</strong>本系统为中医外科专业学术研究参考。丹药多为汞、砷剧毒化合物，现代已严格限制使用；<strong>严禁自行配制、严禁内服</strong>，临床须遵循现行药事法规。详见「安全与法规」栏目。
    </div>

    <h1 class="page-title">中国炼丹术与丹药</h1>
    <div class="page-sub">张觉人 著 · 四川人民出版社 · 1984 · 数字化研究参考系统</div>

    <div class="card">
      <h3 style="margin-top:0">📖 关于本书</h3>
      <p style="margin-bottom:6px">
        本书为中医外科名家张觉人（1890—1981）晚年所著，凝聚其七十年炼制与使用丹药的临床经验。
        上篇总论专谈中国炼丹术的发生与发展，使读者知道医用丹药的来龙去脉；
        下篇各论收集丹药中最有效、最适用的秘验方剂约三十个，按氯化汞、硫化汞、氧化汞三类，分升、降、烧三法介绍。
      </p>
      <p style="margin-bottom:0;color:#8a7a60;font-size:0.85rem">
        炼丹术虽未实现“炼金成仙”的幻想，却为现代化学打下初步基础，并给医药家提供了丹药的炼制法则，
        还发明了火药、指南针等——这是炼丹家对人类的贡献，应加以继承、整理、提高。
      </p>
    </div>

    <h3>三个维度</h3>
    <div class="card" style="display:flex;gap:10px;flex-wrap:wrap" v-for="d in dims" :key="d.title">
      <span style="font-size:1.6rem">{{ d.icon }}</span>
      <div>
        <strong>{{ d.title }}</strong>
        <div style="font-size:0.88rem;color:#6b5c42">{{ d.desc }}</div>
        <el-button size="small" type="danger" plain style="margin-top:6px" @click="$router.push(d.to)">进入 →</el-button>
      </div>
    </div>

    <h3>🩺 辨证选方（新）</h3>
    <div class="card" style="display:flex;gap:10px;border-color:var(--dan-red)">
      <span style="font-size:1.6rem">🩺</span>
      <div>
        <strong>问诊 → 辨证 → 候选方剂</strong>
        <div style="font-size:0.88rem;color:#6b5c42">专业研究模式（医师/研究者）：引导式问诊、可解释辨证、候选方剂附原书依据与安全闸门；大众科普模式：病证常识与就医指引，不推荐方剂。</div>
        <el-button size="small" type="danger" style="margin-top:6px" @click="$router.push('/alchemy/assist')">进入 →</el-button>
      </div>
    </div>

    <h3>快速入口</h3>
    <div class="card">
      <div class="pill-row">
        <span class="tag red" style="cursor:pointer" @click="$router.push('/alchemy/formulas')">🧪 方剂库（{{ formulas.formulas.length }} 方）</span>
        <span class="tag gold" style="cursor:pointer" @click="$router.push('/alchemy/timeline')">🕰️ 时间线（{{ timeline.timeline.length }} 条）</span>
        <span class="tag" style="cursor:pointer" @click="$router.push('/alchemy/glossary')">📖 术语表（{{ glossary.terms.length }} 条）</span>
        <span class="tag" style="cursor:pointer" @click="$router.push('/alchemy/quiz')">✍️ 知识测验</span>
        <span class="tag" style="cursor:pointer" @click="$router.push('/alchemy/original')">🖼️ 原书对照</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import book from '../data/book.json'
import chapters from '../data/chapters.json'
import formulas from '../data/formulas.json'
import glossary from '../data/glossary.json'
import timeline from '../data/timeline.json'

const dims = [
  { icon: '📜', title: '历史 · 源流', desc: '从战国方士到晋唐医药合流，看炼丹术两千年兴衰与对现代化学的贡献。', to: '/alchemy/chapters' },
  { icon: '🧠', title: '理解 · 理论', desc: '内丹与外丹、升降烧三法、氯化汞/硫化汞/氧化汞三类，术语与文献全解。', to: '/alchemy/glossary' },
  { icon: '⚕️', title: '使用 · 研究', desc: '约三十个秘验方剂数据库：组成、炼制、主治与禁忌原文，附现代安全警示。', to: '/alchemy/formulas' },
]
</script>
