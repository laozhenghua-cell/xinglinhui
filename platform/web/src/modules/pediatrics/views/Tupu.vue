<script setup lang="ts">
import { ref, computed } from 'vue'
import { fingerPatterns, faceRegions, wuzangDingli, wuyunLiuqi } from '../data/fingerPatterns'
import FingerPatternFigure from '../components/figures/FingerPatternFigure.vue'
import ShouwenMaiweiTu from '../components/figures/ShouwenMaiweiTu.vue'
import FaceRegionsTu from '../components/figures/FaceRegionsTu.vue'
import YoukeFigures from '../components/figures/YoukeFigures.vue'

/** 原著原图（从扫描件精确裁取） */
const figs = import.meta.glob('../assets/figures/*.png', { eager: true, import: 'default' }) as Record<string, string>
function fig(name: string): string {
  const hit = Object.keys(figs).find((k) => k.endsWith(`/${name}.png`))
  return hit ? figs[hit] : ''
}

const patternFilter = ref('')
const patternMode = ref<'orig' | 'svg'>('orig')
const filtered = computed(() =>
  fingerPatterns.filter(
    (p) => !patternFilter.value || p.name.includes(patternFilter.value) || p.indication.includes(patternFilter.value)
  )
)

/** 大幅图显示模式：orig=原著原图, svg=SVG 重绘 */
const mwMode = ref<'orig' | 'svg'>('orig')
const faceMode = ref<'orig' | 'svg'>('orig')
const youkeTab = ref('mianxue')
const youkeMode = ref<'orig' | 'svg'>('orig')

const youkeTabs = [
  { key: 'mianxue', label: '面各穴图', img: 'youke-mianxue', svg: 'face' as const },
  { key: 'zhangmian', label: '掌面三关六腑八卦图', img: 'youke-zhangmian', svg: 'palm' as const },
  { key: 'shuidi', label: '掌面水底捞月图', img: 'youke-shuidi', svg: null },
  { key: 'shoubei', label: '手背三关五指节图', img: 'youke-shoubei', svg: 'handback' as const },
  { key: 'zu', label: '足部穴图', img: 'youke-zu', svg: 'foot' as const },
]
const youkeCur = computed(() => youkeTabs.find((t) => t.key === youkeTab.value)!)
</script>

<template>
  <div class="page">
    <div class="h-title" style="font-size: 26px">图谱</div>
    <p class="vern" style="margin-top: 6px">
      以下图像直接取自原著扫描件（逐幅精确裁取、去底色），完整保留原书的图式、标注与笔意；
      另附 SVG 重绘图，可按需切换对照。
    </p>

    <div class="h-sec">一、小儿手纹脉位图</div>
    <div class="card">
      <div class="mode-bar no-print">
        <el-segmented v-model="mwMode" :options="[{ label: '原著原图', value: 'orig' }, { label: 'SVG 重绘', value: 'svg' }]" />
      </div>
      <div v-if="mwMode === 'orig'" class="orig-wrap">
        <el-image :src="fig('shouwen-maiwei')" alt="小儿手纹脉位图（原著）" class="orig-img" :preview-src-list="[fig('shouwen-maiwei')]" preview-teleported fit="contain" />
      </div>
      <ShouwenMaiweiTu v-else />
    </div>

    <div class="h-sec">二、手纹十八图式</div>
    <div class="card">
      <div class="mode-bar no-print">
        <el-segmented v-model="patternMode" :options="[{ label: '原著原图', value: 'orig' }, { label: 'SVG 重绘', value: 'svg' }]" />
        <el-input v-model="patternFilter" placeholder="搜索纹形（如：蛇、珠、丫、水字…）" clearable style="max-width: 300px" class="no-print" />
      </div>
      <div class="grid">
        <div v-for="p in filtered" :key="p.key" class="cell">
          <template v-if="patternMode === 'orig'">
            <el-image :src="fig(p.img ?? '')" :alt="`${p.name}（原著原图，点击放大）`" class="orig-img pattern-img" :preview-src-list="[fig(p.img ?? '')]" preview-teleported fit="contain" lazy />
          </template>
          <FingerPatternFigure v-else :pattern="p" :size="112" />
          <div class="cell-meta">
            <span class="cell-name">{{ p.name }}</span>
            <span class="cell-ind">{{ p.indication }}</span>
          </div>
        </div>
      </div>
      <p class="vern" style="margin-top: 12px">
        原著按语："以上手纹，不是有此症必有此纹，是间或有之，恐医看不真生疑难决，故绘之以备识别决症。"
      </p>
    </div>

    <div class="h-sec">三、小儿面部属位图</div>
    <div class="card">
      <div class="mode-bar no-print">
        <el-segmented v-model="faceMode" :options="[{ label: '原著原图', value: 'orig' }, { label: 'SVG 重绘', value: 'svg' }]" />
      </div>
      <div v-if="faceMode === 'orig'" class="orig-wrap">
        <el-image :src="fig('mianbu-shuwei')" alt="小儿面部属位图（原著）" class="orig-img" :preview-src-list="[fig('mianbu-shuwei')]" preview-teleported fit="contain" />
      </div>
      <template v-else>
        <FaceRegionsTu />
        <div class="original">{{ faceRegions.original }}</div>
        <div class="h-sub">望形色审苗窍（节录《幼科铁镜》）</div>
        <ul class="mq">
          <li v-for="m in faceRegions.miaoqiao" :key="m">{{ m }}</li>
        </ul>
        <p class="vern">{{ faceRegions.note }}</p>
      </template>
    </div>

    <div class="h-sec">四、五脏主病定例</div>
    <el-row :gutter="14">
      <el-col v-for="w in wuzangDingli" :key="w.organ" :xs="24" :sm="12" :md="8">
        <div class="card wz">
          <div class="wz-organ">{{ w.organ }}</div>
          <div class="wz-gov">{{ w.governs }}</div>
          <div class="wz-signs">{{ w.signs }}</div>
        </div>
      </el-col>
    </el-row>

    <div class="h-sec">五、司天在泉与脏腑干支</div>
    <div class="card">
      <div class="h-sub">司天歌</div>
      <div class="original" style="text-align: center">{{ wuyunLiuqi.siga.text }}</div>
      <p class="vern">{{ wuyunLiuqi.siga.note }}</p>
      <div class="h-sub">天干合脏腑相属歌</div>
      <div class="original" style="text-align: center">{{ wuyunLiuqi.tiangan }}</div>
      <div class="h-sub">三阴三阳分配脏腑歌</div>
      <div class="original" style="text-align: center">{{ wuyunLiuqi.sanyin }}</div>
      <div class="h-sub">脏腑表里</div>
      <div class="original">{{ wuyunLiuqi.biaoli }}</div>
    </div>

    <div class="h-sec">六、附编《幼科铁镜》诸图</div>
    <div class="card">
      <div class="mode-bar no-print">
        <el-tabs v-model="youkeTab">
          <el-tab-pane v-for="t in youkeTabs" :key="t.key" :label="t.label" :name="t.key" />
        </el-tabs>
        <el-segmented
          v-model="youkeMode"
          :options="[{ label: '原著原图', value: 'orig' }, { label: 'SVG 重绘', value: 'svg' }]"
          :disabled="!youkeCur.svg"
        />
      </div>
      <div v-if="youkeMode === 'orig' || !youkeCur.svg" class="orig-wrap">
        <el-image :src="fig(youkeCur.img)" :alt="`${youkeCur.label}（原著）`" class="orig-img" :preview-src-list="[fig(youkeCur.img)]" preview-teleported fit="contain" />
      </div>
      <YoukeFigures v-else :fig="youkeCur.svg" />
    </div>
  </div>
</template>

<style scoped>
.mode-bar {
  display: flex;
  gap: 14px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 14px;
}
@media (max-width: 768px) { .mode-bar :deep(.el-tabs) { min-width: 0; } }
.mode-bar :deep(.el-tabs) {
  flex: 1;
  min-width: 320px;
}
.mode-bar :deep(.el-tabs__header) {
  margin: 0;
}
.orig-wrap {
  display: flex;
  justify-content: center;
  padding: 10px 0;
}
.orig-img {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  cursor: zoom-in;
}
.pattern-img {
  max-height: 300px;
  width: auto;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 18px;
}
.cell {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  box-shadow: var(--shadow);
}
.cell-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-align: center;
}
.cell-name {
  font-family: var(--font-kai);
  font-weight: 700;
  color: var(--vermilion);
  font-size: 15px;
}
.cell-ind {
  color: var(--ink-soft);
  font-size: 12.5px;
  line-height: 1.6;
}
.mq {
  padding-left: 20px;
  font-size: 13.5px;
  color: var(--ink);
  line-height: 1.9;
}
.wz {
  min-height: 170px;
}
.wz-organ {
  font-family: var(--font-kai);
  font-size: 22px;
  font-weight: 700;
  color: var(--vermilion);
}
.wz-gov {
  font-size: 13px;
  color: var(--jade);
  font-family: var(--font-kai);
  margin: 2px 0 6px;
}
.wz-signs {
  font-size: 12.5px;
  color: var(--ink-soft);
  line-height: 1.75;
}
</style>
