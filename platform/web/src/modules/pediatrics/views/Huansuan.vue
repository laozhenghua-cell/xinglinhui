<script setup lang="ts">
import { ref } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { syndromes } from '../data/syndromes'

/**
 * 古方剂量换算 — 依明清衡制（库平制）：
 * 1 斤 = 16 两 = 596.8g；1 两 = 10 钱 = 37.3g；1 钱 = 10 分 = 3.73g；1 分 = 0.373g。
 * 计件单位（只、枚、丸、片、条、节、撮）不做换算，仅提示。
 */
const G = { liang: 37.3, qian: 3.73, fen: 0.373 }

interface ConvRow {
  name: string
  input: string
  grams: number | null
  note: string
}

const input = ref('')
const rows = ref<ConvRow[]>([])

function parseOne(s: string): { n: number; unit: string } | null {
  const t = s.replace(/\s+/g, '').replace(/（[^）]*）/g, '').replace(/\([^)]*\)/g, '')
  const m = t.match(/^([零一二两三四五六七八九十百半]+)?(两|钱|分)(半)?$/)
  if (!m) return null
  const numStr = m[1] || '一'
  const digits: Record<string, number> = { 零: 0, 一: 1, 二: 2, 两: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9, 十: 10, 百: 100 }
  let n = 0
  if (/^[0-9.]+$/.test(numStr)) {
    n = parseFloat(numStr)
  } else if (numStr === '半') {
    n = 0.5
  } else {
    let cur = 0
    let total = 0
    for (const ch of numStr) {
      if (ch === '十') {
        cur = cur === 0 ? 10 : cur * 10
      } else if (ch === '百') {
        cur = cur === 0 ? 100 : cur * 100
      } else {
        total += cur
        cur = digits[ch] ?? 0
      }
    }
    n = total + cur
  }
  if (m[3]) n += 0.5
  return { n, unit: m[2] }
}

function conv(s: string): { grams: number | null; note: string } {
  if (!s) return { grams: null, note: '' }
  const p = parseOne(s)
  if (!p) {
    if (/只|枚|丸|片|条|节|撮|个/.test(s)) return { grams: null, note: '计件单位，不作换算' }
    return { grams: null, note: '未能识别（示例：二钱、钱半、七分、一两）' }
  }
  const uk = ({ 两: 'liang', 钱: 'qian', 分: 'fen' } as Record<string, keyof typeof G>)[p.unit]
  const per = G[uk]
  const g = p.n * per
  return {
    grams: Math.round((g + Number.EPSILON) * 100) / 100,
    note: `1${p.unit}≈${per}g`,
  }
}

function convert() {
  const lines = input.value.split(/[\n,，、;；]+/).map((s) => s.trim()).filter(Boolean)
  rows.value = lines.map((l) => {
    const m = l.match(/^(.{0,8}?)[：:]?\s*([零一二两三四五六七八九十百半0-9.]+(?:两|钱|分)半?|\S+)$/)
    const name = m ? m[1].trim() : ''
    const dose = m ? m[2].trim() : l
    const r = conv(dose)
    return { name: name || '（未命名）', input: l, grams: r.grams, note: r.note }
  })
}

function loadFang(idx: number) {
  const s = syndromes[idx]
  input.value = s.fangyao.herbs.map((h) => `${h.name} ${h.dose}`).join('，')
  convert()
}
</script>

<template>
  <div class="page">
    <div class="h-title" style="font-size: 26px">古方剂量换算</div>
    <p class="vern" style="margin-top: 6px">
      明清衡制（库平制）：1 两 ≈ 37.3g，1 钱 ≈ 3.73g，1 分 ≈ 0.373g。
      计件单位（只、枚、丸、片）不作换算。
    </p>

    <div class="card">
      <div class="h-sub">输入（每行一味，可带药名；也支持"钱半""二钱七分"式写法）</div>
      <el-input v-model="input" type="textarea" :rows="5" placeholder="如：&#10;羌活 一钱&#10;防风 一钱&#10;薄荷 七分&#10;蝉蜕 十只" class="no-print" />
      <div class="no-print" style="margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap">
        <el-button type="primary" @click="convert">换算</el-button>
        <el-dropdown @command="(i: number) => loadFang(i)">
          <el-button>载入八症方底<el-icon style="margin-left: 4px"><ArrowDown /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-for="(s, i) in syndromes" :key="s.id" :command="i">{{ s.name }}（{{ s.fangyao.name }}）</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <el-table v-if="rows.length" :data="rows" border size="small" style="margin-top: 14px">
        <el-table-column prop="name" label="药味" width="140" />
        <el-table-column prop="input" label="原著剂量" width="180" />
        <el-table-column label="折算（克）" width="140">
          <template #default="{ row }">
            <b v-if="row.grams !== null" style="color: var(--vermilion)">{{ row.grams }} g</b>
            <span v-else style="color: #a0845a">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="note" label="说明" />
      </el-table>
    </div>

    <div class="warn-banner">
      <b>使用注意：</b>古今度量衡、药材炮制与药材质量差异较大，且小儿用药宜从轻剂起步（程氏剂量多为三五岁儿量），
      本换算仅供理解原方比例与教学参考，临床用量须由执业医师按现行药典与患儿年龄体重酌定；
      禁限药材（如犀角）按现行法规执行。
    </div>
  </div>
</template>
