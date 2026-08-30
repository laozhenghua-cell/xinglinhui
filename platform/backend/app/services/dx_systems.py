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
    ("zangfu", "膀胱湿热", "liujing", "少阳病"), ("zangfu", "膀胱湿热", "jingluo", "足少阳胆经"),
    ("bagang", "热证", "liujing", "少阳病"), ("bagang", "热证", "jingluo", "足少阳胆经"),
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
            pairs_out.append({"text": f"{_SYS_NAME[a]}↔{_SYS_NAME[b]}:{active[a]}↔{active[b]}{'✓' if ok else '✗'}", "ok": ok})
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


DANGER_RULES = [
    ("神昏", "神志危候——神昏谵语,病势危重,立即就医"),
    ("昏仆", "神志危候——卒然昏仆,立即就医"),
    ("抽搐", "动风危候——四肢抽搐,病势危重,立即就医"),
    ("角弓反张", "动风危候——角弓反张,立即就医"),
    ("高热不退", "高热危候——高热持续不退,立即就医"),
    ("壮热", "高热危候——壮热不退,谨防传变,及时就医"),
    ("大出血", "出血危候——大出血,立即就医"),
    ("呕血", "出血危候——呕血,立即就医"),
    ("咯血", "出血危候——咯血,立即就医"),
    ("便血不止", "出血危候——便血不止,立即就医"),
    ("崩漏", "出血危候——崩漏量多不止,立即就医"),
    ("呼吸困难", "气道危候——呼吸困难,立即就医"),
    ("喘促", "气道危候——喘促不能平卧,立即就医"),
    ("胸痛剧烈", "胸痹危候——胸痛剧烈,立即就医"),
    ("心痛彻背", "胸痹危候——心痛彻背,立即就医"),
    ("冷汗淋漓", "厥脱危候——冷汗淋漓,阳气欲脱,立即就医"),
    ("四肢厥冷", "厥脱危候——四肢厥冷,谨防厥脱,及时就医"),
]

CARE_BY_ZANG = {
    "肝": "调畅情志,戒怒少忧;夜卧养肝,忌熬夜",
    "心": "安神静养,勿过思虑;劳逸结合",
    "脾": "饮食规律,忌生冷油腻;少食多餐",
    "肺": "避风保暖,戒烟;空气清新,适度呼吸锻炼",
    "肾": "节劳节欲,腰膝保暖;忌久立久行",
    "胃": "少食多餐,忌辛辣刺激;食后稍息",
    "胆": "饮食清淡,忌肥甘厚味;调畅情志",
    "大肠": "多食蔬果粗纤维,定时排便,忌辛辣酒浆",
    "膀胱": "多饮水,忌憋尿,注意下焦清洁",
}

CARE_BY_BAGANG = {
    "寒证": "避风寒,重保暖,忌食生冷",
    "热证": "饮食清淡,忌辛辣炙煿、烟酒",
    "虚证": "劳逸结合,勿过劳,饮食有节以养正气",
    "实证": "饮食有节,勿过饱,保持二便通畅",
    "表证": "避风保暖,慎起居,忌汗出当风",
    "里证": "饮食规律,调护脾胃,忌生冷油腻",
}


def _care_advice(out: dict[str, Any]) -> list[str]:
    """老中医式调护建议:按八纲性质 + 脏腑病位 + 经络归属组合。"""
    tips: list[str] = []
    comps = out["bagang"]["components"]
    for c in comps:
        t = CARE_BY_BAGANG.get(c)
        if t and t not in tips:
            tips.append(t)
    zf = out["zangfu"]["summary"]
    for zang, t in CARE_BY_ZANG.items():
        if zang in zf and t not in tips:
            tips.append(t)
    if not tips:
        tips.append("饮食有节,起居有常,调畅情志")
    return tips[:4]


def _danger_alerts(user_labels: list[str]) -> list[str]:
    """危候警示:命中危重词即提示就医(规则表)。"""
    alerts = []
    joined = "、".join(str(x) for x in user_labels)
    for word, msg in DANGER_RULES:
        if word in joined and msg not in alerts:
            alerts.append(msg)
    return alerts[:3]


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
        if len(lab) > 8:
            continue  # 长文本(如主诉一句话)只取完整词,不拆 bigram,防噪音
        tokens.update(_bigrams(lab, cap=8))
    # 剔除否定核心词及其 bigram
    for n in negated:
        tokens.discard(n)
        for g in _bigrams(n):
            tokens.discard(g)
    # 拼接上下文 bigram 仅取非否定标签(避免"不恶寒"重新引入"恶寒");长文本(主诉)不参与拼接
    positive_labels = [str(x or "").strip() for x in user_labels if str(x or "").strip() and not str(x or "").strip().startswith(("不", "无", "未"))]
    tokens.update(_bigrams("、".join(l for l in positive_labels if len(l) <= 8), cap=60))
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
                "indicators": list(rule["indicators"]),
                "missing": [i for i in rule["indicators"] if i not in hits][:4],
                "explain": rule["explain"],
                "treatment": rule.get("treatment", ""),
                "formulas": rule.get("formulas", []),
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
        # 证据不足(仅 1 分弱命中)不轻易下结论,老中医作风;八纲按四对维度不受此限
        if system != "bagang" and top and top[0]["score"] <= 1:
            summary = "信息不足"
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
    out["care"] = _care_advice(out)
    out["danger"] = _danger_alerts(user_labels)
    out["followup"] = _followup(out)
    out["plain"] = _plain_summary(out)
    return out


# 口语 → 标准证候标签(患者白话主诉解析用;一词可映射多标签)
SYNONYMS: dict[str, list[str]] = {
    # 寒热
    "怕冷": ["恶寒"], "怕凉": ["恶寒"], "发冷": ["恶寒"], "老觉得冷": ["恶寒"],
    "怕风": ["恶风"], "发烧": ["发热"], "发热": ["发热"], "高烧": ["发热"], "低烧": ["发热"],
    "发低烧": ["发热"], "浑身发烫": ["发热"], "着凉": ["恶寒"], "感冒": ["恶寒"],
    "忽冷忽热": ["寒热往来"], "一阵冷一阵热": ["寒热往来"],
    "手脚冰凉": ["畏寒肢冷"], "手脚冷": ["畏寒肢冷"], "手脚发凉": ["畏寒肢冷"], "四肢发凉": ["畏寒肢冷"], "手脚凉": ["畏寒肢冷"],
    "手心脚心热": ["五心烦热"], "下午发热": ["午后潮热"], "午后发热": ["午后潮热"], "骨头发热": ["潮热"],
    # 汗
    "老出汗": ["自汗"], "爱出汗": ["自汗"], "出汗多": ["自汗"], "汗多": ["自汗"],
    "一动就出汗": ["自汗"], "虚汗": ["自汗"], "冒汗": ["自汗"], "出汗": ["自汗"],
    "晚上出汗": ["盗汗"], "夜里出汗": ["盗汗"], "睡着出汗": ["盗汗"], "睡着了出汗": ["盗汗"],
    "不出汗": ["无汗"], "没出汗": ["无汗"],
    "冒冷汗": ["冷汗淋漓"], "出冷汗": ["冷汗淋漓"], "冷汗": ["冷汗淋漓"],
    "头上出汗": ["头汗出"], "只有头出汗": ["头汗出"],
    # 疼痛
    "头疼": ["头痛"], "偏头疼": ["偏头痛"], "后脑勺疼": ["头项强痛"],
    "脖子疼": ["颈痛"], "脖子僵硬": ["头项强痛"], "脖子发硬": ["头项强痛"],
    "胸口疼": ["胸痛"], "胸口痛": ["胸痛"], "心口疼": ["心痛"], "心口痛": ["心痛"],
    "胃疼": ["胃痛"], "胃痛": ["胃痛"], "肚子疼": ["腹痛"], "肚子痛": ["腹痛"],
    "小肚子疼": ["少腹疼痛"], "小腹痛": ["少腹疼痛"],
    "两肋疼": ["胁痛"], "肋骨疼": ["胁痛"], "肋叉子疼": ["胁痛"], "两胁疼": ["胁痛"],
    "腰疼": ["腰痛"], "腰酸": ["腰痛"], "腰不舒服": ["腰痛"], "腰背疼": ["腰痛"],
    "膝盖疼": ["膝髌肿痛"], "关节疼": ["身痛"], "浑身疼": ["身痛"], "肌肉酸": ["身痛"],
    "针扎一样疼": ["刺痛"], "烧着疼": ["灼痛"], "一跳一跳地疼": ["胀痛"],
    # 头身
    "头晕": ["头晕"], "头昏": ["头晕"], "晕乎乎": ["头晕"], "天旋地转": ["眩晕"],
    "耳鸣": ["耳鸣"], "耳聋": ["耳聋"], "耳朵嗡嗡响": ["耳鸣"],
    "眼睛干": ["目涩"], "眼干": ["目涩"], "眼睛涩": ["目涩"], "眼花": ["目眩"], "眼睛红": ["目赤"], "眼红": ["目赤"], "眼屎多": ["目赤"],
    "口干": ["口干"], "嘴干": ["口干"], "嗓子干": ["口干"], "口苦": ["口苦"], "嘴里发苦": ["口苦"],
    "口臭": ["口臭"], "嘴里有味": ["口臭"], "口淡": ["口淡"], "嘴里没味": ["口淡"], "口甜": ["口甜"],
    "嗓子疼": ["咽痛"], "喉咙痛": ["咽痛"], "咽喉痛": ["咽痛"], "嗓子干痒": ["咽痛"],
    "嗓子有痰": ["痰多"], "喉咙有痰": ["痰多"], "咳痰": ["痰多"], "有痰": ["痰多"], "痰多": ["痰多"],
    "黄痰": ["痰黄"], "白痰": ["痰稀白"], "干咳": ["咳嗽"], "咳血": ["咳血"], "痰里带血": ["咳血"],
    "鼻子不通": ["鼻塞"], "鼻塞": ["鼻塞"], "鼻子堵": ["鼻塞"], "流鼻涕": ["流清涕"], "清鼻涕": ["流清涕"], "流清涕": ["流清涕"], "流黄涕": ["流涕"],
    "胸闷": ["胸闷"], "憋气": ["胸闷"], "胸口发闷": ["胸闷"], "喘不上气": ["气喘"], "上不来气": ["气喘"], "气喘": ["气喘"], "气短": ["气短"],
    "心慌": ["心悸"], "心跳快": ["心悸"], "心突突": ["心悸"], "心悸": ["心悸"],
    "面色发黄": ["面色萎黄"], "脸色发白": ["面色苍白"], "脸发白": ["面色苍白"], "脸红": ["面赤"],
    # 二便
    "拉肚子": ["泄泻"], "拉稀": ["泄泻"], "腹泻": ["泄泻"], "大便稀": ["便溏"],
    "大便干": ["大便干结"], "拉不出": ["便秘"], "大便费劲": ["便秘"], "便秘": ["便秘"],
    "拉血": ["便血鲜红"], "大便带血": ["便血鲜红"], "黑便": ["便血暗红"], "大便发黑": ["便血暗红"],
    "放屁多": ["矢气臭秽"], "屁多": ["矢气臭秽"], "拉不干净": ["里急后重"], "老想拉": ["里急后重"], "里急后重": ["里急后重"],
    "尿频": ["尿频"], "老想上厕所": ["尿频"], "总想尿": ["尿频"], "尿急": ["尿急"],
    "撒尿疼": ["尿痛"], "尿痛": ["尿痛"], "尿黄": ["小便短赤"], "小便黄": ["小便短赤"],
    "尿少": ["小便不利"], "尿不出来": ["闭癃"], "尿血": ["尿血"], "尿里带血": ["尿血"],
    "起夜": ["夜尿多"], "夜尿多": ["夜尿多"], "尿床": ["遗尿"], "尿不尽": ["尿频"],
    # 饮食
    "没胃口": ["纳差"], "不想吃": ["纳差"], "吃不下": ["纳差"], "食欲差": ["纳差"], "没食欲": ["纳差"], "不想吃饭": ["纳差"], "吃不下饭": ["纳差"],
    "吃得多": ["消谷善饥"], "老饿": ["消谷善饥"], "饿得快": ["消谷善饥"], "老想吃": ["消谷善饥"],
    "饿了但不想吃": ["饥不欲食"], "恶心": ["恶心"], "想吐": ["恶心", "干呕"], "干呕": ["干呕"],
    "打嗝": ["嗳气"], "嗳气": ["嗳气"], "反酸": ["吞酸"], "吐酸水": ["吞酸"], "烧心": ["吞酸"],
    "肚子胀": ["腹胀"], "胃胀": ["腹胀"], "腹胀": ["腹胀"], "肚子响": ["肠鸣漉漉"], "肠鸣": ["肠鸣漉漉"],
    # 睡眠情志
    "睡不着": ["失眠"], "睡不好": ["失眠"], "失眠": ["失眠"], "入睡难": ["失眠"],
    "多梦": ["多梦"], "易醒": ["失眠"], "睡不踏实": ["失眠"],
    "老犯困": ["嗜睡"], "嗜睡": ["嗜睡"], "睡不醒": ["嗜睡"], "总想睡": ["嗜睡"],
    "心烦": ["心烦"], "烦躁": ["烦躁"], "烦得很": ["烦躁"], "爱发脾气": ["急躁易怒"], "急躁": ["急躁易怒"], "容易急": ["急躁易怒"], "脾气大": ["急躁易怒"],
    "情绪低落": ["情志抑郁"], "高兴不起来": ["情志抑郁"], "郁闷": ["情志抑郁"], "心情不好": ["情志抑郁"], "抑郁": ["情志抑郁"],
    "爱叹气": ["善太息"], "老叹气": ["善太息"], "善太息": ["善太息"],
    "胆小": ["惊惕不安"], "容易受惊": ["惊惕不安"], "一惊一乍": ["惊惕不安"],
    "记性差": ["健忘"], "健忘": ["健忘"], "老忘事": ["健忘"],
    "没精神": ["神疲乏力"], "没劲": ["神疲乏力"], "浑身没劲": ["神疲乏力"], "没力气": ["神疲乏力"],
    "累": ["神疲乏力"], "乏力": ["神疲乏力"], "懒得动": ["神疲乏力"], "没劲儿": ["神疲乏力"],
    # 妇科
    "月经不调": ["月经不调"], "例假不准": ["月经不调"], "例假不规律": ["月经不调"],
    "痛经": ["少腹疼痛"], "来例假肚子疼": ["少腹疼痛"],
    "月经量多": ["崩漏"], "崩漏": ["崩漏"], "白带多": ["带下"], "带下多": ["带下"], "白带发黄": ["带下"],
    "乳房胀痛": ["胸胁胀满"], "乳房胀": ["胸胁胀满"],
    # 其他
    "上火": ["咽痛", "口渴"], "起疹子": ["斑疹"], "出疹子": ["斑疹"], "起红疹": ["斑疹"],
    "水肿": ["小便不利"], "浮肿": ["小便不利"], "腿肿": ["小便不利"],
    "口唇发紫": ["口唇青紫"], "嘴唇发紫": ["口唇青紫"],
    "眼睛发黄": ["目黄"], "眼珠黄": ["黄疸"], "皮肤发黄": ["黄疸"],
    "嗓子呼噜响": ["喉中痰鸣"], "喉咙呼噜响": ["喉中痰鸣"], "呼吸费劲": ["气喘"],
    "饭后胀": ["腹胀"], "吃完饭胀": ["腹胀"], "打饱嗝": ["嗳气"], "恶心干哕": ["干呕"],
    # 方言/口语
    "脑袋瓜子疼": ["头痛"], "脑仁疼": ["头痛"], "胃里泛酸水": ["吞酸"], "泛酸水": ["吞酸"],
    "打寒战": ["恶寒"], "打哆嗦": ["恶寒"], "打摆子": ["寒热往来"], "烧得慌": ["发热"],
    "心里发慌": ["心悸"], "心里扑腾": ["心悸"], "心里发紧": ["胸闷"],
    "手脚麻": ["肢体麻木"], "手麻脚麻": ["肢体麻木"], "半边身子麻": ["肢体麻木"], "胳膊腿麻": ["肢体麻木"],
    "说话不利索": ["言语謇涩"], "嘴歪": ["口㖞"], "嘴歪眼斜": ["口㖞"], "舌头不听使唤": ["言语謇涩"],
    "上茅房勤": ["尿频"], "老往厕所跑": ["尿频"], "解小手勤": ["尿频"],
    "拉羊屎蛋": ["大便干结"], "拉水": ["泄泻"], "拉肚子拉水": ["泄泻"], "五更泻": ["泄泻"], "天亮前拉肚子": ["泄泻"],
    "尿等待": ["小便不利"], "尿不痛快": ["小便不利"], "夜尿频": ["夜尿多"],
    "放响屁": ["矢气臭秽"], "肚子咕咕叫": ["肠鸣漉漉"],
    "困得不行": ["嗜睡"], "犯困": ["嗜睡"], "没精神头": ["神疲乏力"], "浑身发软": ["神疲乏力"],
    "心里烦得慌": ["心烦"], "坐不住": ["烦躁"], "爱着急": ["急躁易怒"], "火气大": ["急躁易怒"],
    "想不开": ["情志抑郁"], "愁眉苦脸": ["情志抑郁"],
    "男科不行": ["阳痿"], "不举": ["阳痿"], "梦遗": ["遗精"], "遗精": ["遗精"], "早泄": ["遗精"],
    "月经推后": ["月经不调"], "月经推迟": ["月经不调"], "月经提前": ["月经不调"], "例假推迟": ["月经不调"],
    "下面痒": ["带下"], "外阴痒": ["带下"],
    # 舌象白话
    "舌头有齿印": ["舌有齿痕"], "舌头有牙印": ["舌有齿痕"], "舌头胖": ["舌胖大"], "舌头大": ["舌胖大"],
    "舌头瘦": ["舌瘦薄"], "舌头有裂纹": ["舌有裂纹"], "舌头发紫": ["舌紫暗"], "舌头紫": ["舌紫暗"],
    "舌头上有瘀斑": ["舌有瘀斑"], "舌苔厚": ["苔腻"], "舌苔白": ["苔白"], "舌苔黄": ["苔黄"],
    "舌苔少": ["少苔"], "没什么舌苔": ["少苔"], "没舌苔": ["无苔"], "舌苔干": ["苔燥"], "舌苔滑": ["苔滑"],
    "舌头红": ["舌红"], "舌头发白": ["舌淡"], "舌头深红": ["舌绛"], "舌尖疼": ["口舌生疮"],
    # 脉象白话
    "脉搏跳得快": ["脉数"], "脉搏快": ["脉数"], "脉搏跳得慢": ["脉迟"], "脉搏慢": ["脉迟"],
    "脉没劲": ["脉虚"], "脉弱无力": ["脉虚"], "脉象弦": ["脉弦"], "脉跳得不齐": ["脉结代"], "脉乱跳": ["脉结代"],
}
_NEG = "不无未没"


def extract_symptom_terms(texts: list[str]) -> list[str]:
    """从白话主诉/长文本中抽取标准证候标签(否定语境如'不发热'跳过)。"""
    import re as _re

    data = _load()
    terms: set[str] = set()
    for sys_name in ("bagang", "liujing", "weiqiyingxue", "zangfu", "sanjiao", "jingluo"):
        for r in data[sys_name]:
            terms.update(i for i in r["indicators"] if 2 <= len(i) <= 6)
    out: list[str] = []
    src = [str(t or "") for t in texts]
    for t in src:
        if len(t) <= 8:
            continue  # 短标签本身已参与匹配
        for term in terms:
            if term not in out:
                for m in _re.finditer(_re.escape(term), t):
                    prev = t[m.start() - 1] if m.start() > 0 else ""
                    if prev in _NEG:
                        continue
                    out.append(term)
                    break
    # 口语映射:长关键词优先(如'晚上出汗'先于'出汗'命中);否定语境跳过;子串重叠不重复映射
    _night_sweat = ["晚上出汗", "夜里出汗", "睡着出汗", "睡着了出汗", "盗汗"]
    _day_sweat = ["老出汗", "爱出汗", "出汗多", "汗多", "一动就出汗", "虚汗", "冒汗", "出汗"]
    _night_ctx = ["晚上", "夜里", "夜间", "睡着", "睡觉", "入睡"]
    for t in src:
        matched: list[str] = []
        # 夜间语境 + 出汗描述 → 归为盗汗(如"晚上老出汗")
        if any(n in t for n in _night_ctx) and any(d in t for d in _day_sweat):
            if "盗汗" not in out:
                out.append("盗汗")
        for kw in sorted(SYNONYMS, key=len, reverse=True):
            if kw not in t:
                continue
            # kw 是已命中更长关键词的子串(如'出汗'属于'不出汗'),跳过
            if any(kw in m and m in t for m in matched):
                continue
            # 夜间出汗语境下不再出"自汗"
            if kw in _day_sweat and (any(k in t for k in _night_sweat) or any(n in t for n in _night_ctx)):
                continue
            idx = t.find(kw)
            if idx > 0 and t[idx - 1] in "不没":
                continue
            after = idx + len(kw)
            if after < len(t) and t[after] in "退止愈消":
                continue  # 如"发热退了"属否定语境
            matched.append(kw)
            for std in SYNONYMS[kw]:
                if std not in out:
                    out.append(std)
    return out


def _plain_summary(out: dict[str, Any]) -> Optional[dict]:
    """一句话白话结论(病患视角)。"""
    zf = out["zangfu"]["summary"]
    if zf == "信息不足":
        zf = out["liujing"]["summary"]
        if zf == "信息不足":
            zf = out["sanjiao"]["summary"]
    if zf == "信息不足":
        return None
    top1 = None
    for sys in ("zangfu", "liujing", "sanjiao", "weiqiyingxue", "jingluo"):
        t = out[sys]["top"]
        if t and t[0]["name"] == zf:
            top1 = t[0]
            break
    if top1 is None:
        return None
    bg = out["bagang"]["summary"] if out["bagang"]["summary"] != "信息不足" else ""
    parts = [f"综合六体系辨证,您这属于「{zf}」"]
    if bg:
        parts.append(f"证属{bg}")
    parts.append(f"病机:{top1.get('explain', '')}")
    if top1.get("treatment"):
        parts.append(f"治当{top1['treatment']}")
    if top1.get("formulas"):
        parts.append(f"代表方:{'、'.join(top1['formulas'][:2])}")
    if out.get("danger"):
        parts.append("⚠️ 已出现危候信号,请立即就医,勿延误")
    return {"verdict": ";".join(parts) + "。", "danger": bool(out.get("danger"))}


_DQ_CACHE: Optional[dict] = None


def _load_dq() -> dict:
    global _DQ_CACHE
    if _DQ_CACHE is None:
        p = Path(__file__).resolve().parent.parent / "data" / "differential_questions.json"
        _DQ_CACHE = json.loads(p.read_text(encoding="utf-8"))
    return _DQ_CACHE


def _followup(out: dict[str, Any]) -> Optional[dict]:
    """鉴别追问:top1/top2 接近时,推荐最能区分二者的问诊问题。"""
    for sys in ("zangfu", "liujing"):
        top = out[sys]["top"]
        if len(top) < 2 or top[0]["score"] < 2:
            continue
        if top[0]["score"] - top[1]["score"] > 2:
            continue
        pool = set(top[0]["indicators"]) | set(top[1]["indicators"])
        scored = []
        for q in _load_dq()["questions"]:
            adds = {lab for opt in q["options"] for lab in opt.get("add", [])}
            overlap = len(adds & pool)
            if overlap:
                scored.append((overlap, q))
        if not scored:
            continue
        scored.sort(key=lambda x: -x[0])
        return {
            "system": sys,
            "top1": top[0]["name"],
            "top2": top[1]["name"],
            "questions": [q for _, q in scored[:3]],
        }
    return None
