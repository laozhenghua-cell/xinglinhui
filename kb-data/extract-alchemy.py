#!/usr/bin/env python3
"""丹药数据提取:formulas/dulong/glossary JSON → 统一知识库规范化 JSON"""
import json, os, hashlib

def oid(prefix, name):
    return prefix + hashlib.md5(str(name or '').encode('utf-8')).hexdigest()[:10]

SRC = "/Users/apple/Documents/deepseek项目/中国炼丹术与丹药体系/03-web/src/data"
OUT = "/Users/apple/Documents/deepseek项目/tcm-platform-merge/kb-data/alchemy.json"

out = {"formulas": [], "herbs": [], "diseases": [], "syndromes": [], "cases": [], "tips": [], "terms": [], "dulong": []}

f = json.load(open(f"{SRC}/formulas.json", encoding="utf-8"))
for i, fml in enumerate(f.get("formulas", []), 1):
    out["formulas"].append({
        "module": "alchemy",
        "origin_id": f"a-{fml.get('id', i)}",
        "name": fml.get("name", ""),
        "aliases": fml.get("aliases", []) or [],
        "source": "张觉人《中国炼丹术与丹药》",
        "category": fml.get("category", ""),
        "composition": [{"name": c.get("drug", ""), "dose": c.get("amount", "")} for c in fml.get("composition", []) or []],
        "function": fml.get("efficacy", ""),
        "indication": fml.get("indication", ""),
        "usage": fml.get("usage", ""),
        "method": fml.get("method", ""),
        "formula_type": "丹药",
        "preparation": fml.get("process", ""),
        "toxicity": fml.get("toxicity", "") or "",
        "extra": {"appearance": fml.get("appearance", ""), "page": fml.get("page", "")},
    })

d = json.load(open(f"{SRC}/dulong.json", encoding="utf-8"))
for sec in d.get("meta", {}).get("sections", []):
    for e in sec.get("entries", []):
        out["dulong"].append({
            "module": "alchemy",
            "section": sec.get("name", ""),
            "n": e.get("n", 0),
            "disease": e.get("d", ""),
            "guide": e.get("g", ""),
        })
out["tips"].append({
    "module": "alchemy",
    "origin_id": oid("a-tip-", "毒龙丹总述"),
    "category": "毒龙丹总述",
    "content": f"用法:{d['meta'].get('usage','')}\n禁忌:{d['meta'].get('caution','')}",
    "source": "张觉人《中国炼丹术与丹药》",
})

g = json.load(open(f"{SRC}/glossary.json", encoding="utf-8"))
for t in g.get("terms", []):
    out["terms"].append({
        "module": "alchemy",
        "origin_id": oid("a-t-", t.get("term", "")),
        "term": t.get("term", ""),
        "definition": t.get("definition", ""),
        "source": f"《中国炼丹术与丹药》第{t.get('page','')}页",
    })

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("丹药提取完成: formulas", len(out["formulas"]), "dulong", len(out["dulong"]), "terms", len(out["terms"]))
