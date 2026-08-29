// 四诊分类症状库(通用十问式 + 儿科原版四步采集)
// 结构:{ section: '望/闻/问/切', groups: [{ name, field: 'tongue|pulse|local|systemic|symptoms|detail', items: [label,...] }] }

const GENERAL = [
  {
    section: '望诊',
    groups: [
      { name: '舌质', field: 'tongue', items: ['舌淡红', '舌淡白', '舌红', '舌绛', '舌紫暗', '舌有瘀斑', '舌胖大', '舌瘦薄', '舌有齿痕', '舌有裂纹', '舌生芒刺'] },
      { name: '舌苔', field: 'tongue', items: ['苔薄白', '苔白', '苔白腻', '苔黄', '苔黄腻', '苔灰黑', '苔少', '无苔', '苔剥落', '苔燥', '苔滑'] },
      { name: '面色神态', field: 'systemic', items: ['面色红赤', '面色苍白', '面色萎黄', '面色青灰', '面垢', '烦躁不安', '神疲乏力', '嗜睡', '神昏', '目赤', '口唇青紫'] },
    ],
  },
  {
    section: '闻诊',
    groups: [
      { name: '声音气味', field: 'systemic', items: ['口臭', '口气酸腐', '咳声重浊', '喉中痰鸣', '呼吸气促', '肠鸣漉漉', '矢气臭秽', '嗳气酸腐'] },
    ],
  },
  {
    section: '问诊',
    groups: [
      { name: '寒热', field: 'symptoms', items: ['发热', '恶寒', '恶风', '寒热往来', '午后潮热', '五心烦热', '畏寒肢冷', '壮热', '低热不退'] },
      { name: '汗', field: 'symptoms', items: ['自汗', '盗汗', '无汗', '汗出热不解', '冷汗淋漓', '头汗出', '手足心汗'] },
      { name: '疼痛', field: 'symptoms', items: ['头痛', '头晕', '腹痛', '胁痛', '腰痛', '胀痛', '刺痛', '隐痛', '冷痛', '灼痛', '绞痛', '游走痛', '疼痛拒按', '疼痛喜按', '痛有定处'] },
      { name: '饮食口味', field: 'symptoms', items: ['纳差', '纳呆', '消谷善饥', '口渴', '口不渴', '口苦', '口淡', '口甜', '喜冷饮', '喜热饮', '恶心', '呕吐', '吞酸'] },
      { name: '二便', field: 'symptoms', items: ['便秘', '大便干结', '便溏', '泄泻', '完谷不化', '便血鲜红', '便血暗红', '黏液便', '里急后重', '肛门灼热', '小便短赤', '小便清长', '小便频数', '夜尿多'] },
      { name: '睡眠情志', field: 'symptoms', items: ['失眠', '多梦', '易醒', '烦躁易怒', '善太息', '心悸', '健忘', '夜啼', '惊惕不安'] },
    ],
  },
  {
    section: '切诊',
    groups: [
      { name: '脉象', field: 'pulse', items: ['脉浮', '脉沉', '脉迟', '脉数', '脉滑', '脉涩', '脉弦', '脉紧', '脉细', '脉弱', '脉洪', '脉濡', '脉缓', '脉结代', '脉芤'] },
    ],
  },
]

// 专科局部体征(按专科补充到"望诊")
const LOCAL_EXTRA = {
  surgery: [
    { name: '疮疡局部', field: 'local', items: ['局部红肿', '漫肿无头', '疮顶高突', '疮顶塌陷', '粟粒样脓头', '根盘紧束', '根脚散漫', '灼热', '化脓', '波动感', '溃烂', '脓水稀薄', '脓水稠厚', '腐肉不脱', '窦道形成', '周围淋巴结肿大'] },
  ],
  anorectal: [
    { name: '肛肠局部', field: 'local', items: ['肛门脱出', '肛门水肿', '肛缘皮赘', '肛裂', '瘘口流脓', '肛周红肿', '肛周硬结', '肛门瘙痒', '肛门潮湿', '肛门疼痛', '便后滴血', '喷射状出血', '肛内有物脱出'] },
  ],
  alchemy: [
    { name: '疮面(丹药外治)', field: 'local', items: ['疮面腐肉', '疮面新肉不生', '疮面出血', '疮面疼痛', '周围红肿', '分泌物多', '疮面不敛', '管壁僵硬'] },
  ],
}

export function buildCategories(specialty = '') {
  const cats = JSON.parse(JSON.stringify(GENERAL))
  if (specialty && LOCAL_EXTRA[specialty]) {
    cats[0].groups.push(...LOCAL_EXTRA[specialty])
  }
  return cats
}

// 儿科:复用《程氏家传儿科秘要》原版四步采集
export function buildPediatricCategories() {
  // 动态导入儿科引擎的 findingGroups
  return import('@/modules/pediatrics/engine/diagnosis').then((m) => {
    const steps = m.findingGroups || []
    const cats = []
    for (const st of steps) {
      const section = st.name || st.step
      const groups = (st.groups || []).map((g) => ({
        name: g.name,
        field: st.step === 'mai' ? 'pulse' : st.step === 'wen' ? 'symptoms' : st.step === 'shouwen' ? 'local' : 'systemic',
        items: (g.findings || []).map((f) => f.label),
      }))
      cats.push({ section, groups })
    }
    return cats
  })
}
