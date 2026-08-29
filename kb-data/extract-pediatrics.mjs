// 儿科数据提取:把 erke TS 数据模块打包导出为规范化 JSON(供统一知识库迁移)
import {
  guanfangYanfang, sanzhengFang, wansanList, waizhiFa,
} from '/Users/apple/Documents/deepseek项目/程氏儿科/webapp/src/data/formulas'
import { syndromes, bazhengZonglun, liuziShuo, songs } from '/Users/apple/Documents/deepseek项目/程氏儿科/webapp/src/data/syndromes'
import { yianList } from '/Users/apple/Documents/deepseek项目/程氏儿科/webapp/src/data/yian'
import { drugTips, yaoxingFu } from '/Users/apple/Documents/deepseek项目/程氏儿科/webapp/src/data/drugTips'
import { deathSigns, shizhengQubi, lizhengHuaihou, manpiJuehou } from '/Users/apple/Documents/deepseek项目/程氏儿科/webapp/src/data/deathSigns'
import { tuinaDaiyaoFu, mianxueTuifa, tanbingFa, shoufaGejue, denghuoJiu } from '/Users/apple/Documents/deepseek项目/程氏儿科/webapp/src/data/tuina'
import { yanzhengLunzhi, chengxianYixun, jiuHen, shisanBukeXue, shiZhuan, jingwenYijiao, guanmenShazei, genghuanYaowei, kanbingMijue } from '/Users/apple/Documents/deepseek项目/程氏儿科/webapp/src/data/maxims'
import { nuejiLunzhi, shuzhengLunzhi, chushengBianzhi } from '/Users/apple/Documents/deepseek项目/程氏儿科/webapp/src/data/misc'
import { writeFileSync } from 'node:fs'
import { createHash } from 'node:crypto'

const oid = (prefix, name) => prefix + createHash('md5').update(String(name || '')).digest('hex').slice(0, 10)

const out = { formulas: [], herbs: [], diseases: [], syndromes: [], cases: [], tips: [] }
const src = '《程氏家传儿科秘要》'

function pushFormula(f, category) {
  out.formulas.push({
    module: 'pediatrics',
    origin_id: oid('p-f-', f.name || ''),
    name: f.name || '',
    aliases: f.alt ? [f.alt] : [],
    source: f.source || src,
    category: category || f.category || '',
    composition: Array.isArray(f.herbs) ? f.herbs.map(h => ({ name: h.name, dose: h.dose || '' })) : [],
    function: f.gongyong || '',
    indication: '',
    usage: f.usage || '',
    formula_type: f.type || '',
    modifications: Array.isArray(f.jiawei) ? JSON.stringify(f.jiawei) : '',
    extra: { decoction: f.decoction || '', note: f.note || '' },
  })
}

for (const f of [...guanfangYanfang, ...sanzhengFang]) pushFormula(f, f.category || '验方')
for (const w of wansanList) pushFormula({ ...w, herbs: [], type: '丸散' }, '丸散')
for (const w of waizhiFa || []) pushFormula({ name: w.name || w, herbs: [], usage: w.usage || w.note || '', type: '外治', gongyong: w.note || '' }, '外治')

// 证型(含八症方药)
for (const s of syndromes) {
  const fangyao = s.fangyao || {}
  out.syndromes.push({
    module: 'pediatrics',
    origin_id: `p-${s.id}`,
    name: s.name,
    aliases: s.altName ? [s.altName] : [],
    yin_yang: '',
    stage: '',
    summary: s.summary || '',
    extra: {
      methods: s.methods || [],
      waihou: s.waihou || {}, bingyin: s.bingyin || {}, shouwen: s.shouwen || {},
      maifa: s.maifa || {}, zhifa: s.zhifa || {}, fangyao,
      bianzheng: s.bianzheng || [],
    },
  })
  const f = s.fangyao
  if (f && (f.name || (Array.isArray(f.herbs) && f.herbs.length))) {
    out.formulas.push({
      module: 'pediatrics',
      origin_id: `p-${s.id}-fang`,
      name: f.name || `${s.name}方`,
      aliases: [],
      source: src,
      category: '八症主方',
      composition: Array.isArray(f.herbs) ? f.herbs.map(h => ({ name: h.name, dose: h.dose || '' })) : [],
      function: s.summary || '',
      indication: s.name,
      usage: f.usage || '',
      formula_type: '内服',
      extra: { syndrome_id: s.id, notes: (f.herbs || []).map(h => (h.note ? `${h.name}:${h.note}` : '')).filter(Boolean).join(';') },
    })
  }
}

for (const y of yianList) {
  out.cases.push({
    module: 'pediatrics',
    origin_id: `p-${y.id}`,
    title: y.title || '',
    disease: y.category || '',
    syndrome: '',
    expert_name: '程康圃',
    source: src,
    chief_complaint: '',
    history: y.original || '',
    treatment: Array.isArray(y.formulas) ? y.formulas.join('、') : '',
    effect: y.yanyu || '',
    extra: { plain: y.plain || '' },
  })
}

function tipsFrom(title, list) {
  const items = Array.isArray(list) ? list : [list]
  for (const it of items) {
    if (!it) continue
    if (typeof it === 'string') { out.tips.push({ module: 'pediatrics', category: title, content: it, source: src }); continue }
    // 对象形态:{intro, items:[...]} / {t, original, plain} / {original, plain} / {name, ...}
    if (Array.isArray(it.items)) { tipsFrom(title, it.items); continue }
    const parts = [it.intro, it.t, it.original, it.plain, it.content, it.note, it.name, it.yanyu].filter(Boolean)
    if (parts.length) {
      out.tips.push({
        module: 'pediatrics',
        origin_id: oid('p-t-', title + (it.t || it.name || it.original || '') + parts.join('')),
        category: title,
        content: parts.join('\n'),
        source: src,
        extra: { name: it.name || it.t || '' },
      })
    }
  }
}
tipsFrom('危候警示', deathSigns)
tipsFrom('医道训诫', [].concat(yanzhengLunzhi, chengxianYixun, jiuHen, shisanBukeXue, shiZhuan, jingwenYijiao, guanmenShazei, genghuanYaowei, kanbingMijue))
tipsFrom('推拿代药', [].concat(tuinaDaiyaoFu, mianxueTuifa, tanbingFa, shoufaGejue, denghuoJiu))
tipsFrom('用药心得', drugTips)
tipsFrom('总论', [].concat(bazhengZonglun, liuziShuo, songs))
tipsFrom('杂论', [].concat(nuejiLunzhi, shuzhengLunzhi, chushengBianzhi))
tipsFrom('药性赋', yaoxingFu)

writeFileSync('/Users/apple/Documents/deepseek项目/tcm-platform-merge/kb-data/pediatrics.json', JSON.stringify(out, null, 1))
console.log('儿科提取完成: formulas', out.formulas.length, 'syndromes', out.syndromes.length, 'cases', out.cases.length, 'tips', out.tips.length)
