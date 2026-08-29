<script setup lang="ts">
import { liuziShuo, songs, bazhengZonglun } from '../data/syndromes'
import { shouwenFa, qiemaiFa, kanwaizhengFa, wenzhenFa, shouwenMaiwei } from '../data/fingerPatterns'
import ShouwenMaiweiTu from '../components/figures/ShouwenMaiweiTu.vue'
</script>

<template>
  <div class="page">
    <div class="h-title" style="font-size: 26px">上编 · 总论</div>

    <!-- 释八症六字说 -->
    <div class="h-sec">释八症六字说</div>
    <div class="card">
      <div class="original">{{ liuziShuo.original }}</div>
      <p class="vern">{{ liuziShuo.plain }}</p>
    </div>
    <el-row :gutter="14">
      <el-col v-for="p in liuziShuo.per" :key="p.s" :xs="24" :sm="12" :md="6">
        <div class="card liuzi-card">
          <div class="lz-s">{{ p.s }}</div>
          <div class="lz-m"><span v-for="m in p.methods" :key="m" class="tag-method">{{ m }}</span></div>
          <div class="lz-t">{{ p.original }}</div>
        </div>
      </el-col>
    </el-row>
    <div class="card">
      <div class="original">{{ liuziShuo.closing }}</div>
    </div>

    <!-- 小儿手纹脉位图 -->
    <div class="h-sec">小儿手纹脉位图</div>
    <div class="card">
      <div class="original">{{ shouwenMaiwei.original }}</div>
      <ShouwenMaiweiTu />
    </div>

    <!-- 三首歌诀 -->
    <div class="h-sec">歌诀三首</div>
    <el-row :gutter="14">
      <el-col v-for="s in songs" :key="s.title" :xs="24" :md="8">
        <div class="card song-card">
          <div class="song-title">{{ s.title }}</div>
          <div class="original" style="text-align: center; font-size: 15px">{{ s.text }}</div>
          <p class="vern">{{ s.note }}</p>
        </div>
      </el-col>
    </el-row>

    <!-- 诊法四篇 -->
    <div class="h-sec">诊法四篇</div>
    <div class="card">
      <div class="h-sub">诊手纹法</div>
      <div class="original">{{ shouwenFa.original }}</div>
      <p class="vern">{{ shouwenFa.plain }}</p>
      <div class="original" style="font-size: 13px">{{ shouwenFa.combined }}</div>
      <p class="vern" style="font-size: 12.5px">{{ shouwenFa.note }}</p>
    </div>
    <div class="card">
      <div class="h-sub">切脉法</div>
      <div class="original">{{ qiemaiFa.original }}</div>
      <p class="vern">{{ qiemaiFa.plain }}</p>
    </div>
    <div class="card">
      <div class="h-sub">看外症法</div>
      <div class="original">{{ kanwaizhengFa.original }}</div>
      <p class="vern">{{ kanwaizhengFa.plain }}</p>
    </div>
    <div class="card">
      <div class="h-sub">问诊法</div>
      <div class="original">{{ wenzhenFa.original }}</div>
      <p class="vern">{{ wenzhenFa.plain }}</p>
    </div>

    <!-- 八症总论 -->
    <div class="h-sec">八症总论</div>
    <div class="card">
      <div class="original">{{ bazhengZonglun.original }}</div>
      <p class="vern">{{ bazhengZonglun.plain }}</p>
      <div v-for="r in bazhengZonglun.rules" :key="r.t">
        <div class="h-sub">{{ r.t }}</div>
        <div class="original" style="font-size: 13.5px">{{ r.original }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.liuzi-card {
  min-height: 208px;
}
.lz-s {
  font-family: var(--font-kai);
  font-size: 19px;
  font-weight: 700;
  color: var(--vermilion);
}
.lz-m {
  margin: 8px 0;
}
.lz-t {
  font-size: 12.5px;
  color: var(--ink-soft);
  line-height: 1.75;
}
.song-card {
  min-height: 190px;
}
.song-title {
  font-family: var(--font-kai);
  font-weight: 700;
  font-size: 16px;
  color: var(--jade);
  margin-bottom: 8px;
}
</style>
