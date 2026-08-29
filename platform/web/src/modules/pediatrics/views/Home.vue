<script setup lang="ts">
import { useRouter } from 'vue-router'
import { liuziShuo } from '../data/syndromes'

const router = useRouter()
const six = ['平肝', '补脾', '泻心']

const modules = [
  { path: '/pediatrics/bianzheng', name: '辨证论治', desc: '四诊采集 → 八症辨证 → 六字立法 → 方药加减 → 报告打印' },
  { path: '/pediatrics/zonglun', name: '总论', desc: '释八症六字说 · 诊手纹法 · 切脉法 · 看外症法 · 问诊法' },
  { path: '/pediatrics/bazheng', name: '八症各论', desc: '风热 急惊 慢惊 慢脾风 脾虚 疳积 燥火 咳嗽' },
  { path: '/pediatrics/tupu', name: '图谱', desc: '手纹脉位图 · 手纹十八图式 · 面部属位图 · 推拿诸穴图' },
  { path: '/pediatrics/fangji', name: '方剂库', desc: '八方底 · 官方验方 · 暑痢疟方 · 丸散 · 外治法' },
  { path: '/pediatrics/yongyao', name: '用药心得', desc: '用药秘验杂说 · 药性赋幼科摘要' },
  { path: '/pediatrics/weihou', name: '危候警示', desc: '死症四十候 · 识症趋避 · 痢症坏候 · 慢脾绝候' },
  { path: '/pediatrics/tuina', name: '推拿代药', desc: '推拿代药赋 · 手法歌诀 · 灯火艾灸法' },
  { path: '/pediatrics/xunjie', name: '医道训诫', desc: '言症论治 · 承先遗训 · 九恨 · 十三不可学 · 十传' },
  { path: '/pediatrics/zice', name: '自测练习', desc: '辨证 · 方药 · 歌诀 · 图谱辨识 · 错题本' },
]
</script>

<template>
  <div class="page">
    <!-- 书名区 -->
    <div class="hero card">
      <div class="hero-left">
        <h1 class="h-title" style="font-size: 34px">程氏家传儿科秘要</h1>
        <p class="hero-sub">清 · 程康圃 著</p>
        <p class="hero-desc">
          岭南儿科名医程康圃（1821—1908）六代业医、五十年临证所得之秘要：
          儿科病证<b>赅以八门</b>，治法<b>约以六字</b>——<span class="hl">平肝、补脾、泻心</span>。
          本系统据原著构建，将"诊手纹 → 切脉 → 看外症 → 问诊 → 辨八症 → 六字立法 → 方药加减"的
          临床路径数字化，供临床辅助辨证论治与系统学习之用。
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="router.push('/pediatrics/bianzheng')">开始辨证论治</el-button>
          <el-button size="large" @click="router.push('/pediatrics/bazheng')">研读八症各论</el-button>
          <el-button size="large" @click="router.push('/pediatrics/zice')">自测练习</el-button>
        </div>
      </div>
      <div class="hero-right">
        <div class="sixzi">
          <div class="sixzi-title">治法六字</div>
          <div class="sixzi-chars">
            <span v-for="c in six" :key="c" class="sixzi-char">{{ c }}</span>
          </div>
          <div class="sixzi-note">小儿肝常有余 · 脾常不足 · 心火常炎</div>
        </div>
      </div>
    </div>

    <!-- 八症六字总览 -->
    <div class="h-sec">八症 · 六字总览</div>
    <el-row :gutter="14">
      <el-col v-for="p in liuziShuo.per" :key="p.s" :xs="12" :sm="8" :md="6">
        <div class="card sy-card" @click="router.push('/pediatrics/bazheng')">
          <div class="sy-name">{{ p.s }}</div>
          <div class="sy-methods">
            <span v-for="m in p.methods" :key="m" class="tag-method">{{ m }}</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 模块导航 -->
    <div class="h-sec">系统模块</div>
    <el-row :gutter="14">
      <el-col v-for="m in modules" :key="m.path" :xs="12" :sm="8" :md="6">
        <div class="card mod-card" @click="router.push(m.path)">
          <div class="mod-name">{{ m.name }}</div>
          <div class="mod-desc">{{ m.desc }}</div>
        </div>
      </el-col>
    </el-row>

    <div class="warn-banner">
      <b>免责声明：</b>本系统内容据《程氏家传儿科秘要》整理，仅用于中医儿科临床参考与教学，
      不构成医疗决策。辨证论治结果须由执业医师结合患儿实际复核；凡原著所列死候、危候，
      系统一律提示立即告知家属并寻求中西医协同救治，不得延误。
    </div>
  </div>
</template>

<style scoped>
.hero {
  display: flex;
  gap: 28px;
  align-items: center;
  flex-wrap: wrap;
  padding: 30px 34px;
}
.hero-left {
  flex: 1;
  min-width: 320px;
}
.hero-sub {
  color: var(--ink-soft);
  font-size: 13.5px;
  margin: 8px 0 14px;
}
.hero-desc {
  line-height: 1.95;
  font-size: 14.5px;
  color: var(--ink);
}
.hero-desc .hl {
  color: var(--vermilion);
  font-weight: 700;
  font-family: var(--font-kai);
}
.hero-actions {
  margin-top: 18px;
}
.hero-right {
  min-width: 240px;
  display: flex;
  justify-content: center;
}
.sixzi {
  background: var(--card);
  border: 2px solid var(--vermilion);
  border-radius: 10px;
  padding: 20px 26px;
  text-align: center;
  box-shadow: var(--shadow);
}
.sixzi-title {
  font-family: var(--font-kai);
  color: var(--ink-soft);
  letter-spacing: 6px;
}
.sixzi-chars {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin: 12px 0;
}
.sixzi-char {
  width: 58px;
  height: 58px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--vermilion);
  color: #fdf6e8;
  font-family: var(--font-kai);
  font-size: 26px;
  border-radius: 8px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.35);
}
.sixzi-note {
  font-size: 12px;
  color: var(--ink-soft);
}
.sy-card,
.mod-card {
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
.sy-card:hover,
.mod-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(43, 35, 24, 0.16);
}
.sy-name {
  font-family: var(--font-kai);
  font-size: 20px;
  font-weight: 700;
  color: var(--vermilion);
  margin-bottom: 8px;
}
.mod-name {
  font-family: var(--font-kai);
  font-size: 16.5px;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 6px;
}
.mod-desc {
  font-size: 12.5px;
  color: var(--ink-soft);
  line-height: 1.7;
}
</style>
