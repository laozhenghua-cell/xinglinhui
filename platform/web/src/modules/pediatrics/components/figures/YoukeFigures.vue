<script setup lang="ts">
/** 附编《幼科铁镜》诸图 — 面各穴图 / 掌面三关六腑八卦图 / 手背三关五指节图 / 足图 */
import { ref } from 'vue'

const props = defineProps<{ fig: 'face' | 'palm' | 'handback' | 'foot' }>()

const tabs = [
  { key: 'face', label: '面各穴图' },
  { key: 'palm', label: '掌面三关六腑八卦图' },
  { key: 'handback', label: '手背三关五指节图' },
  { key: 'foot', label: '足部穴图' },
] as const
const current = ref(props.fig)
</script>

<template>
  <div class="yk">
    <el-segmented v-model="current" :options="tabs.map((t) => ({ label: t.label, value: t.key }))" class="no-print" />

    <!-- ===== 面各穴图 ===== -->
    <div v-if="current === 'face'" class="fig-box">
      <svg viewBox="0 0 360 470" class="yk-svg">
        <!-- 面廓 -->
        <path d="M180,96 C140,96 112,116 104,150 C98,180 96,210 100,240 C106,278 118,312 134,340 C146,362 152,384 153,406 C154,418 162,424 170,422 L176,420 C179,412 182,404 185,396 C188,404 191,412 194,420 L200,422 C208,424 216,418 217,406 C218,384 224,362 236,340 C252,312 264,278 270,240 C274,210 272,180 266,150 C258,116 230,96 180,96 Z" fill="#fdf6e6" stroke="#7d6f52" stroke-width="2" />
        <!-- 发际 -->
        <path d="M126,122 C144,98 166,88 180,88 C194,88 216,98 234,122" fill="none" stroke="#2b2318" stroke-width="2" stroke-linecap="round" />
        <!-- 眉 -->
        <path d="M126,196 Q146,188 164,194" fill="none" stroke="#5a4f3e" stroke-width="2.8" stroke-linecap="round" />
        <path d="M196,194 Q214,188 234,196" fill="none" stroke="#5a4f3e" stroke-width="2.8" stroke-linecap="round" />
        <!-- 眼 -->
        <path d="M122,222 Q136,212 150,222 Q136,234 122,222 Z" fill="#fff" stroke="#5a4f3e" stroke-width="1.6" />
        <circle cx="136" cy="223" r="4.2" fill="#2b2318" />
        <path d="M210,222 Q224,212 238,222 Q224,234 210,222 Z" fill="#fff" stroke="#5a4f3e" stroke-width="1.6" />
        <circle cx="224" cy="223" r="4.2" fill="#2b2318" />
        <!-- 鼻口 -->
        <path d="M180,198 L180,236 C179,248 175,254 171,258 C176,261 180,264 180,268 L180,278 C180,284 174,290 166,292 C158,294 152,290 150,284 L150,278 C150,272 155,268 162,268 C170,268 175,264 175,258 C175,250 177,242 180,236" fill="none" stroke="#7d6f52" stroke-width="1.8" />
        <path d="M180,282 L180,300" fill="none" stroke="#b08a6a" stroke-width="1.4" />
        <path d="M160,308 Q180,320 200,308" fill="none" stroke="#c96a52" stroke-width="2.4" stroke-linecap="round" />
        <circle cx="180" cy="332" r="2.4" fill="#b08a6a" />
        <!-- 耳 -->
        <path d="M78,224 C66,220 60,228 62,240 C64,256 64,272 68,284 C74,294 88,289 88,276 L88,262 C84,250 82,236 82,226 Z" fill="#fdf6e6" stroke="#7d6f52" stroke-width="1.8" />
        <path d="M282,224 C294,220 300,228 298,240 C296,256 296,272 292,284 C286,294 272,289 272,276 L272,262 C276,250 278,236 278,226 Z" fill="#fdf6e6" stroke="#7d6f52" stroke-width="1.8" />

        <!-- 穴位点（朱砂） -->
        <g fill="#b03a2e">
          <circle cx="180" cy="112" r="4.2" />
          <circle cx="180" cy="168" r="4.2" />
          <circle cx="180" cy="206" r="4.2" />
          <circle cx="180" cy="250" r="4.2" />
          <circle cx="180" cy="274" r="4.2" />
          <circle cx="180" cy="314" r="4.2" />
          <circle cx="180" cy="348" r="4.2" />
          <circle cx="100" cy="212" r="4.2" />
          <circle cx="260" cy="212" r="4.2" />
          <circle cx="76" cy="292" r="3.4" />
          <circle cx="284" cy="292" r="3.4" />
        </g>
        <g font-family="Kaiti SC, STKaiti, serif" font-size="13" fill="#2b2318" font-weight="bold">
          <text x="197" y="117">天庭</text>
          <text x="197" y="173">眉心</text>
          <text x="197" y="211">山根</text>
          <text x="197" y="255">年寿</text>
          <text x="197" y="279">准头</text>
          <text x="197" y="319">人中</text>
          <text x="197" y="353">承浆</text>
          <text x="66" y="200">太阳</text>
          <text x="238" y="200">太阴</text>
        </g>

        <!-- 推法示意（虚线箭头） -->
        <g stroke="#c96a52" stroke-width="1.6" fill="none" stroke-dasharray="5 4">
          <path d="M180,164 L180,120" />
          <path d="M180,170 L104,208" />
          <path d="M180,170 L256,208" />
        </g>
        <g fill="#c96a52">
          <path d="M180,116 L175,126 L185,126 Z" />
          <path d="M107,205 L115,211 L109,216 Z" />
          <path d="M253,205 L251,216 L245,211 Z" />
        </g>
        <text x="180" y="420" text-anchor="middle" font-size="12.5" fill="#5a4f3e">开首推法：眉心推额上二十四数；眉心分推太阳太阴九数；</text>
        <text x="180" y="440" text-anchor="middle" font-size="12.5" fill="#5a4f3e">天庭至承浆逐穴一点以代针；太阳太阴可发汗、可止汗。</text>
      </svg>
    </div>

    <!-- ===== 掌面三关六腑八卦图 ===== -->
    <div v-else-if="current === 'palm'" class="fig-box">
      <svg viewBox="0 0 360 470" class="yk-svg">
        <g transform="translate(58,36)">
          <!-- 手指 -->
          <rect x="18" y="8" width="26" height="82" rx="12" fill="#fdf6e6" stroke="#7d6f52" stroke-width="1.8" />
          <rect x="58" y="-2" width="28" height="92" rx="13" fill="#fdf6e6" stroke="#7d6f52" stroke-width="1.8" />
          <rect x="102" y="2" width="28" height="88" rx="13" fill="#fdf6e6" stroke="#7d6f52" stroke-width="1.8" />
          <rect x="146" y="12" width="27" height="78" rx="12" fill="#fdf6e6" stroke="#7d6f52" stroke-width="1.8" />
          <!-- 拇指（脾土） -->
          <path d="M204,92 C232,98 244,118 240,142 C236,158 222,162 210,152 L204,122 Z" fill="#fdf6e6" stroke="#7d6f52" stroke-width="1.8" />
          <!-- 掌 -->
          <path d="M18,92 L212,92 C224,92 230,100 230,112 L230,222 C230,246 212,260 188,260 L42,260 C18,260 6,246 6,222 L6,112 C6,100 12,92 18,92 Z" fill="#fdf6e6" stroke="#7d6f52" stroke-width="2" />
          <!-- 腕 -->
          <rect x="42" y="260" width="152" height="34" rx="8" fill="#f7f1e3" stroke="#7d6f52" stroke-width="1.6" />
          <path d="M60,262 L60,292 M88,262 L88,292 M116,262 L116,292 M144,262 L144,292 M172,262 L172,292" stroke="#c9b98f" stroke-width="1" />

          <!-- 八卦环 -->
          <circle cx="118" cy="176" r="66" fill="none" stroke="#c9a227" stroke-width="1.4" stroke-dasharray="3 3" />

          <!-- 卦名 -->
          <g font-size="12" fill="#4a7a5f" font-family="Kaiti SC, STKaiti, serif" font-weight="bold" text-anchor="middle">
            <text x="118" y="102">离（南）</text>
            <text x="118" y="252">坎（北）</text>
            <text x="192" y="180">震（东）</text>
            <text x="42" y="180">兑（西）</text>
            <text x="168" y="122">巽（东南）</text>
            <text x="66" y="122">坤（西南）</text>
            <text x="168" y="232">艮（东北）</text>
            <text x="66" y="232">乾（西北）</text>
          </g>

          <!-- 卦符（三爻，自上而下） -->
          <g stroke="#4a7a5f" stroke-width="2.4" stroke-linecap="round">
            <!-- 离 ☲ 上实中虚下实 -->
            <g transform="translate(109,94)"><line x1="0" y1="0" x2="18" y2="0" /><line x1="0" y1="7" x2="7" y2="7" /><line x1="11" y1="7" x2="18" y2="7" /><line x1="0" y1="14" x2="18" y2="14" /></g>
            <!-- 坎 ☵ 上虚中实下虚 -->
            <g transform="translate(109,244)"><line x1="0" y1="0" x2="7" y2="0" /><line x1="11" y1="0" x2="18" y2="0" /><line x1="0" y1="7" x2="18" y2="7" /><line x1="0" y1="14" x2="7" y2="14" /><line x1="11" y1="14" x2="18" y2="14" /></g>
            <!-- 震 ☳ 上虚中虚下实 -->
            <g transform="translate(183,172)"><line x1="0" y1="0" x2="7" y2="0" /><line x1="11" y1="0" x2="18" y2="0" /><line x1="0" y1="7" x2="7" y2="7" /><line x1="11" y1="7" x2="18" y2="7" /><line x1="0" y1="14" x2="18" y2="14" /></g>
            <!-- 兑 ☱ 上虚中实下实 -->
            <g transform="translate(33,172)"><line x1="0" y1="0" x2="7" y2="0" /><line x1="11" y1="0" x2="18" y2="0" /><line x1="0" y1="7" x2="18" y2="7" /><line x1="0" y1="14" x2="18" y2="14" /></g>
            <!-- 巽 ☴ 上实中实下虚 -->
            <g transform="translate(159,114)"><line x1="0" y1="0" x2="18" y2="0" /><line x1="0" y1="7" x2="18" y2="7" /><line x1="0" y1="14" x2="7" y2="14" /><line x1="11" y1="14" x2="18" y2="14" /></g>
            <!-- 坤 ☷ 三虚 -->
            <g transform="translate(57,114)"><line x1="0" y1="0" x2="7" y2="0" /><line x1="11" y1="0" x2="18" y2="0" /><line x1="0" y1="7" x2="7" y2="7" /><line x1="11" y1="7" x2="18" y2="7" /><line x1="0" y1="14" x2="7" y2="14" /><line x1="11" y1="14" x2="18" y2="14" /></g>
            <!-- 艮 ☶ 上实中虚下虚 -->
            <g transform="translate(159,224)"><line x1="0" y1="0" x2="18" y2="0" /><line x1="0" y1="7" x2="7" y2="7" /><line x1="11" y1="7" x2="18" y2="7" /><line x1="0" y1="14" x2="7" y2="14" /><line x1="11" y1="14" x2="18" y2="14" /></g>
            <!-- 乾 ☰ 三实 -->
            <g transform="translate(57,224)"><line x1="0" y1="0" x2="18" y2="0" /><line x1="0" y1="7" x2="18" y2="7" /><line x1="0" y1="14" x2="18" y2="14" /></g>
          </g>

          <!-- 水底捞月（掌心弧线） -->
          <path d="M84,196 A34,34 0 1,1 152,196" fill="none" stroke="#1e6b52" stroke-width="1.8" stroke-dasharray="4 4" />
          <path d="M152,188 L158,195 L149,199 Z" fill="#1e6b52" />

          <!-- 小天心 / 总筋 / 天河 -->
          <circle cx="118" cy="252" r="5" fill="#b03a2e" />
          <text x="128" y="257" font-size="12" fill="#2b2318" font-family="Kaiti SC, STKaiti, serif">小天心</text>
          <line x1="118" y1="260" x2="118" y2="298" stroke="#c96a52" stroke-width="2.4" />
          <text x="126" y="304" font-size="12" fill="#2b2318" font-family="Kaiti SC, STKaiti, serif">总筋</text>
          <path d="M118,246 L118,98" stroke="#4a7a5f" stroke-width="1.6" stroke-dasharray="5 4" />
          <text x="92" y="90" font-size="12" fill="#4a7a5f" font-family="Kaiti SC, STKaiti, serif">天河（引水上天河）</text>

          <!-- 三关（桡侧）/ 六腑（尺侧） -->
          <path d="M224,110 L220,234" stroke="#b03a2e" stroke-width="3" stroke-linecap="round" />
          <path d="M224,110 L220,140 L216,150" fill="none" stroke="#b03a2e" stroke-width="1.8" />
          <text x="238" y="176" font-size="12" fill="#b03a2e" font-family="Kaiti SC, STKaiti, serif" transform="rotate(90 238 176)">三关（桡侧·气分）</text>
          <path d="M14,110 L18,234" stroke="#1e6b52" stroke-width="3" stroke-linecap="round" />
          <text x="-206" y="172" font-size="12" fill="#1e6b52" font-family="Kaiti SC, STKaiti, serif" transform="rotate(-90 -206 172)">六腑（尺侧·血分）</text>

          <!-- 脾土 / 肾水 -->
          <text x="214" y="60" font-size="12.5" fill="#b03a2e" font-family="Kaiti SC, STKaiti, serif" font-weight="bold">脾土</text>
          <text x="24" y="42" font-size="12.5" fill="#1e6b52" font-family="Kaiti SC, STKaiti, serif" font-weight="bold">肾水</text>

          <g font-size="12" fill="#5a4f3e" text-anchor="middle">
            <text x="118" y="332">推三关退六腑运八卦，男女俱在左手</text>
            <text x="118" y="354">大指脾面旋推为补、直推至甲为泻</text>
            <text x="118" y="376">水底捞月：掌心弧运，引水上天河</text>
          </g>
        </g>
      </svg>
    </div>

    <!-- ===== 手背三关五指节图 ===== -->
    <div v-else-if="current === 'handback'" class="fig-box">
      <svg viewBox="0 0 360 470" class="yk-svg">
        <g transform="translate(58,36)">
          <!-- 手背 -->
          <rect x="18" y="8" width="26" height="82" rx="12" fill="#f7f1e3" stroke="#7d6f52" stroke-width="1.8" />
          <rect x="58" y="-2" width="28" height="92" rx="13" fill="#f7f1e3" stroke="#7d6f52" stroke-width="1.8" />
          <rect x="102" y="2" width="28" height="88" rx="13" fill="#f7f1e3" stroke="#7d6f52" stroke-width="1.8" />
          <rect x="146" y="12" width="27" height="78" rx="12" fill="#f7f1e3" stroke="#7d6f52" stroke-width="1.8" />
          <path d="M204,92 C232,98 244,118 240,142 C236,158 222,162 210,152 L204,122 Z" fill="#f7f1e3" stroke="#7d6f52" stroke-width="1.8" />
          <path d="M18,92 L212,92 C224,92 230,100 230,112 L230,222 C230,246 212,260 188,260 L42,260 C18,260 6,246 6,222 L6,112 C6,100 12,92 18,92 Z" fill="#f7f1e3" stroke="#7d6f52" stroke-width="2" />
          <rect x="42" y="260" width="152" height="34" rx="8" fill="#f3ecdd" stroke="#7d6f52" stroke-width="1.6" />

          <!-- 五指节（轮揉） -->
          <g fill="#b03a2e">
            <circle cx="31" cy="52" r="3.4" /><circle cx="31" cy="68" r="3.4" />
            <circle cx="72" cy="44" r="3.4" /><circle cx="72" cy="60" r="3.4" /><circle cx="72" cy="76" r="3.4" />
            <circle cx="116" cy="46" r="3.4" /><circle cx="116" cy="62" r="3.4" /><circle cx="116" cy="78" r="3.4" />
            <circle cx="159" cy="54" r="3.4" /><circle cx="159" cy="70" r="3.4" />
            <circle cx="222" cy="124" r="3.4" /><circle cx="222" cy="138" r="3.4" />
          </g>
          <text x="118" y="28" text-anchor="middle" font-size="12.5" fill="#2b2318" font-family="Kaiti SC, STKaiti, serif">五指节（轮揉祛风，代苍术）</text>

          <!-- 上三关 -->
          <path d="M224,110 L220,234" stroke="#b03a2e" stroke-width="3" stroke-linecap="round" />
          <path d="M220,110 L216,140 L224,150" fill="none" stroke="#b03a2e" stroke-width="1.8" />
          <text x="238" y="176" font-size="12" fill="#b03a2e" font-family="Kaiti SC, STKaiti, serif" transform="rotate(90 238 176)">上三关（推上为补）</text>

          <!-- 后溪 -->
          <circle cx="16" cy="228" r="5" fill="#1e6b52" />
          <text x="-214" y="224" font-size="12" fill="#1e6b52" font-family="Kaiti SC, STKaiti, serif" transform="rotate(-90 -214 224)">后溪</text>

          <!-- 威灵 精宁 外劳宫 -->
          <circle cx="148" cy="158" r="5" fill="#b03a2e" />
          <text x="160" y="148" font-size="12" fill="#2b2318" font-family="Kaiti SC, STKaiti, serif">威灵</text>
          <circle cx="88" cy="158" r="5" fill="#b03a2e" />
          <text x="54" y="148" font-size="12" fill="#2b2318" font-family="Kaiti SC, STKaiti, serif">精宁</text>
          <circle cx="118" cy="196" r="5" fill="#c96a52" />
          <text x="128" y="200" font-size="12" fill="#2b2318" font-family="Kaiti SC, STKaiti, serif">外劳宫</text>
          <path d="M148,164 C142,176 130,186 118,190" fill="none" stroke="#c9b98f" stroke-width="1.2" stroke-dasharray="3 3" />
          <path d="M88,164 C94,176 106,186 118,190" fill="none" stroke="#c9b98f" stroke-width="1.2" stroke-dasharray="3 3" />

          <g font-size="12" fill="#5a4f3e" text-anchor="middle">
            <text x="118" y="332">精威拿紧代牛黄贝母；重揉手背同白芍川芎</text>
            <text x="118" y="354">黄蜂入洞：揉外劳将指屈，代防风羌活</text>
          </g>
        </g>
      </svg>
    </div>

    <!-- ===== 足部穴图 ===== -->
    <div v-else class="fig-box">
      <svg viewBox="0 0 360 470" class="yk-svg">
        <g transform="translate(36,26)">
          <!-- 腿 -->
          <path d="M144,0 C136,62 134,122 140,182 L152,202 L204,202 L210,182 C214,122 212,62 204,0 Z" fill="#fdf6e6" stroke="#7d6f52" stroke-width="2" />
          <!-- 膝后委中 -->
          <circle cx="176" cy="96" r="5" fill="#b03a2e" />
          <text x="190" y="100" font-size="12.5" fill="#2b2318" font-family="Kaiti SC, STKaiti, serif">委中（推毕揉之）</text>
          <!-- 足 -->
          <path d="M140,202 L220,202 L248,238 L256,290 C256,300 248,306 240,306 L132,306 C124,306 116,300 116,290 L124,238 Z" fill="#fdf6e6" stroke="#7d6f52" stroke-width="2" />
          <!-- 趾分界 -->
          <path d="M256,270 L232,270 M256,284 L232,284" stroke="#c9b98f" stroke-width="1.2" />
          <path d="M232,302 L208,302 M208,302 L186,302" stroke="#c9b98f" stroke-width="1" />
          <!-- 涌泉 -->
          <ellipse cx="186" cy="268" rx="9" ry="6.5" fill="none" stroke="#b03a2e" stroke-width="2" />
          <circle cx="186" cy="268" r="3.2" fill="#b03a2e" />
          <text x="200" y="256" font-size="12.5" fill="#2b2318" font-family="Kaiti SC, STKaiti, serif">涌泉（左揉代砂仁藿叶）</text>
          <!-- 大敦 -->
          <circle cx="254" cy="240" r="5" fill="#b03a2e" />
          <text x="266" y="228" font-size="12.5" fill="#2b2318" font-family="Kaiti SC, STKaiti, serif">大敦（拿之代钩藤）</text>
          <!-- 昆仑 -->
          <circle cx="120" cy="238" r="5" fill="#b03a2e" />
          <text x="66" y="234" font-size="12.5" fill="#2b2318" font-family="Kaiti SC, STKaiti, serif">昆仑（拿紧救胎寒）</text>
          <!-- 鬼眼 -->
          <circle cx="140" cy="206" r="5" fill="#b03a2e" />
          <text x="40" y="202" font-size="12.5" fill="#2b2318" font-family="Kaiti SC, STKaiti, serif">鬼眼（灸治反折）</text>

          <g font-size="12" fill="#5a4f3e" text-anchor="middle">
            <text x="186" y="352">涌泉右转不揉代朴硝；一推一揉右转参术无差</text>
            <text x="186" y="374">脱肛灸龟尾；张口摇头反折灸鬼眼</text>
          </g>
        </g>
      </svg>
    </div>
  </div>
</template>

<style scoped>
.yk-svg {
  width: 100%;
  max-width: 440px;
  height: auto;
}
.fig-box {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}
</style>
