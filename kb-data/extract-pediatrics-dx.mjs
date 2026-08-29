// 提取儿科原版辨证引擎数据 → JSON(供后端按原著辨证)
import { findingGroups, findingIndex, syndromeRules, dangerRules, comboDangers, jiajianMapping } from '/Users/apple/Documents/deepseek项目/tcm-platform-merge/platform/web/src/modules/pediatrics/engine/diagnosis'
import { syndromes } from '/Users/apple/Documents/deepseek项目/tcm-platform-merge/platform/web/src/modules/pediatrics/data/syndromes'
import { writeFileSync } from 'node:fs'

const findings = []
for (const st of findingGroups) {
  for (const g of st.groups) {
    for (const f of g.findings) {
      findings.push({ key: f.key, label: f.label, step: st.step, group: g.name, hint: f.hint || '' })
    }
  }
}

const synDetails = syndromes.map((s) => ({
  id: s.id,
  name: s.name,
  altName: s.altName || '',
  methods: s.methods || [],
  summary: s.summary || '',
  waihou: s.waihou || {},
  bingyin: s.bingyin || {},
  shouwen: s.shouwen || {},
  maifa: s.maifa || {},
  zhifa: s.zhifa || {},
  fangyao: s.fangyao || {},
  jiajian: s.jiajian || [],
  wansan: s.wansan || [],
}))

const out = {
  findings,
  rules: syndromeRules.map((r) => ({ id: r.id, features: r.features })),
  dangers: dangerRules.map((d) => ({ key: d.key, label: d.label, level: d.level })),
  combos: comboDangers,
  jiajian: jiajianMapping,
  syndromes: synDetails,
}
writeFileSync('/Users/apple/Documents/deepseek项目/tcm-platform-merge/kb-data/pediatrics-dx.json', JSON.stringify(out, null, 1))
console.log('儿科原版辨证引擎数据提取完成: findings', findings.length, '| 规则', out.rules.length, '| 症', synDetails.length)
