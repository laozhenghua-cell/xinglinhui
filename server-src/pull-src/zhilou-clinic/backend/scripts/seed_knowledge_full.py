"""
华夏痔瘘辅助诊疗系统 - 完整知识库种子数据
来源：老中医临床经验总结（中医研究院广安门医院肛肠科）
整理人：寇玉明（学术思想继承人）
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.models import AnorectalHerb, AnorectalFormula, AnorectalCase, PreventionGuide

# ============ 肛肠科常用中药（扩充版）============
HERBS = [
    # 止血药类
    {"name": "槐花", "category": "止血药", "properties": "苦，微寒", "meridians": "肝、大肠经",
     "effects": "凉血止血，清肝泻火", "indications": "肠风便血，痔血", "contraindications": "脾胃虚寒者慎用",
     "dosage": "6-15克", "is_common": True},
    {"name": "地榆", "category": "止血药", "properties": "苦酸，微寒", "meridians": "肝、大肠经",
     "effects": "凉血止血，解毒敛疮", "indications": "便血，痔血，血痢，疮疡", "contraindications": "大面积烧伤不宜外用",
     "dosage": "10-15克", "is_common": True},
    {"name": "侧柏叶", "category": "止血药", "properties": "苦涩，微寒", "meridians": "肺、肝、大肠经",
     "effects": "凉血止血，化痰止咳", "indications": "各种出血证", "contraindications": "无",
     "dosage": "10-15克", "is_common": True},
    {"name": "仙鹤草", "category": "止血药", "properties": "苦涩，平", "meridians": "肺、肝、脾经",
     "effects": "收敛止血，截疟，止痢", "indications": "各种出血证", "contraindications": "无明显禁忌",
     "dosage": "10-15克", "is_common": True},
    {"name": "槐角", "category": "止血药", "properties": "苦，寒", "meridians": "肝、大肠经",
     "effects": "清热泻火，凉血止血", "indications": "肠风便血，痔疮肿痛", "contraindications": "脾胃虚寒者慎用",
     "dosage": "6-12克", "is_common": True},

    # 补益药类
    {"name": "黄芪", "category": "补气药", "properties": "甘，微温", "meridians": "脾、肺经",
     "effects": "补气升阳，益卫固表，托毒生肌", "indications": "脾虚气陷，直肠脱垂，气虚便血",
     "contraindications": "实证、阳证疮疡不宜", "dosage": "15-30克", "is_common": True},
    {"name": "党参", "category": "补气药", "properties": "甘，平", "meridians": "脾、肺经",
     "effects": "补中益气，健脾益肺", "indications": "脾肺气虚，气短乏力", "contraindications": "实证慎用",
     "dosage": "10-15克", "is_common": True},
    {"name": "白术", "category": "补气药", "properties": "苦甘，温", "meridians": "脾、胃经",
     "effects": "健脾益气，燥湿利水", "indications": "脾虚食少，大便溏薄", "contraindications": "阴虚燥渴者慎用",
     "dosage": "10-15克", "is_common": True},
    {"name": "当归", "category": "补血药", "properties": "甘辛，温", "meridians": "肝、心、脾经",
     "effects": "补血活血，调经止痛，润肠通便", "indications": "血虚便秘，痔疮出血",
     "contraindications": "湿盛中满、大便溏泄者慎用", "dosage": "6-12克", "is_common": True},
    {"name": "熟地", "category": "补血药", "properties": "甘，微温", "meridians": "肝、肾经",
     "effects": "补血滋阴，益精填髓", "indications": "血虚萎黄，眩晕心悸", "contraindications": "脾虚便溏者慎用",
     "dosage": "10-15克", "is_common": True},
    {"name": "生地", "category": "补血药", "properties": "甘，寒", "meridians": "心、肝、肾经",
     "effects": "清热凉血，养阴生津", "indications": "血热妄行，便血", "contraindications": "脾虚泄泻者慎用",
     "dosage": "10-15克", "is_common": True},

    # 清热药类
    {"name": "黄连", "category": "清热药", "properties": "苦，寒", "meridians": "心、脾、胃、胆、大肠经",
     "effects": "清热燥湿，泻火解毒", "indications": "湿热痢疾，肛门肿痛", "contraindications": "脾胃虚寒者忌用",
     "dosage": "3-10克", "is_common": True},
    {"name": "黄芩", "category": "清热药", "properties": "苦，寒", "meridians": "肺、胆、脾、大肠经",
     "effects": "清热燥湿，泻火解毒，止血安胎", "indications": "湿热泻痢，便血", "contraindications": "脾胃虚寒者不宜",
     "dosage": "6-15克", "is_common": True},
    {"name": "黄柏", "category": "清热药", "properties": "苦，寒", "meridians": "肾、膀胱、大肠经",
     "effects": "清热燥湿，泻火除蒸，解毒疗疮", "indications": "湿热下注，肛门肿痛", "contraindications": "脾胃虚寒者慎用",
     "dosage": "6-12克", "is_common": True},
    {"name": "栀子", "category": "清热药", "properties": "苦，寒", "meridians": "心、肺、三焦经",
     "effects": "泻火除烦，清热利湿，凉血解毒", "indications": "热毒壅盛，便血", "contraindications": "脾虚便溏者慎用",
     "dosage": "6-10克", "is_common": True},
    {"name": "金银花", "category": "清热药", "properties": "甘，寒", "meridians": "肺、心、胃经",
     "effects": "清热解毒，疏散风热", "indications": "肛周脓肿，疮疡肿毒", "contraindications": "脾胃虚寒者慎用",
     "dosage": "10-20克", "is_common": True},
    {"name": "连翘", "category": "清热药", "properties": "苦，微寒", "meridians": "肺、心、小肠经",
     "effects": "清热解毒，消肿散结", "indications": "痈疽疮毒，瘰疬痰核", "contraindications": "脾胃虚弱者慎用",
     "dosage": "6-15克", "is_common": True},

    # 活血化瘀药类
    {"name": "赤芍", "category": "活血化瘀药", "properties": "苦，微寒", "meridians": "肝经",
     "effects": "清热凉血，散瘀止痛", "indications": "血瘀肿痛，痈肿疮疡", "contraindications": "血虚无瘀者不宜",
     "dosage": "6-12克", "is_common": True},
    {"name": "白芍", "category": "补血药", "properties": "苦酸，微寒", "meridians": "肝、脾经",
     "effects": "养血调经，敛阴止汗，柔肝止痛", "indications": "血虚萎黄，腹痛", "contraindications": "虚寒腹痛者慎用",
     "dosage": "6-15克", "is_common": True},
    {"name": "川芎", "category": "活血化瘀药", "properties": "辛，温", "meridians": "肝、胆、心包经",
     "effects": "活血行气，祛风止痛", "indications": "血瘀气滞诸痛证", "contraindications": "阴虚火旺者慎用",
     "dosage": "3-10克", "is_common": True},
    {"name": "桃仁", "category": "活血化瘀药", "properties": "苦甘，平", "meridians": "心、肝、大肠经",
     "effects": "活血祛瘀，润肠通便", "indications": "血瘀经闭，跌打损伤，肠燥便秘", "contraindications": "孕妇慎用",
     "dosage": "5-10克", "is_common": True},
    {"name": "红花", "category": "活血化瘀药", "properties": "辛，温", "meridians": "心、肝经",
     "effects": "活血通经，散瘀止痛", "indications": "痛经，血瘀腹痛", "contraindications": "孕妇禁用",
     "dosage": "3-10克", "is_common": True},
    {"name": "丹皮", "category": "清热凉血药", "properties": "苦辛，微寒", "meridians": "心、肝、肾经",
     "effects": "清热凉血，活血散瘀", "indications": "热入营血，血滞经闭", "contraindications": "孕妇及月经过多者慎用",
     "dosage": "6-12克", "is_common": True},

    # 理气药类
    {"name": "木香", "category": "理气药", "properties": "辛苦，温", "meridians": "脾、胃、大肠、胆经",
     "effects": "行气止痛，健脾消食", "indications": "脘腹胀痛，泻痢后重", "contraindications": "阴虚津亏者慎用",
     "dosage": "3-10克", "is_common": True},
    {"name": "枳壳", "category": "理气药", "properties": "苦辛，微寒", "meridians": "脾、胃经",
     "effects": "理气宽中，行滞消胀", "indications": "胸胁气滞，胀满疼痛，食积不化", "contraindications": "脾胃虚弱者慎用",
     "dosage": "6-10克", "is_common": True},
    {"name": "槟榔", "category": "驱虫药", "properties": "苦辛，温", "meridians": "胃、大肠经",
     "effects": "杀虫，消积，行气，利水", "indications": "食积气滞，腹胀便秘", "contraindications": "脾虚便溏者慎用",
     "dosage": "3-10克", "is_common": True},

    # 润下药类
    {"name": "麻仁", "category": "润下药", "properties": "甘，平", "meridians": "脾、胃、大肠经",
     "effects": "润肠通便", "indications": "肠燥便秘", "contraindications": "便溏者慎用",
     "dosage": "10-30克", "is_common": True},

    # 祛湿药类
    {"name": "茯苓", "category": "利水渗湿药", "properties": "甘淡，平", "meridians": "心、脾、肾经",
     "effects": "利水渗湿，健脾安神", "indications": "水肿尿少，脾虚食少", "contraindications": "阴虚而无湿热者慎用",
     "dosage": "10-15克", "is_common": True},
    {"name": "泽泻", "category": "利水渗湿药", "properties": "甘淡，寒", "meridians": "肾、膀胱经",
     "effects": "利水渗湿，泄热", "indications": "小便不利，水肿胀满", "contraindications": "肾虚精滑者慎用",
     "dosage": "6-12克", "is_common": True},
    {"name": "车前子", "category": "利水渗湿药", "properties": "甘，寒", "meridians": "肝、肾、肺、小肠经",
     "effects": "清热利尿，渗湿止泻，明目祛痰", "indications": "水肿尿少，湿热泄泻", "contraindications": "肾虚精滑者慎用",
     "dosage": "10-15克", "is_common": True},
    {"name": "苍术", "category": "芳香化湿药", "properties": "辛苦，温", "meridians": "脾、胃经",
     "effects": "燥湿健脾，祛风散寒", "indications": "湿阻中焦，脘腹胀满", "contraindications": "阴虚内热者慎用",
     "dosage": "5-10克", "is_common": True},

    # 收涩药类
    {"name": "五倍子", "category": "收涩药", "properties": "酸涩，寒", "meridians": "肺、大肠、肾经",
     "effects": "敛肺降火，涩肠止泻，固精止遗，敛汗止血", "indications": "肺虚久咳，久泻久痢", "contraindications": "外感咳嗽慎用",
     "dosage": "3-10克", "is_common": True},
    {"name": "乌梅", "category": "收涩药", "properties": "酸涩，平", "meridians": "肝、脾、肺、大肠经",
     "effects": "敛肺，涩肠，生津，安蛔", "indications": "久泻久痢，便血脱肛", "contraindications": "实邪未清者慎用",
     "dosage": "6-12克", "is_common": True},

    # 解表药类
    {"name": "防风", "category": "解表药", "properties": "辛甘，微温", "meridians": "膀胱、肝、脾经",
     "effects": "祛风解表，胜湿止痛，止痉", "indications": "外感风寒，风湿痹痛", "contraindications": "阴血亏虚者慎用",
     "dosage": "5-10克", "is_common": True},
    {"name": "荆芥", "category": "解表药", "properties": "辛，微温", "meridians": "肺、肝经",
     "effects": "祛风解表，透疹止痒，止血", "indications": "感冒风寒，麻疹不透，便血崩漏", "contraindications": "表虚自汗者慎用",
     "dosage": "5-10克", "is_common": True},

    # 升阳药类
    {"name": "升麻", "category": "解表药", "properties": "辛甘，微寒", "meridians": "肺、脾、胃、大肠经",
     "effects": "发表透疹，清热解毒，升举阳气", "indications": "气虚下陷，脱肛", "contraindications": "阴虚火旺者慎用",
     "dosage": "3-10克", "is_common": True},
    {"name": "柴胡", "category": "解表药", "properties": "苦辛，微寒", "meridians": "肝、胆经",
     "effects": "疏散退热，疏肝解郁，升举阳气", "indications": "气虚下陷，脱肛", "contraindications": "肝阳上亢者慎用",
     "dosage": "3-10克", "is_common": True},

    # 更多常用药
    {"name": "人参", "category": "补气药", "properties": "甘，微温", "meridians": "脾、肺、心经",
     "effects": "大补元气，复脉固脱，补脾益肺，生津安神", "indications": "元气虚脱，气血亏虚", "contraindications": "实证、热证忌用",
     "dosage": "3-10克", "is_common": True},
    {"name": "酸枣仁", "category": "安神药", "properties": "甘酸，平", "meridians": "心、肝、胆经",
     "effects": "养心补肝，宁心安神，敛汗生津", "indications": "虚烦不眠，惊悸多梦", "contraindications": "实邪郁火者慎用",
     "dosage": "10-15克", "is_common": True},
    {"name": "龙眼肉", "category": "补血药", "properties": "甘，温", "meridians": "心、脾经",
     "effects": "补益心脾，养血安神", "indications": "气血不足，心悸失眠", "contraindications": "痰火内盛者慎用",
     "dosage": "10-15克", "is_common": True},
    {"name": "远志", "category": "安神药", "properties": "苦辛，微温", "meridians": "心、肾、肺经",
     "effects": "安神益智，祛痰开窍，消肿", "indications": "心肾不交之失眠多梦", "contraindications": "胃溃疡及胃炎患者慎用",
     "dosage": "3-10克", "is_common": True},
    {"name": "大黄", "category": "泻下药", "properties": "苦，寒", "meridians": "脾、胃、大肠、肝、心经",
     "effects": "泻下攻积，清热泻火，凉血解毒，逐瘀通经", "indications": "实热便秘，血热妄行", "contraindications": "孕妇慎用",
     "dosage": "3-12克", "usage_notes": "后下", "is_common": True},
    {"name": "枳实", "category": "理气药", "properties": "苦辛，微寒", "meridians": "脾、胃经",
     "effects": "破气消积，化痰除痞", "indications": "积滞内停，痰湿阻滞", "contraindications": "脾胃虚弱者慎用",
     "dosage": "3-10克", "is_common": True},
    {"name": "瓜蒌仁", "category": "清热化痰药", "properties": "甘，寒", "meridians": "肺、胃、大肠经",
     "effects": "清热化痰，宽胸散结，润肠通便", "indications": "痰热咳嗽，肠燥便秘", "contraindications": "脾虚便溏者慎用",
     "dosage": "10-15克", "is_common": True},
    {"name": "乌药", "category": "理气药", "properties": "辛，温", "meridians": "肺、脾、肾、膀胱经",
     "effects": "行气止痛，温肾散寒", "indications": "气滞疼痛，小便频数", "contraindications": "气虚及内热者慎用",
     "dosage": "6-10克", "is_common": True},
    {"name": "牛膝", "category": "活血药", "properties": "苦酸，平", "meridians": "肝、肾经",
     "effects": "逐瘀通经，补肝肾，强筋骨，利尿通淋，引血下行", "indications": "瘀血阻滞，肝肾不足", "contraindications": "孕妇忌用",
     "dosage": "6-15克", "is_common": True},
    {"name": "秦艽", "category": "祛风湿药", "properties": "苦辛，微寒", "meridians": "胃、肝、胆经",
     "effects": "祛风湿，清湿热，舒筋络", "indications": "风湿痹痛，湿热黄疸", "contraindications": "久病体虚者慎用",
     "dosage": "5-10克", "is_common": True},
    {"name": "皂角刺", "category": "消肿药", "properties": "辛，温", "meridians": "肝、胃经",
     "effects": "消肿托毒，排脓，杀虫", "indications": "痈疽肿毒，瘰疬疮疡", "contraindications": "孕妇忌用",
     "dosage": "3-10克", "is_common": True},
    {"name": "白芷", "category": "解表药", "properties": "辛，温", "meridians": "肺、胃经",
     "effects": "解表散风，燥湿止痛，消肿排脓", "indications": "风寒感冒，头痛，疮疡肿毒", "contraindications": "阴虚火旺者慎用",
     "dosage": "3-10克", "is_common": True},
    {"name": "桔梗", "category": "化痰药", "properties": "苦辛，平", "meridians": "肺经",
     "effects": "宣肺，利咽，祛痰，排脓", "indications": "咳嗽痰多，咽喉肿痛，肺痈吐脓", "contraindications": "阴虚久咳者慎用",
     "dosage": "3-10克", "is_common": True},
    {"name": "山栀", "category": "清热药", "properties": "苦，寒", "meridians": "心、肺、三焦经",
     "effects": "泻火除烦，清热利湿，凉血解毒", "indications": "热病心烦，湿热黄疸", "contraindications": "脾虚便溏者慎用",
     "dosage": "6-10克", "is_common": True},
    {"name": "归尾", "category": "活血药", "properties": "甘辛，温", "meridians": "肝、心、脾经",
     "effects": "活血祛瘀，调经止痛", "indications": "瘀血阻滞，跌打损伤", "contraindications": "孕妇慎用",
     "dosage": "6-12克", "is_common": True},
    {"name": "地丁", "category": "清热解毒药", "properties": "苦辛，寒", "meridians": "肝、胃经",
     "effects": "清热解毒，消痈散结", "indications": "疔疮肿毒，乳痈肠痈", "contraindications": "脾胃虚寒者慎用",
     "dosage": "15-30克", "is_common": True},
    {"name": "天花粉", "category": "清热药", "properties": "甘微苦，微寒", "meridians": "肺、胃经",
     "effects": "清热生津，消肿排脓", "indications": "热病伤津，痈肿疮疡", "contraindications": "脾胃虚寒者慎用",
     "dosage": "10-15克", "is_common": True},
    {"name": "知母", "category": "清热药", "properties": "苦甘，寒", "meridians": "肺、胃、肾经",
     "effects": "清热泻火，滋阴润燥", "indications": "热病烦渴，阴虚火旺", "contraindications": "脾胃虚寒者慎用",
     "dosage": "6-12克", "is_common": True},
    {"name": "麦冬", "category": "养阴药", "properties": "甘微苦，微寒", "meridians": "心、肺、胃经",
     "effects": "养阴润肺，益胃生津，清心除烦", "indications": "肺燥干咳，虚劳烦热", "contraindications": "脾胃虚寒者慎用",
     "dosage": "6-12克", "is_common": True},
    {"name": "青蒿", "category": "清虚热药", "properties": "苦辛，寒", "meridians": "肝、胆经",
     "effects": "清虚热，凉血，解暑", "indications": "阴虚发热，暑邪发热", "contraindications": "脾胃虚寒者慎用",
     "dosage": "6-12克", "is_common": True},
    {"name": "鳖甲", "category": "滋阴药", "properties": "咸，微寒", "meridians": "肝、肾经",
     "effects": "滋阴潜阳，软坚散结", "indications": "阴虚内热，瘰疬痰核", "contraindications": "脾胃虚寒者慎用",
     "dosage": "9-24克", "usage_notes": "先煎", "is_common": True},
    {"name": "补骨脂", "category": "补阳药", "properties": "辛苦，温", "meridians": "肾、脾经",
     "effects": "补肾壮阳，固精缩尿，温脾止泻", "indications": "肾阳不足，脾肾阳虚", "contraindications": "阴虚火旺者忌用",
     "dosage": "6-10克", "is_common": True},
    {"name": "肉豆蔻", "category": "收涩药", "properties": "辛，温", "meridians": "脾、胃、大肠经",
     "effects": "涩肠止泻，温中行气", "indications": "虚泻久泻，脘腹胀痛", "contraindications": "湿热泻痢者忌用",
     "dosage": "3-10克", "is_common": True},
    {"name": "灶心土", "category": "止血药", "properties": "辛，温", "meridians": "脾、胃经",
     "effects": "温中止血，止呕止泻", "indications": "脾胃虚寒，呕吐泄泻，便血崩漏", "contraindications": "阴虚火旺者慎用",
     "dosage": "30-60克", "usage_notes": "煎汤代水", "is_common": True},
    {"name": "陈皮", "category": "理气药", "properties": "苦辛，温", "meridians": "脾、肺经",
     "effects": "理气健脾，燥湿化痰", "indications": "脾胃气滞，脘腹胀满，呕吐", "contraindications": "气虚及阴虚燥咳者慎用",
     "dosage": "3-10克", "is_common": True},
    {"name": "桂枝", "category": "解表药", "properties": "辛甘，温", "meridians": "心、肺、膀胱经",
     "effects": "发汗解肌，温通经脉，助阳化气", "indications": "风寒感冒，寒凝血滞", "contraindications": "温热病及阴虚阳盛者忌用",
     "dosage": "3-10克", "is_common": True},
    {"name": "朴硝", "category": "泻下药", "properties": "咸苦，寒", "meridians": "胃、大肠经",
     "effects": "泻热通便，润燥软坚，清热消肿", "indications": "实热便秘，痈肿疮疡", "contraindications": "孕妇忌用",
     "dosage": "10-15克", "usage_notes": "外用适量", "is_common": True},
    {"name": "马齿苋", "category": "清热解毒药", "properties": "酸，寒", "meridians": "肝、大肠经",
     "effects": "清热解毒，凉血止血，止痢", "indications": "热毒血痢，痈肿疔疮", "contraindications": "脾胃虚寒者慎用",
     "dosage": "15-30克", "usage_notes": "外用适量", "is_common": True},
    {"name": "瓦松", "category": "清热解毒药", "properties": "酸，平", "meridians": "肝、脾经",
     "effects": "清热解毒，止血，利湿", "indications": "吐血便血，痔疮肿痛，湿疹", "contraindications": "脾胃虚寒者慎用",
     "dosage": "15-30克", "usage_notes": "外用适量", "is_common": True},
    {"name": "艾叶", "category": "温里药", "properties": "辛苦，温", "meridians": "肝、脾、肾经",
     "effects": "温经止血，散寒止痛", "indications": "虚寒性出血，脘腹冷痛", "contraindications": "阴虚血热者忌用",
     "dosage": "3-10克", "usage_notes": "外用适量", "is_common": True},
    {"name": "川椒", "category": "温里药", "properties": "辛，热", "meridians": "脾、胃、肾经",
     "effects": "温中止痛，杀虫止痒", "indications": "脘腹冷痛，虫积腹痛，湿疹瘙痒", "contraindications": "阴虚火旺者忌用",
     "dosage": "3-6克", "usage_notes": "外用适量", "is_common": True},
    {"name": "明矾", "category": "收涩药", "properties": "酸涩，寒", "meridians": "肺、脾、肝、大肠经",
     "effects": "收敛止血，解毒杀虫，燥湿止痒", "indications": "久泻久痢，便血，湿疹瘙痒", "contraindications": "无湿热者慎用",
     "dosage": "1-3克", "usage_notes": "外用适量", "is_common": True},
    {"name": "百部", "category": "止咳平喘药", "properties": "甘苦，微温", "meridians": "肺经",
     "effects": "润肺止咳，杀虫灭虱", "indications": "新久咳嗽，蛲虫病，体虱", "contraindications": "热咳者慎用",
     "dosage": "3-10克", "usage_notes": "外用适量", "is_common": True},
    {"name": "白鲜皮", "category": "清热燥湿药", "properties": "苦，寒", "meridians": "脾、胃经",
     "effects": "清热燥湿，祛风止痒，解毒", "indications": "湿热疮毒，黄疸，风湿痹痛", "contraindications": "虚寒证忌用",
     "dosage": "6-15克", "is_common": True},
    {"name": "苦参", "category": "清热燥湿药", "properties": "苦，寒", "meridians": "心、肝、胃、大肠、膀胱经",
     "effects": "清热燥湿，杀虫，利尿", "indications": "湿热泻痢，黄疸，湿疹瘙痒", "contraindications": "脾胃虚寒者慎用",
     "dosage": "5-10克", "usage_notes": "外用适量", "is_common": True},
]

# ============ 经典方剂（验方）============
FORMULAS = [
    # 痔疮治疗方剂
    {
        "name": "槐花散加味",
        "source": "经验方",
        "composition": "槐花12克，侧柏叶10克，炒荆芥10克，枳壳10克，防风10克，生地15克，地榆10克，仙鹤草15克，麻仁9克，生甘草10克",
        "usage": "水煎服，日服一剂",
        "function": "清热疏风，和血止血",
        "indications": "以便秘、出血、疼痛为主的各期内痔、混合痔、炎性外痔",
        "syndrome_type": "实热证",
        "disease_types": []
    },
    {
        "name": "地榆散加味",
        "source": "经验方",
        "composition": "地榆12克，黄芩10克，黄连10克，山栀10克，槐花10克，当归12克，赤芍10克，川芎6克，甘草6克",
        "usage": "水煎服，日服一剂",
        "function": "清热凉血，活血止血",
        "indications": "血热型痔疮出血",
        "syndrome_type": "实热证",
        "disease_types": []
    },
    {
        "name": "五神汤加味",
        "source": "经验方",
        "composition": "茯苓10克，金银花20克，牛膝10克，车前子10克，地丁15克，黄芩10克，归尾10克，赤芍10克，甘草10克",
        "usage": "水煎服，日服一剂",
        "function": "清热利湿，活血化瘀",
        "indications": "湿热瘀滞型痔疮、血栓外痔、嵌顿性内痔",
        "syndrome_type": "湿热瘀滞型",
        "disease_types": []
    },
    {
        "name": "活血散瘀汤",
        "source": "经验方",
        "composition": "桃仁10克，红花6克，当归10克，赤芍10克，丹皮10克，乌药10克，枳实6克，泽泻10克，大黄6克（后下）",
        "usage": "水煎服，日服一剂",
        "function": "活血化瘀，行气止痛",
        "indications": "气滞血瘀型痔疮",
        "syndrome_type": "气滞血瘀型",
        "disease_types": []
    },
    {
        "name": "归脾汤加味",
        "source": "《济生方》加减",
        "composition": "人参10克，黄芪10克，白术10克，茯苓10克，枣仁10克，龙眼肉10克，远志10克，木香6克，甘草6克，灶心土80克，升麻10克",
        "usage": "水煎服，日服一剂",
        "function": "益气健脾，补血止血",
        "indications": "脾虚不摄型痔疮出血",
        "syndrome_type": "虚寒证",
        "disease_types": []
    },
    {
        "name": "八珍汤",
        "source": "《正体类要》",
        "composition": "熟地15克，白芍10克，当归15克，川芎10克，党参15克，白术12克，茯苓10克，炙黄芪30克，木香10克，炙甘草6克",
        "usage": "水煎服，日服一剂",
        "function": "补气益血",
        "indications": "气血亏损型痔疮，便血日久",
        "syndrome_type": "气血亏损型",
        "disease_types": []
    },
    {
        "name": "补中益气汤",
        "source": "《脾胃论》",
        "composition": "黄芪30克，党参15克，白术12克，当归10克，陈皮6克，升麻6克，柴胡6克，炙甘草6克",
        "usage": "水煎服，日服一剂",
        "function": "补中益气，升阳举陷",
        "indications": "直肠脱垂，脾虚气陷型痔疮",
        "syndrome_type": "脾虚气陷",
        "disease_types": []
    },

    # 肛周脓肿治疗方剂
    {
        "name": "内疏黄连汤加减",
        "source": "《外科正宗》加减",
        "composition": "黄连10克，黄芩6克，大黄6克，栀子10克，桔梗6克，木香6克，槟榔6克，连翘10克，赤白芍各10克，全当归10克，甘草6克",
        "usage": "水煎服，日服一剂",
        "function": "清泻实热，宣散郁结",
        "indications": "肛周脓肿初起，实热壅盛",
        "syndrome_type": "热毒蕴结",
        "disease_types": []
    },
    {
        "name": "青蒿鳖甲汤加减",
        "source": "《温病条辨》加减",
        "composition": "青蒿12克，鳖甲12克，柴胡10克，黄芩10克，生地15克，白芍10克，知母10克，生黄芪15克，麦冬10克",
        "usage": "水煎服，日服一剂",
        "function": "清虚热，散毒气",
        "indications": "虚热型肛周脓肿，阴虚精亏",
        "syndrome_type": "正虚邪恋",
        "disease_types": []
    },
    {
        "name": "托里消毒散加味",
        "source": "《外科正宗》加减",
        "composition": "黄芪20克，党参10克，当归10克，白芍10克，白术10克，茯苓10克，金银花15克，白芷6克，桔梗6克，皂角刺10克，甘草6克",
        "usage": "水煎服，日服一剂",
        "function": "益气补血，托里排脓",
        "indications": "肛周脓肿后期，正虚邪恋",
        "syndrome_type": "正虚邪恋",
        "disease_types": []
    },

    # 肛裂治疗方剂
    {
        "name": "凉血地黄汤",
        "source": "经验方",
        "composition": "生地15克，当归10克，地榆10克，槐花10克，黄芩10克，天花粉10克，升麻6克，赤芍10克，甘草6克",
        "usage": "水煎服，日服一剂",
        "function": "凉血止血，养阴润燥",
        "indications": "肛裂出血，血热肠燥",
        "syndrome_type": "血热肠燥",
        "disease_types": []
    },
    {
        "name": "止痛如神汤",
        "source": "《兰室秘藏》",
        "composition": "秦艽10克，桃仁10克，皂角子6克，苍术10克，防风10克，黄柏10克，当归10克，泽泻10克，大黄6克（后下），槟榔10克，甘草6克",
        "usage": "水煎服，日服一剂",
        "function": "活血祛风，清热利湿",
        "indications": "肛裂疼痛，湿热型痔疮疼痛",
        "syndrome_type": "湿热下注",
        "disease_types": []
    },

    # 肛门疣赘治疗方剂
    {
        "name": "萆薢渗湿汤",
        "source": "《疡科心得集》",
        "composition": "萆薢10克，苡仁15克，黄柏10克，赤茯苓10克，丹皮10克，泽泻10克，通草6克，滑石10克（包煎）",
        "usage": "水煎服，日服一剂",
        "function": "清热利湿",
        "indications": "肛门湿疹，湿热下注型",
        "syndrome_type": "湿热下注",
        "disease_types": []
    },
    {
        "name": "杞菊地黄汤",
        "source": "《医级》",
        "composition": "熟地15克，山萸肉15克，山药12克，泽泻12克，茯苓12克，丹皮12克，枸杞子15克，菊花12克",
        "usage": "水煎服，日服一剂",
        "function": "滋补肝肾",
        "indications": "肛门疣赘，肝肾阴虚型",
        "syndrome_type": "肝肾阴虚",
        "disease_types": []
    },
    {
        "name": "丹栀逍遥散",
        "source": "《内科摘要》",
        "composition": "丹皮12克，栀子10克，柴胡9克，当归12克，白芍12克，白术10克，茯苓12克，甘草6克，薄荷5克，生姜3片",
        "usage": "水煎服，日服一剂",
        "function": "行气活血",
        "indications": "肛门疣赘，气滞血瘀型",
        "syndrome_type": "气滞血瘀",
        "disease_types": []
    },

    # 肛门疖肿治疗方剂
    {
        "name": "五味消毒饮",
        "source": "《医宗金鉴》",
        "composition": "金银花20克，野菊花15克，蒲公英15克，紫地丁15克，天葵子10克",
        "usage": "水煎服，日服一剂",
        "function": "清热解毒",
        "indications": "热毒疖肿",
        "syndrome_type": "热毒蕴结",
        "disease_types": []
    },
    {
        "name": "黄芩滑石汤加减",
        "source": "《温病条辨》加减",
        "composition": "黄芩15克，茯苓10克，木通6克，猪苓10克，泽泻10克，苡仁20克，滑石15克，甘草10克",
        "usage": "水煎服，日服一剂",
        "function": "清热利湿",
        "indications": "湿热疖肿，病程日久",
        "syndrome_type": "湿热搏结",
        "disease_types": []
    },

    # 直肠脱垂治疗方剂
    {
        "name": "参茸提肛散",
        "source": "经验方",
        "composition": "人参6克，鹿茸4克（研末冲服），炒白术8克，全当归8克，补骨脂6克，肉豆蔻4克，黄芪20克，乌梅10克，甘草3克",
        "usage": "每日一剂，水煎服",
        "function": "调荣养血，益气固脱",
        "indications": "产后气血亏损引起的直肠脱垂",
        "syndrome_type": "气血两虚",
        "disease_types": []
    },
    {
        "name": "黄芪健中汤加减",
        "source": "《金匮要略》加减",
        "composition": "黄芪15克，桂枝10克，白芍10克，白术10克，生姜3片，大枣7枚，陈棕炭10克，侧柏叶10克，陈皮10克，甘草6克",
        "usage": "水煎服，日服一剂",
        "function": "固气升提，止血止泻",
        "indications": "内痔脱出严重，长期便血，消化不良，腹泻者",
        "syndrome_type": "脾胃虚寒",
        "disease_types": []
    },
    {
        "name": "当归连翘汤",
        "source": "经验方",
        "composition": "当归12克，连翘12克，生地12克，白芍10克，白芷6克，党参16克，白术10克，阿胶12克，甘草6克，地榆10克，乌梅10克，大枣7枚",
        "usage": "水煎服，每日一剂",
        "function": "补虚清热，和血疏风",
        "indications": "气血亏损兼有湿热的痔疮",
        "syndrome_type": "虚中夹实",
        "disease_types": []
    },
    {
        "name": "四物汤合增液汤",
        "source": "经典方合方",
        "composition": "生地16克，玄参16克，赤芍10克，当归10克，麦冬10克，大腹皮10克，车前子10克，川芎6克，碧玉散20克（包）",
        "usage": "水煎服，每日一剂，分二次服",
        "function": "生津润燥，活血化瘀，消肿利湿",
        "indications": "嵌顿痔，血虚津乏，筋脉瘀阻",
        "syndrome_type": "血虚津乏",
        "disease_types": []
    },

    # 外用方剂（熏洗、外敷）
    {
        "name": "消肿止痛洗剂",
        "source": "经验方",
        "composition": "瓦松30克，五倍子30克，马齿苋30克，艾叶30克，川椒30克",
        "usage": "煎水1000毫升熏洗，日1-2次",
        "function": "消肿止痛，收敛",
        "indications": "外痔发炎、血栓外痔、内痔脱出嵌顿、直肠脱垂及术后伤口水肿疼痛等",
        "syndrome_type": "通用",
        "formula_type": "fumigation",
        "disease_types": []
    },
    {
        "name": "熏洗方（通用）",
        "source": "经验方",
        "composition": "朴硝30克，马齿苋20克，瓦松15克，归尾15克，赤芍15克，黄柏15克，苍术15克",
        "usage": "煎水约1000毫升，趁热先熏后洗，或浸布湿敷于患处，每日2-3次坐浴",
        "function": "清热解毒，活血祛瘀，利湿软坚，消肿止痛",
        "indications": "痔瘘、肛痈炎症期，肛裂便后疼痛，以及全身所患之痈、疽、疔、疖属于急性期炎症者",
        "syndrome_type": "通用",
        "formula_type": "fumigation",
        "disease_types": []
    },
    {
        "name": "湿疹洗剂",
        "source": "经验方",
        "composition": "马齿苋30克，赤芍15克，地榆20克，苦参30克，白鲜皮20克，明矾10克，百部80克，川椒10克",
        "usage": "煎水坐浴",
        "function": "清热利湿，活血止痒",
        "indications": "肛门湿疹，肛门瘙痒",
        "syndrome_type": "湿热下注",
        "formula_type": "fumigation",
        "disease_types": []
    },
    {
        "name": "血竭散",
        "source": "《沈氏尊生》",
        "composition": "血竭3克，大黄20克，玄明粉30克，煅自然铜30克",
        "usage": "水煎，每日一剂，分二次熏洗",
        "function": "活血定痛，清热解毒，消肿利湿",
        "indications": "嵌顿痔，外痔肿痛",
        "syndrome_type": "通用",
        "formula_type": "fumigation",
        "disease_types": []
    },
    {
        "name": "四黄膏",
        "source": "经验方",
        "composition": "黄连、黄芩、黄柏、栀子各等份，共研细末。凡士林70克，四黄粉30克，共同混合调匀成膏",
        "usage": "外敷患处",
        "function": "清热消肿，凉血止痛",
        "indications": "内痔、外痔发炎、水肿、术后疼痛，痈、疽、疔、疖红肿",
        "syndrome_type": "通用",
        "formula_type": "external",
        "disease_types": []
    },
    {
        "name": "金黄膏",
        "source": "传统方",
        "composition": "黄柏、大黄、姜黄、白芷各60克，川朴、陈皮、苍术、南星、甘草各25克，天花粉30克，共研细末",
        "usage": "以茶水调和外敷或配成30%凡士林软膏敷贴，日敷2次",
        "function": "软坚散结，清热消肿",
        "indications": "慢性肛周脓肿，疮疡肿毒",
        "syndrome_type": "通用",
        "formula_type": "external",
        "disease_types": []
    },
    {
        "name": "玉露膏",
        "source": "传统方",
        "composition": "芙蓉花叶，晒干研成细末，用凡士林调匀成30%软膏",
        "usage": "敷患处，日2次",
        "function": "清热解毒，消肿止痛",
        "indications": "急性肛周脓肿外敷",
        "syndrome_type": "通用",
        "formula_type": "external",
        "disease_types": []
    },
    {
        "name": "九华膏",
        "source": "传统方",
        "composition": "九华膏成品",
        "usage": "外用纱条换药，或直接涂抹患处",
        "function": "祛腐生肌",
        "indications": "肛裂，术后创面换药",
        "syndrome_type": "通用",
        "formula_type": "external",
        "notes": "化腐期使用，促进创面清洁",
        "disease_types": []
    },
    {
        "name": "生肌玉红膏",
        "source": "传统方",
        "composition": "玉红膏成品",
        "usage": "外用换药",
        "function": "生肌敛疮",
        "indications": "肛瘘术后生肌期换药，创面促进愈合",
        "syndrome_type": "通用",
        "formula_type": "external",
        "notes": "生肌期使用，促进肉芽生长",
        "disease_types": []
    },
    {
        "name": "化腐生肌散",
        "source": "经验方",
        "composition": "红粉5克，珠砂10克，石膏15克，乳香10克，没药10克",
        "usage": "共研细末，调成糊状，以棉纸做成条，蘸药后插入瘘道中，每日2次",
        "function": "化腐生肌，托里透毒",
        "indications": "肛瘘保守治疗，瘘道换药",
        "syndrome_type": "通用",
        "formula_type": "external",
        "disease_types": []
    },
    {
        "name": "收肛散",
        "source": "经验方",
        "composition": "收敛固脱药物组成",
        "usage": "外敷，配合纱布垫加压固定",
        "function": "收敛固脱，消肿利湿",
        "indications": "直肠脱垂外用",
        "syndrome_type": "通用",
        "formula_type": "external",
        "disease_types": []
    },

    # 枯痔类核心方剂
    {
        "name": "无砒枯痔散",
        "source": "1955年改良",
        "composition": "白矾30克，雄黄15克，乳香15克，没药15克，儿茶15克，冰片3克",
        "usage": "共研极细末，用时取适量药末塞入痔核根部，7-10天换药一次",
        "function": "枯痔化痔，使痔核坏死脱落",
        "indications": "I-II期内痔",
        "syndrome_type": "通用",
        "formula_type": "external",
        "modifications": "1955年改进传统枯痔散，去掉剧毒白砒，避免砒中毒，使病人痛苦大大减轻，且治愈后不易复发",
        "notes": "制作：各药分别研细末，过120目筛，混合均匀，密封保存。使用时需严格掌握适应症，操作规范，避免药物进入肛管粘膜造成损伤",
        "disease_types": []
    },
    {
        "name": "二矾枯痔锭",
        "source": "经验方",
        "composition": "明矾（枯矾）40克，胆矾10克，乳香10克，没药10克，冰片2克",
        "usage": "共研细末，加黄蜡适量制成锭剂，每锭约2克。用时将药锭塞入痔核基底部，每周1次",
        "function": "枯痔收敛，化腐止血",
        "indications": "I-II期内痔出血",
        "syndrome_type": "通用",
        "formula_type": "external",
        "notes": "制作方法：1.明矾入锅炒至枯白，冷却研末；2.胆矾研细末；3.乳香、没药去油研末；4.冰片研细；5.黄蜡隔水溶化；6.将各药末混合均匀，趁热与黄蜡调和，制成锭状，冷却后密封保存。使用时用改制的枯痔锭投药器推送",
        "disease_types": []
    },
    {
        "name": "明矾注射液（4%）",
        "source": "1959年首创",
        "composition": "明矾4克，注射用水100ml",
        "usage": "用于注射治疗I-II期内痔。每个痔核注射2-4ml，每周1次",
        "function": "收敛固脱，使痔核硬化萎缩",
        "indications": "I-II期内痔",
        "syndrome_type": "通用",
        "formula_type": "external",
        "notes": "制作：1.取明矾4g，加注射用水至100ml；2.加热溶解，过滤；3.高压灭菌；4.分装安瓿。注射方法：在痔核基底部粘膜下注射，使粘膜隆起成丘状。1959年首先采用此法，为后来理想注射疗法奠定基础",
        "disease_types": []
    },
    {
        "name": "明矾注射液（6%）",
        "source": "经验方",
        "composition": "明矾6克，注射用水100ml",
        "usage": "用于治疗成人完全性直肠脱垂。直肠粘膜下多点注射",
        "function": "收敛固脱，使粘膜下组织纤维化粘连",
        "indications": "成人完全性直肠脱垂",
        "syndrome_type": "通用",
        "formula_type": "external",
        "modifications": "根据'酸可收敛、涩可固脱'理论，从反复临床试验中总结出治疗直肠脱垂的新方法。1981年通过部级鉴定，全愈率99.5%，无直肠狭窄、性功能障碍等后遗症",
        "notes": "制作同4%明矾液。注射方法：在脱出的直肠粘膜下分点注射，每点2-3ml，使粘膜隆起，总量20-40ml。注射后局部加压包扎，卧床休息",
        "disease_types": []
    },

    # 外用制剂详细配方
    {
        "name": "九华膏（完整配方）",
        "source": "传统名方",
        "composition": "当归60克，白芷60克，甘草60克，生地60克，黄连30克，黄芩30克，黄柏30克，天花粉30克，大黄30克，血竭15克，乳香15克，没药15克，轻粉9克，麻油1000ml，黄蜡240克",
        "usage": "制成膏药，用纱条蘸药膏外敷或插入瘘管、创面",
        "function": "祛腐生肌，消肿止痛，化腐清热",
        "indications": "肛瘘术后化腐期换药，痔疮术后创面，肛裂",
        "syndrome_type": "通用",
        "formula_type": "external",
        "notes": "制作方法：1.将当归、白芷、甘草、生地、黄连、黄芩、黄柏、天花粉、大黄入麻油中浸泡3天；2.用文火煎熬至药枯，去渣；3.继续熬至滴水成珠；4.加入黄蜡溶化；5.待温度降至60度左右，加入血竭、乳香、没药、轻粉粉末，搅匀；6.倾入水中冷却，制成膏剂。化腐期使用，促进腐肉脱落，创面清洁",
        "disease_types": []
    },
    {
        "name": "生肌散",
        "source": "传统方",
        "composition": "煅石膏30克，煅龙骨30克，煅赤石脂30克，血竭10克，乳香10克，没药10克，冰片3克，珍珠粉3克",
        "usage": "共研极细末，撒于创面或调麻油外敷",
        "function": "生肌敛疮，收口愈伤",
        "indications": "肛瘘、痔疮术后生肌期换药",
        "syndrome_type": "通用",
        "formula_type": "external",
        "notes": "制作方法：1.石膏、龙骨、赤石脂分别煅红，冷却研细；2.乳香、没药去油研末；3.血竭、珍珠粉研细；4.冰片另研；5.各药过120目筛，混合均匀，密封保存。生肌期使用，促进肉芽生长",
        "disease_types": []
    },
    {
        "name": "珍珠散",
        "source": "传统方",
        "composition": "珍珠粉10克，琥珀粉10克，血竭10克，象皮10克，煅龙骨20克，煅石膏20克，冰片2克",
        "usage": "共研极细末，撒于创面",
        "function": "收口生肌，敛疮止痛",
        "indications": "肛瘘、痔疮术后收口期，瘢痕中心小创面久不愈合",
        "syndrome_type": "通用",
        "formula_type": "external",
        "notes": "制作方法：各药分别研成极细粉末，过120目筛，混合均匀，密封保存。收口期使用，促进创面最终愈合。如瘢痕中心有小创面仍不易愈合，在排除假愈合后，外用珍珠散常可收到比较满意的效果",
        "disease_types": []
    },
    {
        "name": "红粉纱条",
        "source": "传统方",
        "composition": "红升丹（红粉）适量，凡士林适量",
        "usage": "将红粉与凡士林调成糊状（比例约1:3），涂于纱条上，插入瘘管或敷于创面",
        "function": "提脓去腐，化管祛腐",
        "indications": "肛瘘术后化腐期换药，促进管道腐脱",
        "syndrome_type": "通用",
        "formula_type": "external",
        "notes": "制作方法：取红升丹粉末，与凡士林按1:3比例调匀成糊状，涂于无菌纱条上即可使用。强调：初时宜重化腐，用红粉纱条蚀管祛腐，待创面腐脱管化，则应改用生肌玉红膏换药",
        "disease_types": []
    },
    {
        "name": "小败毒膏",
        "source": "传统成药",
        "composition": "成药制剂",
        "usage": "每次20克，日服2-3次",
        "function": "清热解毒，消肿止痛",
        "indications": "急性肛周脓肿内服",
        "syndrome_type": "实热证",
        "notes": "用于急性肛周脓肿内治",
        "disease_types": []
    },
    {
        "name": "犀黄丸",
        "source": "传统成药",
        "composition": "成药制剂",
        "usage": "每次20克，日服2次",
        "function": "软坚散结，清热消肿",
        "indications": "慢性肛周脓肿",
        "syndrome_type": "虚热证",
        "notes": "用于慢性肛周脓肿，气血虚弱，正虚邪恋者",
        "disease_types": []
    },

    # 辅助用药
    {
        "name": "麻仁润肠丸",
        "source": "传统成药",
        "composition": "火麻仁、苦杏仁、大黄、枳实、厚朴、白芍等",
        "usage": "每日1-2丸，温开水送服",
        "function": "润肠通便",
        "indications": "肠燥便秘，大便干结，肛裂便秘",
        "syndrome_type": "肠燥证",
        "notes": "用于肛裂、痔疮便秘患者",
        "disease_types": []
    },
    {
        "name": "麻仁滋脾丸",
        "source": "传统成药",
        "composition": "火麻仁、白术、枳实、厚朴、大黄、白芍、陈皮等",
        "usage": "每日1-2丸，温开水送服",
        "function": "润肠通便，健脾益气",
        "indications": "脾虚便秘",
        "syndrome_type": "脾虚证",
        "notes": "用于脾虚型便秘，肛门疾病伴脾虚者",
        "disease_types": []
    },
    {
        "name": "消炎痛栓",
        "source": "西药制剂",
        "composition": "吲哚美辛",
        "usage": "每日1-2次，每次1粒，纳入肛内",
        "function": "消炎止痛",
        "indications": "新鲜肛裂，痔疮术后疼痛",
        "syndrome_type": "通用",
        "formula_type": "external",
        "notes": "用于肛裂病人止痛消炎",
        "disease_types": []
    },
    {
        "name": "利多卡因软膏（5%）",
        "source": "西药制剂",
        "composition": "盐酸利多卡因5%",
        "usage": "外涂肛裂局部",
        "function": "局部麻醉止痛",
        "indications": "肛裂疼痛，缓解括约肌痉挛",
        "syndrome_type": "通用",
        "formula_type": "external",
        "notes": "用于减轻肛门疼痛，缓解括约肌痉挛",
        "disease_types": []
    },
    {
        "name": "封闭注射液（亚甲兰地卡因）",
        "source": "经验方",
        "composition": "亚甲兰0.26克，地卡因0.2克，蒸馏水加至100毫升",
        "usage": "局部封闭，每次5-10毫升，每周1-2次",
        "function": "局部麻醉，缓解痉挛，止痛",
        "indications": "肛裂疼痛，括约肌痉挛",
        "syndrome_type": "通用",
        "formula_type": "external",
        "notes": "制作：按比例配制，高压灭菌，分装。用于肛裂局部封闭治疗",
        "disease_types": []
    },
    {
        "name": "布比卡因封闭液",
        "source": "现代药物",
        "composition": "0.25%布比卡因6毫升",
        "usage": "在病人长强穴做扇形注射，隔日一次，5次为一疗程",
        "function": "长效局部麻醉，解除括约肌痉挛",
        "indications": "肛裂疼痛，括约肌痉挛",
        "syndrome_type": "通用",
        "formula_type": "external",
        "notes": "用于肛裂封闭疗法，缓解疼痛和括约肌痉挛",
        "disease_types": []
    },

    # 内服成药方
    {
        "name": "地槐止血丸",
        "source": "经验方",
        "composition": "地榆炭60克，槐角120克，防风60克，黄柏60克",
        "usage": "共研细末，炼蜜为丸，丸重10克，每日服二丸",
        "function": "清利湿热，止血通便",
        "indications": "各期痔疮出血、肛裂疼痛出血、肠风下血",
        "syndrome_type": "通用",
        "notes": "制作方法：1.地榆炒炭；2.槐角炒黄；3.防风、黄柏分别炒制；4.四药共研细末，过80目筛；5.炼蜜为丸，每丸10克；6.蜡皮封装。经验方，临床疗效确切",
        "disease_types": []
    },
    {
        "name": "复方痔疮栓",
        "source": "经验方",
        "composition": "地榆粉20克，黄柏10克，次没食子酸铋10克，仙鹤草素6片，地卡因0.7克，冰片0.7克，栓剂基质100克，做成肛门栓70枚",
        "usage": "每晚临睡前纳入肛内1-2枚",
        "function": "消炎、止血、止痛",
        "indications": "内痔出血、肛窦炎、肛裂出血疼痛",
        "syndrome_type": "通用",
        "formula_type": "external",
        "disease_types": []
    },
]

# ============ 典型医案（临床实录）============
CASES = [
    # 痔疮医案（3例）
    {
        "title": "实热内蕴痔疮出血案",
        "disease_type": "痔疮",
        "patient_info": "男，40岁",
        "chief_complaint": "大便带血一月余",
        "symptoms": "便干难解，3-4日一次，小便短赤。舌红、苔黄，脉弦数",
        "tongue_pulse": "舌红苔黄，脉弦数",
        "syndrome": "实热内蕴，血热肠燥",
        "treatment_principle": "清热止血，润肠通便",
        "formula": "槐花散加减",
        "treatment_process": "槐花12克，侧柏叶10克，炒荆芥10克，枳壳10克，防风10克，生地15克，地榆10克，仙鹤草15克，麻仁9克，生甘草10克",
        "outcome": "五日后复诊，便血已止。续用前方五剂而痊愈。",
        "key_points": "实热内蕴者治以清热止血为主，佐以润肠通便",
        "source": "临床经验"
    },
    {
        "title": "湿热下注血栓外痔案",
        "disease_type": "痔疮",
        "patient_info": "男，24岁",
        "chief_complaint": "肛门肿痛三天",
        "symptoms": "便干，无血，口苦，纳食欠佳。舌质红，苔黄腻，脉弦滑数",
        "tongue_pulse": "舌质红，苔黄腻，脉弦滑数",
        "syndrome": "湿热下注，气滞血瘀",
        "treatment_principle": "清热利湿，活血化瘀",
        "formula": "五神汤加减",
        "treatment_process": "茯苓10克，金银花20克，牛膝10克，车前子10克，地丁15克，黄芩10克，归尾10克，赤芍10克，甘草10克。三日后疼痛减轻，改用活血散瘀汤加减",
        "outcome": "初诊三日后疼痛减轻，改方后五日痊愈。",
        "key_points": "湿热瘀滞型痔疮先清热利湿，继以活血化瘀",
        "source": "临床经验"
    },
    {
        "title": "气血亏损产后痔疮案",
        "disease_type": "痔疮",
        "patient_info": "女，28岁（产后）",
        "chief_complaint": "大便带血三个月",
        "symptoms": "面色无华，神疲乏力，少气懒言，纳食差。脉细弱，舌淡白",
        "tongue_pulse": "脉细弱，舌淡白",
        "syndrome": "气血亏损，气不摄血",
        "treatment_principle": "补气益血",
        "formula": "八珍汤",
        "treatment_process": "熟地15克，白芍10克，当归15克，川芎10克，党参15克，白术12克，茯苓10克，炙黄芪30克，木香10克，炙甘草6克",
        "outcome": "七日后便血已止。续服前方半个月，诸症均消。嘱服人参养荣丸巩固。",
        "key_points": "产后气血两虚致便血，宜补气益血，不宜单用止血之品",
        "source": "临床经验"
    },

    # 肛周脓肿医案（2例）
    {
        "title": "实热壅盛肛周脓肿消散案",
        "disease_type": "肛周脓肿",
        "patient_info": "男，32岁",
        "chief_complaint": "肛旁肿胀疼痛二天",
        "symptoms": "身热，口渴喜冷饮，大便秘结，小便短赤。舌质红，苔黄腻，脉弦滑数",
        "tongue_pulse": "舌质红，苔黄腻，脉弦滑数",
        "syndrome": "实热壅盛，下注肛门",
        "treatment_principle": "清泻实热，宣散郁结",
        "formula": "内疏黄连汤加减",
        "treatment_process": "黄连10克，黄芩6克，大黄6克，栀子10克，桔梗6克，木香6克，槟榔6克，连翘10克，赤白芍各10克，全当归10克，甘草6克",
        "outcome": "五日后肛旁肿痛消失。继用前方三剂清余热，痊愈。",
        "key_points": "肛周脓肿初期实热壅盛者，及时清泻实热可使脓肿消散，免去手术之苦",
        "source": "临床经验"
    },
    {
        "title": "正虚邪恋肛周脓肿溃后不收案",
        "disease_type": "肛周脓肿",
        "patient_info": "男，45岁",
        "chief_complaint": "肛周脓肿切开术后两月余创口不愈",
        "symptoms": "脓汁清稀，时有潮热盗汗，懒言乏力，面色无华。脉细弱，舌淡红苔薄白",
        "tongue_pulse": "脉细弱，舌淡红苔薄白",
        "syndrome": "正虚邪恋，气血不足",
        "treatment_principle": "益气补血，托里排脓",
        "formula": "托里消毒散加味",
        "treatment_process": "黄芪20克，党参10克，当归10克，白芍10克，白术10克，茯苓10克，金银花15克，白芷6克，桔梗6克，皂角刺10克，甘草6克",
        "outcome": "服药十剂后创面逐渐缩小，脓汁转浓。续服二十剂，创口完全愈合。",
        "key_points": "脓肿溃后久不收口者多属正虚邪恋，宜托里补虚",
        "source": "临床经验"
    },

    # 肛裂医案（2例）
    {
        "title": "血热肠燥肛裂案",
        "disease_type": "肛裂",
        "patient_info": "女，35岁",
        "chief_complaint": "肛门疼痛伴便血半年",
        "symptoms": "便干如羊粪，便时及便后肛门剧痛，持续数小时，便纸带血。舌红苔黄，脉弦数",
        "tongue_pulse": "舌红苔黄，脉弦数",
        "syndrome": "血热肠燥",
        "treatment_principle": "凉血止血，养阴润燥",
        "formula": "凉血地黄汤",
        "treatment_process": "生地15克，当归10克，地榆10克，槐花10克，黄芩10克，天花粉10克，升麻6克，赤芍10克，甘草6克",
        "outcome": "服药七剂后疼痛明显减轻，大便转软。续服十剂，肛裂愈合。",
        "key_points": "肛裂多因大便干燥所致，治疗当润肠通便为先",
        "source": "临床经验"
    },
    {
        "title": "湿热下注肛裂疼痛案",
        "disease_type": "肛裂",
        "patient_info": "男，42岁",
        "chief_complaint": "肛门疼痛三月",
        "symptoms": "便时肛门剧痛难忍，便后持续疼痛，坐立不安。口苦，小便黄。舌质红，苔黄腻，脉滑数",
        "tongue_pulse": "舌质红，苔黄腻，脉滑数",
        "syndrome": "湿热下注",
        "treatment_principle": "活血祛风，清热利湿",
        "formula": "止痛如神汤",
        "treatment_process": "秦艽10克，桃仁10克，皂角子6克，苍术10克，防风10克，黄柏10克，当归10克，泽泻10克，大黄6克（后下），槟榔10克，甘草6克",
        "outcome": "服药五剂疼痛大减，十剂后基本无痛。配合温水坐浴，一月后裂口愈合。",
        "key_points": "肛裂疼痛剧烈者用止痛如神汤，配合外治法效果更佳",
        "source": "临床经验"
    },

    # 肛门疣赘医案（2例）
    {
        "title": "湿热下注肛门湿疹案",
        "disease_type": "肛门疣赘",
        "patient_info": "男，38岁",
        "chief_complaint": "肛门瘙痒伴赘皮半年",
        "symptoms": "肛门潮湿瘙痒，局部皮肤肥厚，小便黄赤。舌红苔黄腻，脉滑数",
        "tongue_pulse": "舌红苔黄腻，脉滑数",
        "syndrome": "湿热下注",
        "treatment_principle": "清热利湿",
        "formula": "萆薢渗湿汤",
        "treatment_process": "萆薢10克，苡仁15克，黄柏10克，赤茯苓10克，丹皮10克，泽泻10克，通草6克，滑石10克（包煎）",
        "outcome": "服药十剂后瘙痒明显减轻，湿疹消退。续服半月，诸症消失。",
        "key_points": "肛门湿疹多属湿热下注，治以清热利湿为主",
        "source": "临床经验"
    },
    {
        "title": "肝肾阴虚肛门瘙痒案",
        "disease_type": "肛门疣赘",
        "patient_info": "女，50岁",
        "chief_complaint": "肛门瘙痒三年",
        "symptoms": "夜间瘙痒尤甚，伴腰膝酸软，头晕耳鸣，口干。舌红少苔，脉细数",
        "tongue_pulse": "舌红少苔，脉细数",
        "syndrome": "肝肾阴虚",
        "treatment_principle": "滋补肝肾",
        "formula": "杞菊地黄汤",
        "treatment_process": "熟地15克，山萸肉15克，山药12克，泽泻12克，茯苓12克，丹皮12克，枸杞子15克，菊花12克",
        "outcome": "服药二十剂后瘙痒大减，腰膝酸软改善。继服一月，瘙痒消失。",
        "key_points": "顽固性肛门瘙痒日久者多属阴虚，宜滋补肝肾",
        "source": "临床经验"
    },

    # 肛门疖肿医案（2例）
    {
        "title": "热毒蕴结肛门疖肿案",
        "disease_type": "肛门疖肿",
        "patient_info": "男，28岁",
        "chief_complaint": "肛旁红肿疼痛三天",
        "symptoms": "局部红肿灼热，触痛明显，伴发热。舌红苔黄，脉数",
        "tongue_pulse": "舌红苔黄，脉数",
        "syndrome": "热毒蕴结",
        "treatment_principle": "清热解毒",
        "formula": "五味消毒饮",
        "treatment_process": "金银花20克，野菊花15克，蒲公英15克，紫地丁15克，天葵子10克",
        "outcome": "服药三剂后红肿消退，疼痛减轻。续服五剂，疖肿消散。",
        "key_points": "肛门疖肿初起用五味消毒饮清热解毒可使其消散",
        "source": "临床经验"
    },
    {
        "title": "湿热搏结肛门疖肿案",
        "disease_type": "肛门疖肿",
        "patient_info": "男，40岁",
        "chief_complaint": "肛旁反复生疖半年",
        "symptoms": "局部红肿反复发作，伴口苦口黏，小便黄。舌红苔黄腻，脉滑数",
        "tongue_pulse": "舌红苔黄腻，脉滑数",
        "syndrome": "湿热搏结",
        "treatment_principle": "清热利湿",
        "formula": "黄芩滑石汤加减",
        "treatment_process": "黄芩15克，茯苓10克，木通6克，猪苓10克，泽泻10克，苡仁20克，滑石15克，甘草10克",
        "outcome": "服药十五剂后疖肿不再复发，湿热症状消失。随访半年未复发。",
        "key_points": "反复发作的肛门疖肿多属湿热内蕴，治以清热利湿",
        "source": "临床经验"
    },

    # 直肠脱垂医案（3例）
    {
        "title": "气虚下陷小儿直肠脱垂案",
        "disease_type": "直肠脱垂",
        "patient_info": "男，3.5岁",
        "chief_complaint": "便后肛门有物脱出半年",
        "symptoms": "食少，睡眠不佳，面色恍白，目睛无彩。舌淡苔少，脉象虚弱",
        "tongue_pulse": "舌淡苔少，脉象虚弱",
        "syndrome": "脾肺气虚，中气下陷",
        "treatment_principle": "补脾益肺，升提固涩",
        "formula": "补中益气汤加减",
        "treatment_process": "黄芪15克，党参10克，白术8克，当归6克，陈皮4克，升麻4克，柴胡4克，五味子5克，甘草4克",
        "outcome": "服药七剂后脱出明显减少。续服半月痊愈，随访一年未复发。",
        "key_points": "小儿直肠脱垂多属气虚下陷，用补中益气汤加减",
        "source": "临床经验"
    },
    {
        "title": "气血亏损产后脱肛案",
        "disease_type": "直肠脱垂",
        "patient_info": "女，29岁（产后）",
        "chief_complaint": "产后脱肛两个月",
        "symptoms": "便后脱肛需手托回纳，面色苍白，神疲乏力，头晕心悸。舌淡苔白，脉细弱",
        "tongue_pulse": "舌淡苔白，脉细弱",
        "syndrome": "气血两虚",
        "treatment_principle": "调荣养血，益气固脱",
        "formula": "参茸提肛散",
        "treatment_process": "人参6克，鹿茸4克（研末冲服），炒白术8克，全当归8克，补骨脂6克，肉豆蔻4克，黄芪20克，乌梅10克，甘草3克",
        "outcome": "服药十五剂后脱肛明显减轻。续服一月，脱肛痊愈。配合提肛锻炼，随访两年未复发。",
        "key_points": "产后脱肛多因气血亏损，用参茸提肛散效果显著",
        "source": "临床经验"
    },
    {
        "title": "脾肾阳虚老年脱肛案",
        "disease_type": "直肠脱垂",
        "patient_info": "男，68岁",
        "chief_complaint": "脱肛十年，加重半年",
        "symptoms": "稍用力即脱肛，难以回纳，畏寒肢冷，腰膝酸软，小便清长。舌淡胖有齿痕，脉沉细无力",
        "tongue_pulse": "舌淡胖有齿痕，脉沉细无力",
        "syndrome": "脾肾阳虚",
        "treatment_principle": "温补脾肾，固涩提升",
        "formula": "补中益气汤合金匮肾气丸加减",
        "treatment_process": "黄芪30克，党参15克，白术12克，当归10克，升麻6克，柴胡6克，熟地15克，山药12克，山萸肉10克，肉桂3克，附子6克，补骨脂10克，炙甘草6克",
        "outcome": "服药一月后脱肛明显改善，畏寒症状好转。续服两月，脱肛基本控制。",
        "key_points": "老年脱肛日久多属脾肾阳虚，需温补脾肾",
        "source": "临床经验"
    },
]

# ============ 预防保健指南（扩充版）============
PREVENTION_GUIDES = [
    {
        "disease_type": "痔疮",
        "title": "痔疮预防与保健指南",
        "prevention_points": [
            "保持大便通畅，养成定时排便习惯",
            "饮食清淡，忌辛辣刺激、酗酒",
            "避免久坐久立久蹲",
            "适当运动，坚持提肛锻炼",
            "保持肛门清洁",
            "女性注意孕期保健",
            "避免腹泻和便秘"
        ],
        "dietary_advice": "多食蔬菜水果，保持大便通畅。忌食辛辣刺激之品如辣椒、大蒜、烈酒等。宜食清淡易消化食物。",
        "lifestyle_advice": "避免久坐久站，适当活动。便后温水坐浴。保持心情舒畅，避免情绪激动。",
        "exercise_advice": "提肛运动：每日早晚各做30-50次。方法：吸气时提肛，呼气时放松。散步、太极拳等有氧运动亦有益。",
        "postop_care": "化腐期（术后1-7天）：创面分泌物较多，以祛腐为主，使用九华膏纱条换药。生肌期（7-14天）：创面渐洁净，以生肌为主，改用生肌散。收口期（14天后）：创面缩小，促进愈合，使用珍珠散。术后坚持每日温水坐浴，定期扩肛。",
        "acupuncture_points": [
            "长强：主穴，直刺0.5-1寸",
            "承山：配穴，直刺1-1.5寸",
            "百会：虚证配穴，平刺或灸",
            "足三里：健脾益气，直刺1-2寸",
            "脾俞：脾虚配穴",
            "血海：血热配穴",
            "曲池：血热配穴"
        ],
        "sitz_bath_formula": "苦参30克，地榆30克，槐花20克，五倍子15克，明矾10克。煎水熏洗，每日2-3次，每次15-20分钟。",
        "warning_signs": [
            "便血量增多或持续不止",
            "痔核嵌顿肿痛剧烈",
            "肛门剧痛伴发热",
            "大便习惯改变或便中带血需排除肠道肿瘤"
        ]
    },
    {
        "disease_type": "肛裂",
        "title": "肛裂预防与保健指南",
        "prevention_points": [
            "保持大便软化通畅，多食蔬果纤维",
            "便后温水坐浴，保持肛门清洁",
            "避免腹泻和便秘",
            "及时治疗肛窦炎",
            "避免过度用力排便",
            "便后轻柔擦拭，避免损伤"
        ],
        "dietary_advice": "多食富含纤维的蔬菜水果，如芹菜、菠菜、香蕉等。多饮水，保持大便软化。忌食辛辣刺激食物。",
        "lifestyle_advice": "养成定时排便习惯，便意来时不要忍便。便后温水坐浴可缓解肛门括约肌痉挛。",
        "exercise_advice": "适当运动促进肠蠕动。提肛运动可增强肛门括约肌功能。避免久坐。",
        "postop_care": "术后每日温水坐浴2-3次，保持创面清洁。局部外用九华膏促进愈合。口服润肠通便之品（麻仁丸等）。避免便秘，保持大便通畅。",
        "acupuncture_points": [
            "长强：主穴，缓解疼痛",
            "承山：配穴，止痛",
            "大肠俞：调理大肠功能",
            "支沟：通便",
            "血海：血热配穴",
            "太冲：气滞配穴"
        ],
        "sitz_bath_formula": "苦参20克，黄柏15克，地榆20克，槐花15克，五倍子10克。煎水温洗，每日2-3次。",
        "warning_signs": [
            "疼痛持续加重",
            "肛裂经久不愈超过2月",
            "出现肛门狭窄",
            "形成皮赘或哨兵痔"
        ]
    },
    {
        "disease_type": "肛周脓肿",
        "title": "肛周脓肿预防与保健指南",
        "prevention_points": [
            "保持肛门清洁干燥",
            "及时治疗肛窦炎和肛乳头炎",
            "避免辛辣刺激食物",
            "增强体质，避免过度疲劳",
            "糖尿病患者控制血糖",
            "避免肛门外伤"
        ],
        "dietary_advice": "饮食清淡，忌食辛辣刺激、油腻食物。多食新鲜蔬果，保持大便通畅。",
        "lifestyle_advice": "保持肛周清洁卫生，便后温水清洗。增强体质，避免劳累。糖尿病患者积极控制血糖。",
        "exercise_advice": "适度运动增强体质，但急性期应休息。待脓肿治愈后可恢复正常运动。",
        "postop_care": "术后充分引流，每日换药，冲洗脓腔。内服清热解毒之品（五味消毒饮等）。注意观察有无肛瘘形成。保持创面清洁，按时换药直至愈合。",
        "acupuncture_points": [
            "长强：主穴，清热解毒",
            "会阴：局部取穴",
            "大肠俞：调理大肠",
            "曲池：清热解毒",
            "合谷：热毒盛配穴",
            "血海：热毒盛配穴"
        ],
        "sitz_bath_formula": "金银花30克，野菊花20克，蒲公英30克，地丁20克，苦参20克。煎水熏洗，早期促进消散，后期促进愈合。",
        "warning_signs": [
            "高热不退或寒战",
            "局部肿痛迅速扩大",
            "出现尿潴留",
            "脓肿破溃后形成肛瘘"
        ]
    },
    {
        "disease_type": "直肠脱垂",
        "title": "直肠脱垂预防与保健指南",
        "prevention_points": [
            "增强体质，适当锻炼",
            "积极治疗慢性咳嗽、便秘、腹泻",
            "避免蹲厕过久和过度用力",
            "坚持提肛运动",
            "小儿注意营养，防止久泻",
            "老年人避免重体力劳动"
        ],
        "dietary_advice": "营养均衡，增强体质。老年人多食易消化食物，保持大便通畅。小儿注意营养，防止腹泻。",
        "lifestyle_advice": "养成良好排便习惯，避免蹲厕过久。坚持提肛锻炼。治疗慢性咳嗽、便秘等诱因。",
        "exercise_advice": "提肛运动：每日3-5次，每次30-50下。仰卧起坐、深蹲等可增强腹肌和盆底肌。老年人量力而行。",
        "postop_care": "术后卧床休息，控制排便3天。进食少渣饮食。口服补中益气丸巩固。坚持提肛运动。避免重体力劳动和腹压增高活动。",
        "acupuncture_points": [
            "百会：升阳举陷，灸法更佳",
            "长强：主穴，提肛固脱",
            "大肠俞：调理大肠",
            "足三里：健脾益气",
            "气海：益气固脱，可灸",
            "脾俞：脾虚配穴"
        ],
        "sitz_bath_formula": "五倍子30克，明矾15克，石榴皮20克。煎水坐浴，有收敛固涩作用。每日1-2次。",
        "warning_signs": [
            "脱出物无法回纳",
            "脱出物发生嵌顿水肿",
            "伴有便血或黏液便",
            "合并其他肛肠疾病"
        ]
    },
    {
        "disease_type": "肛门疣赘",
        "title": "肛门疣赘及湿疹预防保健指南",
        "prevention_points": [
            "保持肛门清洁干燥",
            "避免搔抓刺激",
            "穿宽松透气内衣",
            "积极治疗原发病如痔疮、肛瘘",
            "避免潮湿和过度清洗",
            "调节情绪，避免精神紧张"
        ],
        "dietary_advice": "忌食辛辣刺激、鱼虾海鲜等发物。饮食清淡，多食新鲜蔬果。戒烟限酒。",
        "lifestyle_advice": "保持肛周清洁干燥，便后温水清洗，软布擦干。避免搔抓。穿纯棉透气内裤，勤换洗。",
        "exercise_advice": "适度运动增强体质。避免久坐潮湿环境。保持心情舒畅。",
        "postop_care": "术后保持创面清洁。按医嘱换药。避免刺激性食物。观察有无复发。",
        "acupuncture_points": [
            "长强：局部取穴",
            "大肠俞：调理大肠",
            "曲池：清热止痒",
            "血海：养血止痒",
            "三阴交：滋阴止痒"
        ],
        "sitz_bath_formula": "苦参30克，地肤子20克，白鲜皮20克，黄柏15克，蛇床子15克。煎水熏洗，清热燥湿止痒。",
        "warning_signs": [
            "瘙痒剧烈影响生活",
            "疣赘迅速增大",
            "出现破溃流脓",
            "顽固不愈超过三月需排除其他疾病"
        ]
    },
    {
        "disease_type": "肛门疖肿",
        "title": "肛门疖肿预防保健指南",
        "prevention_points": [
            "保持肛周皮肤清洁",
            "避免摩擦和外伤",
            "增强体质，避免熬夜劳累",
            "糖尿病患者控制血糖",
            "避免辛辣刺激饮食",
            "及时治疗毛囊炎、疖肿"
        ],
        "dietary_advice": "清淡饮食，忌食辛辣刺激、油腻煎炸食物。多食新鲜蔬果，多饮水。",
        "lifestyle_advice": "保持肛周清洁卫生。穿宽松透气内衣。避免局部摩擦刺激。增强体质。",
        "exercise_advice": "适度运动增强免疫力。急性期应休息，避免剧烈运动。",
        "postop_care": "保持创面清洁，按时换药。内服清热解毒中药。避免再次感染。",
        "acupuncture_points": [
            "阿是穴：局部取穴",
            "曲池：清热解毒",
            "合谷：清热消肿",
            "足三里：健脾益气"
        ],
        "sitz_bath_formula": "金银花20克，野菊花15克，蒲公英20克，地丁15克。煎水温洗，清热解毒消肿。",
        "warning_signs": [
            "疖肿迅速扩大",
            "伴有发热畏寒",
            "局部红肿范围扩大",
            "反复发作需查血糖等"
        ]
    }
]


async def seed():
    """执行完整知识库种子数据导入"""
    async with AsyncSessionLocal() as session:
        print("开始清理旧数据...")
        await session.execute(text("DELETE FROM anorectal_herbs WHERE tenant_id IS NULL"))
        await session.execute(text("DELETE FROM anorectal_formulas WHERE tenant_id IS NULL"))
        await session.execute(text("DELETE FROM anorectal_cases WHERE tenant_id IS NULL"))
        await session.execute(text("DELETE FROM prevention_guides WHERE tenant_id IS NULL"))
        print("✅ 旧数据清理完成\n")

        # 插入中药
        print("正在导入中药数据...")
        for h in HERBS:
            herb_data = h.copy()
            # 将 meridians 字符串转为列表（如果需要）
            if 'meridians' in herb_data and isinstance(herb_data['meridians'], str):
                herb_data['meridians'] = [m.strip() for m in herb_data['meridians'].split('、')]
            session.add(AnorectalHerb(**herb_data))
        print(f"✅ 成功导入 {len(HERBS)} 味中药\n")

        # 插入方剂
        print("正在导入方剂数据...")
        for f in FORMULAS:
            formula_data = f.copy()
            # composition 保持字符串，因为包含剂量
            if 'disease_types' not in formula_data:
                formula_data['disease_types'] = []
            session.add(AnorectalFormula(**formula_data))
        print(f"✅ 成功导入 {len(FORMULAS)} 首方剂\n")

        # 插入医案
        print("正在导入临床医案...")
        for c in CASES:
            case_data = c.copy()
            session.add(AnorectalCase(**case_data))
        print(f"✅ 成功导入 {len(CASES)} 例医案\n")

        # 插入预防保健
        print("正在导入预防保健指南...")
        for p in PREVENTION_GUIDES:
            guide_data = p.copy()
            # acupuncture_points 已经是列表格式
            session.add(PreventionGuide(**guide_data))
        print(f"✅ 成功导入 {len(PREVENTION_GUIDES)} 条预防保健指南\n")

        await session.commit()
        print("=" * 60)
        print("🎉 老中医临床经验知识库导入完成！")
        print("=" * 60)
        print(f"📚 中药：{len(HERBS)} 味")
        print(f"📜 方剂：{len(FORMULAS)} 首")
        print(f"📖 医案：{len(CASES)} 例")
        print(f"📋 预防保健：{len(PREVENTION_GUIDES)} 条")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed())
