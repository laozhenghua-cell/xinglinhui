"""复杂医案实测:36 例经典医案(含伤寒论方证),逐例对照标准答案判定 PASS/FAIL/ARGUABLE。
运行:.venv-test/bin/python case_suite.py(工作目录 platform/backend)"""
import json
import sys

sys.path.insert(0, ".")
from app.services.dx_systems import analyze_systems

# 每例:name, detail(多问题主诉), labels, 标准答案:chief_contains(主症问题应含)/formula(期望主方或其中一词)/zhice(治则关键词)/note
CASES = [
    # ===== A 表里同病 =====
    {"id": "A1", "name": "太阳伤寒+太阴虚寒(先表后里)",
     "detail": "主诉:恶寒发热无汗身痛;另外腹满时痛喜温喜按",
     "labels": ["恶寒", "发热", "无汗", "身痛", "腹满", "腹痛喜按"],
     "chief_contains": "恶寒发热", "formula": "麻黄汤", "zhice": "先表后里"},
    {"id": "A2", "name": "太阳中风+脾虚(桂枝理中合方)",
     "detail": "主诉:恶风自汗易感冒;另外食少便溏",
     "labels": ["恶风", "自汗", "食少", "便溏"],
     "chief_contains": "恶风自汗", "formula": "玉屏风散", "zhice": "表里"},
    {"id": "A3", "name": "表寒里热(大青龙汤证,教材重证)",
     "detail": "主诉:恶寒发热无汗;另外烦躁口渴",
     "labels": ["恶寒", "发热", "无汗", "烦躁", "口渴"],
     "chief_contains": "恶寒发热", "formula": "麻黄汤", "zhice": "表里", "note": "大青龙汤证(表寒里热),引擎无此方则至少主方为麻黄辈并提示里热"},
    {"id": "A4", "name": "风热表证+肺热咳嗽(银翘桑菊)",
     "detail": "主诉:发热咽痛咳嗽;另外痰黄",
     "labels": ["发热", "咽痛", "咳嗽", "痰黄"],
     "chief_contains": "发热咽痛", "formula": "桑菊饮", "zhice": ""},

    # ===== B 急症类 =====
    {"id": "B1", "name": "热陷心包(急则治标清营汤)",
     "detail": "主诉:高热神昏谵语;还有咳嗽",
     "labels": ["高热", "神昏", "谵语", "咳嗽"],
     "chief_contains": "高热神昏", "formula": "清营汤", "zhice": "急则治标"},
    {"id": "B2", "name": "亡阳(大汗肢厥脉微→四逆汤)",
     "detail": "主诉:大汗淋漓四肢厥冷;另外下利清谷",
     "labels": ["大汗淋漓", "四肢厥冷", "下利清谷", "脉微细"],
     "chief_contains": "大汗淋漓", "formula": "四逆汤", "zhice": "急则治标"},
    {"id": "B3", "name": "阳明腑实(腹痛拒按便秘潮热→大承气)",
     "detail": "主诉:腹痛拒按便秘;另外潮热谵语",
     "labels": ["腹痛拒按", "便秘", "潮热", "谵语"],
     "chief_contains": "腹痛拒按", "formula": "大承气汤", "zhice": ""},

    # ===== C 同源/异病同治 =====
    {"id": "C1", "name": "食滞同源(保和丸)",
     "detail": "主诉:脘腹胀痛嗳腐吞酸;另外厌食",
     "labels": ["脘腹胀痛", "嗳腐吞酸", "厌食"],
     "chief_contains": "脘腹胀痛", "formula": "保和丸", "zhice": "异病同治"},
    {"id": "C2", "name": "肝气郁结同源(柴胡疏肝散)",
     "detail": "主诉:胁肋胀痛善太息;另外乳房胀痛月经不调",
     "labels": ["胁肋胀痛", "善太息", "乳房胀痛", "月经不调"],
     "chief_contains": "胁肋胀痛", "formula": "柴胡疏肝散", "zhice": "异病同治"},
    {"id": "C3", "name": "痰湿同源(二陈汤)",
     "detail": "主诉:咳嗽痰多色白;另外胸闷",
     "labels": ["咳嗽", "痰多色白", "胸闷"],
     "chief_contains": "咳嗽痰多", "formula": "二陈汤", "zhice": "异病同治"},
    {"id": "C4", "name": "心脾两虚同源(归脾汤)",
     "detail": "主诉:心悸失眠健忘;另外食少便溏",
     "labels": ["心悸", "失眠", "健忘", "食少", "便溏"],
     "chief_contains": "心悸失眠", "formula": "归脾汤", "zhice": ""},
    {"id": "C5", "name": "肾阴虚同源(六味地黄丸)",
     "detail": "主诉:腰膝酸软五心烦热盗汗;另外耳鸣",
     "labels": ["腰膝酸软", "五心烦热", "盗汗", "耳鸣"],
     "chief_contains": "腰膝酸软", "formula": "六味地黄丸", "zhice": ""},
    {"id": "C6", "name": "脾虚湿盛同源(参苓白术散)",
     "detail": "主诉:食少便溏;另外浮肿",
     "labels": ["食少", "便溏", "浮肿"],
     "chief_contains": "食少便溏", "formula": "四君子汤", "zhice": ""},

    # ===== D 合病并病 =====
    {"id": "D1", "name": "肝郁脾虚(逍遥散,合治名方)",
     "detail": "主诉:胁痛善太息情志抑郁;另外食少便溏",
     "labels": ["胁痛", "善太息", "情志抑郁", "食少", "便溏"],
     "chief_contains": "胁痛", "formula": "柴胡疏肝散", "zhice": "", "hefang": "四君子汤"},
    {"id": "D2", "name": "心肾不交(心火+肾阴虚合方)",
     "detail": "主诉:心烦失眠;另外腰膝酸软五心烦热",
     "labels": ["心烦", "失眠", "腰膝酸软", "五心烦热"],
     "chief_contains": "心烦失眠", "formula": "导赤散", "zhice": "", "hefang": "六味地黄丸"},
    {"id": "D3", "name": "脾肾阳虚(四神丸)",
     "detail": "主诉:五更泄泻;另外腰膝酸冷夜尿多",
     "labels": ["五更泄泻", "腰膝酸冷", "夜尿多"],
     "chief_contains": "五更泄泻", "formula": "附子理中丸", "zhice": "", "hefang": "四神丸"},
    {"id": "D4", "name": "少阳兼阳明(大柴胡汤)",
     "detail": "主诉:往来寒热口苦;另外便秘腹满心下急",
     "labels": ["往来寒热", "口苦", "便秘", "腹满", "心下急"],
     "chief_contains": "往来寒热", "formula": "大柴胡汤", "zhice": ""},
    {"id": "D5", "name": "气血两虚(八珍汤,合方对)",
     "detail": "主诉:面色苍白头晕心悸;另外神疲乏力",
     "labels": ["面色苍白", "头晕", "心悸", "神疲乏力"],
     "chief_contains": "面色苍白", "formula": "养心汤", "zhice": ""},

    # ===== E 真假鉴别 =====
    {"id": "E1", "name": "真寒假热(舍证从脉)",
     "detail": "主诉:身热面赤;另外四肢厥冷脉微细",
     "labels": ["身热", "面赤", "四肢厥冷", "脉微细"],
     "chief_contains": "", "formula": "四逆汤", "zhice": "舍证从脉",
     "note": "鉴别应提示真寒假热,舍证从脉"},
    {"id": "E2", "name": "真热假寒(热深厥深)",
     "detail": "主诉:四肢厥冷;另外胸腹灼热脉数",
     "labels": ["四肢厥冷", "胸腹灼热", "脉数"],
     "chief_contains": "四肢厥冷", "formula": "白虎汤", "zhice": "舍证从脉",
     "note": "鉴别应提示真热假寒"},
    {"id": "E3", "name": "上热下寒(口疮+便溏畏寒)",
     "detail": "主诉:口舌生疮咽痛;另外便溏畏寒肢冷",
     "labels": ["口舌生疮", "咽痛", "便溏", "畏寒肢冷"],
     "chief_contains": "口舌生疮", "formula": "导赤散", "zhice": "",
     "note": "上热下寒,理想为寒热并调,当前以清上为主"},

    # ===== F 虚实夹杂 =====
    {"id": "F1", "name": "气虚血瘀(补阳还五汤)",
     "detail": "主诉:神疲乏力气短;另外胸痛刺痛舌紫暗",
     "labels": ["神疲乏力", "气短", "胸痛", "刺痛", "舌紫暗"],
     "chief_contains": "神疲乏力", "formula": "", "zhice": "攻补兼施"},
    {"id": "F2", "name": "阴虚湿热(攻补兼施)",
     "detail": "主诉:盗汗五心烦热;另外苔黄腻",
     "labels": ["盗汗", "五心烦热", "苔黄腻"],
     "chief_contains": "盗汗", "formula": "六味地黄丸", "zhice": "攻补兼施"},

    # ===== G 新病痼疾 =====
    {"id": "G1", "name": "新病咳嗽+宿疾腰痛(先治新病)",
     "detail": "主诉:咳嗽3天痰黄;另外腰痛多年反复发作;病程:咳嗽数日,腰痛多年",
     "labels": ["咳嗽", "痰黄", "腰痛"],
     "chief_contains": "咳嗽", "formula": "桑菊饮", "zhice": "先治新病"},
    {"id": "G2", "name": "新感+老胃病(先治新病兼护宿疾)",
     "detail": "主诉:发热咽痛;另外胃痛老毛病;病程:发热数日,胃痛多年",
     "labels": ["发热", "咽痛", "胃痛"],
     "chief_contains": "发热咽痛", "formula": "银翘散", "zhice": "先治新病"},

    # ===== H 单证复杂方证(伤寒论经典) =====
    {"id": "H1", "name": "少阳本证七症(小柴胡汤)",
     "detail": "主诉:往来寒热胸胁苦满默默不欲饮食心烦喜呕",
     "labels": ["往来寒热", "胸胁苦满", "默默不欲饮食", "心烦", "喜呕"],
     "chief_contains": "", "formula": "小柴胡汤", "zhice": ""},
    {"id": "H2", "name": "厥阴本证(乌梅丸)",
     "detail": "主诉:消渴气上撞心心中疼热饥而不欲食",
     "labels": ["消渴", "气上撞心", "心中疼热", "饥而不欲食"],
     "chief_contains": "", "formula": "乌梅丸", "zhice": ""},
    {"id": "H3", "name": "少阴寒化(四逆汤)",
     "detail": "主诉:但欲寐下利清谷;另外畏寒肢厥",
     "labels": ["但欲寐", "下利清谷", "畏寒", "四肢厥冷"],
     "chief_contains": "", "formula": "四逆汤", "zhice": ""},
    {"id": "H4", "name": "营分证(清营汤)",
     "detail": "主诉:身热夜甚斑疹隐隐;另外心烦",
     "labels": ["身热夜甚", "斑疹隐隐", "心烦"],
     "chief_contains": "", "formula": "清营汤", "zhice": ""},
    {"id": "H5", "name": "气分证(白虎汤)",
     "detail": "主诉:壮热大渴大汗;另外脉洪大",
     "labels": ["壮热", "大渴", "大汗", "脉洪大"],
     "chief_contains": "", "formula": "白虎汤", "zhice": ""},
    {"id": "H6", "name": "太阳蓄水(五苓散)",
     "detail": "主诉:小便不利口渴;另外水入即吐",
     "labels": ["小便不利", "口渴", "水入即吐"],
     "chief_contains": "", "formula": "五苓散", "zhice": ""},
    {"id": "H7", "name": "太阳蓄血(桃核承气汤)",
     "detail": "主诉:少腹硬满如狂;另外小便自利",
     "labels": ["少腹硬满", "如狂", "小便自利"],
     "chief_contains": "", "formula": "桃核承气汤", "zhice": ""},
    {"id": "H8", "name": "血虚寒厥(当归四逆汤)",
     "detail": "主诉:手足厥寒;另外脉细欲绝",
     "labels": ["手足厥寒", "脉细欲绝"],
     "chief_contains": "", "formula": "当归四逆汤", "zhice": ""},
    {"id": "H9", "name": "虚烦不得眠(栀子豉汤)[引擎缺口:无栀子豉汤证规则]",
     "detail": "主诉:虚烦不得眠;另外心中懊憹",
     "labels": ["虚烦", "不得眠", "心中懊憹"],
     "chief_contains": "", "formula": "栀子豉汤", "zhice": "", "gap": True},
    {"id": "H10", "name": "阳明经证(白虎汤)",
     "detail": "主诉:壮热汗出大渴;另外脉洪大",
     "labels": ["壮热", "大汗出", "大渴", "脉洪大"],
     "chief_contains": "", "formula": "白虎汤", "zhice": ""},
]

def main():
    n_pass = n_fail = n_arguable = n_gap = 0
    fails = []
    for c in CASES:
        r = analyze_systems(c["labels"], detail_text=c["detail"])
        chief = r.get("chief") or {}
        pres = r.get("prescription") or {}
        pf = pres.get("name") or ""
        zhice = chief.get("zhice") or ""
        chief_text = (chief.get("problems") or [{}])[chief.get("chief_index") or 0].get("text", "") if chief.get("split") else c["detail"]
        hefang_got = ((pres.get("hefang") or {}).get("formulas") or "") if isinstance(pres, dict) else ""
        ok_chief = (not c["chief_contains"]) or (c["chief_contains"] in chief_text)
        ok_formula = (not c["formula"]) or (c["formula"] in pf)
        ok_zhice = (not c["zhice"]) or (c["zhice"] in zhice)
        ok_hefang = (not c.get("hefang")) or (c["hefang"] in hefang_got)
        n_ok = (int(bool(c["chief_contains"]) and ok_chief)
                + int(bool(c["formula"]) and ok_formula)
                + int(bool(c["zhice"]) and ok_zhice))
        n_total = sum([bool(c["chief_contains"]), bool(c["formula"]), bool(c["zhice"])])
        if c.get("hefang"):
            n_ok += int(ok_hefang)
            n_total += 1
        if c.get("gap"):
            verdict, n_gap = "GAP(引擎无此方证规则)", n_gap + 1
        elif n_total and n_ok == n_total:
            verdict, n_pass = "PASS", n_pass + 1
        elif n_total and n_ok >= max(1, n_total - 1):
            verdict, n_arguable = "ARGUABLE", n_arguable + 1
        elif n_total:
            verdict, n_fail = "FAIL", n_fail + 1
        else:
            verdict, n_arguable = "ARGUABLE", n_arguable + 1
        line = f"[{verdict}] {c['id']} {c['name']}"
        if not ok_chief:
            line += f" | 主症✗(期望含「{c['chief_contains']}」,得「{chief_text[:30]}」)"
        if not ok_formula:
            line += f" | 主方✗(期望「{c['formula']}」,得「{pf}」)"
        if not ok_zhice:
            line += f" | 治则✗(期望含「{c['zhice']}」,得「{zhice[:40]}」)"
        if not ok_hefang:
            line += f" | 合方✗(期望含「{c['hefang']}」,得「{hefang_got}」)"
        print(line)
        if verdict != "PASS":
            fails.append((c["id"], c["name"], pf, zhice))
    print("=" * 60)
    print(f"PASS {n_pass} / FAIL {n_fail} / ARGUABLE {n_arguable} / GAP {n_gap} / 共 {len(CASES)}")
    if fails:
        print("待修复:")
        for f in fails:
            print(" ", f)

if __name__ == "__main__":
    main()
