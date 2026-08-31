<script setup lang="ts">
/** 小儿手纹脉位图 — 食指三关与左右手六部脉位（原著上编"小儿手纹脉位图"） */
</script>

<template>
  <div class="maiwei">
    <svg viewBox="0 0 460 400" class="maiwei-svg" role="img" aria-label="小儿手纹脉位图">
      <defs>
        <linearGradient id="mwSkin" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#fbf1dd" />
          <stop offset="0.5" stop-color="#fdf6e6" />
          <stop offset="1" stop-color="#f3e6cb" />
        </linearGradient>
      </defs>

      <!-- ===== 左：食指三关图 ===== -->
      <g transform="translate(20,16)">
        <text x="90" y="24" text-anchor="middle" font-size="15" font-family="Kaiti SC, STKaiti, serif" fill="#2b2318" font-weight="bold">食指三关（指纹）</text>
        <!-- 手指 -->
        <path d="M86,54 C74,54 70,61 70,72 L70,116 C60,118 55,125 55,132 L55,164 L70,164 L70,206 L55,206 L55,238 L70,238 L70,286 L55,286 L55,300 C55,313 66,323 86,323 C106,323 117,313 117,300 L117,286 L102,286 L102,238 L117,238 L117,206 L102,206 L102,164 L117,164 L117,132 C117,125 112,118 102,116 L102,72 C102,61 98,54 86,54 Z" fill="url(#mwSkin)" stroke="#7d6f52" stroke-width="2" stroke-linejoin="round" />
        <!-- 指甲 -->
        <path d="M76,58 C76,47 96,47 96,58 L96,69 C96,75 76,75 76,69 Z" fill="#f6ead3" stroke="#7d6f52" stroke-width="1.6" />
        <path d="M82,68 C84,65 88,65 90,68 C89,73 83,73 82,68 Z" fill="#fdf6e6" />
        <!-- 指节纹 -->
        <path d="M70,158 C74,160 80,162 86,162 C92,162 98,160 102,159" fill="none" stroke="#c9b98f" stroke-width="1.4" />
        <path d="M70,250 C74,252 80,254 86,254 C92,254 98,252 102,251" fill="none" stroke="#c9b98f" stroke-width="1.4" />
        <!-- 纹线（朱砂，波浪状） -->
        <path d="M86,316 C84,304 88,296 86,288 C84,280 88,270 86,262 C84,252 88,242 86,232 C84,222 88,212 86,202 C84,194 88,186 86,178" fill="none" stroke="#b03a2e" stroke-width="3.4" stroke-linecap="round" />
        <!-- 三关标注 + 分隔括号 -->
        <g font-family="Kaiti SC, STKaiti, serif" fill="#8a4a2a">
          <line x1="122" y1="60" x2="128" y2="60" stroke="#c9b98f" stroke-width="1.2" />
          <text x="131" y="65" font-size="14">命关</text>
          <line x1="122" y1="200" x2="128" y2="200" stroke="#c9b98f" stroke-width="1.2" />
          <text x="131" y="205" font-size="14">气关</text>
          <line x1="122" y1="300" x2="128" y2="300" stroke="#c9b98f" stroke-width="1.2" />
          <text x="131" y="305" font-size="14">风关</text>
        </g>
        <text x="90" y="352" text-anchor="middle" font-size="13" fill="#8a4a2a" font-family="Kaiti SC, STKaiti, serif">风轻 · 气重 · 命危</text>
        <text x="90" y="372" text-anchor="middle" font-size="14" fill="#5a4f3e">病初起纹在风关，出至命关为病甚</text>
        <!-- 虎口 -->
        <path d="M117,318 C128,322 134,330 133,338" fill="none" stroke="#8a7c5f" stroke-width="1.6" stroke-dasharray="3 3" />
        <text x="137" y="348" font-size="14" fill="#5a4f3e">虎口（大肠经）</text>
      </g>

      <!-- ===== 右：左右手六部脉位 ===== -->
      <g transform="translate(238,16)">
        <text x="110" y="24" text-anchor="middle" font-size="15" font-family="Kaiti SC, STKaiti, serif" fill="#2b2318" font-weight="bold">六部脉位（寸关尺）</text>
        <!-- 右手 -->
        <g transform="translate(0,40)">
          <text x="52" y="-4" text-anchor="middle" font-size="13.5" font-family="Kaiti SC, STKaiti, serif" fill="#4a7a5f">右手</text>
          <rect x="8" y="4" width="88" height="66" rx="6" fill="#fdf6e6" stroke="#7d6f52" stroke-width="1.6" />
          <line x1="8" y1="26" x2="96" y2="26" stroke="#c9b98f" stroke-width="1" />
          <line x1="8" y1="48" x2="96" y2="48" stroke="#c9b98f" stroke-width="1" />
          <text x="52" y="21" text-anchor="middle" font-size="13" fill="#b03a2e">肺大肠 · 寸</text>
          <text x="52" y="43" text-anchor="middle" font-size="13" fill="#b03a2e">脾胃 · 关</text>
          <text x="52" y="65" text-anchor="middle" font-size="15" fill="#b03a2e">命三焦 · 尺</text>
        </g>
        <!-- 左手 -->
        <g transform="translate(110,40)">
          <text x="52" y="-4" text-anchor="middle" font-size="13.5" font-family="Kaiti SC, STKaiti, serif" fill="#4a7a5f">左手</text>
          <rect x="8" y="4" width="88" height="66" rx="6" fill="#fdf6e6" stroke="#7d6f52" stroke-width="1.6" />
          <line x1="8" y1="26" x2="96" y2="26" stroke="#c9b98f" stroke-width="1" />
          <line x1="8" y1="48" x2="96" y2="48" stroke="#c9b98f" stroke-width="1" />
          <text x="52" y="21" text-anchor="middle" font-size="13" fill="#1e6b52">心小肠 · 寸</text>
          <text x="52" y="43" text-anchor="middle" font-size="13" fill="#1e6b52">肝胆 · 关</text>
          <text x="52" y="65" text-anchor="middle" font-size="15" fill="#1e6b52">膀胱肾 · 尺</text>
        </g>
        <!-- 脏腑表里注 -->
        <g transform="translate(0,116)">
          <rect x="0" y="0" width="206" height="146" rx="6" fill="#fbf7ec" stroke="#d8cdb4" stroke-width="1.2" />
          <text x="10" y="21" font-size="15" font-family="Kaiti SC, STKaiti, serif" fill="#2b2318" font-weight="bold">脏腑表里（病气相连）</text>
          <g font-size="14" fill="#5a4f3e">
            <text x="10" y="42">心—小肠　肝—胆　脾—胃</text>
            <text x="10" y="62">肺—大肠　肾—膀胱</text>
            <text x="10" y="88">左寸心克右寸肺，</text>
            <text x="10" y="107">左关肝克右关脾——</text>
            <text x="10" y="126">左手脉大于右手，</text>
            <text x="10" y="141">为木胜相克。</text>
          </g>
        </g>
        <g font-size="15" fill="#5a4f3e">
          <text x="110" y="298" text-anchor="middle">两手纹与两手脉同参：</text>
          <text x="110" y="318" text-anchor="middle">纹浮紫 ＋ 脉浮数 → 该脏风热</text>
          <text x="110" y="338" text-anchor="middle">如右手纹浮紫、右脉浮数 → 脾经风热</text>
        </g>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.maiwei-svg {
  width: 100%;
  max-width: 640px;
  height: auto;
  display: block;
  margin: 8px auto 0;
}
</style>
