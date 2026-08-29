<script setup lang="ts">
import { ref, computed } from 'vue'
import { yianList } from '../data/yian'

const cat = ref('全部')
const kw = ref('')
const openIds = ref<string[]>([])
const cats = ['全部', ...new Set(yianList.map((y) => y.category))]

const filtered = computed(() =>
  yianList.filter(
    (y) =>
      (cat.value === '全部' || y.category === cat.value) &&
      (!kw.value || y.title.includes(kw.value) || y.original.includes(kw.value) || y.plain.includes(kw.value))
  )
)
</script>

<template>
  <div class="page">
    <div class="h-title" style="font-size: 26px">医案库</div>
    <p class="vern" style="margin-top: 6px">
      采自附编《幼科铁镜》效案。夏禹铸曰："两代效集充栋不能尽载，聊取疑难之症约略附之各症之末，
      用以资事斯道者之相较验云。"——共 {{ yianList.length }} 则，皆书姓氏、历验不爽。
    </p>

    <div class="card no-print filters">
      <el-select v-model="cat" style="width: 180px">
        <el-option v-for="c in cats" :key="c" :label="c" :value="c" />
      </el-select>
      <el-input v-model="kw" placeholder="搜索医案（症名、方名、关键词）" clearable style="max-width: 340px" />
    </div>

    <el-collapse v-model="openIds" accordion>
      <el-collapse-item v-for="y in filtered" :key="y.id" :name="y.id">
        <template #title>
          <span class="tag-syndrome">{{ y.category }}</span>
          <b class="yian-title">{{ y.title }}</b>
        </template>
        <div class="original">{{ y.original }}</div>
        <p class="yanyu">——{{ y.yanyu }}</p>
        <p class="vern">【按】{{ y.plain }}</p>
        <div v-if="y.formulas.length" class="fml">
          <span class="fml-label">用方：</span>
          <span v-for="f in y.formulas" :key="f" class="tag-method">{{ f }}</span>
        </div>
      </el-collapse-item>
    </el-collapse>
    <p v-if="!filtered.length" class="vern" style="text-align: center; padding: 30px 0">无匹配医案</p>
  </div>
</template>

<style scoped>
.filters {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.yian-title {
  margin-left: 10px;
  font-family: var(--font-kai);
  font-size: 15.5px;
  color: var(--ink);
}
.yanyu {
  color: var(--vermilion);
  font-family: var(--font-kai);
  font-size: 13px;
  margin: 6px 0;
}
.fml {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}
.fml-label {
  font-size: 12.5px;
  color: var(--ink-soft);
}
</style>
