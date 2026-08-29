<script setup lang="ts">
import { tuinaDaiyaoFu, mianxueTuifa, tanbingFa, shoufaGejue, zhangmianTu, shoubeiTu, xiaotianxin, denghuoJiu } from '../data/tuina'
import YoukeFigures from '../components/figures/YoukeFigures.vue'

const pairs: [string, string][] = [
  ['推上三关', '麻黄、肉桂'],
  ['退下六腑', '滑石、羚羊'],
  ['水底捞月', '黄连、犀角'],
  ['天河引水', '黄芩、黄柏、连翘'],
  ['大指脾面旋推', '人参、白术'],
  ['大指脾面直泻', '灶心土、石膏'],
  ['大肠侧推虎口', '诃子、炮姜'],
  ['大肠反推', '大黄、枳实'],
  ['涌泉右转不揉', '朴硝'],
  ['一推一揉右转', '人参、白术'],
  ['食指泻肺', '桑皮、桔梗'],
  ['旋推止嗽', '五味子、款冬花'],
  ['精威拿紧', '牛黄、贝母'],
  ['肺俞重揉', '半夏、南星'],
  ['黄蜂入洞', '防风、羌活'],
  ['捧耳摇头', '生地、木香'],
  ['五指节轮揉', '苍术'],
  ['足拿大敦鞋带', '钩藤'],
  ['后溪推上', '猪苓、泽泻'],
  ['小指补肾', '杜仲、地黄'],
  ['涌泉左揉', '砂仁、藿香'],
  ['重揉手背', '白芍、川芎'],
  ['脐风灯火十三', '再造之恩'],
  ['定惊元宵十五', '仙丹不啻'],
]
</script>

<template>
  <div class="page">
    <div class="h-title" style="font-size: 26px">推拿代药（附编《幼科铁镜》）</div>
    <p class="vern" style="margin-top: 6px">
      夏禹铸："推拿古人以之代药……特赋出某推当某药、某拿抵某味，使人晓得用推拿便是用药味。
      药味既不可误投，推拿又何可乱用。"
    </p>

    <div class="h-sec">一、推拿代药赋</div>
    <div class="card">
      <div class="original">{{ tuinaDaiyaoFu.original }}</div>
      <p class="vern">{{ tuinaDaiyaoFu.plain }}</p>
    </div>

    <div class="h-sec">二、推拿代药对照表</div>
    <div class="card">
      <el-table :data="pairs" border>
        <el-table-column prop="0" label="推拿手法" width="200">
          <template #default="{ row }"><b style="font-family: var(--font-kai); color: var(--vermilion)">{{ row[0] }}</b></template>
        </el-table-column>
        <el-table-column prop="1" label="所代之药" width="220">
          <template #default="{ row }"><span style="color: var(--jade)">{{ row[1] }}</span></template>
        </el-table-column>
        <el-table-column label="性味参照" prop="1">
          <template #default>寒热温平，药之四性；推拿揉掐，性与药同</template>
        </el-table-column>
      </el-table>
    </div>

    <div class="h-sec">三、面各穴图与推法</div>
    <div class="card">
      <div class="original">{{ mianxueTuifa.original }}</div>
      <p class="vern">{{ mianxueTuifa.plain }}</p>
      <YoukeFigures fig="face" />
    </div>

    <div class="h-sec">四、探病法</div>
    <div class="card">
      <div class="original" style="text-align: center">{{ tanbingFa.original }}</div>
      <p class="vern">{{ tanbingFa.plain }}</p>
    </div>

    <div class="h-sec">五、掌面 · 手背 · 足部诸图</div>
    <div class="card">
      <YoukeFigures fig="palm" />
      <p class="vern" style="margin-top: 14px">{{ zhangmianTu.plain }}　{{ xiaotianxin.plain }}</p>
      <YoukeFigures fig="handback" style="margin-top: 18px" />
      <p class="vern" style="margin-top: 14px">{{ shoubeiTu.plain }}</p>
      <YoukeFigures fig="foot" style="margin-top: 18px" />
    </div>

    <div class="h-sec">六、手法歌诀（摘录）</div>
    <el-row :gutter="14">
      <el-col v-for="g in shoufaGejue" :key="g.title" :xs="24" :md="12">
        <div class="card song">
          <div class="song-t">{{ g.title }}</div>
          <div class="original" style="font-size: 13px">{{ g.text }}</div>
        </div>
      </el-col>
    </el-row>

    <div class="h-sec">七、灯火艾灸法</div>
    <div class="card">
      <el-table :data="denghuoJiu" border>
        <el-table-column prop="name" label="法名" width="160" />
        <el-table-column prop="usage" label="用法" />
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.song {
  min-height: 120px;
}
.song-t {
  font-family: var(--font-kai);
  font-weight: 700;
  color: var(--jade);
  margin-bottom: 6px;
}
</style>
