// 辨证选方规则引擎（纯前端，可解释）
// 三层辩证：按病（病灶/疮形方向）+ 按证（阴阳证型）+ 按分期（未溃/成脓/已溃）
// 输入 answers: { [stepId]: [optionId, ...] } → 输出证型、安全闸门、候选方剂（含排除说明）
import ontology from '../data/assist-ontology.json'
import rules from '../data/assist-rules.json'
import tags from '../data/assist-tags.json'
import formulasData from '../data/formulas.json'
import dulong from '../data/dulong.json'

const DULONG_SECTIONS = dulong.meta.sections
const INTERNAL_KEYS = {}
{
  const step = ontology.steps.find((s) => s.id === 'internal')
  if (step) for (const o of step.options) INTERNAL_KEYS[o.id] = o.keys || []
}

function dulongGuides(answers) {
  const sel = (answers.internal || []).filter((id) => INTERNAL_KEYS[id])
  if (!sel.length) return null
  const seen = new Set()
  const out = []
  for (const id of sel) {
    for (const key of INTERNAL_KEYS[id]) {
      for (const sec of DULONG_SECTIONS) {
        for (const e of sec.entries) {
          const k = sec.id + ':' + e.n
          if (!seen.has(k) && e.d.includes(key)) {
            seen.add(k)
            out.push({ sec: sec.name, d: e.d, g: e.g })
          }
        }
      }
    }
  }
  return out.length ? out : null
}

export function runEngine(answers) {
  const all = Object.values(answers).flat()
  const has = (id) => all.includes(id)

  // 1. 安全闸门（优先）
  const redFlags = []
  for (const f of rules.safety.red) {
    if (f.any.some(has)) redFlags.push({ id: f.id, message: f.message })
  }
  const yellowFlags = []
  for (const f of rules.safety.yellow) {
    if (f.any.some(has)) yellowFlags.push({ id: f.id, message: f.message })
  }

  // 2. 证型
  const syndromes = []
  for (const s of rules.syndromes) {
    const hits = s.any.filter(has)
    if (hits.length >= s.minHits) {
      syndromes.push({ id: s.id, name: s.name, explain: s.explain, hits })
    }
  }
  const yangHit = syndromes.some((s) => s.id === 'sy_yang')
  const yinHit = syndromes.some((s) => s.id === 'sy_yin')

  // 3. 分期与证型过滤
  const stageSel = (answers.stage || [])[0]
  function stageExcluded(f) {
    const t = tags.tags[f.id]
    if (!t || !t.stage || !stageSel) return null
    return t.stage.includes(stageSel) ? null : t.note
  }
  function syndromeExcluded(f) {
    const t = tags.tags[f.id]
    if (!t || !t.syndrome) return null
    if (yangHit && t.syndrome.length === 1 && t.syndrome[0] === 'yin') return t.note
    if (yinHit && t.syndrome.length === 1 && t.syndrome[0] === 'yang') return t.note
    return null
  }
  function tagChips(f) {
    const t = tags.tags[f.id]
    if (!t) return []
    const chips = []
    if (t.stage) chips.push(...t.stage.map((s) => tags.meta.stage[s]))
    if (t.syndrome) chips.push(...t.syndrome.map((s) => tags.meta.syndrome[s]))
    return chips
  }

  // 4. 候选方剂（红旗下不推荐；按证/按分期过滤并记录理由）
  const recommendations = []
  const guides = redFlags.length === 0 ? dulongGuides(answers) : null
  if (redFlags.length === 0) {
    for (const r of rules.recommend) {
      const hits = r.match.any.filter(has)
      const plusOk = !r.match.plus || r.match.plus.some(has)
      if (hits.length > 0 && plusOk) {
        const kept = []
        const excluded = []
        for (const id of r.formulas) {
          const f = formulasData.formulas.find((x) => x.id === id)
          if (!f) continue
          const exStage = stageExcluded(f)
          const exSyn = syndromeExcluded(f)
          const exNote = exSyn || exStage
          if (exNote) {
            excluded.push({ f, reason: exNote, kind: exSyn ? '证' : '期' })
          } else {
            const item = { f, chips: tagChips(f) }
            if (f.id === 'F30' && guides) item.guides = guides
            kept.push(item)
          }
        }
        recommendations.push({ id: r.id, title: r.title, basis: r.basis, hits, kept, excluded })
      }
    }
  }

  // 5. 是否完成关键必答
  const missing = ['special', 'poison'].filter((k) => !(answers[k] && answers[k].length))

  return {
    answers,
    redFlags,
    yellowFlags,
    syndromes,
    recommendations,
    missing,
    blocked: redFlags.length > 0,
    cautious: yellowFlags.length > 0,
    totalFormulas: formulasData.formulas.length,
    ontology: ontology.steps,
    disclaimer: rules.meta.position,
    stageSelected: stageSel || null,
    guides,
    dulongTotal: DULONG_SECTIONS.reduce((n, s) => n + s.entries.length, 0),
  }
}
