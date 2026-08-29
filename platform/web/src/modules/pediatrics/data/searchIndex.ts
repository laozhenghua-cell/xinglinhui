/**
 * 全文检索索引 — 聚合全书结构化数据（八症、方剂、纹形、诊法、用药、
 * 死候、训诫、推拿、医案、三症、题库等），供站内即时搜索。
 */
import { syndromes, liuziShuo, songs, bazhengZonglun } from './syndromes'
import { fingerPatterns, shouwenFa, qiemaiFa, kanwaizhengFa, wenzhenFa, shouwenMaiwei, faceRegions, wuzangDingli, wuyunLiuqi } from './fingerPatterns'
import { guanfangYanfang, sanzhengFang, wansanList, waizhiFa } from './formulas'
import { deathSigns, shizhengQubi, lizhengHuaihou, manpiJuehou } from './deathSigns'
import { drugTips, yaoxingFu } from './drugTips'
import { tuinaDaiyaoFu, mianxueTuifa, tanbingFa, shoufaGejue, denghuoJiu } from './tuina'
import { yanzhengLunzhi, chengxianYixun, jiuHen, shisanBukeXue, shiZhuan, jingwenYijiao, guanmenShazei, genghuanYaowei, kanbingMijue } from './maxims'
import { yianList } from './yian'
import { nuejiLunzhi, shuzhengLunzhi, chushengBianzhi } from './misc'
import { quizBank } from './quiz'

export interface SearchRecord {
  id: string
  cat: string
  title: string
  text: string
  route: string
  keywords: string
}

export const searchIndex: SearchRecord[] = []

function add(cat: string, title: string, text: string, route: string, keywords = '') {
  searchIndex.push({ id: `${cat}-${searchIndex.length}`, cat, title, text, route, keywords })
}

// 八症
for (const s of syndromes) {
  add(
    '八症',
    `${s.name}${s.altName ? '（' + s.altName + '）' : ''} · ${s.methods.join('')}`,
    `${s.summary}\n外候：${s.waihou.original}\n病因：${s.bingyin.original}\n手纹：${s.shouwen.original}\n脉法：${s.maifa.original}\n治法：${s.zhifa.original}\n方药：${s.fangyao.name} ${s.fangyao.herbs.map((h) => h.name + h.dose).join('、')}\n加减：${s.jiajian.map((j) => j.cond + '→' + j.add).join('；')}`,
    '/bazheng',
    `${s.name} ${s.altName ?? ''} ${s.methods.join(' ')} ${s.fangyao.herbs.map((h) => h.name).join(' ')}`
  )
}
add('总论', '释八症六字说', liuziShuo.original + liuziShuo.closing, '/zonglun', '八症 六字 平肝 补脾 泻心')
add('总论', '八症总论', bazhengZonglun.original, '/zonglun')
for (const sg of songs) add('歌诀', sg.title, sg.text + sg.note, '/zonglun', sg.title)

// 诊法
add('诊法', '诊手纹法', shouwenFa.original + shouwenFa.combined + shouwenFa.note, '/zonglun', '指纹 浮沉 青紫 淡滞 三关 风关 气关 命关')
add('诊法', '切脉法', qiemaiFa.original, '/zonglun', '脉 浮沉 迟数 滑紧 有力 无力')
add('诊法', '看外症法', kanwaizhengFa.original, '/zonglun', '望诊 唇 鼻 眼 舌 耳背 头发 肚皮 肾囊')
add('诊法', '问诊法', wenzhenFa.original, '/zonglun', '热型 二便 泻色 渴饮 潮热')
add('诊法', '小儿手纹脉位图', shouwenMaiwei.original + shouwenMaiwei.right.join(' ') + shouwenMaiwei.left.join(' '), '/tupu', '脉位 寸关尺 三关')

// 十八纹形
for (const p of fingerPatterns) {
  add('纹形', `${p.name}${p.altName ? '（' + p.altName + '）' : ''}`, `${p.shape} ${p.indication} ${p.basis}`, '/tupu', `${p.name} 指纹 纹形`)
}

// 面部与脏腑
add('望诊', '小儿面部属位图', faceRegions.original + faceRegions.miaoqiao.join('；'), '/tupu', '面部 额心 鼻脾 左颊肝 右颊肺 颏肾 五色 苗窍')
for (const w of wuzangDingli) add('望诊', `五脏主病定例·${w.organ}${w.governs}`, w.signs, '/tupu', w.organ + w.governs)
add('杂录', '司天歌', wuyunLiuqi.siga.text + wuyunLiuqi.siga.note, '/tupu', '五运六气 司天 在泉')
add('杂录', '天干合脏腑相属歌', wuyunLiuqi.tiangan, '/tupu', '天干 脏腑')
add('杂录', '脏腑表里', wuyunLiuqi.biaoli, '/tupu', '表里 心小肠 肝胆 脾胃 肺大肠 肾膀胱')

// 方剂
for (const f of [...guanfangYanfang, ...sanzhengFang]) {
  add(
    '方剂',
    `${f.name}（${f.category}）`,
    `${f.gongyong}\n${f.usage}\n组成：${f.herbs.map((h) => h.name + (h.dose ? h.dose : '') + (h.note ? '（' + h.note + '）' : '')).join('、')}${f.jiawei ? '\n加减：' + f.jiawei.map((j) => j.cond + '→' + j.add).join('；') : ''}`,
    '/fangji',
    f.name + ' ' + f.herbs.map((h) => h.name).join(' ')
  )
}
for (const w of wansanList) add('方剂', `丸散·${w.name}`, `${w.usage} ${w.note}`, '/fangji', w.name)
for (const w of waizhiFa) add('方剂', `外治·${w.name}`, w.method + w.note, '/fangji', w.name + ' 灯火 艾灸 贴脐')

// 用药
for (const tip of drugTips) {
  for (const it of tip.items) {
    add('用药', `${tip.title.replace(/^[一二三四五六七]、/, '')}`, it.original + it.plain, '/yongyao', '')
  }
}
add('用药', '药性赋幼科摘要', yaoxingFu.sections.map((s) => s.title + '：' + s.text).join('\n'), '/yongyao', '药性 寒热温平')

// 危候
for (const d of deathSigns) add('危候', `死症·${d.name}：${d.sign}`, `${d.name} ${d.sign}（${d.level}）`, '/weihou', d.name + d.sign)
for (const q of shizhengQubi) add('危候', `识症趋避·${q.t}`, q.original, '/weihou', q.t)
for (const l of lizhengHuaihou) add('危候', `痢症坏候·${l.t}`, l.original, '/weihou', l.t)
add('危候', '慢脾风绝候', manpiJuehou.original + manpiJuehou.plain, '/weihou', '慢脾风 死候')

// 训诫
for (const y of yanzhengLunzhi) add('训诫', `言症论治·${y.t}`, y.original + y.plain, '/xunjie', y.t)
for (const x of chengxianYixun.items) add('训诫', `承先遗训·${x.t}`, x.original, '/xunjie', x.t)
for (const h of jiuHen.items) add('训诫', h.t, h.original, '/xunjie', '九恨')
for (const s of shisanBukeXue.items) add('训诫', `十三不可学·${s}`, s, '/xunjie', '十三不可学')
for (const c of shiZhuan.items) add('训诫', c.t, c.original, '/xunjie', '十传')
add('训诫', '摹看手指筋纹乃医家异教说', jingwenYijiao.original + jingwenYijiao.plain, '/xunjie', '指纹 异教')
for (const g of guanmenShazei) add('训诫', g.title, g.original, '/xunjie', '关门杀贼 开门揖盗')
add('训诫', '汤方内更换药味说', genghuanYaowei.original, '/xunjie', '汤头 加减')
add('训诫', '看病秘诀', kanbingMijue.original, '/xunjie', '望色 苗窍')

// 推拿
add('推拿', '推拿代药赋', tuinaDaiyaoFu.original + tuinaDaiyaoFu.plain, '/tuina', '推拿 代药 三关 六腑')
add('推拿', '面各穴图推法', mianxueTuifa.original + mianxueTuifa.plain, '/tuina', '天庭 眉心 太阳 太阴 承浆')
add('推拿', '探病法', tanbingFa.original + tanbingFa.plain, '/tuina', '十指 三指按额')
for (const g of shoufaGejue) add('推拿', `手法·${g.title}`, g.text, '/tuina', g.title)
for (const d of denghuoJiu) add('推拿', `灯火灸·${d.name}`, d.usage, '/tuina', d.name)

// 三症与幼科铁镜
add('三症', '疟疾论治', nuejiLunzhi.original + nuejiLunzhi.signs + nuejiLunzhi.prognosis, '/fangji', '疟疾 小柴胡 补中益气')
add('三症', '暑症论治', shuzhengLunzhi.original + shuzhengLunzhi.plain, '/fangji', '暑 香薷饮 六和汤 霍乱转筋')
for (const c of chushengBianzhi) add('附编', c.title, c.original + c.plain, '/xunjie', c.title)

// 医案
for (const y of yianList) {
  add('医案', `${y.title}（${y.category}）`, `${y.original}\n${y.yanyu}\n${y.plain}${y.formulas.length ? '\n用方：' + y.formulas.join('、') : ''}`, '/yian', `${y.title} ${y.category} ${y.formulas.join(' ')}`)
}

// 题库
for (const q of quizBank) {
  add('题库', `${q.category}·${q.question}`, `${q.options.join('；')}\n解：${q.explain}`, '/zice', q.question)
}

/** 搜索：标题/正文/关键词包含任一查询词（空格分词，全部命中） */
export function doSearch(query: string, limit = 60): SearchRecord[] {
  const terms = query.trim().split(/\s+/).filter(Boolean)
  if (!terms.length) return []
  const out: { rec: SearchRecord; score: number }[] = []
  for (const rec of searchIndex) {
    const title = rec.title.toLowerCase()
    const text = rec.text.toLowerCase()
    const kw = rec.keywords.toLowerCase()
    let score = 0
    let hitAll = true
    for (const t of terms) {
      const tl = t.toLowerCase()
      let s = 0
      if (title.includes(tl)) s += 8
      if (kw.includes(tl)) s += 6
      if (text.includes(tl)) s += 2
      if (s === 0) {
        hitAll = false
        break
      }
      score += s
    }
    if (hitAll) out.push({ rec, score })
  }
  out.sort((a, b) => b.score - a.score)
  return out.slice(0, limit).map((o) => o.rec)
}

export const searchCategories = [...new Set(searchIndex.map((r) => r.cat))]
