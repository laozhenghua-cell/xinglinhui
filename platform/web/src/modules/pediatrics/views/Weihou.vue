<script setup lang="ts">
import { ref, computed } from 'vue'
import { deathSigns, deathSignsNote, shizhengQubi, lizhengHuaihou, manpiJuehou } from '../data/deathSigns'

const tab = ref('sizheng')
const levelFilter = ref('')
const filtered = computed(() =>
  deathSigns.filter((d) => !levelFilter.value || d.level === levelFilter.value)
)
</script>

<template>
  <div class="page">
    <div class="h-title" style="font-size: 26px">危候警示</div>
    <div class="warn-banner">
      <b>原著告诫：</b>"以上坏症皆为死候。小儿病久或急惊症则每有此见，见则不可言吉，须告明在先；
      但亦要用药挽救，不可坐视不理，以冀其死里回生。"
      临床遇下列征象，请立即告知家属并寻求中西医协同救治。
    </div>

    <el-tabs v-model="tab" class="no-print">
      <el-tab-pane label="死症四十候" name="sizheng" />
      <el-tab-pane label="识症趋避" name="qubi" />
      <el-tab-pane label="痢症坏候" name="liji" />
      <el-tab-pane label="慢脾风绝候" name="manpi" />
    </el-tabs>

    <template v-if="tab === 'sizheng'">
      <div class="card">
        <el-radio-group v-model="levelFilter" class="no-print" size="small">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="极危">极危</el-radio-button>
          <el-radio-button value="危">危</el-radio-button>
          <el-radio-button value="重">重</el-radio-button>
        </el-radio-group>
        <div class="grid">
          <div v-for="(d, i) in filtered" :key="i" class="ds" :class="d.level">
            <span class="ds-no">{{ String(i + 1).padStart(2, '0') }}</span>
            <span class="ds-sign">{{ d.sign }}</span>
            <span class="ds-name">{{ d.name }}</span>
            <span class="ds-level">{{ d.level }}</span>
          </div>
        </div>
        <p class="vern" style="margin-top: 12px">{{ deathSignsNote }}</p>
      </div>
    </template>

    <template v-else-if="tab === 'qubi'">
      <div class="card">
        <p class="vern">
          识症趋避——程氏告诫后辈：遇死症、难症当尽其所学而挽救之；"勿苟且应酬及不必计较钱财"。
        </p>
        <div v-for="(q, i) in shizhengQubi" :key="i" class="qb">
          <div class="qb-t">{{ String(i + 1).padStart(2, '0') }} · {{ q.t }}</div>
          <div class="original" style="font-size: 13.5px">{{ q.original }}</div>
        </div>
      </div>
    </template>

    <template v-else-if="tab === 'liji'">
      <div class="card">
        <div v-for="(l, i) in lizhengHuaihou" :key="i" class="qb">
          <div class="qb-t">{{ l.t }}</div>
          <div class="original" style="font-size: 13.5px">{{ l.original }}</div>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="card">
        <div class="original">{{ manpiJuehou.original }}</div>
        <div class="warn-banner">{{ manpiJuehou.plain }}</div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 8px;
  margin-top: 14px;
}
.ds {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 7px 10px;
  background: var(--paper-light);
  font-size: 13px;
}
.ds.jiwei,
.ds.极危 {
  border-left: 4px solid #c0392b;
}
.ds.危 {
  border-left: 4px solid #d97a29;
}
.ds.重 {
  border-left: 4px solid #a8842c;
}
.ds-no {
  color: #a0845a;
  font-size: 11.5px;
}
.ds-sign {
  color: var(--ink);
  font-weight: 600;
}
.ds-name {
  color: var(--vermilion);
  font-family: var(--font-kai);
  font-size: 12.5px;
}
.ds-level {
  margin-left: auto;
  font-size: 11px;
  color: #c0392b;
}
.qb {
  margin-bottom: 14px;
}
.qb-t {
  font-family: var(--font-kai);
  font-weight: 700;
  color: var(--vermilion);
  margin-bottom: 4px;
}
</style>
