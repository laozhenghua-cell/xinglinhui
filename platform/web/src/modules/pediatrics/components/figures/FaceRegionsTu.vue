<script setup lang="ts">
/** 小儿面部属位图 — 额心、鼻脾、左颊肝、右颊肺、颏肾；五色主病；苗窍望诊 */
</script>

<template>
  <div class="face">
    <svg viewBox="0 0 400 560" class="face-svg" role="img" aria-label="小儿面部属位图">
      <defs>
        <linearGradient id="faceSkin" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#fdf7e9" />
          <stop offset="1" stop-color="#f5e9d0" />
        </linearGradient>
      </defs>

      <!-- 双耳 -->
      <g>
        <path d="M86,236 C72,232 66,240 68,252 C70,268 70,286 74,300 C82,312 98,306 98,290 L98,276 C94,262 92,246 92,234 Z" fill="url(#faceSkin)" stroke="#7d6f52" stroke-width="2" />
        <path d="M82,254 C79,262 79,276 82,288" fill="none" stroke="#c9b98f" stroke-width="1.4" />
        <path d="M314,236 C328,232 334,240 332,252 C330,268 330,286 326,300 C318,312 302,306 302,290 L302,276 C306,262 308,246 308,234 Z" fill="url(#faceSkin)" stroke="#7d6f52" stroke-width="2" />
        <path d="M318,254 C321,262 321,276 318,288" fill="none" stroke="#c9b98f" stroke-width="1.4" />
        <circle cx="83" cy="304" r="3.2" fill="#b03a2e" />
        <circle cx="317" cy="304" r="3.2" fill="#b03a2e" />
        <text x="64" y="324" font-size="11" fill="#5a4f3e">耳垂尖</text>
        <text x="330" y="324" font-size="11" fill="#5a4f3e">耳垂尖</text>
      </g>

      <!-- 面廓 -->
      <path d="M200,96 C148,96 108,120 96,160 C86,196 84,232 90,268 C96,306 112,348 132,384 C146,410 156,436 158,462 C160,478 170,486 180,484 L186,482 C190,472 194,462 198,452 C202,462 206,472 210,482 L216,484 C226,486 236,478 238,462 C240,436 250,410 264,384 C284,348 300,306 306,268 C312,232 310,196 300,160 C288,120 252,96 200,96 Z" fill="url(#faceSkin)" stroke="#7d6f52" stroke-width="2.2" />

      <!-- 发际与双鬓 -->
      <path d="M124,132 C140,104 170,88 200,88 C230,88 260,104 276,132" fill="none" stroke="#2b2318" stroke-width="2.4" stroke-linecap="round" />
      <path d="M112,168 C106,196 106,224 112,248" fill="none" stroke="#2b2318" stroke-width="2" stroke-linecap="round" opacity="0.75" />
      <path d="M288,168 C294,196 294,224 288,248" fill="none" stroke="#2b2318" stroke-width="2" stroke-linecap="round" opacity="0.75" />

      <!-- 额部（心·离火） -->
      <path d="M128,158 C150,118 250,118 272,158 L272,186 C256,196 144,196 128,186 Z" fill="#f9eceb" fill-opacity="0.75" stroke="#d9a49b" stroke-width="1.2" />
      <!-- 左颊（肝·震木） -->
      <path d="M96,220 C106,196 122,188 130,196 C140,224 142,258 136,292 C128,330 112,352 102,358 C96,314 92,268 96,220 Z" fill="#e8f2ec" fill-opacity="0.8" stroke="#9cbfae" stroke-width="1.2" />
      <!-- 右颊（肺·兑金） -->
      <path d="M304,220 C294,196 278,188 270,196 C260,224 258,258 264,292 C272,330 288,352 298,358 C304,314 308,268 304,220 Z" fill="#f7f1e3" fill-opacity="0.9" stroke="#d8cdb4" stroke-width="1.2" />

      <!-- 眉 -->
      <path d="M142,206 Q160,198 178,204" fill="none" stroke="#5a4f3e" stroke-width="3" stroke-linecap="round" />
      <path d="M222,204 Q240,198 258,206" fill="none" stroke="#5a4f3e" stroke-width="3" stroke-linecap="round" />

      <!-- 目（肝窍） -->
      <g>
        <path d="M134,232 Q148,222 162,232 Q148,244 134,232 Z" fill="#fff" stroke="#5a4f3e" stroke-width="1.8" />
        <circle cx="148" cy="233" r="5" fill="#2b2318" />
        <circle cx="149.5" cy="230.5" r="1.6" fill="#fff" />
        <path d="M238,232 Q252,222 266,232 Q252,244 238,232 Z" fill="#fff" stroke="#5a4f3e" stroke-width="1.8" />
        <circle cx="252" cy="233" r="5" fill="#2b2318" />
        <circle cx="253.5" cy="230.5" r="1.6" fill="#fff" />
      </g>

      <!-- 鼻（脾·中土）：山根、年寿、准头 -->
      <path d="M200,206 L200,240 C199,252 195,258 191,262 C196,265 200,268 200,272 L200,280 C200,286 194,292 186,294 C179,296 173,292 171,286 L171,280 C171,274 176,270 183,270 C192,270 196,266 196,262 C196,254 198,246 200,240" fill="none" stroke="#7d6f52" stroke-width="2" stroke-linejoin="round" />
      <ellipse cx="178" cy="288" rx="10" ry="8" fill="none" stroke="#7d6f52" stroke-width="1.6" />
      <ellipse cx="222" cy="288" rx="10" ry="8" fill="none" stroke="#7d6f52" stroke-width="1.6" />

      <!-- 人中、承浆、口 -->
      <path d="M200,282 L200,308" fill="none" stroke="#b08a6a" stroke-width="1.6" />
      <path d="M176,314 Q188,328 200,330 Q212,328 224,314" fill="none" stroke="#c96a52" stroke-width="2.6" stroke-linecap="round" />
      <path d="M182,322 Q200,330 218,322" fill="none" stroke="#c96a52" stroke-width="1.4" stroke-linecap="round" />
      <circle cx="200" cy="342" r="2.6" fill="#b08a6a" />

      <!-- 颏（肾·坎水） -->
      <path d="M158,392 C172,372 228,372 242,392 C242,420 230,444 200,448 C170,444 158,420 158,392 Z" fill="#ececec" fill-opacity="0.85" stroke="#8b8b8b" stroke-width="1.2" />

      <!-- 太阳（穴） -->
      <circle cx="118" cy="176" r="3.6" fill="#b03a2e" />
      <circle cx="282" cy="176" r="3.6" fill="#b03a2e" />

      <!-- 五脏属位标注 -->
      <g font-family="Kaiti SC, STKaiti, serif" font-weight="bold">
        <text x="200" y="132" text-anchor="middle" font-size="15" fill="#c0392b">额 · 心（离火）</text>
        <text x="92" y="304" text-anchor="middle" font-size="14" fill="#1e6b52">左颊 · 肝</text>
        <text x="92" y="320" text-anchor="middle" font-size="12.5" fill="#1e6b52">（震木）</text>
        <text x="308" y="304" text-anchor="middle" font-size="14" fill="#8a7c5f">右颊 · 肺</text>
        <text x="308" y="320" text-anchor="middle" font-size="12.5" fill="#8a7c5f">（兑金）</text>
        <text x="200" y="270" text-anchor="middle" font-size="13" fill="#c9a227">鼻 · 脾（中土）</text>
        <text x="200" y="478" text-anchor="middle" font-size="14" fill="#333">颏 · 肾（坎水）</text>
      </g>

      <!-- 苗窍引线 -->
      <g font-size="11.5" fill="#5a4f3e" stroke="#c9b98f" stroke-width="0.9">
        <line x1="252" y1="233" x2="346" y2="210" />
        <circle cx="346" cy="210" r="2" fill="#c9b98f" stroke="none" />
        <text x="349" y="205">目为肝窍</text>
        <line x1="200" y1="330" x2="346" y2="380" />
        <circle cx="346" cy="380" r="2" fill="#c9b98f" stroke="none" />
        <text x="349" y="384">唇为脾胃窍</text>
        <line x1="200" y1="222" x2="346" y2="146" />
        <circle cx="346" cy="146" r="2" fill="#c9b98f" stroke="none" />
        <text x="349" y="141">鼻为肺窍</text>
        <line x1="79" y1="252" x2="30" y2="196" />
        <circle cx="30" cy="196" r="2" fill="#c9b98f" stroke="none" />
        <text x="4" y="192">耳齿为肾窍</text>
        <line x1="200" y1="336" x2="30" y2="392" />
        <circle cx="30" cy="392" r="2" fill="#c9b98f" stroke="none" />
        <text x="4" y="398">舌为心之苗</text>
        <line x1="118" y1="176" x2="34" y2="150" />
        <circle cx="34" cy="150" r="2" fill="#c9b98f" stroke="none" />
        <text x="4" y="130">太阳（黑掩太阳主死候）</text>
      </g>

      <!-- 五色主病 -->
      <g transform="translate(0,500)">
        <rect x="36" y="0" width="328" height="52" rx="8" fill="#fbf7ec" stroke="#d8cdb4" stroke-width="1" />
        <text x="48" y="18" font-size="12" font-family="Kaiti SC, STKaiti, serif" fill="#2b2318" font-weight="bold">五色主病</text>
        <g font-size="11.5" fill="#5a4f3e">
          <circle cx="52" cy="36" r="6" fill="#c0392b" />
          <text x="63" y="40">红热心</text>
          <circle cx="130" cy="36" r="6" fill="#1e6b52" />
          <text x="141" y="40">青肝风</text>
          <circle cx="208" cy="36" r="6" fill="#c9a227" />
          <text x="219" y="40">黄脾伤</text>
          <circle cx="286" cy="36" r="6" fill="#9aa7ad" />
          <text x="297" y="40">白肺寒</text>
          <circle cx="352" cy="36" r="6" fill="#333" />
          <text x="363" y="40">黑肾败</text>
        </g>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.face-svg {
  width: 100%;
  max-width: 470px;
  height: auto;
  display: block;
  margin: 8px auto 0;
}
</style>
