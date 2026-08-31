<template>
  <div>
    <h1 class="page-title">目录 · 全书章节</h1>
    <div class="page-sub">上篇总论（理论源流）· 下篇各论（方剂实务）· 附录</div>
    <div class="safety-banner">
      <strong>⚠️</strong> 下篇各论所载丹药均为汞、砷剧毒化合物制剂。阅读与研究时严禁自行配制、严禁内服。
    </div>

    <template v-for="part in chapters.parts" :key="part.part">
      <h3>{{ part.part }}</h3>
      <div v-for="ch in part.chapters" :key="ch.id" class="card" style="cursor:pointer"
           @click="$router.push('/alchemy/chapter/' + ch.id)">
        <strong>{{ ch.no }} {{ ch.title }}</strong>
        <span style="float:right;flex-shrink:0;color:#b9a87e;font-size:0.8rem">阅读 →</span>
        <div v-if="ch.bookPages && ch.bookPages.length" style="font-size:0.78rem;color:#9a8a6c;margin-top:4px">
          原书第 {{ ch.bookPages.join('、') }} 页
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import chapters from '../data/chapters.json'
</script>
