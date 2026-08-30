// 知识总库 — 8 类内容元信息与字段映射（与后端 /api/v1/kb 契约对齐）

export const KB_TYPES = [
  { key: 'formulas', label: '方剂', icon: '💊', color: '#409EFF' },
  { key: 'herbs', label: '中药', icon: '🌿', color: '#67C23A' },
  { key: 'diseases', label: '病种', icon: '🩹', color: '#E6A23C' },
  { key: 'syndromes', label: '证型', icon: '🔬', color: '#9C27B0' },
  { key: 'cases', label: '医案', icon: '📋', color: '#F56C6C' },
  { key: 'tips', label: '要诀', icon: '📜', color: '#20A39E' },
  { key: 'terms', label: '术语', icon: '📖', color: '#8E6C4F' },
  { key: 'dulong', label: '引药', icon: '🐉', color: '#C0392B' },
  { key: 'classics', label: '典籍', icon: '📜', color: '#7A5A2E' },
  { key: 'yifang', label: '医方集解', icon: '🧾', color: '#B07A2E' }
]

export const TYPE_MAP = Object.fromEntries(KB_TYPES.map((t) => [t.key, t]))

export const MODULES = [
  { key: 'surgery', label: '外科疮疡' },
  { key: 'anorectal', label: '肛肠痔漏' },
  { key: 'pediatrics', label: '儿科' },
  { key: 'alchemy', label: '丹药研究' }
]

export const MODULE_MAP = Object.fromEntries(MODULES.map((m) => [m.key, m.label]))

// 列表/搜索结果中“主名称”字段（契约：terms 用 term、dulong 用 disease、cases 用 title、tips 截断 content）
export const NAME_FIELD = {
  formulas: 'name',
  herbs: 'name',
  diseases: 'name',
  syndromes: 'name',
  cases: 'title',
  tips: 'category',
  terms: 'term',
  dulong: 'disease',
  classics: 'article',
  yifang: 'name'
}

export function displayName(type, item) {
  if (!item) return ''
  const key = NAME_FIELD[type]
  const v = key ? item[key] : undefined
  if (v != null && String(v).trim() !== '') return String(v)
  return item.name || item.term || item.title || item.disease || item.content || ''
}

export function truncate(text, len = 60) {
  const s = String(text == null ? '' : text)
  return s.length > len ? s.slice(0, len) + '…' : s
}

// 详情页 description 展示字段（特殊字段 composition/aliases/meridians/extra 单独处理，不在此列）
export const TYPE_FIELDS = {
  formulas: [
    ['source', '出处'], ['category', '类别'], ['function', '功效'],
    ['indication', '适应证'], ['usage', '用法用量'], ['method', '治法'],
    ['formula_type', '方剂类型'], ['contraindications', '禁忌'],
    ['modifications', '加减'], ['preparation', '制备'], ['toxicity', '毒性']
  ],
  herbs: [
    ['pinyin', '拼音'], ['category', '分类'], ['properties', '性味'],
    ['effects', '功效'], ['indications', '主治'], ['contraindications', '禁忌'],
    ['dosage', '用量'], ['usage_notes', '用法注意']
  ],
  diseases: [
    ['category', '分类'], ['location', '部位'], ['morphology', '形态'],
    ['characteristics', '特点'], ['differential', '鉴别'], ['prognosis', '预后'],
    ['western_equiv', '西医对应'], ['source', '出处'], ['is_dangerous', '是否危险']
  ],
  syndromes: [
    ['yin_yang', '阴阳'], ['stage', '阶段'], ['local_signs', '局部症状'],
    ['systemic_signs', '全身症状'], ['tongue_pulse', '舌脉'], ['summary', '总结']
  ],
  cases: [
    ['disease', '病种'], ['syndrome', '证型'], ['patient_info', '患者信息'],
    ['chief_complaint', '主诉'], ['history', '病史'], ['treatment', '治疗'],
    ['effect', '疗效'], ['source', '出处'], ['expert_name', '医家'], ['category', '分类']
  ],
  tips: [['category', '类别'], ['content', '内容', 'truncate'], ['source', '出处']],
  terms: [['definition', '释义'], ['source', '出处']],
  dulong: [['section', '章节'], ['n', '序号'], ['guide', '引药']],
  classics: [['book', '典籍'], ['article', '条文'], ['original', '原文', 'truncate'], ['plain', '白话', 'truncate']],
  yifang: [['category', '分类'], ['function', '功效'], ['indications', '主治'], ['contraindications', '禁忌'], ['source', '出处']]
}

// 列表页“主名称列”标题（tips 的 name 即截断 content）
export const NAME_LABEL = {
  formulas: '方名',
  herbs: '药名',
  diseases: '病名',
  syndromes: '证型',
  cases: '标题',
  tips: '内容',
  terms: '术语',
  dulong: '病名',
  yifang: '方名'
}

// 列表页附加列（除主名称列外）
export const LIST_COLUMNS = {
  formulas: [
    { prop: 'composition', label: '组成', kind: 'composition' },
    { prop: 'function', label: '功效' },
    { prop: 'category', label: '类别' },
    { prop: 'source', label: '出处' }
  ],
  herbs: [
    { prop: 'properties', label: '性味' },
    { prop: 'effects', label: '功效' },
    { prop: 'category', label: '分类' },
    { prop: 'indications', label: '主治' }
  ],
  diseases: [
    { prop: 'category', label: '分类' },
    { prop: 'location', label: '部位' },
    { prop: 'characteristics', label: '特点' }
  ],
  syndromes: [
    { prop: 'yin_yang', label: '阴阳' },
    { prop: 'stage', label: '阶段' },
    { prop: 'summary', label: '总结' }
  ],
  cases: [
    { prop: 'disease', label: '病' },
    { prop: 'syndrome', label: '证' },
    { prop: 'chief_complaint', label: '主诉' },
    { prop: 'effect', label: '疗效' }
  ],
  tips: [
    { prop: 'category', label: '类别' },
    { prop: 'source', label: '出处' }
  ],
  terms: [
    { prop: 'definition', label: '释义' },
    { prop: 'source', label: '出处' }
  ],
  dulong: [
    { prop: 'guide', label: '引药' },
    { prop: 'section', label: '章节' },
    { prop: 'n', label: '序号' }
  ],
  yifang: [
    { prop: 'category', label: '分类' },
    { prop: 'composition', label: '组成', kind: 'composition' },
    { prop: 'function', label: '功效' },
    { prop: 'source', label: '出处' }
  ]
}

export function formatComposition(composition) {
  if (!Array.isArray(composition)) return composition || ''
  return composition
    .map((c) => {
      if (c && typeof c === 'object') {
        const name = c.name || ''
        const dose = c.dose != null ? String(c.dose) : (c.dosage != null ? String(c.dosage) : '')
        return dose ? `${name} ${dose}` : name
      }
      return String(c)
    })
    .join('、')
}
