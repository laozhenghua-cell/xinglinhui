import type { DeathSign } from './types'

/**
 * 死症四十候 — 原著"死症四十候"（存见三十八候，附注说明）。
 * 又：识症趋避十三则、痢症坏候七则、慢脾风绝候。
 */
export const deathSigns: DeathSign[] = [
  { name: '气绝', sign: '啼泣无声', level: '极危', category: '死症四十候' },
  { name: '脾气坏', sign: '长厥不醒', level: '极危', category: '死症四十候' },
  { name: '肺绝', sign: '鼻孔开张', level: '极危', category: '死症四十候' },
  { name: '气绝', sign: '病久气喘', level: '极危', category: '死症四十候' },
  { name: '肌坏', sign: '久病作肿', level: '危', category: '死症四十候' },
  { name: '肝风证', sign: '鱼口鱼目', level: '危', category: '死症四十候' },
  { name: '骨绝', sign: '干呕无物', level: '极危', category: '死症四十候' },
  { name: '脾绝', sign: '眼眶深陷', level: '极危', category: '死症四十候' },
  { name: '胃死', sign: '唇牙枯白', level: '极危', category: '死症四十候' },
  { name: '水克火', sign: '舌黑如煤', level: '极危', category: '死症四十候' },
  { name: '气绝', sign: '气无出入', level: '极危', category: '死症四十候' },
  { name: '骨烂', sign: '牙齿臭落', level: '极危', category: '死症四十候' },
  { name: '肾绝', sign: '胸陷（原书此条字迹存疑，疑为囟陷）', level: '极危', category: '死症四十候' },
  { name: '肝死脾', sign: '青缠口角', level: '极危', category: '死症四十候' },
  { name: '全阴', sign: '黑掩太阳', level: '极危', category: '死症四十候' },
  { name: '骨绝', sign: '喉如拽锯', level: '极危', category: '死症四十候' },
  { name: '肝心绝', sign: '弄舌抵唇', level: '极危', category: '死症四十候' },
  { name: '肺绝', sign: '急作哑声', level: '极危', category: '死症四十候' },
  { name: '土绝', sign: '吐泻不止', level: '极危', category: '死症四十候' },
  { name: '血绝', sign: '发直如竖', level: '极危', category: '死症四十候' },
  { name: '心坏', sign: '舌肿发惊', level: '极危', category: '死症四十候' },
  { name: '脱液', sign: '病深无泪', level: '危', category: '死症四十候' },
  { name: '肝克胃死', sign: '肚痛无声', level: '极危', category: '死症四十候' },
  { name: '属阴', sign: '面黑无神', level: '极危', category: '死症四十候' },
  { name: '肝血绝', sign: '爪甲青黑', level: '极危', category: '死症四十候' },
  { name: '肝绝', sign: '手常抱头', level: '极危', category: '死症四十候' },
  { name: '胃绝', sign: '唇不盖齿', level: '极危', category: '死症四十候' },
  { name: '胃坏', sign: '人中黑陷', level: '极危', category: '死症四十候' },
  { name: '肝肾绝', sign: '阴囊束缩', level: '极危', category: '死症四十候' },
  { name: '肝胃坏', sign: '饮食撑喉', level: '极危', category: '死症四十候' },
  { name: '脾绝', sign: '头汗手冷', level: '极危', category: '死症四十候' },
  { name: '肾气绝', sign: '目无光彩', level: '极危', category: '死症四十候' },
  { name: '肺坏', sign: '鼻干黑煤', level: '极危', category: '死症四十候' },
  { name: '肺脱', sign: '眼皮反张', level: '极危', category: '死症四十候' },
  { name: '收甚', sign: '肝脉浮大', level: '危', category: '死症四十候' },
  { name: '有收烂', sign: '频泻黑水', level: '危', category: '死症四十候' },
  { name: '气下绝', sign: '肛门如筒', level: '极危', category: '死症四十候' },
  { name: '肝克胃死', sign: '肚痛无声', level: '极危', category: '死症四十候' },
]

export const deathSignsNote =
  '以上坏症皆为死候。小儿病久或急惊症则每有此见，见则不可言吉，须告明在先；但亦要用药挽救，不可坐视不理，以冀其死里回生。' +
  '（注：原著"死症四十候"存见三十八候，存疑。）'

/** 识症趋避（原著"识症趋避"十三条） */
export const shizhengQubi: TextPairLike[] = [
  {
    t: '风热抽掣频作',
    original:
      '风热发搐，人事倦怠、无精神，频频有日作多次者，为风深难治——盖热深厥亦深也，抽掣一次病即深一次。',
  },
  {
    t: '呕吐泻兼作',
    original:
      '凡呕吐泻兼作，久而不止者症必不利，每每吐出宿物不化，与干呕无物症同，俱死候。',
  },
  { t: '脾虚作肿兼喘', original: '脾虚作肿症已深矣，若兼气喘更属难治；身壮病初起肿者轻。' },
  { t: '久病忽喘', original: '久病忽作气喘者难治；惊风重气喘者难治。' },
  { t: '泻痢作肿', original: '泄泻发冷、痢疾作肿者症深。' },
  { t: '肚痛啼不出声', original: '肚痛啼声不出者难治。' },
  { t: '痰喘积久', original: '痰喘积久而不下者难治；久病作肿者亦难治。' },
  { t: '胃口不旺', original: '久病胃口不旺者症甚难治——有胃则生、无胃则死也，必凶。' },
  { t: '热退口烂齿大', original: '热症火虽退而口烂、门牙软大齿者必死。' },
  { t: '药证相反而剧', original: '病是症而服是症之药剂，愈剂愈剧者必不祥，此为缓急相左。' },
  {
    t: '上喘下泻',
    original:
      '上而气喘、下而泄泻不止者为难治——下气定喘则大肠气泄而泄泻愈甚，闭气止泻则气上涌其喘愈甚，两下相碍故难治。然亦以止泻为先。',
  },
  { t: '鼻生黑煤', original: '鼻生黑煤，洗而忽然者难治。此乃新识，至紧。' },
  {
    t: '死症告明',
    original:
      '死症难治必先告明，令其多请高明。如东家深信深求，须尽自己所学而救之，存一片济世心，斯时钱财必不计较，或证转凶为吉，则名与利自不负人也。然必先告明生死无妨方可下手，先脱干系自不妨事。切勿见危而不救，则非存心济世者矣；勿苟且应酬、顺情了事，症候好丑勿轻言不妨，以图侥幸。',
  },
]

export interface TextPairLike {
  t: string
  original: string
  plain?: string
}

/** 痢症坏候（原著"痢症坏候"） */
export const lizhengHuaihou: TextPairLike[] = [
  { t: '色败', original: '便痢纯清血色：鲜者顺，色败者逆。' },
  { t: '色黑如泥', original: '日久色黑如泥者逆（红变深）。' },
  { t: '色如鱼脑', original: '色如鱼脑者逆（白变深）。' },
  { t: '色如屋尘', original: '色如屋上尘者逆（黄变深）。' },
  {
    t: '脱肛',
    original: '日久脱肛：有皱纹症尚缓，元气尚有也；无皱纹如筒者逆，元气败也。',
  },
  { t: '作肿', original: '日久面、目、手及肚腹作肿者逆。' },
  {
    t: '能食有神',
    original:
      '不论病之新久、症之顺逆，而人能吃饭有神者尚有指望——胃气不减、元气未失也。',
  },
]

/** 慢脾风绝候（并入死候判定） */
export const manpiJuehou = {
  original:
    '慢脾风第一危急之候：一味呕吐、泄泻白屎汤不止，手足常冷无温，闭目亡魂，唇色淡白，不饮食，不语；汗出而滑、身冷气长吁者无望；脉浮泛无力、脉息离乱、数到十余至、重按则无者，此散脉也，难望有生。',
  plain: '慢脾风出现呕泻不止、手足冷、闭目失神、冷汗身冷、散脉者，为脾绝之候，须立即抢救并告知家属。',
}
