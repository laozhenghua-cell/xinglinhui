"""录入——妇科白带(张觉人《红蓼山馆医集》疑难病症外治经验)

用法: cd backend && python3 -m scripts.seed_gynecology
"""
import asyncio

from sqlalchemy import delete, select

from app.database import SessionLocal, init_db
from app.models import Case, ExpertCase, ExpertExperience, Formula
from app.tcm import classify_toxicity

DOMAIN = "妇科"

FORMULAS = [
    {"name": "烛宫丹", "composition": "蛇床子、白矾、母丁香、肉桂、杏仁、吴萸、北细辛、砂仁、牡蛎、菟丝子、薏苡仁、川椒、麝香", "function": "温宫散寒、杀虫止带", "indication": "白带(带下)、滴虫性阴道炎", "usage": "研末蜂蜜拌丸如龙眼大,纱布包,纳入阴道(坐药)", "usage_type": "外用"},
    {"name": "蛇花水", "composition": "蛇床子、花椒、白矾、杏仁、艾叶", "function": "杀虫止痒、清洁阴道", "indication": "白带外洗、坐药前冲洗", "usage": "煎水去渣,冲洗阴道", "usage_type": "外用"},
]

DOSAGES = {
    "烛宫丹": "蛇床子120g、白矾/母丁香/肉桂/杏仁/吴萸/北细辛/砂仁/牡蛎/菟丝子/薏苡仁/川椒各90g、麝香3g。研末,30%生蜂蜜拌丸",
    "蛇花水": "蛇床子30g、花椒3g、白矾15g、杏仁15g、艾叶15g。煎水冲洗",
}

EXPERT = [
    {"category": "妇科", "expert_name": "",
     "syndrome_points": "白带(带下)分虚寒、湿热、肝郁、脾虚等型:虚寒者带如痰涕、色白、脐腹作痛、畏寒、脉沉迟细弱;湿热者带黄赤似浓涕、喜凉恶热、脉实大洪数;肝郁者胸胁胀满、带下清血滑利、脉弦数;脾虚者带黄似脓有臭、纳减、脉迟弱。",
     "internal_treatment": "内治分八法:散寒、固脱、利湿、清热、补脾、疏肝、益肾、升阳。",
     "external_treatment": "烛宫丹坐药(蛇床子、白矾、母丁香、肉桂、杏仁、吴萸、细辛、砂仁、牡蛎、菟丝子、薏苡仁、川椒、麝香,蜜丸纱布包纳阴道),配蛇花水冲洗。滴虫性白带疗效100%。",
     "source": ""},
]

CASES = [
    {"category": "妇科", "expert_name": "", "diagnosis": "顽固性白带(带下)",
     "history": "张觉人原配爱人即顽固性白带典型患者,自民国元年(1912)结婚后至民国八年(1919)都未生育,原因即因白带。历经中西医药治疗均未彻底根除,白带量多、缠绵淋漓。",
     "syndrome": "湿热下注,带脉失约",
     "treatment": "以烛宫丹坐药纳入阴道、蛇花水冲洗,初用每天换药1次、3天后两三天换药1次,轻症三五枚、重者不超过15枚即愈。",
     "effect": "两周内全部治愈,后连生子女3人均健壮,未复发;50年临床中用此方治愈白带不下数百人,滴虫性白带疗效达100%。"},
]

CASE_PATIENTS = [
    ("张妻", "女", None, None),
]


async def seed() -> None:
    await init_db()
    async with SessionLocal() as db:
        # 幂等:先清妇科域旧数据
        await db.execute(delete(ExpertExperience).where(ExpertExperience.domain == DOMAIN))
        await db.execute(delete(ExpertCase).where(ExpertCase.domain == DOMAIN))
        await db.execute(delete(Case).where(Case.domain == DOMAIN))
        existing = {n: f for n, f in (await db.execute(select(Formula.name, Formula))).all()}
        added = 0
        updated = 0
        contraindications = "坐药/外洗,仅供外用,孕妇及经期忌用。"
        for f in FORMULAS:
            if f["name"] in existing:
                row = existing[f["name"]]
                row.composition = f["composition"]
                row.dosage = DOSAGES.get(f["name"])
                row.function = f["function"]
                row.indication = f.get("indication", "")
                row.usage_type = f["usage_type"]
                row.usage = f["usage"]
                row.contraindications = contraindications
                row.toxicity = classify_toxicity(f["composition"], f["usage_type"])
                row.domain = DOMAIN
                row.source = "《红蓼山馆医集》"
                updated += 1
            else:
                db.add(Formula(
                    name=f["name"],
                    source="《红蓼山馆医集》",
                    composition=f["composition"],
                    dosage=DOSAGES.get(f["name"]),
                    function=f["function"],
                    indication=f.get("indication", ""),
                    method=f["usage_type"],
                    usage_type=f["usage_type"],
                    usage=f["usage"],
                    contraindications=contraindications,
                    toxicity=classify_toxicity(f["composition"], f["usage_type"]),
                    domain=DOMAIN,
                ))
                added += 1
        for e in EXPERT:
            db.add(ExpertExperience(**e, domain=DOMAIN))
        for c in CASES:
            db.add(ExpertCase(**c, domain=DOMAIN))
        for c, meta in zip(CASES, CASE_PATIENTS):
            db.add(Case(
                patient_name=meta[0],
                gender=meta[1],
                age=meta[2],
                disease_id=None,
                chief_complaint=c["diagnosis"],
                history=c.get("history", ""),
                syndrome=c["syndrome"],
                treatment=c["treatment"],
                effect=c["effect"],
                source="名家",
                domain=DOMAIN,
            ))
        await db.commit()
    print(f"✅ 妇科录入完成: 新增 {added} 首 / 更新 {updated} 首 + {len(EXPERT)} 病种经验 + {len(CASES)} 验案")


if __name__ == "__main__":
    asyncio.run(seed())
