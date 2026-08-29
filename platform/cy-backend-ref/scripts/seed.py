"""种子数据录入 —— 中医外科疮疡病种与方药

完整病种 86 个(13 章各论)+ 方药 82 附方。

用法:
    cd backend
    python3 -m scripts.seed
"""
import asyncio

from app.database import SessionLocal, init_db
from app.models import Disease, Formula, Image, Syndrome, TreatmentRule

from .seed_data import BOOK_PLATES, COMMON_NURSING, DOSAGES, FORMULAS, MODIFICATIONS, PREPARATIONS, SPECIFIC_RULES, SYNDROMES, WARNINGS
from .seed_diseases import DISEASES


def build_rules(treat: dict, formula_ids: dict, is_yang: bool = True, category: str = None, is_dangerous: bool = False, has_specific_initial: bool = False) -> list:
    """论治规则:病种 × 阶段 → 内治方 + 外治。

    按病种大类区分治则,避免通用消托补框架误用:
    - 疔疮(尤其颜面疔疮)成脓:清热解毒透脓、提脓拔毒,忌切开挤压,防走黄;
    - 阴证(无头疽/瘰疬/乳岩/冻疮)成脓:温托透脓;溃后:温补气血;
    - 阳证(痈/有头疽/疖等)成脓:托法透脓、切开排脓。
    """
    rules = []
    internal = treat.get("内治", "")
    initial_formula = None
    # 取「内治」文字中最早出现的方剂(即初起方),而非按方剂库顺序首配
    best_pos = len(internal) + 1
    for fname, fid in formula_ids.items():
        pos = internal.find(fname)
        if pos != -1 and pos < best_pos:
            best_pos = pos
            initial_formula = fid

    is_face_furuncle = category == "疔" and is_dangerous

    # ---- 成脓期治则(按病种大类区分) ----
    if category == "疔":
        abscess_formula = "五味消毒饮"
        abscess_external = "严禁挤压;五五丹或九一丹点疔头提脓拔毒;脓成熟局限者沿皮纹极小切口引流,颜面疔疮尤须慎重"
        abscess_note = "疔疮成脓,宜清热解毒合透脓拔毒:五味消毒饮加皂角刺、穿山甲透脓,或合透脓散;忌纯用补托;颜面疔疮忌挤压、过早切开,防走黄。"
    elif category == "脱疽":
        abscess_formula = "四妙勇安汤"
        abscess_external = treat.get("外治", "")
        abscess_note = "脱疽成脓,宜清热解毒、活血通络,忌大切开,以保肢为要;溃后分型论治(寒湿温通、血瘀活血、热毒清热、气血虚温补)。"
    elif not is_yang:
        abscess_formula = "托里透脓汤"
        abscess_external = treat.get("外治", "")
        abscess_note = "阴证酿脓,宜温托透脓、扶正托里,忌寒凉凝滞,不宜过早切开。"
    else:
        abscess_formula = "透脓散"
        abscess_external = "切开排脓引流;外敷金黄散;掺九一丹或八二丹提脓祛腐"
        abscess_note = "脓已成,宜托法透脓,及时切开排脓,切勿过早补益(闭门留寇)。"

    # ---- 溃后治则 ----
    if not is_yang:
        ulcer_formula = "十全大补汤"
        ulcer_external = "脓尽腐脱后掺生肌散收口"
        ulcer_note = "阴证溃后气血更虚,宜温补气血、生肌收口。"
    else:
        ulcer_formula = "八珍汤"
        ulcer_external = "脓尽腐脱后掺生肌散或八宝丹生肌收口"
        ulcer_note = "溃后气血已伤,宜补法扶正;脓尽方可用生肌收口药。"

    danger_note = "颜面疔疮,严禁挤压,防走黄。" if is_face_furuncle else ""

    # 有头疽(脑疽/发背/对心发等)危险证:溃后须防毒邪内陷(火陷、干陷、虚陷)
    if is_dangerous and category == "有头疽":
        ulcer_note += " 有头疽溃后正气大虚,须防毒邪内陷(火陷、干陷、虚陷),密切观察神志、体温、疮形变化,及时扶正托毒。"

    if is_yang:
        if not has_specific_initial:
            rules.append({
                "stage": "初起", "syndrome": "火毒炽盛",
                "formula": initial_formula,
                "external": treat.get("外治", ""),
                "note": f"治则:{treat.get('治则', '')}; 内治:{internal}" + (f"。{danger_note}" if danger_note else ""),
            })
        rules.append({
            "stage": "成脓", "syndrome": "热盛肉腐",
            "formula": formula_ids.get(abscess_formula),
            "external": abscess_external,
            "note": abscess_note,
        })
        rules.append({
            "stage": "溃后", "syndrome": "气血两虚",
            "formula": formula_ids.get(ulcer_formula),
            "external": ulcer_external,
            "note": ulcer_note,
        })
    else:
        if not has_specific_initial:
            rules.append({
                "stage": "初起", "syndrome": "寒湿凝滞",
                "formula": initial_formula,
                "external": treat.get("外治", ""),
                "note": f"治则:{treat.get('治则', '')}; 内治:{internal}(阴证,宜温通化痰散结)",
            })
        rules.append({
            "stage": "成脓", "syndrome": "正虚酿脓",
            "formula": formula_ids.get(abscess_formula),
            "external": abscess_external,
            "note": abscess_note,
        })
        rules.append({
            "stage": "溃后", "syndrome": "气血两虚",
            "formula": formula_ids.get(ulcer_formula),
            "external": ulcer_external,
            "note": ulcer_note,
        })
    return rules


async def seed() -> None:
    await init_db()
    async with SessionLocal() as db:
        # 清空(种子可重复执行)
        for model in (TreatmentRule, Image, Disease, Syndrome, Formula):
            await db.execute(model.__table__.delete())

        # 证型
        syndrome_ids = {}
        for s in SYNDROMES:
            obj = Syndrome(**s)
            db.add(obj)
            await db.flush()
            syndrome_ids[s["name"]] = obj.id

        # 方药
        formula_ids = {}
        for f in FORMULAS:
            obj = Formula(**f)
            # 附标准剂量;丸散丹成药/外用方无每味克数者,以「组成+服法」兜底,保证方方有药量信息
            obj.dosage = DOSAGES.get(f["name"]) or (
                f["composition"] + ("。" + f["usage"] if f.get("usage") else "")
            )
            obj.modifications = MODIFICATIONS.get(f["name"])  # 附随证加减
            obj.preparation = PREPARATIONS.get(f["name"])  # 附丹药炼制方法
            warn = WARNINGS.get(f["name"])  # 附毒性/禁用安全警示
            if warn:
                obj.contraindications = (obj.contraindications + "; " if obj.contraindications else "") + warn
            db.add(obj)
            await db.flush()
            formula_ids[f["name"]] = obj.id

        # 病种 + 论治规则
        specific_initial = {dname for dname, _syn, stage, *_ in SPECIFIC_RULES if stage == "初起"}
        # 分型辨证病种(病机分型,不按阴阳/阶段消托补)
        TYPE_BASED_NAMES = {
            "脱疽", "糖尿病坏疽", "闭塞性动脉硬化坏疽", "坏死性皮肤血管炎", "恶脉", "股白肿",
            "瘰疬", "冻疮", "乳岩", "丹毒", "臁疮", "褥疮",
        }
        name_to_id = {}
        for d in DISEASES:
            treat = d.pop("treat")
            is_yang = d.get("is_yang", True)
            category = d.get("category")
            is_dangerous = d.get("is_dangerous", False)
            is_sores = d.get("is_sores", True)
            differentiation = "分型" if d.get("name") in TYPE_BASED_NAMES else "消托补"
            obj = Disease(**d)
            obj.differentiation = differentiation
            db.add(obj)
            await db.flush()
            name_to_id[obj.name] = obj.id
            # 非疮疡病种(头癣/烧伤/皮肤病/直肠溃疡/红斑狼疮)不走消托补三阶段,只存治则/内治/外治
            if not is_sores:
                db.add(TreatmentRule(
                    disease_id=obj.id,
                    stage="初起",
                    syndrome_id=None,
                    internal_formula_id=None,
                    external_treatment=treat.get("外治", ""),
                    nursing=COMMON_NURSING,
                    note=f"治则:{treat.get('治则', '')}; 内治:{treat.get('内治', '')}",
                ))
                continue
            # 分型病种(脱疽/瘰疬/冻疮/乳岩/丹毒/臁疮/褥疮)不套消托补,由SPECIFIC_RULES提供分型
            if differentiation == "分型":
                continue
            for r in build_rules(treat, formula_ids, is_yang, category, is_dangerous, obj.name in specific_initial):
                db.add(TreatmentRule(
                    disease_id=obj.id,
                    stage=r["stage"],
                    syndrome_id=syndrome_ids[r["syndrome"]],
                    internal_formula_id=r["formula"],
                    external_treatment=r["external"],
                    nursing=COMMON_NURSING,
                    note=r["note"],
                ))

        # 病种证型细分规则(复杂病种的精准分型)
        for dname, syn_name, stage, fname, external, note in SPECIFIC_RULES:
            if dname in name_to_id and syn_name in syndrome_ids and fname in formula_ids:
                db.add(TreatmentRule(
                    disease_id=name_to_id[dname],
                    stage=stage,
                    syndrome_id=syndrome_ids[syn_name],
                    internal_formula_id=formula_ids[fname],
                    external_treatment=external,
                    nursing=COMMON_NURSING,
                    note=note,
                    is_specific=True,
                ))

        # 书本参考图版
        for path, caption, category in BOOK_PLATES:
            db.add(Image(disease_id=None, image_type="book", category=category, path=path, caption=caption))

        await db.commit()

    # 统计输出
    async with SessionLocal() as db:
        from sqlalchemy import func, select
        for model in (Disease, Syndrome, Formula, TreatmentRule, Image):
            n = (await db.execute(select(func.count()).select_from(model))).scalar()
            print(f"  {model.__tablename__}: {n}")


if __name__ == "__main__":
    asyncio.run(seed())
    print("✅ 种子数据录入完成")
