"""录入——外科四大绝症与八种险症(马培之《外科传薪集》临证心法)
四大绝症:板疳、失荣、乳癌、肾漏(难治,须向病家说明)
八种险症:百会疽、当胸心漏、背中对心发、两腰肾枢发、腹中疽、尾闾对口、谷道悬痈、腿上伏兔疽
用法: cd backend && python3 -m scripts.seed_dangerous
"""
import asyncio

from sqlalchemy import delete, select

from app.database import SessionLocal, init_db
from app.models import Disease, TreatmentRule

# (病名, 类别, 好发部位, 疮形特点, 特征, 鉴别, 预后, 西医对照, 是否绝症)
DANGEROUS = [
    # ===== 四大绝症 =====
    ("失荣", "疮疡杂病", "颈部(耳前后、颈侧)", "颈部肿块,坚硬如石,推之不移,皮色不变或紫暗,日久溃破翻花", "颈部无痛性肿块渐大,坚硬如岩,常见中老年,消瘦乏力", "与瘰疬(多串珠、可软溃)、颈痈(红肿热痛)鉴别", "四大绝症之一,相当于颈部恶性淋巴瘤/淋巴结转移癌,须转诊肿瘤专科", "颈部恶性肿瘤/淋巴瘤", True),
    ("乳癌", "乳岩", "乳房", "乳房肿块坚硬如石,边界不清,凹凸不平,皮核相亲,后期乳头内陷、橘皮样变、溃破翻花", "乳房无痛性肿块渐大,质地坚硬,常见中年女性", "与乳癖(肿块柔软、随月经消长)、乳痈(红肿热痛、成脓)鉴别", "四大绝症之一,即乳岩晚期,须转诊乳腺外科", "乳腺癌", True),
    ("肾漏", "疮疡杂病", "腰部(肾俞穴附近)", "腰部窦道/漏管,脓水清稀淋漓,久不收口", "腰部慢性流脓窦道,常见腰椎结核/肾周脓肿穿破", "与腰痈(急性红肿成脓)、附骨疽鉴别", "四大绝症之一,腰部窦道多属难治,须查明病因(结核/脓肿)", "腰部慢性窦道/瘘管", True),
    ("板疳", "疮疡杂病", "口唇、生殖器", "硬结如板,边缘整齐,不痛不痒,基底坚硬,溃后如翻花", "早期硬下疳(梅毒初疮),不痛不痒,传染性强", "与软下疳(疼痛、边缘不规则)、口疮鉴别", "四大绝症之一,即梅毒硬下疳,须转性病专科规范治疗", "梅毒硬下疳", True),
    # ===== 八种险症 =====
    ("百会疽", "有头疽", "头顶百会穴", "头顶痈肿,红肿高突,根脚散漫,疮顶如蜂房", "生于百会穴(诸阳之会),毒邪易内陷", "与头疖(浅表小疮)、秃发疮鉴别", "八种险症之一,头顶疽易走黄内陷,注意补养气血,须密切观察", "头顶部痈", False),
    ("当胸心漏", "疮疡杂病", "胸前心口(膻中)处", "胸前窦道/漏管,直通胸腔,脓液随呼吸而出", "胸前漏管深通胸腔,危险", "与胸壁痈(未成漏)鉴别", "八种险症之一,胸漏恐通心包/胸腔,须转胸外科", "胸壁窦道", False),
    ("背中对心发", "有头疽", "背部(对心处)", "背部发背,对心而发,红肿如盘,根脚散漫,疮顶多脓头", "背部对心处发背,毒易内陷心包", "与一般背疽(位置偏侧)鉴别", "八种险症之一,对心发易内陷,须重托补,密切观察", "背部痈(对心发)", False),
    ("两腰肾枢发", "疮疡杂病", "腰部(两侧肾俞穴)", "腰部两侧痈肿,漫肿无头或高突,皮色不变或红", "生于腰部肾枢处,毒易内入肾脏", "与肾漏(慢性漏管)、腰痈鉴别", "八种险症之一,腰部痈须防内陷及成漏", "腰部痈", False),
    ("腹中疽", "疮疡杂病", "腹部", "腹壁痈疽,红肿疼痛,或漫肿,深达腹肌", "生于腹壁,深则及腹膜", "与肠痈(腹痛拒按、转移性右下腹痛)鉴别", "八种险症之一,腹壁疽深则恐及腹腔,须转外科", "腹壁痈", False),
    ("尾闾对口", "有头疽", "尾骶部(尾闾穴)", "尾骶部痈肿,红肿高突,疮顶如蜂房,久不收口易成漏", "生于尾骶部,局部血运差,易溃烂成漏", "与尾骶藏毛窦、骶部压疮鉴别", "八种险症之一,尾骶痈易成漏难愈", "尾骶部痈", False),
    ("谷道悬痈", "疮疡杂病", "肛门(会阴)", "肛门周围痈肿,红肿热痛,深则及肛周,成脓后或从肛门溃出", "生于肛门(谷道)会阴处,即肛周脓肿", "与痔疮(便血、脱出)、肛瘘(已有漏管)鉴别", "八种险症之一,肛周脓肿须及时切开排脓,防成肛瘘", "肛周脓肿", False),
    ("腿上伏兔疽", "无头疽", "大腿(伏兔穴,股外侧)", "大腿股外侧深部漫肿,皮色不变或微红,疼痛彻骨,不化脓或溃后流清稀脓", "生于大腿伏兔处之附骨疽,深在筋骨", "与大腿痈(浅表红肿)、流注(多发游走)鉴别", "八种险症之一,伏兔疽深在筋骨,难溃难敛", "股骨骨髓炎/大腿深部脓肿", False),
]


async def seed() -> None:
    await init_db()
    async with SessionLocal() as db:
        existing = {n: d for n, d in (await db.execute(select(Disease.name, Disease))).all()}
        added = updated = 0
        # 险症绝症阴阳:四大绝症(慢性恶证)多阴证;有头疽类(百会/对心发/对口)阳证;漏管/无头疽阴证
        IS_YANG = {
            "失荣": False, "乳癌": False, "肾漏": False, "板疳": False,
            "百会疽": True, "当胸心漏": False, "背中对心发": True,
            "两腰肾枢发": True, "腹中疽": True, "尾闾对口": True,
            "谷道悬痈": True, "腿上伏兔疽": False,
        }
        for name, category, loc, morph, char, diff, prog, west, is_doomed in DANGEROUS:
            data = dict(
                name=name, category=category, location=loc, morphology=morph,
                characteristics=char, differential=diff, prognosis=prog,
                western_equiv=west, is_dangerous=True, is_sores=False,
                is_yang=IS_YANG.get(name, True),
                source="《外科传薪集》",
            )
            if name in existing:
                d = existing[name]
                for k, v in data.items():
                    setattr(d, k, v)
                updated += 1
            else:
                db.add(Disease(**data))
                added += 1
        await db.commit()

        # 为险症/绝症补"转诊"论治规则(初起期)
        dname_to_id = {n: i for i, n in (await db.execute(select(Disease.id, Disease.name))).all()}
        await db.execute(delete(TreatmentRule).where(TreatmentRule.note.like("险症绝症转诊%")))
        rules = 0
        for name, *_ in DANGEROUS:
            if name not in dname_to_id:
                continue
            db.add(TreatmentRule(
                disease_id=dname_to_id[name],
                stage="初起",
                syndrome_id=None,
                internal_formula_id=None,
                external_treatment="以外科常规换药、引流为主,不作过度攻伐。",
                nursing="严禁挤压、过早切开;注意观察病情变化。",
                note="险症绝症转诊:本病属外科险症/绝症,须向病家说明病情,并及时转诊上级医院/专科(肿瘤科、胸外科、性病科等)规范诊治,本系统仅供辨证参考。",
                is_specific=False,
            ))
            rules += 1
        await db.commit()
    print(f"✅ 险症绝症录入完成: 新增 {added} 病种 / 更新 {updated} 病种(四大绝症4 + 八种险症8) + 转诊规则 {rules} 条")


if __name__ == "__main__":
    asyncio.run(seed())
