"""舌象拍照识别 — Qwen-VL 结构化 + 规则归一化到六体系引擎词表。

链路:照片 base64 → ai_gateway.vision(舌诊专用提示词) → JSON 特征
     → tongue_rules.json 归一化/校验 → 症状标签列表(并入 analyze_systems 的 user_labels)
失败策略:AI 不可用/非舌象照片 → 返回 source=unavailable / not_tongue,由前端回退手动点选,绝不断问诊流。
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from app.core.ai_gateway import AIError, vision

logger = logging.getLogger("tongue_ai")

_RULES_CACHE: Optional[dict] = None

TONGUE_PROMPT = (
    "你是中医舌诊专家。请对这张舌象照片做客观描述(只描述所见,不辨证):"
    "舌色(tongue_color:淡红/淡白/红/鲜红/绛/深绛/紫/紫暗/青紫)、"
    "苔色(coating_color:白/黄/灰/黑/灰黑/无苔)、"
    "苔质(coating_texture:薄/厚/腻/厚腻/燥/滑/剥/无)、"
    "舌形(shape:胖大/瘦薄/齿痕/裂纹/点刺/正常)、"
    "舌态(state:歪斜/颤动/短缩/正常)、"
    "分区(zones:{tip/center/root/sides}各取 正常/红/绛/紫/瘀斑/苔厚)、"
    "整体置信度 confidence(0-1)、是否为可辨识的舌象照片 not_tongue(true/false)。"
    "只返回 JSON(字段:tongue_color, coating_color, coating_texture, shape, state, zones, confidence, not_tongue)。"
)


def _load_rules() -> dict:
    global _RULES_CACHE
    if _RULES_CACHE is None:
        try:
            p = Path(__file__).resolve().parent.parent / "data" / "tongue_rules.json"
            _RULES_CACHE = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            _RULES_CACHE = {}
    return _RULES_CACHE


def normalize_tongue(feats: dict[str, Any]) -> dict[str, Any]:
    """把 VL 特征 JSON 归一化为引擎词表标签。纯函数,可单测/评测。"""
    rules = _load_rules()
    labels: list[str] = []
    color = str(feats.get("tongue_color") or "").strip()
    coating_color = str(feats.get("coating_color") or "").strip()
    coating_texture = str(feats.get("coating_texture") or "").strip()
    shape = str(feats.get("shape") or "").strip()
    state = str(feats.get("state") or "").strip()
    zones = feats.get("zones") or {}
    if not isinstance(zones, dict):
        zones = {}

    # 舌色
    for key, ls in (rules.get("color_map") or {}).items():
        if key in color:
            labels.extend(ls)
            break
    # 瘀斑/瘀点(可能在舌色或分区描述里)
    joined_all = json.dumps(feats, ensure_ascii=False)
    if any(t in joined_all for t in (rules.get("瘀斑_terms") or ["瘀斑", "瘀点"])):
        if "舌有瘀斑" not in labels:
            labels.append("舌有瘀斑")
    # 苔
    if coating_color:
        picked = False
        for r in rules.get("coating_rules") or []:
            if r.get("color") == coating_color and r.get("texture") == coating_texture:
                labels.extend(r.get("labels") or [])
                picked = True
                break
        if not picked:
            for r in rules.get("coating_rules") or []:
                if r.get("color") == coating_color and not r.get("texture"):
                    labels.extend(r.get("labels") or [])
                    break
    # 舌形/舌态
    for m in (rules.get("shape_map") or {}).get(shape, []):
        labels.append(m)
    for m in (rules.get("state_map") or {}).get(state, []):
        labels.append(m)
    # 分区(舌尖红/舌边尖红)
    zone_rules = rules.get("zone_map") or {}
    for zk, zmap in zone_rules.items():
        zv = str(zones.get(zk) or "").strip()
        for k, ls in zmap.items():
            if k in zv:
                labels.extend(ls)
    # 矛盾校验:无苔/剥苔时去掉 苔X 色苔标签(保留"少苔"表示阴伤)
    no_coating = coating_color in ("无苔", "无") or coating_texture in ("剥", "无")
    if no_coating:
        labels = [x for x in labels if not (x.startswith("苔") and x != "少苔")]
    # 去重保序
    seen: set[str] = set()
    out = []
    for x in labels:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return {"labels": out, "source": "rules-normalized"}


async def analyze_tongue(image_b64: str) -> dict[str, Any]:
    """舌象识别主入口。返回 {labels, source, feats, confidence, not_tongue}。"""
    try:
        res = await vision(image_b64, provider="qwen", prompt=TONGUE_PROMPT)
    except AIError as e:
        logger.warning("tongue vision failed: %s", repr(e))
        return {"labels": [], "source": "unavailable", "feats": None, "confidence": None, "not_tongue": False, "message": "AI 舌诊服务暂不可用,请手动点选舌象"}
    feats = res.get("json") or {}
    if not isinstance(feats, dict):
        feats = {}
    not_tongue = bool(feats.get("not_tongue")) or (isinstance(feats.get("raw_text"), str))
    if not_tongue:
        return {"labels": [], "source": "not-tongue", "feats": feats, "confidence": None, "not_tongue": True, "message": "未识别到清晰的舌象,请对准舌头重拍或手动点选"}
    norm = normalize_tongue(feats)
    conf = None
    try:
        conf = float(feats.get("confidence"))
    except (TypeError, ValueError):
        conf = None
    return {
        "labels": norm["labels"],
        "source": norm["source"],
        "feats": feats,
        "confidence": conf,
        "not_tongue": False,
        "low_confidence": conf is not None and conf < float((_load_rules().get("meta") or {}).get("confidence_floor", 0.6)),
    }
