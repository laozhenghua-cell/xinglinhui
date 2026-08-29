"""多辨证体系引擎:八纲 / 六经 / 卫气营血 并行对照。

输入:用户四诊标签(中文词) → 输出各体系得分与证据(指标词命中)。
规则数据:app/data/diagnosis_systems.json(经典提纲归纳)。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

_DATA: Optional[dict] = None


def _load() -> dict:
    global _DATA
    if _DATA is None:
        p = Path(__file__).resolve().parent.parent / "data" / "diagnosis_systems.json"
        _DATA = json.loads(p.read_text(encoding="utf-8"))
    return _DATA


def _bigrams(text: str, cap: int = 40) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    grams = [text[i : i + 2] for i in range(len(text) - 1)]
    seen, out = set(), []
    for g in grams:
        if g not in seen:
            seen.add(g)
            out.append(g)
        if len(out) >= cap:
            break
    return out


STOP_BIGRAMS = {"大便", "小便", "腹部", "口渴", "腹痛"}

# 整体性二便术语:内部 bigram(如"自利")不应误命中其他证型
BOWEL_NEUTRAL = {
    "小便自利", "大便自利", "二便自利",
    "小便自调", "大便自调", "二便自调",
    "小便正常", "大便正常", "二便正常",
}

# 六经提纲锚点:得分并列时提纲词优先(如太少两感之"但欲寐")
LIUJING_ANCHORS = {
    "但欲寐": "shaoyin", "往来寒热": "shaoyang", "头项强痛": "taiyang",
    "胃家实": "yangming", "气上撞心": "jueyin", "消渴": "jueyin", "时腹自痛": "taiyin",
}

_SYS_ORDER = ("bagang", "liujing", "weiqiyingxue", "zangfu", "sanjiao", "jingluo")
_SYS_NAME = {"bagang": "八纲", "liujing": "六经", "weiqiyingxue": "卫气营血", "zangfu": "脏腑", "sanjiao": "三焦", "jingluo": "经络"}

# 体系间结论对照表(交叉印证):(体系A, 结论A, 体系B, 结论B) 视为互洽
_ALIGN = {
    # 脏腑 ↔ 六经
    ("zangfu", "肝气郁结", "liujing", "少阳病"), ("zangfu", "肝火上炎", "liujing", "少阳病"),
    ("zangfu", "肝阳上亢", "liujing", "厥阴病"), ("zangfu", "心火亢盛", "liujing", "少阴病"),
    ("zangfu", "脾气虚", "liujing", "太阴病"), ("zangfu", "脾阳虚", "liujing", "太阴病"),
    ("zangfu", "寒湿困脾", "liujing", "太阴病"), ("zangfu", "风寒束肺", "liujing", "太阳病"),
    ("zangfu", "风热犯肺", "liujing", "太阳病"), ("zangfu", "肾阳虚", "liujing", "少阴病"),
    ("zangfu", "肾阴虚", "liujing", "少阴病"), ("zangfu", "胃热炽盛", "liujing", "阳明病"),
    ("zangfu", "胃阴虚", "liujing", "阳明病"), ("zangfu", "胆郁痰扰", "liujing", "少阳病"),
    ("zangfu", "大肠湿热", "liujing", "阳明病"), ("zangfu", "膀胱湿热", "liujing", "太阳病"),
    # 脏腑 ↔ 经络(本经)
    ("zangfu", "肝气郁结", "jingluo", "足厥阴肝经"), ("zangfu", "肝火上炎", "jingluo", "足厥阴肝经"),
    ("zangfu", "肝阳上亢", "jingluo", "足厥阴肝经"), ("zangfu", "肝血虚", "jingluo", "足厥阴肝经"),
    ("zangfu", "肝风内动", "jingluo", "足厥阴肝经"), ("zangfu", "心气虚", "jingluo", "手少阴心经"),
    ("zangfu", "心血虚", "jingluo", "手少阴心经"), ("zangfu", "心火亢盛", "jingluo", "手少阴心经"),
    ("zangfu", "心血瘀阻", "jingluo", "手少阴心经"), ("zangfu", "脾气虚", "jingluo", "足太阴脾经"),
    ("zangfu", "脾阳虚", "jingluo", "足太阴脾经"), ("zangfu", "寒湿困脾", "jingluo", "足太阴脾经"),
    ("zangfu", "湿热蕴脾", "jingluo", "足太阴脾经"), ("zangfu", "肺气虚", "jingluo", "手太阴肺经"),
    ("zangfu", "肺阴虚", "jingluo", "手太阴肺经"), ("zangfu", "风寒束肺", "jingluo", "手太阴肺经"),
    ("zangfu", "风热犯肺", "jingluo", "手太阴肺经"), ("zangfu", "痰热壅肺", "jingluo", "手太阴肺经"),
    ("zangfu", "痰湿阻肺", "jingluo", "手太阴肺经"), ("zangfu", "肾阳虚", "jingluo", "足少阴肾经"),
    ("zangfu", "肾阴虚", "jingluo", "足少阴肾经"), ("zangfu", "肾精不足", "jingluo", "足少阴肾经"),
    ("zangfu", "肾不纳气", "jingluo", "足少阴肾经"), ("zangfu", "胃热炽盛", "jingluo", "足阳明胃经"),
    ("zangfu", "胃寒", "jingluo", "足阳明胃经"), ("zangfu", "食滞胃脘", "jingluo", "足阳明胃经"),
    ("zangfu", "胃阴虚", "jingluo", "足阳明胃经"), ("zangfu", "胆郁痰扰", "jingluo", "足少阳胆经"),
    ("zangfu", "大肠湿热", "jingluo", "手阳明大肠经"), ("zangfu", "膀胱湿热", "jingluo", "足太阳膀胱经"),
    # 六经 ↔ 经络
    ("liujing", "太阳病", "jingluo", "足太阳膀胱经"), ("liujing", "太阳病", "jingluo", "手太阴肺经"),
    ("liujing", "阳明病", "jingluo", "足阳明胃经"), ("liujing", "少阳病", "jingluo", "足少阳胆经"),
    ("liujing", "少阳病", "jingluo", "足厥阴肝经"), ("liujing", "太阴病", "jingluo", "足太阴脾经"),
    ("liujing", "少阴病", "jingluo", "足少阴肾经"), ("liujing", "少阴病", "jingluo", "手少阴心经"),
    ("liujing", "厥阴病", "jingluo", "足厥阴肝经"), ("liujing", "厥阴病", "jingluo", "手厥阴心包经"),
    # 卫气营血 ↔ 三焦 / 脏腑 / 六经
    ("weiqiyingxue", "卫分证", "sanjiao", "邪犯肺卫"), ("weiqiyingxue", "气分证", "sanjiao", "阳明燥热"),
    ("weiqiyingxue", "气分证", "sanjiao", "阳明腑实"), ("weiqiyingxue", "气分证", "sanjiao", "邪热壅肺"),
    ("weiqiyingxue", "气分证", "sanjiao", "太阴湿热"), ("weiqiyingxue", "营分证", "sanjiao", "热陷心包"),
    ("weiqiyingxue", "卫分证", "zangfu", "风热犯肺"), ("weiqiyingxue", "气分证", "zangfu", "痰热壅肺"),
    ("weiqiyingxue", "气分证", "zangfu", "胃热炽盛"), ("weiqiyingxue", "卫分证", "liujing", "太阳病"),
    ("weiqiyingxue", "卫分证", "jingluo", "手太阴肺经"), ("weiqiyingxue", "卫分证", "zangfu", "风寒束肺"),
    ("weiqiyingxue", "营分证", "zangfu", "心火亢盛"), ("liujing", "少阴病", "weiqiyingxue", "营分证"),
    ("weiqiyingxue", "营分证", "jingluo", "手少阴心经"),
    # 三焦 ↔ 脏腑 / 经络 / 六经
    ("sanjiao", "邪犯肺卫", "zangfu", "风热犯肺"), ("sanjiao", "邪犯肺卫", "zangfu", "风寒束肺"),
    ("sanjiao", "邪热壅肺", "zangfu", "痰热壅肺"), ("sanjiao", "肾阴耗损", "zangfu", "肾阴虚"),
    ("sanjiao", "虚风内动", "zangfu", "肝风内动"), ("sanjiao", "太阴湿热", "zangfu", "湿热蕴脾"),
    ("sanjiao", "阳明燥热", "zangfu", "胃热炽盛"),
    ("sanjiao", "邪犯肺卫", "jingluo", "手太阴肺经"), ("sanjiao", "邪热壅肺", "jingluo", "手太阴肺经"),
    ("sanjiao", "热陷心包", "jingluo", "手厥阴心包经"), ("sanjiao", "阳明燥热", "jingluo", "足阳明胃经"),
    ("sanjiao", "阳明腑实", "jingluo", "足阳明胃经"), ("sanjiao", "太阴湿热", "jingluo", "足太阴脾经"),
    ("sanjiao", "肾阴耗损", "jingluo", "足少阴肾经"), ("sanjiao", "虚风内动", "jingluo", "足厥阴肝经"),
    ("sanjiao", "阳明燥热", "liujing", "阳明病"), ("sanjiao", "阳明腑实", "liujing", "阳明病"),
    ("sanjiao", "邪犯肺卫", "liujing", "太阳病"),
    # 八纲 ↔ 各体系(八纲侧取 components 标签)
    ("bagang", "表证", "liujing", "太阳病"), ("bagang", "里证", "liujing", "阳明病"),
    ("bagang", "里证", "liujing", "太阴病"), ("bagang", "里证", "liujing", "少阴病"),
    ("bagang", "里证", "liujing", "厥阴病"), ("bagang", "热证", "liujing", "阳明病"),
    ("bagang", "热证", "liujing", "少阴病"), ("bagang", "寒证", "liujing", "太阴病"),
    ("bagang", "寒证", "liujing", "少阴病"), ("bagang", "虚证", "liujing", "太阴病"),
    ("bagang", "虚证", "liujing", "少阴病"), ("bagang", "实证", "liujing", "阳明病"),
    ("bagang", "实证", "liujing", "少阳病"), ("bagang", "阴证", "liujing", "太阴病"),
    ("bagang", "阴证", "liujing", "少阴病"), ("bagang", "阳证", "liujing", "太阳病"),
    ("bagang", "阳证", "liujing", "阳明病"),
    ("bagang", "表证", "weiqiyingxue", "卫分证"), ("bagang", "里证", "weiqiyingxue", "气分证"),
    ("bagang", "里证", "weiqiyingxue", "营分证"), ("bagang", "里证", "weiqiyingxue", "血分证"),
    ("bagang", "热证", "weiqiyingxue", "气分证"), ("bagang", "热证", "weiqiyingxue", "营分证"),
    ("bagang", "热证", "weiqiyingxue", "血分证"),
    ("bagang", "表证", "zangfu", "风寒束肺"), ("bagang", "表证", "zangfu", "风热犯肺"),
    ("bagang", "寒证", "zangfu", "风寒束肺"), ("bagang", "热证", "zangfu", "风热犯肺"),
    ("bagang", "热证", "zangfu", "心火亢盛"), ("bagang", "热证", "zangfu", "肝火上炎"),
    ("bagang", "热证", "zangfu", "胃热炽盛"), ("bagang", "热证", "zangfu", "痰热壅肺"),
    ("bagang", "热证", "zangfu", "热陷心包"), ("bagang", "热证", "zangfu", "大肠湿热"),
    ("bagang", "热证", "zangfu", "膀胱湿热"), ("bagang", "热证", "zangfu", "湿热蕴脾"),
    ("bagang", "寒证", "zangfu", "脾阳虚"), ("bagang", "寒证", "zangfu", "肾阳虚"),
    ("bagang", "寒证", "zangfu", "胃寒"), ("bagang", "寒证", "zangfu", "寒湿困脾"),
    ("bagang", "虚证", "zangfu", "脾气虚"), ("bagang", "虚证", "zangfu", "肺气虚"),
    ("bagang", "虚证", "zangfu", "心气虚"), ("bagang", "虚证", "zangfu", "心血虚"),
    ("bagang", "虚证", "zangfu", "肝血虚"), ("bagang", "虚证", "zangfu", "肾阳虚"),
    ("bagang", "虚证", "zangfu", "肾阴虚"), ("bagang", "虚证", "zangfu", "肾精不足"),
    ("bagang", "虚证", "zangfu", "肺阴虚"), ("bagang", "虚证", "zangfu", "胃阴虚"),
    ("bagang", "虚证", "zangfu", "脾阳虚"), ("bagang", "实证", "zangfu", "肝气郁结"),
    ("bagang", "实证", "zangfu", "肝火上炎"), ("bagang", "实证", "zangfu", "肝风内动"),
    ("bagang", "实证", "zangfu", "心火亢盛"), ("bagang", "实证", "zangfu", "心血瘀阻"),
    ("bagang", "实证", "zangfu", "痰热壅肺"), ("bagang", "实证", "zangfu", "痰湿阻肺"),
    ("bagang", "实证", "zangfu", "寒湿困脾"), ("bagang", "实证", "zangfu", "湿热蕴脾"),
    ("bagang", "实证", "zangfu", "胃热炽盛"), ("bagang", "实证", "zangfu", "食滞胃脘"),
    ("bagang", "实证", "zangfu", "大肠湿热"), ("bagang", "实证", "zangfu", "膀胱湿热"),
    ("bagang", "阴证", "zangfu", "肾阳虚"), ("bagang", "阴证", "zangfu", "脾阳虚"),
    ("bagang", "阴证", "zangfu", "肾阴虚"), ("bagang", "阴证", "zangfu", "肺阴虚"),
    ("bagang", "阴证", "zangfu", "胃阴虚"), ("bagang", "阳证", "zangfu", "心火亢盛"),
    ("bagang", "阳证", "zangfu", "肝火上炎"), ("bagang", "阳证", "zangfu", "胃热炽盛"),
    ("bagang", "表证", "sanjiao", "邪犯肺卫"), ("bagang", "里证", "sanjiao", "阳明燥热"),
    ("bagang", "里证", "sanjiao", "阳明腑实"), ("bagang", "里证", "sanjiao", "太阴湿热"),
    ("bagang", "里证", "sanjiao", "肾阴耗损"), ("bagang", "里证", "sanjiao", "虚风内动"),
    ("bagang", "热证", "sanjiao", "阳明燥热"), ("bagang", "热证", "sanjiao", "阳明腑实"),
    ("bagang", "热证", "sanjiao", "热陷心包"), ("bagang", "虚证", "sanjiao", "肾阴耗损"),
    ("bagang", "虚证", "sanjiao", "虚风内动"), ("bagang", "阳证", "sanjiao", "热陷心包"),
    ("bagang", "表证", "jingluo", "手太阴肺经"), ("bagang", "里证", "jingluo", "足少阴肾经"),
    ("bagang", "里证", "jingluo", "足太阴脾经"), ("bagang", "里证", "jingluo", "足阳明胃经"),
    ("bagang", "里证", "jingluo", "手少阴心经"), ("bagang", "里证", "jingluo", "足厥阴肝经"),
    ("bagang", "里证", "jingluo", "足太阳膀胱经"), ("bagang", "里证", "jingluo", "手阳明大肠经"),
    ("bagang", "里证", "jingluo", "手厥阴心包经"), ("bagang", "实证", "jingluo", "足厥阴肝经"),
    ("bagang", "热证", "jingluo", "手少阴心经"), ("bagang", "热证", "jingluo", "足阳明胃经"),
    ("bagang", "寒证", "jingluo", "足少阴肾经"), ("bagang", "虚证", "jingluo", "足少阴肾经"),
}


def _pair_covered(a_key: str, b_key: str) -> bool:
    return any((x[0] == a_key and x[2] == b_key) or (x[0] == b_key and x[2] == a_key) for x in _ALIGN)


def _pair_aligned(a_key: str, a_val: str, b_key: str, b_val: str) -> bool:
    return (a_key, a_val, b_key, b_val) in _ALIGN or (b_key, b_val, a_key, a_val) in _ALIGN


def _consistency(out: dict[str, Any]) -> dict[str, Any]:
    """六体系结论交叉印证:按对照表计算一致性评分。"""
    active = {k: out[k]["summary"] for k in _SYS_ORDER if out[k]["summary"] != "信息不足"}
    comps = out["bagang"]["components"] if "bagang" in active else []
    pairs_out, checked, aligned = [], 0, 0
    for i in range(len(_SYS_ORDER)):
        for j in range(i + 1, len(_SYS_ORDER)):
            a, b = _SYS_ORDER[i], _SYS_ORDER[j]
            if a not in active or b not in active:
                continue
            if not _pair_covered(a, b):
                continue
            checked += 1
            ok = _pair_aligned(a, active[a], b, active[b])
            if not ok and a == "bagang":
                ok = any(_pair_aligned("bagang", c, b, active[b]) for c in comps)
            if not ok and b == "bagang":
                ok = any(_pair_aligned(a, active[a], "bagang", c) for c in comps)
            if ok:
                aligned += 1
            pairs_out.append(f"{_SYS_NAME[a]}↔{_SYS_NAME[b]}:{active[a]}↔{active[b]}{'✓' if ok else '✗'}")
    score = round(aligned / checked, 2) if checked else None
    if score is None:
        verdict = "体系对照库未覆盖该组合"
    elif score >= 0.99:
        verdict = "六体系结论高度互洽"
    elif score >= 0.6:
        verdict = "基本互洽"
    elif score >= 0.3:
        verdict = "部分互洽,存在分歧"
    else:
        verdict = "体系间结论不一致,建议复核"
    return {"score": score, "pairs": pairs_out, "verdict": verdict}


def _dynamic(out: dict[str, Any]) -> dict[str, Any]:
    """动态推理:六经合病/并病、卫气营血同病、三焦传变。"""
    dyn: dict[str, Any] = {"liujing_merge": [], "weiqi_merge": [], "sanjiao_trans": None}
    # 1) 六经合病/并病
    top = [t for t in out["liujing"]["top"] if t["score"] > 0]
    if len(top) >= 2 and top[0]["score"] >= 2:
        m = [top[0]]
        for t in top[1:]:
            if t["score"] >= 2 and t["score"] >= 0.5 * top[0]["score"]:
                m.append(t)
        if len(m) >= 2:
            order = {"taiyang": 0, "yangming": 1, "shaoyang": 2, "taiyin": 3, "shaoyin": 4, "jueyin": 5}
            m.sort(key=lambda t: order.get(t["key"], 9))
            if len(m) == 3 and all(t["key"] in ("taiyang", "yangming", "shaoyang") for t in m):
                label = "三阳合病"
            else:
                label = "".join(t["name"].replace("病", "") for t in m[:2]) + "合病"
            dyn["liujing_merge"].append({
                "label": label,
                "evidence": [f"{t['name']}({t['score']}分)" for t in m],
                "note": "两经(或三经)证候同时并见为合病;一经未罢又见他经为并病,须结合病程先后。",
            })
    # 2) 卫气营血同病
    scores = {t["key"]: t["score"] for t in out["weiqiyingxue"]["top"]}
    names = {t["key"]: t["name"] for t in out["weiqiyingxue"]["top"]}
    act = {k: v for k, v in scores.items() if v >= 2}
    for a, b, label in (("wei", "qi", "卫气同病"), ("qi", "ying", "气营两燔"), ("ying", "xue", "营血并见"), ("qi", "xue", "气血两燔")):
        if a in act and b in act:
            dyn["weiqi_merge"].append({
                "label": label,
                "evidence": [f"{names[a]}({act[a]}分)", f"{names[b]}({act[b]}分)"],
            })
    # 3) 三焦传变
    groups = {"上焦": ["sj_weifan", "sj_feire", "sj_xinbao"], "中焦": ["sj_ym_jing", "sj_ym_fu", "sj_ty_shi"], "下焦": ["sj_shenyin", "sj_xufeng"]}
    hit: dict[str, int] = {}
    for jiao, keys in groups.items():
        ss = [t["score"] for t in out["sanjiao"]["top"] if t["key"] in keys]
        if ss and max(ss) >= 2:
            hit[jiao] = max(ss)
    stage, hint = None, None
    if hit:
        top1 = out["sanjiao"]["top"][0]["key"] if out["sanjiao"]["top"] else ""
        if top1 == "sj_xinbao":
            stage, hint = "邪陷心包(逆传)", "肺卫之邪不解,径入心包,病情重笃"
        elif {"上焦", "中焦", "下焦"} <= set(hit):
            stage, hint = "三焦俱病", "上中下三焦同病,邪势弥漫"
        elif "上焦" in hit and "中焦" in hit:
            stage, hint = "上焦→中焦(顺传)", "邪由肺卫入里,病势深入阳明/太阴"
        elif "中焦" in hit and "下焦" in hit:
            stage, hint = "中焦→下焦", "邪入下焦,肝肾真阴被灼"
        elif "上焦" in hit and "下焦" in hit:
            stage, hint = "上焦直趋下焦", "不经中焦,径入下焦"
        elif "上焦" in hit:
            stage, hint = "病在上焦", "邪在肺卫"
        elif "中焦" in hit:
            stage, hint = "病在中焦", "邪在阳明/太阴"
        else:
            stage, hint = "病在下焦", "邪在肝肾"
    dyn["sanjiao_trans"] = {"stage": stage or "信息不足", "hint": hint or "", "evidence": [f"{j}({v}分)" for j, v in hit.items()]}
    return dyn


def _score_indicators(indicators: list[str], tokens: list[str]) -> tuple[int, list[str]]:
    """指标词命中计分:完整词 2 分,bigram 命中 1 分(去重;共用前缀词排除)。"""
    score = 0
    hits: list[str] = []
    for ind in indicators:
        if ind in tokens:
            score += 2
            hits.append(ind)
            continue
        for g in _bigrams(ind):
            if g in STOP_BIGRAMS:
                continue
            if g in tokens and ind not in hits:
                score += 1
                hits.append(ind)
                break
    return score, hits


def analyze_systems(user_labels: list[str]) -> dict[str, Any]:
    """并行输出三个体系的对照结论。"""
    data = _load()
    # 用户标签 token 集:原词 + 四诊切分 + bigram
    tokens = set()
    negated = set()  # 否定词(不X/无X)里的核心词,不参与正向匹配
    for lab in user_labels:
        lab = str(lab or "").strip()
        if not lab:
            continue
        if lab.startswith(("不", "无", "未")):
            negated.add(lab[1:])
            continue
        tokens.add(lab)
        if lab in BOWEL_NEUTRAL:
            continue  # 整体术语不拆 bigram,防"自利"等误命中
        tokens.update(_bigrams(lab, cap=8))
    # 剔除否定核心词及其 bigram
    for n in negated:
        tokens.discard(n)
        for g in _bigrams(n):
            tokens.discard(g)
    # 拼接上下文 bigram 仅取非否定标签(避免"不恶寒"重新引入"恶寒")
    positive_labels = [str(x or "").strip() for x in user_labels if str(x or "").strip() and not str(x or "").strip().startswith(("不", "无", "未"))]
    tokens.update(_bigrams("、".join(positive_labels), cap=60))
    # 拼接上下文 bigram 亦剔除二便整体术语的内部词(如"便自/自利")
    for lab in positive_labels:
        if lab in BOWEL_NEUTRAL:
            for g in _bigrams(lab):
                tokens.discard(g)

    PAIRS = [("表", "里"), ("寒", "热"), ("虚", "实"), ("阴", "阳")]

    out: dict[str, Any] = {}
    for system in ("bagang", "liujing", "weiqiyingxue", "zangfu", "sanjiao", "jingluo"):
        items = []
        for rule in data[system]:
            score, hits = _score_indicators(rule["indicators"], list(tokens))
            items.append({
                "key": rule["key"],
                "name": rule["name"],
                "score": score,
                "hits": hits,
                "explain": rule["explain"],
            })
        items.sort(key=lambda x: -x["score"])
        max_score = max((i["score"] for i in items), default=1)
        top = [i for i in items if i["score"] > 0][:3]
        if system == "liujing" and top:
            # 提纲锚点并列优先(太少两感等)
            for anch, key in LIUJING_ANCHORS.items():
                if anch not in tokens:
                    continue
                if top[0]["key"] == key:
                    break
                idx = next((i for i, t in enumerate(top) if t["key"] == key), -1)
                if idx > 0 and top[idx]["score"] >= top[0]["score"]:
                    top.insert(0, top.pop(idx))
                    break
        summary = top[0]["name"] if top else "信息不足"
        components: list[str] = []
        if system == "bagang":
            by_key = {i["key"]: i for i in items}
            for a, b in PAIRS:
                sa = by_key[a]["score"]
                sb = by_key[b]["score"]
                if sa == 0 and sb == 0:
                    continue
                components.append(by_key[a]["name"] if sa >= sb else by_key[b]["name"])
            summary = "·".join(components) if components else "信息不足"
        out[system] = {
            "name": {"bagang": "八纲辨证", "liujing": "六经辨证", "weiqiyingxue": "卫气营血辨证", "zangfu": "脏腑辨证", "sanjiao": "三焦辨证", "jingluo": "经络辨证"}[system],
            "top": top,
            "summary": summary,
            "components": components,
            "confidence": round(top[0]["score"] / max(2, max_score), 2) if top else 0,
        }
    out["consistency"] = _consistency(out)
    out["dynamic"] = _dynamic(out)
    return out
