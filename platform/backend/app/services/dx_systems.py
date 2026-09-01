"""多辨证体系引擎:八纲 / 六经 / 卫气营血 并行对照。

输入:用户四诊标签(中文词) → 输出各体系得分与证据(指标词命中)。
规则数据:app/data/diagnosis_systems.json(经典提纲归纳)。
"""
from __future__ import annotations

import json
import re
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


STOP_BIGRAMS = {"大便", "小便", "腹部", "口渴", "腹痛", "头身", "面色"}

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


def analyze_systems(user_labels: list[str], time_key: str = "", sick_year: int = 0, birth_year: int = 0, detail_text: str = "") -> dict[str, Any]:
    """多辨证体系引擎。
    time_key: 发病/加重时辰(morning/forenoon/afternoon/evening/night/dawn/none);
    sick_year/birth_year: 发病年/出生年(五运六气推算);
    detail_text: 原始主诉长文本(用于多问题分解与抓主证)。"""
    data = _load()
    # 时间辨证:时辰 → 提示 + 证候加权词(并入标签参与计分)
    time_info = _time_dx(time_key)
    labels = list(user_labels)
    for t in time_info["add"]:
        if t not in labels:
            labels.append(t)
    # 用户标签 token 集:原词 + 四诊切分 + bigram
    tokens = set()
    negated = set()  # 否定词(不X/无X)里的核心词,不参与正向匹配
    for lab in labels:
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
            if system == "liujing":
                # 分型证据并入经证得分(蓄水证之"小便不利"等即太阳经证据);
                # 只并入经纲未列的证据词,避免"畏寒"等纲内词被双重计分
                base_inds = set(rule["indicators"])
                v_inds: list[str] = []
                for v in rule.get("variants", []):
                    for i in v.get("indicators", []):
                        if i not in base_inds and i not in v_inds:
                            v_inds.append(i)
                vscore, vhits = _score_indicators(v_inds, list(tokens))
                score += vscore
                for h in vhits:
                    if h not in hits:
                        hits.append(h)
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
                "variants": rule.get("variants", []),
                "mechanism": rule.get("mechanism", ""),
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
            # 六经分型:对 top1 经证再辨子型(中风/伤寒、寒化/热化等);证据须 ≥3 分,单凭一词不下分型
            best_v = None
            for v in top[0].get("variants", []):
                sc, vhits = _score_indicators(v["indicators"], list(tokens))
                if sc >= 3 and (best_v is None or sc > best_v["score"]):
                    best_v = {"key": v["key"], "name": v["name"], "score": sc, "hits": vhits,
                              "treatment": v.get("treatment", ""), "formulas": v.get("formulas", [])}
            top[0]["variant"] = best_v
        if system == "zangfu" and top:
            # 脏腑分型:对 top1 证型再辨子型(命门火衰/气化不利、阴虚火旺/精亏等)
            best_v = None
            for v in top[0].get("variants", []):
                sc, vhits = _score_indicators(v["indicators"], list(tokens))
                if sc > 0 and (best_v is None or sc >= best_v["score"]):
                    best_v = {"key": v["key"], "name": v["name"], "score": sc, "hits": vhits,
                              "treatment": v.get("treatment", ""), "formulas": v.get("formulas", [])}
            top[0]["variant"] = best_v
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
                if sa >= 2 and sb >= 2:
                    # 双方证候并见(表里同病/寒热错杂/阴阳两虚),同时输出
                    components.append(by_key[a]["name"])
                    components.append(by_key[b]["name"])
                else:
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
    followup = _followup(out)
    out["followup"] = followup
    out["ask"] = _ask_questions(user_labels, followup)
    out["modifications"] = _modifications(user_labels, out)
    out["menlei"] = _menlei(user_labels, out)
    out["discern"] = _discern(labels)  # 须在拟方之前:真假鉴别用于开方纠偏
    out["fangzheng"] = _fangzheng(user_labels)
    chief = _chief_analysis(detail_text, out)
    out["chief"] = chief
    out["prescription"] = _prescription(user_labels, out, chief)
    out["time"] = time_info
    out["wuyun"] = _wuyun(sick_year, birth_year)
    out["mechanism"] = _mechanism_summary(out)
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

_SYN_CACHE: Optional[dict] = None


def _load_synonyms() -> dict:
    """口语映射表:优先 data/synonyms.json(种子数据),缺省回退内置常量。"""
    global _SYN_CACHE
    if _SYN_CACHE is None:
        try:
            p = Path(__file__).resolve().parent.parent / "data" / "synonyms.json"
            _SYN_CACHE = json.loads(p.read_text(encoding="utf-8"))["synonyms"]
        except Exception:
            _SYN_CACHE = dict(SYNONYMS)
    return _SYN_CACHE


def invalidate_synonyms_cache() -> None:
    """管理后台增删改后清缓存。"""
    global _SYN_CACHE
    _SYN_CACHE = None


def extract_symptom_terms(texts: list[str], synonyms: Optional[dict] = None) -> list[str]:
    """从白话主诉/长文本中抽取标准证候标签(否定语境如'不发热'跳过)。
    synonyms: 口语映射表;缺省从 data/synonyms.json 加载,亦可由调用方传入 DB 版(管理后台可热更新)。"""
    import re as _re

    data = _load()
    terms: set[str] = set()
    for sys_name in ("bagang", "liujing", "weiqiyingxue", "zangfu", "sanjiao", "jingluo"):
        for r in data[sys_name]:
            terms.update(i for i in r["indicators"] if 2 <= len(i) <= 6)
    syn = synonyms if synonyms is not None else _load_synonyms()
    out: list[str] = []
    src = [str(t or "") for t in texts]
    for t in src:
        if len(t) <= 3:
            continue  # 超短标签本身已参与匹配
        for term in terms:
            if term not in out:
                for m in _re.finditer(_re.escape(term), t):
                    prev = t[m.start() - 1] if m.start() > 0 else ""
                    if prev and prev in _NEG:
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
        for kw in sorted(syn, key=len, reverse=True):
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
            for std in syn[kw]:
                if std not in out:
                    out.append(std)
    return out


_JIAJIAN_CACHE: Optional[list] = None
_MENLEI_CACHE: Optional[list] = None
_TIME_CACHE: Optional[list] = None

GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"
WUYUN_MAP = {"甲": ("土", True), "己": ("土", False), "乙": ("金", False), "庚": ("金", True),
             "丙": ("水", True), "辛": ("水", False), "丁": ("木", False), "壬": ("木", True),
             "戊": ("火", True), "癸": ("火", False)}
SITIAN_MAP = {"子": ("少阴君火", "阳明燥金"), "午": ("少阴君火", "阳明燥金"),
              "丑": ("太阴湿土", "太阳寒水"), "未": ("太阴湿土", "太阳寒水"),
              "寅": ("少阳相火", "厥阴风木"), "申": ("少阳相火", "厥阴风木"),
              "卯": ("阳明燥金", "少阴君火"), "酉": ("阳明燥金", "少阴君火"),
              "辰": ("太阳寒水", "太阴湿土"), "戌": ("太阳寒水", "太阴湿土"),
              "巳": ("厥阴风木", "少阳相火"), "亥": ("厥阴风木", "少阳相火")}
WUXING_QI = {"土": "湿", "金": "燥", "水": "寒", "木": "风", "火": "热"}


def _time_dx(time_key: str) -> dict:
    global _TIME_CACHE
    if _TIME_CACHE is None:
        try:
            p = Path(__file__).resolve().parent.parent / "data" / "time_dx.json"
            _TIME_CACHE = json.loads(p.read_text(encoding="utf-8"))["rules"]
        except Exception:
            _TIME_CACHE = []
    for r in _TIME_CACHE:
        if r.get("key") == time_key:
            return {"key": r["key"], "label": r["label"], "hint": r.get("hint", ""), "add": r.get("add", [])}
    return {"key": "", "label": "", "hint": "", "add": []}


def _discern(user_labels: list[str]) -> list[str]:
    """脉证相参/假象鉴别(舍证从脉)。"""
    joined = "、".join(str(x) for x in user_labels)
    out: list[str] = []
    hot_signs = any(x in joined for x in ("面赤", "面红", "身热", "发热", "胸腹灼热"))
    cold_limbs = any(x in joined for x in ("四肢厥冷", "手足厥冷", "肢厥"))
    weak_pulse = any(x in joined for x in ("脉微细", "脉微", "脉沉微"))
    if hot_signs and cold_limbs and weak_pulse:
        out.append("真寒假热(阴盛格阳):身热面赤而肢厥脉微,当舍证从脉,急温其阳(通脉四逆辈)")
    elif hot_signs and cold_limbs and ("脉沉数" in joined or "脉数" in joined):
        out.append("真热假寒(热深厥深):肢厥而胸腹灼热脉数,当舍证从脉,急清其热(白虎、承气辈)")
    if ("胸腹灼热" in joined) and cold_limbs:
        out.append("肢厥与胸腹灼热并见,阳郁于内,不可误投温药")
    if ("口渴喜冷饮" in joined or "喜冷饮" in joined) and cold_limbs:
        out.append("肢厥而喜冷饮,里热无疑,慎用温补")
    return out


def _wuyun(sick_year: int, birth_year: int) -> Optional[dict]:
    """五运六气推算:干支 → 岁运(太过/不及)+ 司天在泉 + 易病调护提示。"""
    if not sick_year and not birth_year:
        return None
    res: dict[str, Any] = {}
    if sick_year:
        g = GAN[(sick_year - 4) % 10]
        z = ZHI[(sick_year - 4) % 12]
        yun, over = WUYUN_MAP[g]
        sitian, zaiquan = SITIAN_MAP[z]
        qi = WUXING_QI[yun]
        res = {
            "year": sick_year,
            "ganzhi": f"{g}{z}",
            "yun": yun,
            "over": over,
            "sitian": sitian,
            "zaiquan": zaiquan,
            "hint": (f"岁运:{yun}运{'太过' if over else '不及'},{qi}气{'偏盛' if over else '不足'};"
                     f"{sitian}司天,{zaiquan}在泉。全年以{sitian}与{zaiquan}之气为纲,"
                     f"辨证宜兼察{qi}气之盛衰;调护随岁气寒热燥湿而施。"),
        }
    if birth_year:
        g = GAN[(birth_year - 4) % 10]
        yun, over = WUYUN_MAP[g]
        qi = WUXING_QI[yun]
        res["birth"] = {
            "year": birth_year,
            "ganzhi": f"{g}{ZHI[(birth_year - 4) % 12]}",
            "hint": f"出生之年{yun}运{'太过' if over else '不及'},禀赋偏{qi}({yun}型体质),临床宜兼顾其体质偏性。",
        }
    return res


def _mechanism_summary(out: dict[str, Any]) -> Optional[dict]:
    """病机提要:六经开阖枢 + 脏腑升降出入。"""
    lj = out["liujing"]["top"]
    zf = out["zangfu"]["top"]
    lj_m = (lj[0].get("mechanism") if lj and lj[0].get("mechanism") else "") if lj else ""
    zf_m = (zf[0].get("mechanism") if zf and zf[0].get("mechanism") else "") if zf else ""
    if not lj_m and not zf_m:
        return None
    parts = [p for p in (lj_m, zf_m) if p]
    return {"liujing": lj_m, "zangfu": zf_m, "summary": "。".join(parts) + "。"}


# ============ 抓主证 · 辨证论治思路(多问题主诉) ============

_PROBLEM_SEPS = re.compile(r"[。!?！？]|还有|另外|同时|并且|而且|以及|加上|伴随|另外就是")
_DANGER_TERMS = ("高热", "神昏", "抽搐", "昏迷", "剧痛", "大出血", "咯血", "便血不止",
                 "呼吸困难", "喘促欲脱", "大汗淋漓", "冷汗淋漓", "昏仆", "气脱", "亡阳")
_CHRONIC_TERMS = ("多年", "反复发作", "老毛病", "1年以上", "半年-1年", "多年老", "慢性")

# 经典合方对(两证并见时的合方惯例;source 标注为合方惯例,不假托古籍)
HEFANG_PAIRS = [
    {"pair": ("桂枝汤", "玉屏风散"), "note": "表虚自汗、易感风邪者,调和营卫兼益气固表", "source": "合方惯例"},
    {"pair": ("小柴胡汤", "四君子汤"), "note": "枢机不利兼脾虚气弱者,和解兼益气", "source": "合方惯例"},
    {"pair": ("平胃散", "五苓散"), "note": "即胃苓汤之意,燥湿运脾兼利水渗湿", "source": "合方惯例,胃苓汤见《丹溪心法》"},
    {"pair": ("四物汤", "四君子汤"), "note": "即八珍汤之意,气血双补", "source": "合方惯例,八珍汤见《正体类要》"},
    {"pair": ("二陈汤", "平胃散"), "note": "燥湿化痰兼行气和胃", "source": "合方惯例"},
    {"pair": ("六味地黄丸", "交泰丸"), "note": "心肾不交,滋阴降火兼交通心肾", "source": "合方惯例"},
    {"pair": ("理中汤", "四神丸"), "note": "脾肾阳虚泄泻,温中兼温肾涩肠", "source": "合方惯例"},
    {"pair": ("附子理中丸", "四神丸"), "note": "脾肾阳虚五更泄泻,温补脾肾兼涩肠止泻", "source": "合方惯例"},
    {"pair": ("银翘散", "桑菊饮"), "note": "风热袭表咳嗽,辛凉解表兼宣肺止咳", "source": "合方惯例"},
    {"pair": ("逍遥散", "四物汤"), "note": "肝郁血虚,疏肝解郁兼养血调经", "source": "合方惯例"},
    {"pair": ("生脉散", "沙参麦冬汤"), "note": "气阴两伤,益气生津兼润肺养胃", "source": "合方惯例"},
    {"pair": ("归脾汤", "酸枣仁汤"), "note": "心脾两虚不寐,健脾养心兼养血安神", "source": "合方惯例"},
    {"pair": ("桂枝汤", "理中汤"), "note": "太阳太阴并病,表里双解,参桂枝人参汤之意", "source": "《伤寒论》桂枝人参汤"},
    {"pair": ("柴胡疏肝散", "四君子汤"), "note": "肝郁脾虚,疏肝解郁兼健脾益气,参逍遥散之意", "source": "逍遥散见《太平惠民和剂局方》"},
    {"pair": ("导赤散", "六味地黄丸"), "note": "心火亢盛兼肾阴不足,清心利水兼滋肾养阴(泻南补北)", "source": "合方惯例"},
]


def _split_problems(detail_text: str) -> tuple[list[str], str]:
    """把主诉长文本拆成多个"问题"短语;返回 (问题列表, 病程片段)。"""
    if not detail_text:
        return [], ""
    segs = [s.strip() for s in re.split(r"[;；]", detail_text) if s.strip()]
    chief_seg = ""
    course_seg = ""
    for s in segs:
        if s.startswith("主诉"):
            chief_seg = re.sub(r"^主诉[:：]?", "", s).strip()
        elif s.startswith("病程"):
            course_seg = re.sub(r"^病程[:：]?", "", s).strip()
        elif s.startswith("诱因") or s.startswith("病因"):
            continue
        else:
            chief_seg = (chief_seg + ";" + s) if chief_seg else s
    if not chief_seg and segs:
        chief_seg = segs[0]
    if not chief_seg:
        return [], course_seg
    parts = [p.strip("; ;,,") for p in _PROBLEM_SEPS.split(chief_seg) if p.strip("; ;,,")]
    # 合并过短碎片到前一问题;但独立症状词(指标词)不合并
    data = _load()
    indicators: set[str] = set()
    for sys_name in ("bagang", "liujing", "weiqiyingxue", "zangfu", "sanjiao", "jingluo"):
        for r in data[sys_name]:
            indicators.update(i for i in r["indicators"] if 2 <= len(i) <= 8)
    merged: list[str] = []
    for p in parts:
        is_term = p in indicators or any(2 <= len(i) <= 8 and i in p for i in indicators if len(i) >= 4)
        if merged and len(p) <= 3 and not is_term:
            merged[-1] += "," + p
        else:
            merged.append(p)
    return merged, course_seg


def _problem_terms(problem: str) -> list[str]:
    """问题短语 → 参与计分的标签:原句 + 逗号/顿号片段 + 白话解析标签。"""
    terms: list[str] = []
    if problem not in terms:
        terms.append(problem)
    for frag in re.split(r"[、,，]", problem):
        frag = frag.strip()
        if 2 <= len(frag) <= 10 and frag not in terms:
            terms.append(frag)
    for t in extract_symptom_terms([problem]):
        if t not in terms:
            terms.append(t)
    return terms


def _chief_analysis(detail_text: str, out: dict[str, Any]) -> dict[str, Any]:
    """抓主证:主诉多问题分解 → 主次判定 → 同源/合病 → 治则治法。

    主次顺序:①危候问题(急则治标) > ②主诉首见问题(患者最难受者先说) > ③六体系结论最强者。
    """
    problems, course_seg = _split_problems(detail_text)
    if len(problems) <= 1:
        return {"split": False, "problems": [], "chief_index": None, "chief_reason": "",
                "tongyuan": False, "merge": [], "zhice": "", "note": ""}
    infos = []
    for p in problems:
        terms = _problem_terms(p)
        sub = analyze_systems(terms)
        zf = sub["zangfu"]
        lj = sub["liujing"]
        zf_top = zf["top"][0] if zf["top"] else None
        lj_top = lj["top"][0] if lj["top"] else None
        score = 0
        name = ""
        cands = []
        if zf["summary"] != "信息不足" and zf_top:
            cands.append((zf_top["score"], zf["summary"]))
        if lj["summary"] != "信息不足" and lj_top:
            cands.append((lj_top["score"], lj["summary"]))
        if sub["weiqiyingxue"]["summary"] != "信息不足" and sub["weiqiyingxue"]["top"]:
            cands.append((sub["weiqiyingxue"]["top"][0]["score"], sub["weiqiyingxue"]["summary"]))
        if sub["sanjiao"]["summary"] != "信息不足" and sub["sanjiao"]["top"]:
            cands.append((sub["sanjiao"]["top"][0]["score"], sub["sanjiao"]["summary"]))
        if cands:
            score, name = max(cands, key=lambda x: x[0])
        infos.append({
            "text": p[:60],
            "terms": terms[:12],
            "zangfu": zf["summary"],
            "liujing": lj["summary"],
            "name": name,
            "score": score,
            "lj_score": lj_top["score"] if lj_top and lj["summary"] != "信息不足" else 0,
            "danger": any(d in p for d in _DANGER_TERMS),
        })
    # 主次判定
    chief_index = 0
    chief_reason = ""
    danger_idx = next((i for i, x in enumerate(infos) if x["danger"]), None)
    if danger_idx is not None:
        chief_index = danger_idx
        chief_reason = "此问题含危候信号,急则治标,先解其急"
    else:
        first_score = infos[0]["score"]
        best = max(range(len(infos)), key=lambda i: infos[i]["score"])
        if first_score >= 2:
            chief_index = 0
            chief_reason = "列于主诉之首,患者自述最先、最重者,当先辨治"
        else:
            chief_index = best
            chief_reason = f"六体系结论最明确者(「{infos[best]['name'] or '证候未明'}」,{infos[best]['score']} 分证据)"
    chief = infos[chief_index]
    # 同源 / 合病判定
    chief_keys: set[str] = set()
    if chief["zangfu"] != "信息不足":
        zt = out["zangfu"]["top"]
        # 用整体输出取该证型 key(问题内子分析没有 key,这里用名字比对即可)
        chief_keys.add("zf:" + chief["zangfu"])
    if chief["liujing"] != "信息不足":
        chief_keys.add("lj:" + chief["liujing"])
    others = [x for i, x in enumerate(infos) if i != chief_index]
    tongyuan = True
    merge: list[dict] = []
    for o in others:
        if o["name"] == "信息不足" or o["name"] == chief["name"]:
            continue
        if o["score"] < 3:
            continue  # 弱结论(仅一二词)不构成"第二证",视为主证的兼症
        o_keys = set()
        if o["zangfu"] != "信息不足":
            o_keys.add("zf:" + o["zangfu"])
        if o["liujing"] != "信息不足":
            o_keys.add("lj:" + o["liujing"])
        if o_keys & chief_keys or o["name"] == chief["name"]:
            continue  # 同一证候可解释 → 同源
        tongyuan = False
        merge.append({"a": chief["name"] or chief["zangfu"] or chief["liujing"],
                      "b": o["name"] or o["zangfu"] or o["liujing"],
                      "text": o["text"]})
    # 治则治法
    zhice = _zhice(infos, out, course_seg, tongyuan, len(merge) > 0, chief_index)
    # 思路文字
    note_parts = [f"主诉含 {len(infos)} 个问题,以「{chief['text'][:30]}」为主症({chief_reason})"]
    if tongyuan:
        note_parts.append(f"其余问题皆可由「{chief['name'] or '同一证候'}」解释,异病同治,一方统之,兼症随主方加减")
    elif merge:
        note_parts.append("诸证非同源,当合病并病论治," + zhice)
    note = ";".join(note_parts) + "。"
    return {"split": True, "problems": infos, "chief_index": chief_index,
            "chief_reason": chief_reason, "tongyuan": tongyuan, "merge": merge,
            "zhice": zhice, "note": note}


def _zhice(infos: list[dict], out: dict[str, Any], course_seg: str, tongyuan: bool, has_merge: bool, chief_idx: int = 0) -> str:
    """治则治法:标本缓急、表里先后、攻补兼施。"""
    _disc = "|".join(out.get("discern") or [])
    if "真热假寒" in _disc:
        return "脉证相参:舍证从脉,热深厥深,急清其热(白虎、承气辈)"
    if "真寒假热" in _disc:
        return "脉证相参:舍证从脉,阴盛格阳,急温其阳(通脉四逆辈)"
    if any(x["danger"] for x in infos):
        return "急则治标:先解危候,急症缓解后再图其本"
    comps = out["bagang"]["components"]
    if "表证" in comps and "里证" in comps:
        return "表里同病:先表后里(表解乃可攻里);表里俱急者表里双解"
    if "虚证" in comps and "实证" in comps:
        return "虚实夹杂:攻补兼施,扶正祛邪,观其缓急而定主次"
    # 虚实夹杂启发式:主证属虚(阴虚/阳虚/气虚/血虚/精亏),他证属邪实(热/湿/痰/瘀/滞/火/食)
    chief_name = infos[chief_idx]["name"] or ""
    others = [x for i, x in enumerate(infos) if i != chief_idx]
    _xu = ("虚", "亏", "不足")
    _shi = ("热", "湿", "痰", "瘀", "滞", "火", "食", "结")
    if any(k in chief_name for k in _xu) and any(any(k in (x["name"] or "") for k in _shi) for x in others):
        return "虚实夹杂:攻补兼施,扶正祛邪,观其缓急而定主次"
    if any(c in course_seg for c in _CHRONIC_TERMS) and len(infos) > 1:
        return "新病痼疾并存:先治新病,兼护宿疾"
    if tongyuan:
        return "异病同治:诸症同源,一方统之,兼症随证加减"
    if has_merge:
        has_biao = any(x["liujing"] == "太阳病" and x["lj_score"] >= 2 for x in infos)
        has_li = any(x["zangfu"] != "信息不足" or x["liujing"] in ("阳明病", "太阴病", "少阴病", "厥阴病") for x in infos)
        if has_biao and has_li:
            return "表里同病:先表后里,表解乃可攻里;表里俱急者表里双解"
        return "合病并病:主证为主,兼证为辅,两方合用或分先后而治"
    return "先主后次:主证得解,兼症自除;兼症突出者随主方加减"


_FANGZHENG_CACHE: Optional[list] = None


def _load_fangzheng() -> list:
    global _FANGZHENG_CACHE
    if _FANGZHENG_CACHE is None:
        try:
            p = Path(__file__).resolve().parent.parent / "data" / "fangzheng.json"
            _FANGZHENG_CACHE = json.loads(p.read_text(encoding="utf-8"))["rules"]
        except Exception:
            _FANGZHENG_CACHE = []
    return _FANGZHENG_CACHE


def _fangzheng(user_labels: list[str]) -> list[dict]:
    """方证辨证:主症必见+或然症→经典方(附原文出处与鉴别要点)。"""
    joined = "、".join(str(x) for x in user_labels)
    out: list[dict] = []
    for r in _load_fangzheng():
        must_hits = [m for m in r.get("must", []) if m in joined]
        if len(must_hits) < r.get("min_must", 1):
            continue
        if any(e in joined for e in r.get("exclude", [])):
            continue
        may_hits = [m for m in r.get("may", []) if m in joined]
        score = len(must_hits) * 3 + len(may_hits)
        if score < 3:
            continue
        out.append({"key": r["key"], "name": r["name"], "formula": r["formula"],
                    "score": score, "must_hits": must_hits, "may_hits": may_hits,
                    "original": r.get("original", ""), "treatment": r.get("treatment", ""),
                    "jianbie": r.get("jianbie", "")})
    out.sort(key=lambda x: -x["score"])
    return out[:5]


def _hefang_for(chief_sub: dict[str, Any], other_subs: list[dict[str, Any]], primary: Optional[str] = None) -> Optional[dict]:
    """合方建议:主方与兼证代表方若在经典合方对中,给出合方提示(优先以实际主方配对)。"""
    def top_formulas(sub: dict) -> set[str]:
        fs: set[str] = set()
        for sys in ("zangfu", "liujing", "sanjiao", "weiqiyingxue", "jingluo"):
            t = sub.get(sys, {}).get("top") or []
            if t and sub[sys]["summary"] != "信息不足":
                for f in t[0].get("formulas") or []:
                    fs.add(f)
            v = t[0].get("variant") if t else None
            if v:
                for f in v.get("formulas") or []:
                    fs.add(f)
        return fs

    if primary:
        # 有实际主方时,严格以主方配对(避免"麻黄汤主证却建议桂枝汤合方"的错配)
        for o in other_subs:
            o_fs = top_formulas(o)
            for pair in HEFANG_PAIRS:
                a, b = pair["pair"]
                if primary == a and b in o_fs:
                    return {"formulas": f"{a}合{b}", "note": pair["note"], "source": pair["source"]}
                if primary == b and a in o_fs:
                    return {"formulas": f"{b}合{a}", "note": pair["note"], "source": pair["source"]}
        return None
    chief_fs = top_formulas(chief_sub)
    for o in other_subs:
        o_fs = top_formulas(o)
        for pair in HEFANG_PAIRS:
            a, b = pair["pair"]
            if a in chief_fs and b in o_fs:
                return {"formulas": f"{a}合{b}", "note": pair["note"], "source": pair["source"]}
            if b in chief_fs and a in o_fs:
                return {"formulas": f"{b}合{a}", "note": pair["note"], "source": pair["source"]}
    return None


def _load_yifang_lib() -> list:
    global _MENLEI_CACHE
    if _MENLEI_CACHE is None:
        try:
            p = Path(__file__).resolve().parent.parent / "data" / "yifang_seed.json"
            _MENLEI_CACHE = json.loads(p.read_text(encoding="utf-8"))["formulas"]
        except Exception:
            _MENLEI_CACHE = []
    return _MENLEI_CACHE


def _menlei(user_labels: list[str], out: dict[str, Any]) -> list[dict]:
    """医方集解治法门类辨证:症状+八纲+脏腑结论 → 治法门类 → 门类代表方。"""
    joined = "、".join(str(x) for x in user_labels)
    comps = out["bagang"]["components"]
    zf = out["zangfu"]["summary"]
    picks: list[tuple[str, str]] = []

    def has(*ks):
        return any(k in joined for k in ks)

    if "表证" in comps or has("恶寒", "发热", "鼻塞", "流清涕"):
        picks.append(("发表之剂", "解表祛邪"))
    if has("痰", "咳喘") or zf in ("痰湿阻肺", "痰热壅肺", "胆郁痰扰"):
        picks.append(("除痰之剂", "化痰止咳"))
    if has("浮肿", "水肿", "带下", "困重", "湿") or zf in ("湿热蕴脾", "寒湿困脾", "大肠湿热", "膀胱湿热", "太阴湿热"):
        picks.append(("利湿之剂", "利水渗湿"))
    if has("胀痛", "痞满", "嗳气", "善太息", "胸闷") or zf in ("肝气郁结", "食滞胃脘"):
        picks.append(("理气之剂", "行气解郁"))
    if has("刺痛", "瘀斑", "舌紫暗", "痛有定处", "痛经") or zf in ("心血瘀阻",):
        picks.append(("理血之剂", "活血化瘀"))
    if has("痒", "痹", "麻木", "抽搐", "震颤") or zf in ("肝风内动", "虚风内动"):
        picks.append(("祛风之剂", "祛风通络"))
    if "寒证" in comps or zf in ("胃寒", "脾阳虚", "肾阳虚"):
        picks.append(("祛寒之剂", "温里散寒"))
    if "热证" in comps or zf in ("心火亢盛", "肝火上炎", "胃热炽盛"):
        picks.append(("泻火之剂", "清热泻火"))
    if "虚证" in comps or zf in ("脾气虚", "肾阴虚", "肾阳虚", "肺气虚", "心血虚", "肝血虚", "胃阴虚", "脾阳虚"):
        picks.append(("补养之剂", "补虚扶正"))
    if has("便秘", "腹满", "燥屎", "大便干结"):
        picks.append(("攻里之剂", "攻下里实"))
    if has("嗳腐", "厌食") or zf == "食滞胃脘":
        picks.append(("消导之剂", "消食导滞"))
    if has("遗精", "自汗", "盗汗", "久泻", "崩漏"):
        picks.append(("收涩之剂", "固涩止脱"))
    if has("疮", "痈", "疔"):
        picks.append(("痈疡之剂", "解毒消痈"))
    if has("月经", "经期", "胎", "带下", "产后"):
        picks.append(("经产之剂", "调经安胎"))
    if has("暑"):
        picks.append(("清暑之剂", "清暑益气"))
    if has("干咳", "口干", "便干"):
        picks.append(("润燥之剂", "润燥生津"))
    seen: set[str] = set()
    uniq = []
    for ml, zhifa in picks:
        if ml not in seen:
            seen.add(ml)
            uniq.append((ml, zhifa))
    prefer: set[str] = set()
    zf_clear = out["zangfu"]["summary"] != "信息不足"
    for sys in ("zangfu", "liujing", "sanjiao"):
        t = out[sys]["top"]
        if t:
            if sys == "liujing" and zf_clear and not t[0].get("variant"):
                continue
            prefer.update(t[0].get("formulas") or [])
            if t[0].get("variant"):
                prefer.update(t[0]["variant"].get("formulas") or [])
    yf = _load_yifang_lib()
    # 相关词:患者标签中的证候词(含分型指标词),用于门类内选方精排
    rel_terms: set[str] = set()
    for lab in user_labels:
        lab = str(lab or "")
        if 2 <= len(lab) <= 6:
            rel_terms.add(lab)
            rel_terms.update(_bigrams(lab, cap=4))
    res: list[dict] = []
    for ml, zhifa in uniq[:5]:
        base = ml.replace("之剂", "")
        cands = [f for f in yf if (f.get("category") or "").startswith(base)]

        def _rel(f: dict) -> int:
            text = f"{f.get('function', '')} {f.get('indications', '')}"
            return sum(1 for t in rel_terms if t and t in text)

        # 优先证型主方;其余按主治/功效与症状词相关性排序
        pref = sorted((f for f in cands if f["name"] in prefer), key=lambda f: -_rel(f))
        rest = sorted((f for f in cands if f["name"] not in prefer), key=lambda f: -_rel(f))
        top_cands = (pref + rest)[:3]
        res.append({"menlei": ml, "zhifa": zhifa,
                    "formulas": [{"name": f["name"], "source": f.get("source", "")} for f in top_cands]})
    return res


def _load_jiajian() -> list:
    global _JIAJIAN_CACHE
    if _JIAJIAN_CACHE is None:
        try:
            p = Path(__file__).resolve().parent.parent / "data" / "jiajian_rules.json"
            _JIAJIAN_CACHE = json.loads(p.read_text(encoding="utf-8"))["rules"]
        except Exception:
            _JIAJIAN_CACHE = []
    return _JIAJIAN_CACHE


def _prescription(user_labels: list[str], out: dict[str, Any], chief: Optional[dict] = None) -> Optional[dict]:
    """拟方合成:首选主方 + 随症加减 → 一张完整处方单(药+量+加减理由)。
    首选优先级:六经分型方 > 脏腑强结论(≥4分) > 六经通用方 > 脏腑一般结论。
    多问题主诉时以"主症问题"的结论定主方(抓主要矛盾);并给出合病合方建议。"""
    lj = out["liujing"]["top"]
    zf = out["zangfu"]["top"]
    zf_summary = out["zangfu"]["summary"]
    wq = out["weiqiyingxue"]
    hefang = None
    chief_sub = None
    if chief and chief.get("split") and chief.get("chief_index") is not None:
        ci = chief["chief_index"]
        chief_sub = analyze_systems(chief["problems"][ci]["terms"])
        lj = chief_sub["liujing"]["top"]
        zf = chief_sub["zangfu"]["top"]
        zf_summary = chief_sub["zangfu"]["summary"]
        wq = chief_sub["weiqiyingxue"]
        # 分型证据可能横跨多个问题(如蓄水:小便不利+水入即吐),同经时用全问题证据辨分型
        all_terms: list[str] = []
        for p in chief["problems"]:
            all_terms.extend(p["terms"])
        sub_all = analyze_systems(all_terms)
        lj_all = sub_all["liujing"]
        if (lj_all["top"] and lj_all["top"][0].get("variant") is not None
                and (not lj or lj[0].get("key") == lj_all["top"][0].get("key"))):
            lj = lj_all["top"]
    primary = None
    lj_variant = None
    if lj and lj[0].get("variant"):
        lj_variant = (lj[0]["variant"].get("formulas") or [None])[0]
    zf_first = (zf[0].get("formulas") or [None])[0] if zf and zf_summary != "信息不足" else None
    zf_score = zf[0]["score"] if zf else 0
    lj_first = (lj[0].get("formulas") or [None])[0] if lj else None
    # 卫气营血明确结论(气分/营分/血分)参与开方(温病证候,脏腑六经常不覆盖)
    wq_top = wq.get("top") or []
    wq_first = (wq_top[0].get("formulas") or [None])[0] if wq_top and wq["summary"] != "信息不足" else None
    wq_score = wq_top[0]["score"] if wq_top else 0
    # 真假鉴别纠偏:真热假寒误投温剂、真寒假热误投凉剂,皆临床大忌
    _WARM = {"四逆汤", "通脉四逆汤", "理中汤", "附子理中丸", "桂枝汤", "麻黄汤", "当归四逆汤",
             "真武汤", "金匮肾气丸", "四神丸", "吴茱萸汤"}
    _COOL = {"白虎汤", "大承气汤", "小承气汤", "调胃承气汤", "清营汤", "犀角地黄汤",
             "黄连解毒汤", "龙胆泻肝汤", "导赤散"}
    # 方证定方:方证强命中(≥6分)且明显胜出时,以经典方证之方为主方(证型层负责释病机)
    fz = out.get("fangzheng") or []
    if fz and fz[0]["score"] >= 6 and (len(fz) < 2 or fz[0]["score"] > fz[1]["score"]):
        fz_primary = fz[0]["formula"]
        if any(f["name"] == fz_primary for f in _load_yifang_lib()):
            primary = fz_primary
            fz_set = True
        else:
            fz_set = False
    else:
        fz_set = False
    if not fz_set:
        if lj_variant:
            primary = lj_variant
        elif zf_first and zf_score >= 4:
            primary = zf_first
        elif wq_first and wq_score >= 3:
            primary = wq_first
        elif lj_first:
            primary = lj_first
        elif zf_first:
            primary = zf_first
    _discern_txt = "|".join(out.get("discern") or [])
    if not primary:
        return None
    if "真热假寒" in _discern_txt and primary in _WARM:
        primary = "白虎汤"
    elif "真寒假热" in _discern_txt and primary in _COOL:
        primary = "四逆汤"
    if chief_sub is not None:
        ci = chief["chief_index"]
        others = [analyze_systems(chief["problems"][i]["terms"])
                  for i in range(len(chief["problems"])) if i != ci]
        hefang = _hefang_for(chief_sub, others, primary)
    base = next((f for f in _load_yifang_lib() if f["name"] == primary), None)
    if not base:
        return None
    mods = {m["formula"]: m["entries"] for m in _modifications(user_labels, out)}
    items = [{"name": c.get("name", ""), "dosage": c.get("dosage", ""), "note": "原方"}
             for c in base.get("composition", [])]
    for e in mods.get(primary, []):
        for a in e.get("add", []):
            items.append({"name": a.get("name", ""), "dosage": a.get("dosage", ""),
                          "note": f"加:{a.get('reason', '')}({e.get('source', '')})"})
        for rm in e.get("remove", []):
            items = [i for i in items if i["name"] != rm]
    return {"name": primary, "source": base.get("source", ""), "items": items, "hefang": hefang}


def _modifications(user_labels: list[str], out: dict[str, Any]) -> list[dict]:
    """随症加减:按主方(含六经分型主方)匹配兼症加减规则(加味/减味+出处)。"""
    joined = "、".join(str(x) for x in user_labels)
    formula_names: list[str] = []
    zf_clear = out["zangfu"]["summary"] != "信息不足"
    for sys in ("zangfu", "liujing", "sanjiao", "weiqiyingxue", "jingluo"):
        t = out[sys]["top"]
        if t and out[sys]["summary"] != "信息不足":
            if sys == "liujing" and zf_clear and not t[0].get("variant"):
                continue  # 脏腑已明确时,六经无分型的通用主方不参与开方
            for fn in t[0].get("formulas") or []:
                if fn not in formula_names:
                    formula_names.append(fn)
    lj = out["liujing"]["top"]
    if lj and lj[0].get("variant"):
        for fn in lj[0]["variant"].get("formulas") or []:
            if fn not in formula_names:
                formula_names.append(fn)
    elif lj and out["zangfu"]["summary"] == "信息不足":
        for fn in lj[0].get("formulas") or []:
            if fn not in formula_names:
                formula_names.append(fn)
    res: list[dict] = []
    for rule in _load_jiajian():
        if rule.get("formula") not in formula_names:
            continue
        entries = []
        for e in rule.get("entries", []):
            if all(c in joined for c in e.get("cond", [])):
                entries.append({"add": e.get("add", []), "remove": e.get("remove", []), "source": e.get("source", "")})
        if entries:
            res.append({"formula": rule["formula"], "entries": entries})
    return res


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


def _ask_questions(user_labels: list[str], followup: Optional[dict]) -> list[dict]:
    """症状→鉴别问句反向引导:按患者已述症状触发关键问句(如'肚子疼'→反问喜按拒按)。"""
    joined = "、".join(str(x) for x in user_labels)
    followup_ids = {q.get("id") for q in (followup or {}).get("questions", [])}
    scored = []
    for q in _load_dq()["questions"]:
        if q.get("id") in followup_ids:
            continue  # 与体系追问去重
        trigs = q.get("triggers") or []
        n = sum(1 for t in trigs if t in joined)
        if not n:
            continue
        # 已答跳过:该题任一选项标签已出现且非触发词本身 → 视为已答
        trig_set = set(trigs)
        answered = any(lab in joined for opt in q["options"] for lab in opt.get("add", []) if lab not in trig_set)
        if answered:
            continue
        scored.append((n, q))
    scored.sort(key=lambda x: -x[0])
    return [q for _, q in scored[:3]]
