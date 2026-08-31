<script setup lang="ts">
import { ref, computed } from 'vue'
import { syndromes } from '../data/syndromes'
import { suduRows, chuanbian, jianbieTips } from '../data/sudu'

const tab = ref('gelun')
const isMobile = ref(window.matchMedia('(max-width: 768px)').matches)
window.matchMedia('(max-width: 768px)').addEventListener('change', e => { isMobile.value = e.matches })
const activeId = ref(syndromes[0].id)
const active = computed(() => syndromes.find((s) => s.id === activeId.value)!)

const liu = [
  { t: '外候', k: 'waihou' },
  { t: '病因', k: 'bingyin' },
  { t: '手纹', k: 'shouwen' },
  { t: '脉法', k: 'maifa' },
  { t: '治法', k: 'zhifa' },
  { t: '方药', k: 'fangyao' },
] as const
</script>

<template>
  <div class="page">
    <div class="h-title" style="font-size: 26px">下编 · 各论八症治法</div>
    <p class="vern" style="margin-top: 6px">
      八症论治每一症候皆以<b>外候、病因、手纹、脉法、治法、方药</b>六个原则立法；
      各方为"方底"，须依条下加减法加入药味始齐。
    </p>

    <el-tabs v-model="tab" class="no-print">
      <el-tab-pane label="八症各论" name="gelun" />
      <el-tab-pane label="八症鉴别速查表" name="sudu" />
    </el-tabs>

    <!-- 八症各论 -->
    <template v-if="tab === 'gelun'">
    <el-tabs v-model="activeId" class="no-print">
      <el-tab-pane v-for="s in syndromes" :key="s.id" :name="s.id" :label="`${s.order}. ${s.name}`" />
    </el-tabs>

    <div class="card">
      <div class="head">
        <div>
          <span class="order">第{{ active.order }}条</span>
          <span class="name">{{ active.name }}</span>
          <span v-if="active.altName" class="alt">（{{ active.altName }}）</span>
        </div>
        <div class="methods">
          <span v-for="m in active.methods" :key="m" class="tag-method">{{ m }}</span>
        </div>
      </div>
      <p class="summary">{{ active.summary }}</p>

      <div v-for="l in liu" :key="l.k">
        <div class="h-sub">{{ l.t }}</div>
        <template v-if="l.k === 'fangyao'">
          <div class="original">{{ active.fangyao.name }}：{{ active.fangyao.usage }}</div>
          <el-table :data="active.fangyao.herbs" size="small" border>
            <el-table-column prop="name" label="药味" width="110" />
            <el-table-column prop="dose" label="剂量" width="90" />
            <el-table-column prop="note" label="原著注" />
          </el-table>
        </template>
        <template v-else>
          <div class="original">{{ (active[l.k] as any).original }}</div>
          <p class="vern">{{ (active[l.k] as any).plain }}</p>
        </template>
      </div>

      <template v-if="active.jiajian.length">
        <div class="h-sub">加减法（兼某症加某药）</div>
        <el-table :data="active.jiajian" size="small" border>
          <el-table-column prop="cond" label="兼证" width="200" />
          <el-table-column prop="add" label="加味" />
        </el-table>
      </template>

      <template v-if="active.wansan.length">
        <div class="h-sub">丸散</div>
        <p v-for="w in active.wansan" :key="w.cond + w.powder" class="vern">{{ w.cond }}：{{ w.powder }}</p>
      </template>

      <template v-if="active.prognosis">
        <div class="h-sub">预后与顺逆</div>
        <div class="original">{{ active.prognosis.original }}</div>
        <p class="vern">{{ active.prognosis.plain }}</p>
      </template>

      <template v-if="active.relation">
        <div class="h-sub">与诸症关系</div>
        <p class="vern">{{ active.relation }}</p>
      </template>
    </div>
    </template>

    <!-- 八症鉴别速查表 -->
    <template v-else>
      <div class="card">
        <div class="h-sub">{{ chuanbian.title }}</div>
        <el-steps :active="3" finish-status="success" align-center class="no-print cb-steps">
          <el-step v-for="(st, i) in chuanbian.steps" :key="st.name" :title="st.name" :description="st.desc" :status="i < 2 ? 'success' : 'process'" />
        </el-steps>
      </div>

      <div class="card">
        <el-table :data="suduRows" border size="default" class="sudu-table">
          <el-table-column prop="name" label="八症" width="92" fixed>
            <template #default="{ row }"><b style="font-family: var(--font-kai); color: var(--vermilion); font-size: 15px">{{ row.name }}</b></template>
          </el-table-column>
          <el-table-column prop="waihou" label="主证外候" min-width="220" />
          <el-table-column v-if="!isMobile" prop="shouwen" label="手纹" min-width="170" />
          <el-table-column v-if="!isMobile" prop="mai" label="脉象" min-width="130" />
          <el-table-column prop="zhifa" label="治法" width="130" />
          <el-table-column prop="fang" label="方底" min-width="220" />
          <el-table-column prop="jianbie" label="鉴别要点" min-width="200" />
        </el-table>
      </div>

      <div class="h-sec">疑似证鉴别四则</div>
      <el-row :gutter="14">
        <el-col v-for="t in jianbieTips" :key="t.title" :xs="24" :md="12">
          <div class="card tip">
            <div class="tip-title">{{ t.title }}</div>
            <p class="vern">{{ t.text }}</p>
          </div>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  border-bottom: 1px dashed var(--line);
  padding-bottom: 12px;
}
.order {
  display: inline-block;
  background: var(--vermilion);
  color: #fdf6e8;
  border-radius: 4px;
  padding: 2px 10px;
  font-size: 12.5px;
  margin-right: 10px;
}
.name {
  font-family: var(--font-kai);
  font-size: 26px;
  font-weight: 700;
  color: var(--ink);
}
.alt {
  color: var(--ink-soft);
  font-size: 13.5px;
}
.summary {
  color: var(--ink-soft);
  line-height: 1.9;
  font-size: 14px;
  background: var(--paper-light);
  border-radius: 6px;
  padding: 10px 14px;
}
.cb-steps :deep(.el-step__description) {
  font-size: 12px;
  color: var(--ink-soft);
  max-width: 220px;
  margin: 0 auto;
}
.tip-title {
  font-family: var(--font-kai);
  font-weight: 700;
  font-size: 16px;
  color: var(--jade);
  margin-bottom: 6px;
}
.tip {
  min-height: 150px;
}
</style>
