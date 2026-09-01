"""局部评测回归:镜像 /api/v1/dx/eval 的检查逻辑 + 舌象归一化 + 抓主证检查。
用法:.venv-test/bin/python eval_local.py(工作目录 platform/backend)"""
import json
import sys

sys.path.insert(0, ".")
from app.services.dx_systems import analyze_systems, extract_symptom_terms
from app.services.tongue_ai import normalize_tongue

data = json.loads(open("app/data/eval_samples.json", encoding="utf-8").read())
samples = data["samples"]
per: dict = {}
fails = []

for sm in samples:
    result = analyze_systems(
        sm["labels"],
        time_key=sm.get("time_key", ""),
        sick_year=sm.get("sick_year", 0),
        birth_year=sm.get("birth_year", 0),
        detail_text=sm.get("detail", ""),
    )
    for sys_key in ("bagang", "liujing", "weiqiyingxue", "zangfu", "sanjiao", "jingluo"):
        got = result[sys_key]["summary"]
        exp = sm["expected"].get(sys_key)
        if exp:
            st = per.setdefault(sys_key, [0, 0]); st[1] += 1
            ok = (all(x in result[sys_key].get("components", []) for x in exp)
                  if sys_key == "bagang" and isinstance(exp, list) else got == exp)
            if ok: st[0] += 1
            else: fails.append((sm["id"], sys_key, got, exp))
    if sm["expected"].get("consistency") is not None:
        cons = result.get("consistency") or {}
        st = per.setdefault("consistency", [0, 0]); st[1] += 1
        ok = cons.get("score") is not None and cons["score"] >= sm["expected"]["consistency"]
        if ok: st[0] += 1
        else: fails.append((sm["id"], "consistency", cons.get("score"), sm["expected"]["consistency"]))
    if sm["expected"].get("dynamic"):
        dyn = result.get("dynamic") or {}
        ml = "|".join([m.get("label", "") for m in dyn.get("liujing_merge", [])])
        ml += "|" + "|".join([m.get("label", "") for m in dyn.get("weiqi_merge", [])])
        stage = (dyn.get("sanjiao_trans") or {}).get("stage", "")
        for k, want in sm["expected"]["dynamic"].items():
            st = per.setdefault("dynamic", [0, 0]); st[1] += 1
            ok = (want in stage) if k == "sanjiao_trans" else (want in ml)
            if ok: st[0] += 1
            else: fails.append((sm["id"], "dynamic-" + k, (ml, stage), want))
    if sm["expected"].get("treatment_has"):
        t = ((result.get("zangfu") or {}).get("top") or [{}])[0].get("treatment", "")
        st = per.setdefault("treatment", [0, 0]); st[1] += 1
        ok = sm["expected"]["treatment_has"] in t
        if ok: st[0] += 1
        else: fails.append((sm["id"], "treatment", t, sm["expected"]["treatment_has"]))
    if sm["expected"].get("formula_has"):
        got = ((result.get("zangfu") or {}).get("top") or [{}])[0].get("formulas", [])
        st = per.setdefault("formula", [0, 0]); st[1] += 1
        ok = any(sm["expected"]["formula_has"] in x for x in got)
        if ok: st[0] += 1
        else: fails.append((sm["id"], "formula", got, sm["expected"]["formula_has"]))
    if sm["expected"].get("danger_has"):
        joined = "|".join(result.get("danger") or [])
        st = per.setdefault("danger", [0, 0]); st[1] += 1
        ok = sm["expected"]["danger_has"] in joined
        if ok: st[0] += 1
        else: fails.append((sm["id"], "danger", joined, sm["expected"]["danger_has"]))
    if sm["expected"].get("followup"):
        fu = result.get("followup")
        st = per.setdefault("followup", [0, 0]); st[1] += 1
        ok = bool(fu and fu.get("questions"))
        if ok: st[0] += 1
        else: fails.append((sm["id"], "followup", None, None))
    if sm["expected"].get("plain_has"):
        got = (result.get("plain") or {}).get("verdict", "")
        st = per.setdefault("plain", [0, 0]); st[1] += 1
        ok = sm["expected"]["plain_has"] in got
        if ok: st[0] += 1
        else: fails.append((sm["id"], "plain", got[:60], sm["expected"]["plain_has"]))
    if sm["expected"].get("colloquial"):
        st = per.setdefault("colloquial", [0, 0]); st[1] += 1
        got = extract_symptom_terms(sm["labels"])
        ok = all(x in got for x in sm["expected"]["colloquial"])
        if ok: st[0] += 1
        else: fails.append((sm["id"], "colloquial", got, sm["expected"]["colloquial"]))
    if sm["expected"].get("ask_has"):
        ids = [q.get("id", "") for q in (result.get("ask") or [])]
        fu_ids = [q.get("id", "") for q in (result.get("followup") or {}).get("questions", [])]
        st = per.setdefault("ask", [0, 0]); st[1] += 1
        ok = sm["expected"]["ask_has"] in ids + fu_ids
        if ok: st[0] += 1
        else: fails.append((sm["id"], "ask", ids + fu_ids, sm["expected"]["ask_has"]))
    if sm["expected"].get("variant_has"):
        v = ((result.get("liujing") or {}).get("top") or [{}])[0].get("variant") or {}
        v2 = ((result.get("zangfu") or {}).get("top") or [{}])[0].get("variant") or {}
        got = (v.get("formulas") or []) + (v2.get("formulas") or [])
        st = per.setdefault("variant", [0, 0]); st[1] += 1
        ok = sm["expected"]["variant_has"] in got
        if ok: st[0] += 1
        else: fails.append((sm["id"], "variant", got, sm["expected"]["variant_has"]))
    if sm["expected"].get("menlei_has"):
        mls = [m.get("menlei", "") for m in (result.get("menlei") or [])]
        st = per.setdefault("menlei", [0, 0]); st[1] += 1
        ok = sm["expected"]["menlei_has"] in mls
        if ok: st[0] += 1
        else: fails.append((sm["id"], "menlei", mls, sm["expected"]["menlei_has"]))
    if sm["expected"].get("prescription_has"):
        got = (result.get("prescription") or {}).get("name", "")
        st = per.setdefault("prescription", [0, 0]); st[1] += 1
        ok = sm["expected"]["prescription_has"] in got
        if ok: st[0] += 1
        else: fails.append((sm["id"], "prescription", got, sm["expected"]["prescription_has"]))
    if sm["expected"].get("mechanism_has"):
        got = (result.get("mechanism") or {}).get("summary", "")
        st = per.setdefault("mechanism", [0, 0]); st[1] += 1
        ok = sm["expected"]["mechanism_has"] in got
        if ok: st[0] += 1
        else: fails.append((sm["id"], "mechanism", got[:50], sm["expected"]["mechanism_has"]))
    if sm["expected"].get("time_hint"):
        got = (result.get("time") or {}).get("hint", "")
        st = per.setdefault("time", [0, 0]); st[1] += 1
        ok = sm["expected"]["time_hint"] in got
        if ok: st[0] += 1
        else: fails.append((sm["id"], "time", got[:40], sm["expected"]["time_hint"]))
    if sm["expected"].get("discern_has"):
        joined = "|".join(result.get("discern") or [])
        st = per.setdefault("discern", [0, 0]); st[1] += 1
        ok = sm["expected"]["discern_has"] in joined
        if ok: st[0] += 1
        else: fails.append((sm["id"], "discern", joined, sm["expected"]["discern_has"]))
    if sm["expected"].get("wuyun_has"):
        got = (result.get("wuyun") or {}).get("hint", "")
        st = per.setdefault("wuyun", [0, 0]); st[1] += 1
        ok = sm["expected"]["wuyun_has"] in got
        if ok: st[0] += 1
        else: fails.append((sm["id"], "wuyun", got[:50], sm["expected"]["wuyun_has"]))
    if sm["expected"].get("modification_has"):
        mods = result.get("modifications") or []
        herbs = [a.get("name", "") for m in mods for e in m["entries"] for a in e.get("add", [])]
        st = per.setdefault("modification", [0, 0]); st[1] += 1
        ok = sm["expected"]["modification_has"] in herbs
        if ok: st[0] += 1
        else: fails.append((sm["id"], "modification", herbs, sm["expected"]["modification_has"]))
    # 抓主证(多问题主诉)
    if sm["expected"].get("chief_has"):
        c = result.get("chief") or {}
        st = per.setdefault("chief", [0, 0]); st[1] += 1
        chief_text = (c.get("problems") or [{}])[c.get("chief_index") or 0].get("text", "")
        ok = sm["expected"]["chief_has"] in chief_text
        if ok: st[0] += 1
        else: fails.append((sm["id"], "chief", chief_text, sm["expected"]["chief_has"]))
    if sm["expected"].get("strategy_has"):
        c = result.get("chief") or {}
        st = per.setdefault("strategy", [0, 0]); st[1] += 1
        got = c.get("zhice", "")
        ok = sm["expected"]["strategy_has"] in got
        if ok: st[0] += 1
        else: fails.append((sm["id"], "strategy", got[:50], sm["expected"]["strategy_has"]))
    if sm["expected"].get("tongyuan") is not None:
        c = result.get("chief") or {}
        st = per.setdefault("tongyuan", [0, 0]); st[1] += 1
        ok = bool(c.get("tongyuan")) == bool(sm["expected"]["tongyuan"])
        if ok: st[0] += 1
        else: fails.append((sm["id"], "tongyuan", c.get("tongyuan"), sm["expected"]["tongyuan"]))
    if sm["expected"].get("fangzheng_has"):
        st = per.setdefault("fangzheng", [0, 0]); st[1] += 1
        got = "|".join(f.get("formula", "") for f in (result.get("fangzheng") or []))
        ok = sm["expected"]["fangzheng_has"] in got
        if ok: st[0] += 1
        else: fails.append((sm["id"], "fangzheng", got, sm["expected"]["fangzheng_has"]))
    if sm["expected"].get("hefang_has"):
        st = per.setdefault("hefang", [0, 0]); st[1] += 1
        got = ((result.get("prescription") or {}).get("hefang") or {}).get("formulas", "")
        ok = sm["expected"]["hefang_has"] in got
        if ok: st[0] += 1
        else: fails.append((sm["id"], "hefang", got, sm["expected"]["hefang_has"]))

# 舌象归一化
tongue_cases = [
    ({"tongue_color": "红", "coating_color": "黄", "coating_texture": "腻", "shape": "齿痕", "state": "正常", "zones": {"tip": "红", "center": "正常", "root": "腻", "sides": "正常"}}, ["舌红", "苔黄腻", "齿痕舌", "舌尖红"]),
    ({"tongue_color": "淡白", "coating_color": "白", "coating_texture": "薄", "shape": "胖大", "state": "正常", "zones": {}}, ["舌淡", "苔白", "胖大舌"]),
    ({"tongue_color": "紫", "coating_color": "无苔", "coating_texture": "剥", "shape": "裂纹", "state": "正常", "zones": {"sides": "瘀斑"}}, ["舌紫暗", "少苔", "舌有瘀斑", "裂纹舌"]),
    ({"tongue_color": "淡红", "coating_color": "白", "coating_texture": "薄", "shape": "正常", "state": "正常", "zones": {}}, ["苔白"]),
    ({"tongue_color": "绛", "coating_color": "黄", "coating_texture": "燥", "shape": "正常", "state": "正常", "zones": {}}, ["舌绛", "苔黄燥"]),
    ({"tongue_color": "红", "coating_color": "黄", "coating_texture": "剥", "shape": "正常", "state": "正常", "zones": {}}, ["舌红"]),
    ({"tongue_color": "深绛", "coating_color": "无", "coating_texture": "无", "shape": "点刺", "state": "正常", "zones": {}}, ["舌深绛", "少苔", "点刺舌"]),
]
st = per.setdefault("tongue", [0, 0])
for feats, exp in tongue_cases:
    st[1] += 1
    got = sorted(normalize_tongue(feats)["labels"])
    if got == sorted(exp): st[0] += 1
    else: fails.append(("tongue", feats.get("tongue_color"), got, exp))

tot_c = sum(v[0] for v in per.values()); tot_n = sum(v[1] for v in per.values())
print("per-system:", {k: f"{v[0]}/{v[1]}" for k, v in per.items()})
print(f"OVERALL: {tot_c}/{tot_n} = {tot_c/tot_n:.4f}")
if fails:
    print("FAILS:")
    for f in fails: print(" ", f)
