<script setup lang="ts">
import { ref } from 'vue'
import { drugTips, yaoxingFu } from '../data/drugTips'

const tab = ref('miyan')
</script>

<template>
  <div class="page">
    <div class="h-title" style="font-size: 26px">用药心得</div>
    <p class="vern" style="margin-top: 6px">
      用药秘验杂说——程氏五十年临证经验总结："一字一句皆从五十年中临症经验得来，绝无半点欺人之语。"
    </p>

    <el-tabs v-model="tab" class="no-print">
      <el-tab-pane label="用药秘验杂说" name="miyan" />
      <el-tab-pane label="药性赋幼科摘要（附编）" name="yaoxing" />
    </el-tabs>

    <template v-if="tab === 'miyan'">
      <div v-for="tip in drugTips" :key="tip.title" class="card">
        <div class="h-sub">{{ tip.title }}</div>
        <div v-for="(it, i) in tip.items" :key="i" class="tip-item">
          <div class="original" style="font-size: 13.5px">{{ it.original }}</div>
          <p class="vern" style="font-size: 12.5px">{{ it.plain }}</p>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="card">
        <div class="original" style="font-size: 13.5px">{{ yaoxingFu.intro }}</div>
      </div>
      <div v-for="sec in yaoxingFu.sections" :key="sec.title" class="card">
        <div class="h-sub">{{ sec.title }}</div>
        <div class="original" style="font-size: 13.5px">{{ sec.text }}</div>
        <p v-if="sec.note" class="vern" style="font-size: 12.5px; color: var(--vermilion)">{{ sec.note }}</p>
      </div>
      <div class="card">
        <p class="vern">{{ yaoxingFu.note }}</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.tip-item {
  margin-bottom: 14px;
}
</style>
