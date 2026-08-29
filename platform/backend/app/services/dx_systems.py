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
    return out
