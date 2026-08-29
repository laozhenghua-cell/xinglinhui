<template>
  <div>
    <h1 class="page-title">辨证选方 · 辅助参考</h1>
    <div class="page-sub">基于原书 33 方主治与中医外科辨证常规 · 仅供学术研究参考</div>
    <div class="safety-banner">
      <strong>⚠️</strong> 本模块不构成医疗建议。丹药为汞、砷剧毒化合物，临床使用须由执业中医师在现行法规框架内决策。
    </div>

    <div class="card" style="padding:20px">
      <div style="display:flex;gap:12px;align-items:flex-start">
        <span style="font-size:1.8rem">👥</span>
        <div style="flex:1">
          <h3 style="margin:0 0 6px">大众科普模式</h3>
          <p style="margin:0;font-size:0.9rem;color:#6b5c42">
            了解中医外科病证常识（痈、疽、疔、瘰疬、瘘管……）与就医指引（红黄绿旗）。
            <strong>不提供方剂推荐。</strong>
          </p>
          <el-button type="primary" plain style="margin-top:10px" @click="$router.push('/alchemy/assist/public')">进入科普自测 →</el-button>
        </div>
      </div>
    </div>

    <div class="card" style="padding:20px;border-color:var(--dan-red)">
      <div style="display:flex;gap:12px;align-items:flex-start">
        <span style="font-size:1.8rem">⚕️</span>
        <div style="flex:1">
          <h3 style="margin:0 0 6px">专业研究模式</h3>
          <p style="margin:0;font-size:0.9rem;color:#6b5c42">
            面向中医外科医师与研究者：引导式问诊（部位→疮形→脓液→全身症状→舌脉）→ 辨证结论
            → 候选方剂（附原书依据、用法禁忌与安全警示）。
          </p>
          <el-button type="danger" style="margin-top:10px" @click="$router.push('/alchemy/assist/professional')">进入专业模式 →</el-button>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 style="margin-top:0">使用须知</h3>
      <ul style="font-size:0.88rem;color:#5c5240;padding-left:18px;line-height:1.9">
        <li>问诊结论来自规则引擎，规则全部可解释（每条推荐附原书主治原文）。</li>
        <li>任何中毒征象（口腔金属味、牙龈出血、震颤、少尿血尿）或危急重症（高热神昏、呼吸困难）均触发红旗，系统不推荐任何方剂并要求立即就医。</li>
        <li>孕妇、哺乳期、儿童、肝肾功能不全、过敏史者一律排除全部丹药方剂。</li>
        <li>候选方剂仅为史料级研究参考，不是处方；剂量、用法以原书原文与现行药典为准。</li>
      </ul>
    </div>
  </div>
</template>
