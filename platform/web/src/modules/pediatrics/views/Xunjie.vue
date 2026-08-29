<script setup lang="ts">
import { ref } from 'vue'
import {
  yanzhengLunzhi,
  chengxianYixun,
  jiuHen,
  shisanBukeXue,
  shiZhuan,
  jingwenYijiao,
  guanmenShazei,
  genghuanYaowei,
  kanbingMijue,
} from '../data/maxims'

const tab = ref('yanzheng')
</script>

<template>
  <div class="page">
    <div class="h-title" style="font-size: 26px">医道训诫</div>

    <el-tabs v-model="tab" class="no-print">
      <el-tab-pane label="言症论治（二十七条）" name="yanzheng" />
      <el-tab-pane label="承先遗训" name="yixun" />
      <el-tab-pane label="九恨 · 十三不可学 · 十传" name="youke" />
      <el-tab-pane label="论说（异教 · 关门杀贼等）" name="lunshuo" />
    </el-tabs>

    <template v-if="tab === 'yanzheng'">
      <div class="card">
        <p class="vern">
          言症论治是补充八症之不足，辨症清楚、主次分明、理法方药有条不紊，最便于学习。
        </p>
        <div v-for="(y, i) in yanzhengLunzhi" :key="i" class="yn">
          <div class="yn-t">{{ String(i + 1).padStart(2, '0') }} · {{ y.t }}</div>
          <div class="original" style="font-size: 13.5px">{{ y.original }}</div>
          <p class="vern" style="font-size: 12.5px">{{ y.plain }}</p>
        </div>
      </div>
    </template>

    <template v-else-if="tab === 'yixun'">
      <div class="card">
        <p class="vern">{{ chengxianYixun.intro }}</p>
        <div v-for="(x, i) in chengxianYixun.items" :key="i" class="yn">
          <div class="yn-t">{{ x.t }}</div>
          <div class="original" style="font-size: 13.5px">{{ x.original }}</div>
        </div>
      </div>
    </template>

    <template v-else-if="tab === 'youke'">
      <div class="card">
        <div class="h-sub">九恨（幼科庸医之恨）</div>
        <p class="vern" style="font-size: 12.5px">{{ jiuHen.intro }}</p>
        <div v-for="h in jiuHen.items" :key="h.t" class="yn">
          <div class="yn-t">{{ h.t }}</div>
          <div class="original" style="font-size: 13px">{{ h.original }}</div>
        </div>
      </div>
      <div class="card">
        <div class="h-sub">十三不可学</div>
        <p class="vern" style="font-size: 12.5px">{{ shisanBukeXue.intro }}</p>
        <ol class="sbsx">
          <li v-for="(s, i) in shisanBukeXue.items" :key="i">{{ s }}</li>
        </ol>
      </div>
      <div class="card">
        <div class="h-sub">十传</div>
        <p class="vern" style="font-size: 12.5px">{{ shiZhuan.intro }}</p>
        <div v-for="(c, i) in shiZhuan.items" :key="i" class="yn">
          <div class="yn-t">{{ c.t }}</div>
          <div class="original" style="font-size: 13.5px">{{ c.original }}</div>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="card">
        <div class="h-sub">摹看手指筋纹乃医家异教说（与程氏诊手纹法并存互参）</div>
        <div class="original" style="font-size: 13.5px">{{ jingwenYijiao.original }}</div>
        <p class="vern" style="font-size: 12.5px">{{ jingwenYijiao.plain }}</p>
      </div>
      <div v-for="g in guanmenShazei" :key="g.title" class="card">
        <div class="h-sub">{{ g.title }}</div>
        <div class="original" style="font-size: 13.5px">{{ g.original }}</div>
      </div>
      <div class="card">
        <div class="h-sub">汤方内更换药味说</div>
        <div class="original" style="font-size: 13.5px">{{ genghuanYaowei.original }}</div>
      </div>
      <div class="card">
        <div class="h-sub">看病秘诀</div>
        <div class="original" style="font-size: 13.5px">{{ kanbingMijue.original }}</div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.yn {
  margin-bottom: 16px;
}
.yn-t {
  font-family: var(--font-kai);
  font-weight: 700;
  color: var(--vermilion);
  margin-bottom: 4px;
}
.sbsx {
  padding-left: 22px;
  line-height: 2.1;
  font-size: 14px;
  color: var(--ink);
}
</style>
