"""录入——骨伤科方(张觉人《红蓼山馆医集》马钱子组方/接骨跌打方)

用法: cd backend && python3 -m scripts.seed_orthopedics
"""
import asyncio

from sqlalchemy import delete, select

from app.database import SessionLocal, init_db
from app.models import Formula
from app.tcm import build_warnings, classify_toxicity

DOMAIN = "骨伤"

# 骨伤/马钱子组方(接骨、跌打、痹证)
FORMULAS = [
    {"name": "秘传接骨丹", "composition": "制马钱子、制枳壳、土鳖虫、三七、乳香、没药、血竭、制自然铜、闹羊花", "function": "接骨续筋、消肿止痛", "indication": "跌打损伤、骨折", "usage": "研细末,每服2~2.5g,黄酒送服,忌风", "usage_type": "内服"},
    {"name": "接骨至灵丹", "composition": "马钱子、枳壳、乳香、制自然铜、地鳖虫", "function": "接骨续损、活血止痛", "indication": "骨折及一切跌打损伤", "usage": "研末,每服6g,好酒送服", "usage_type": "内服"},
    {"name": "九分散", "composition": "马钱子(去毛)、麻黄、乳香、没药", "function": "活血散瘀、续筋接骨", "indication": "跌打损伤(青肿、错折、破皮)", "usage": "研末,每服2.7g黄酒送服,或烧酒调敷患处;孕妇忌内服", "usage_type": "内服外用"},
    {"name": "加味九分散", "composition": "马钱子、麻黄、乳香、没药、土鳖、自然铜", "function": "活血散瘀、续筋接骨", "indication": "跌打损伤", "usage": "研末,黄酒调敷患处,内伤服2.7g黄酒送下", "usage_type": "内服外用"},
    {"name": "舒筋活血散", "composition": "土鳖、乳香、没药、大黄、血竭、骨碎补、红花、制自然铜、制马钱子", "function": "活血逐瘀、止痛消肿、接骨", "indication": "骨折、跌打损伤", "usage": "研末,每服4.5g,早晚各一次,至骨折痊愈", "usage_type": "内服"},
    {"name": "伤科白药", "composition": "马钱子、枳壳、三七、青礞石、大海马、苏木", "function": "接骨续损", "indication": "跌打损伤、骨折", "usage": "研末,每服1.5g黄酒送下", "usage_type": "内服"},
    {"name": "骨伤至宝丹", "composition": "制马钱子、制枳壳、土鳖虫、三七、制自然铜、闹羊花、木香", "function": "接骨续损、活血止痛", "indication": "各种骨折", "usage": "研末,每服1.5g,临睡黄酒下", "usage_type": "内服"},
    {"name": "龙马自来丹", "composition": "马钱子、地龙", "function": "通络止痉", "indication": "癫痫、脚气", "usage": "香油炸马钱子至紫研末,加地龙末,面糊为丸如绿豆大,每服1~1.2g临卧盐水送下", "usage_type": "内服"},
    {"name": "振颓丸", "composition": "马钱子、生乳香、生没药、蜈蚣、穿山甲、当归、人参、白术", "function": "通络起废、补气活血", "indication": "半身不遂、肢体痿废", "usage": "蜜丸如梧子大,每服6g,开水送下,孕妇忌服", "usage_type": "内服"},
]

DOSAGES = {
    "秘传接骨丹": "制马钱子30g、制枳壳30g、土鳖虫10个、三七3g、乳香15g、没药15g、血竭60g、制自然铜3g、闹羊花15g(酒炒)。研末,每服2~2.5g",
    "接骨至灵丹": "马钱子30g、枳壳21g、乳香22.5g、制自然铜6g、地鳖虫30g。研末,每服6g",
    "九分散": "马钱子(去毛)120g、麻黄120g、乳香120g、没药120g。研末,每服2.7g",
    "加味九分散": "马钱子、麻黄、乳香、没药、土鳖、自然铜各等分。研末",
    "舒筋活血散": "土鳖6g、乳香6g、没药6g、大黄6g、血竭9g、骨碎补6g、红花6g、制自然铜9g、制马钱子9g。研末,每服4.5g",
    "伤科白药": "马钱子30g、枳壳(炒)60g、三七15g、青礞石15g、大海马(焙干)1对、苏木18g。研末,每服1.5g",
    "骨伤至宝丹": "制马钱子30g、制枳壳60g、土鳖虫21个、三七15g、制自然铜15g、闹羊花1.5g、木香1.5g。研末,每服1.5g",
    "龙马自来丹": "马钱子240g、地龙8条。香油炸马钱子至紫,面糊为丸,每服1~1.2g",
    "振颓丸": "马钱子30g、生乳香30g、生没药30g、蜈蚣5条、穿山甲30g、当归30g、人参60g、白术60g。蜜丸,每服6g",
}


async def seed() -> None:
    await init_db()
    async with SessionLocal() as db:
        existing = {n: f for n, f in (await db.execute(select(Formula.name, Formula))).all()}
        added = 0
        updated = 0
        for f in FORMULAS:
            comp = f["composition"]
            ind = f.get("indication", "")
            usage_type = f["usage_type"]
            contraindications = build_warnings(comp, ind, usage_type)
            toxicity = classify_toxicity(comp, usage_type)
            if f["name"] in existing:
                row = existing[f["name"]]
                row.composition = comp
                row.dosage = DOSAGES.get(f["name"])
                row.function = f["function"]
                row.indication = ind
                row.usage_type = usage_type
                row.usage = f["usage"]
                row.contraindications = contraindications
                row.toxicity = toxicity
                row.domain = DOMAIN
                row.source = "《红蓼山馆医集》"
                updated += 1
            else:
                db.add(Formula(
                    name=f["name"],
                    source="《红蓼山馆医集》",
                    composition=comp,
                    dosage=DOSAGES.get(f["name"]),
                    function=f["function"],
                    indication=ind,
                    method="伤科",
                    usage_type=usage_type,
                    usage=f["usage"],
                    contraindications=contraindications,
                    toxicity=toxicity,
                    domain=DOMAIN,
                ))
                added += 1
        await db.commit()
    print(f"✅ 骨伤科录入完成: 新增 {added} 首 / 更新 {updated} 首")


if __name__ == "__main__":
    asyncio.run(seed())
