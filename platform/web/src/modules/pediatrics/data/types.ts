/** 程氏家传儿科秘要 — 数据模型 */

export interface TextPair {
  /** 原文（据原著整理校订） */
  original: string;
  /** 白话要点 */
  plain: string;
}

export interface JiaJianItem {
  /** 兼证/情况 */
  cond: string;
  /** 加用药物 */
  add: string;
  /** 备注（原著夹注等） */
  note?: string;
}

export interface WanSanItem {
  /** 情形 */
  cond: string;
  /** 丸散名 */
  powder: string;
}

export interface HerbSpec {
  name: string;
  dose: string;
  note?: string;
}

export interface Formula {
  name: string;
  alt?: string;
  usage: string;
  herbs: HerbSpec[];
  decoction?: string;
  source?: string;
}

export interface Syndrome {
  id: string;
  order: number;
  name: string;
  altName?: string;
  /** 六字治法标签 */
  methods: string[];
  /** 一句话提要 */
  summary: string;
  waihou: TextPair;
  bingyin: TextPair;
  shouwen: TextPair;
  maifa: TextPair;
  zhifa: TextPair;
  fangyao: Formula;
  jiajian: JiaJianItem[];
  wansan: WanSanItem[];
  prognosis?: TextPair;
  /** 与急慢惊等症的关系提示 */
  relation?: string;
}

export interface FingerPattern {
  key: string;
  name: string;
  altName?: string;
  /** 形样描述（用于绘图与辨识） */
  shape: string;
  /** 主病 */
  indication: string;
  /** 原著依据 */
  basis: string;
  /** 图形类型（供 SVG 组件选择） */
  kind: string;
  /** 原著原图（从扫描件精确裁取） */
  img?: string;
}

export interface DeathSign {
  name: string;
  sign: string;
  level: '极危' | '危' | '重';
  category: string;
}

export interface HerbTip {
  title: string;
  items: TextPair[];
}

export interface QuizItem {
  id: string;
  category: string;
  type: 'single' | 'multi';
  question: string;
  options: string[];
  answer: number[];
  explain: string;
  source?: string;
}
