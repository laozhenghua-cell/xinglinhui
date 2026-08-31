<script setup lang="ts">
import { ref } from 'vue'
import { guanfangYanfang, sanzhengFang, wansanList, waizhiFa } from '../data/formulas'
import { syndromes } from '../data/syndromes'

const tab = ref('bafang')

</script>

<template>
  <div class="page">
    <div class="h-title" style="font-size: 26px">方剂库</div>
    <p class="vern" style="margin-top: 6px">
      八方为"方底"，药味未齐，必有照条下加法加入方底内然后药性始齐；
      官方验方"或参入自己方中、或加一二味均可，灵便在人不拘执"。
    </p>

    <el-tabs v-model="tab" class="no-print">
      <el-tab-pane label="八症方底" name="bafang" />
      <el-tab-pane label="官方常用验方" name="guanfang" />
      <el-tab-pane label="三症诸方（疟·暑·痢）" name="sanzheng" />
      <el-tab-pane label="丸散一览" name="wansan" />
      <el-tab-pane label="外治法" name="waizhi" />
    </el-tabs>

    <!-- 八症方底 -->
    <template v-if="tab === 'bafang'">
      <div v-for="s in syndromes" :key="s.id" class="card">
        <div class="f-head">
          <span class="tag-syndrome">{{ s.name }}</span>
          <b class="f-name">{{ s.fangyao.name }}</b>
          <span class="f-usage">{{ s.fangyao.usage }}</span>
        </div>
        <el-table :data="s.fangyao.herbs" size="small" border>
          <el-table-column prop="name" label="药味" width="110" />
          <el-table-column prop="dose" label="剂量" width="90" />
          <el-table-column prop="note" label="原著注" />
        </el-table>
        <p v-if="s.fangyao.source" class="vern" style="font-size: 12px">出处：{{ s.fangyao.source }}</p>
      </div>
    </template>

    <!-- 官方验方 -->
    <template v-else-if="tab === 'guanfang'">
      <div v-for="f in guanfangYanfang" :key="f.name" class="card">
        <div class="f-head">
          <b class="f-name">{{ f.name }}</b>
          <span v-if="f.alt" class="vern" style="font-size: 12px">{{ f.alt }}</span>
        </div>
        <p class="f-gong">{{ f.gongyong }}</p>
        <p class="f-usage">{{ f.usage }}</p>
        <el-table v-if="f.herbs.length" :data="f.herbs" size="small" border>
          <el-table-column prop="name" label="药味" width="130" />
          <el-table-column prop="dose" label="剂量" width="110" />
          <el-table-column prop="note" label="原著注" />
        </el-table>
        <template v-if="f.jiawei">
          <div class="h-sub">加味法</div>
          <el-table :data="f.jiawei" size="small" border>
            <el-table-column prop="cond" label="情形" width="200" />
            <el-table-column prop="add" label="加味" />
          </el-table>
        </template>
      </div>
    </template>

    <!-- 三症诸方 -->
    <template v-else-if="tab === 'sanzheng'">
      <div v-for="f in sanzhengFang" :key="f.name" class="card">
        <div class="f-head">
          <span class="tag-syndrome">{{ f.category }}</span>
          <b class="f-name">{{ f.name }}</b>
        </div>
        <p class="f-gong">{{ f.gongyong }}</p>
        <p class="f-usage">{{ f.usage }}</p>
        <el-table v-if="f.herbs.length" :data="f.herbs" size="small" border>
          <el-table-column prop="name" label="药味" width="130" />
          <el-table-column prop="dose" label="剂量" width="110" />
          <el-table-column prop="note" label="原著注" />
        </el-table>
        <template v-if="f.jiawei">
          <div class="h-sub">加减法</div>
          <el-table :data="f.jiawei" size="small" border>
            <el-table-column prop="cond" label="情形" width="220" />
            <el-table-column prop="add" label="加味" />
          </el-table>
        </template>
      </div>
    </template>

    <!-- 丸散 -->
    <template v-else-if="tab === 'wansan'">
      <div class="card">
        <el-table :data="wansanList" border size="default">
          <el-table-column prop="name" label="丸散名" width="160" />
          <el-table-column prop="usage" label="原著用法" />
          <el-table-column prop="note" label="功效" width="220" />
        </el-table>
        <p class="vern" style="margin-top: 10px">
          原著凡例："如惊风散、万灵丹等所载各方原附卷末，惜剥蚀不可复辨，俟当查酌补入使称完璧。"
        </p>
      </div>
    </template>

    <!-- 外治法 -->
    <template v-else>
      <div v-for="w in waizhiFa" :key="w.name" class="card">
        <div class="h-sub">{{ w.name }}</div>
        <div class="original">{{ w.method }}</div>
        <p class="vern">{{ w.note }}</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.f-head {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.f-name {
  font-family: var(--font-kai);
  font-size: 17.5px;
  color: var(--ink);
}
.f-usage {
  color: var(--vermilion);
  font-size: 12.5px;
}
.f-gong {
  color: var(--jade);
  font-size: 13.5px;
  line-height: 1.8;
}
</style>
