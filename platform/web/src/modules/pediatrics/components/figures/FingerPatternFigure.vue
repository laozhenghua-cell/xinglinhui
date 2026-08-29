<script setup lang="ts">
import type { FingerPattern } from '../../data/types'

const props = defineProps<{ pattern: FingerPattern; size?: number }>()

/**
 * 食指轮廓与三关坐标：viewBox 0 0 120 340；指尖在上。
 * 三关分界：命关 y 18~118，气关 y 118~218，风关 y 218~322。
 * 原著为墨线简笔，本图以朱砂色示"血络"，形样依原著图式与《证治准绳》互参。
 */
const FINGER =
  'M60,20 C50,20 45,27 45,36 L45,58 C40,62 37,68 37,75 L37,102 C41,104 45,104 45,104 L45,152 C40,154 37,160 37,167 L37,194 C41,196 45,196 45,196 L45,244 C40,246 37,252 37,259 L37,286 C41,288 45,288 45,288 L45,306 C45,320 54,329 60,329 C66,329 75,320 75,306 L75,288 C79,288 83,288 83,286 L83,259 C83,252 80,246 75,244 L75,196 C79,196 83,196 83,194 L83,167 C83,160 80,154 75,152 L75,104 C79,104 83,104 83,102 L83,75 C83,68 80,62 75,58 L75,36 C75,27 70,20 60,20 Z'

function patternPath(kind: string): string {
  switch (kind) {
    // 流珠：只一点红于风关
    case 'dot':
      return 'M56,262 m-9,0 a9,9 0 1,1 18,0 a9,9 0 1,1 -18,0'
    // 环珠：点差大，中空如环
    case 'ring':
      return 'M56,262 m-14,0 a14,14 0 1,1 28,0 a14,14 0 1,1 -28,0 M56,262 m-5.5,0 a5.5,5.5 0 1,1 11,0 a5.5,5.5 0 1,1 -11,0'
    // 长珠：圆而长
    case 'longdot':
      return 'M56,244 C50,244 47,254 47,262 C47,272 50,282 56,282 C62,282 65,272 65,262 C65,254 62,244 56,244 Z'
    // 来蛇：长散出气关，一头大、一头尖
    case 'laishe':
      return 'M60,318 C63,306 62,296 58,288 C54,280 50,272 49,262 C47,248 50,236 56,226 C61,218 64,210 63,201 M63,201 m-0,0 C53,197 47,201 46,208 C45,217 51,222 63,223 C73,224 80,218 80,209 C80,202 73,197 63,197'
    // 去蛇：大头向气关，尾细
    case 'qushe':
      return 'M62,318 C66,308 66,296 62,286 C58,276 55,266 55,254 C55,242 58,234 63,228 M55,254 m-0,0 C43,254 38,259 38,268 C38,278 45,282 55,282 C63,282 68,278 68,269 C68,260 63,255 55,255'
    // 弓反里（弓背向拇指侧）
    case 'bow-in':
      return 'M41,296 C33,280 39,262 41,244 C42,226 37,210 41,192'
    // 弓反外（弓背向小指侧）
    case 'bow-out':
      return 'M79,296 C87,280 81,262 79,244 C78,226 83,210 79,192'
    // 枪形：直上
    case 'qiang':
      return 'M60,312 C60,300 60,288 60,276 C60,248 60,220 60,192 M60,312 L56,302 M60,312 L64,302'
    // 鱼骨形：纹分支歧
    case 'yugu':
      return 'M60,314 L60,202 M60,300 L51,290 M60,282 L51,272 M60,264 L51,254 M60,246 L51,236 M60,228 L51,218 M60,210 L51,202 M60,300 L69,290 M60,282 L69,272 M60,264 L69,254 M60,246 L69,236 M60,228 L69,218 M60,210 L69,202'
    // 水字形：三脉并行如波
    case 'shuizi':
      return 'M51,314 C48,304 53,296 51,288 C49,280 53,270 51,262 C49,252 53,242 51,234 C49,224 53,214 51,204 C50,196 52,190 51,184 M60,314 C57,304 62,296 60,288 C58,280 62,270 60,262 C58,252 62,242 60,234 C58,224 62,214 60,204 C59,196 61,190 60,184 M69,314 C66,304 71,296 69,288 C67,280 71,270 69,262 C67,252 71,242 69,234 C67,224 71,214 69,204 C68,196 70,190 69,184'
    // 针形（长针）：细长透命关
    case 'zhen':
      return 'M60,318 L60,128 M60,128 L56,146 M60,128 L64,146 M60,318 L57,306 M60,318 L63,306'
    // 透关射指：命脉向里（拇指侧）
    case 'shezhi':
      return 'M60,318 L60,240 M60,240 C59,214 55,188 48,160 C45,148 43,134 42,118'
    // 透关射甲：命脉向外（指甲侧）
    case 'shejia':
      return 'M60,318 L60,240 M60,240 C61,214 65,188 72,160 C75,148 77,134 78,118'
    // 人字纹（开长丫）
    case 'renzi':
      return 'M60,316 C60,300 60,284 60,270 C60,258 58,248 53,238 C49,230 47,222 47,214 M60,270 C60,258 62,248 67,238 C71,230 73,222 73,214 M47,214 L47,206 M73,214 L73,206'
    // 短丫纹
    case 'duanya':
      return 'M60,312 C60,302 60,292 60,282 M60,282 L52,272 M60,282 L68,272'
    // 乱纹：参差离乱
    case 'luan':
      return 'M50,308 C54,298 47,290 53,282 C59,274 49,266 54,258 C58,250 52,242 56,234 C60,226 53,218 57,210 M67,306 C62,296 70,288 65,280 C61,272 69,264 64,256 C60,248 68,240 63,232 C59,224 66,216 62,208 M58,204 C62,198 55,194 59,190 C63,186 57,182 60,178'
    // 大小字形：乙字一大一小
    case 'daxiaoz':
      return 'M56,314 C52,306 61,298 56,291 C51,284 60,276 55,269 C51,263 58,256 55,249 C52,243 58,238 56,232 M67,306 C64,300 70,294 66,289 C62,284 69,278 65,273 C61,268 68,263 65,258 C63,253 68,250 66,246'
    // 连珠形：如珠相贯
    case 'lianzhu':
      return 'M60,306 L60,196 M60,300 m-8,0 a8,8 0 1,1 16,0 a8,8 0 1,1 -16,0 M60,272 m-8,0 a8,8 0 1,1 16,0 a8,8 0 1,1 -16,0 M60,244 m-8,0 a8,8 0 1,1 16,0 a8,8 0 1,1 -16,0 M60,216 m-8,0 a8,8 0 1,1 16,0 a8,8 0 1,1 -16,0'
    default:
      return ''
  }
}

const FILLED = new Set(['dot', 'longdot', 'laishe', 'qushe', 'lianzhu'])
const path = patternPath(props.pattern.kind)
</script>

<template>
  <figure class="fp" :title="`${pattern.name}：${pattern.shape}`">
    <svg :width="size ?? 132" :height="(size ?? 132) * 340 / 120" viewBox="0 0 120 340" role="img" :aria-label="pattern.name">
      <defs>
        <linearGradient id="fpSkin" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#fbf1dd" />
          <stop offset="0.5" stop-color="#fdf6e6" />
          <stop offset="1" stop-color="#f3e6cb" />
        </linearGradient>
      </defs>
      <!-- 指甲（甲板+月牙） -->
      <path d="M51,25 C51,17 69,17 69,25 L69,33 C69,38 51,38 51,33 Z" fill="#f6ead3" stroke="#8a7c5f" stroke-width="1.6" />
      <path d="M55,32 C57,30 63,30 65,32 C64,36 56,36 55,32 Z" fill="#fdf6e6" opacity="0.9" />
      <!-- 食指轮廓 -->
      <path :d="FINGER" fill="url(#fpSkin)" stroke="#7d6f52" stroke-width="1.8" stroke-linejoin="round" />
      <!-- 指节横纹 -->
      <path d="M45,118 C49,120 55,122 62,122 C68,122 72,121 75,120" fill="none" stroke="#c9b98f" stroke-width="1.3" />
      <path d="M45,217 C49,219 55,221 62,221 C68,221 72,220 75,219" fill="none" stroke="#c9b98f" stroke-width="1.3" />
      <!-- 三关分隔与标注 -->
      <line x1="86" y1="118" x2="92" y2="118" stroke="#c9b98f" stroke-width="1" />
      <line x1="86" y1="218" x2="92" y2="218" stroke="#c9b98f" stroke-width="1" />
      <g font-family="Kaiti SC, STKaiti, serif" font-size="11.5" fill="#8a4a2a">
        <text x="95" y="72">命关</text>
        <text x="95" y="170">气关</text>
        <text x="95" y="271">风关</text>
      </g>
      <!-- 纹形（朱砂） -->
      <path :d="path" fill="none" stroke="#b03a2e" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" />
      <path v-if="FILLED.has(pattern.kind)" :d="path" fill="#b03a2e" fill-rule="evenodd" opacity="0.92" />
      <!-- 高光 -->
      <path :d="path" fill="none" stroke="#d97a5a" stroke-width="0.8" stroke-linecap="round" opacity="0.45" />
    </svg>
    <figcaption class="fp-cap">
      <span class="fp-name">{{ pattern.name }}</span>
      <span class="fp-ind">{{ pattern.indication }}</span>
    </figcaption>
  </figure>
</template>

<style scoped>
.fp {
  margin: 0;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.fp svg {
  filter: drop-shadow(0 1px 2px rgba(43, 35, 24, 0.12));
}
.fp-cap {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12.5px;
}
.fp-name {
  font-family: var(--font-kai);
  font-weight: 700;
  color: var(--vermilion);
  font-size: 15px;
}
.fp-ind {
  color: var(--ink-soft);
  max-width: 200px;
  line-height: 1.6;
}
</style>
