#!/usr/bin/env python3
"""
从《疮疡图谱》PDF提取数据并生成种子数据
"""
import sys
import json
from pathlib import Path

# 基于图谱第22-40页的疮疡类型
ULCER_TYPES = [
    {
        "ulcer_type": "yinyangju",
        "chinese_name": "印堂疔",
        "location": "头面部",
        "location_detail": "印堂穴处（两眉之间）",
        "category": "疔",
        "morphology": {
            "color": "鲜红",
            "size": "粟粒样膨隆",
            "shape": "圆形",
            "texture": "根深坚硬",
            "pain": "时痒时痛，形小根硬"
        },
        "clinical_features": "初起顶有一粟粒样脓头，时痒时痛，形小根硬，根盘收束，图示脓头破溃，麻栓外脱之时",
        "treatment_principle": "清热解毒",
        "internal_treatment": {
            "formulas": [
                {
                    "name": "五味消毒饮加减",
                    "composition": "金银花、野菊花、蒲公英、紫花地丁、紫背天葵"
                }
            ]
        },
        "external_treatment": {
            "topical": [
                {"name": "油调膏", "usage": "或玉露散外敷"}
            ]
        },
        "page_number": 22
    },
    {
        "ulcer_type": "yanjiaoju",
        "chinese_name": "眼角疔",
        "location": "头面部",
        "location_detail": "眼角内侧起",
        "category": "疔",
        "morphology": {
            "color": "黄白相杂",
            "size": "其色黄白",
            "shape": "圆形",
            "texture": "根盘坚硬",
            "pain": "上下眼泡，右眼开合难"
        },
        "treatment_principle": "提脓拔毒",
        "page_number": 23
    },
    {
        "ulcer_type": "bigenju",
        "chinese_name": "鼻根疔",
        "location": "头面部",
        "location_detail": "鼻根部起一粟粒大脓头",
        "category": "疔",
        "morphology": {
            "color": "坚硬根深",
            "size": "周围略肿胀",
            "shape": "圆形",
            "texture": "火毒不倒"
        },
        "clinical_features": "鼻根起一粟粒大脓头，坚硬根深，周围略肿胀，色红，图示脓头尚未破溃，麻栓外脱",
        "treatment_principle": "同印堂疔",
        "page_number": 23
    },
    {
        "ulcer_type": "biju",
        "chinese_name": "鼻疔",
        "location": "头面部",
        "location_detail": "鼻尖或鼻孔内",
        "category": "疔",
        "morphology": {
            "color": "黄白相杂",
            "size": "根盘坚硬",
            "texture": "麻栓未脱",
            "pain": "属于初期"
        },
        "clinical_features": "图示鼻尖部起一粟米大脓头，根盘坚硬，黄白相杂，色嫩红，周围肿势不到，属于初期",
        "treatment_principle": "提脓解毒",
        "internal_treatment": {
            "formulas": [{"name": "五味消毒饮加减"}]
        },
        "external_treatment": {
            "topical": [{"name": "油调膏", "usage": "玉露散外敷"}]
        },
        "page_number": 23
    },
    {
        "ulcer_type": "biyiju",
        "chinese_name": "鼻翼疔",
        "location": "头面部",
        "location_detail": "右侧鼻翼起一粟粒大脓头",
        "category": "疔",
        "morphology": {
            "color": "根盘赤收束",
            "size": "肿势廷向鼻部及鼻部",
            "shape": "圆形",
            "texture": "连及鼻唇上唇"
        },
        "clinical_features": "图示鼻翼大，火毒外泄",
        "treatment_principle": "同鼻疔",
        "page_number": 25
    },
    {
        "ulcer_type": "renzhongju",
        "chinese_name": "人中疔",
        "location": "头面部",
        "location_detail": "人中穴处",
        "category": "疔",
        "morphology": {
            "color": "约黄白色膨头",
            "size": "伸屈鼻部及鼻部",
            "shape": "圆形",
            "texture": "周围肿势不到，属于初期"
        },
        "clinical_features": "位于人中穴处，约黄白色膨头，有黄白色膨头，其形且小，但根深且硬，图示脓头尚大，色嫩红，周围肿势不到，属于初期",
        "treatment_principle": "同鼻疔",
        "page_number": 25
    },
    {
        "ulcer_type": "yingxiangju",
        "chinese_name": "迎香疔",
        "location": "头面部",
        "location_detail": "迎香穴处之疔",
        "category": "疔",
        "clinical_features": "右侧迎香穴有一粟米大脓头，坚硬根深，连及鼻翼肿大，图示脓外大肿，火毒外泄",
        "treatment_principle": "同鼻疔",
        "page_number": 25
    },
    {
        "ulcer_type": "eganju",
        "chinese_name": "颚疔",
        "location": "头面部",
        "location_detail": "颚部两鼻部",
        "category": "疔",
        "morphology": {
            "color": "为火毒肿盛",
            "size": "相当于西医所称的和、痛、急性蜂窝组炎"
        },
        "clinical_features": "疔症在两鼻部生疔，统称为颚疔，本病名较早见于明《杨医准绳·卷上》。相当于西医所称的和、痛、急性蜂窝组炎",
        "page_number": 25
    },
    {
        "ulcer_type": "eju",
        "chinese_name": "颚疔（颚疔）",
        "chinese_name_alt": "右颚部红肿",
        "location": "头面部",
        "location_detail": "左颚部红肿，中央透蓝已破，麻栓头已破溃，麻栓未脱，火毒外泄",
        "category": "疔",
        "page_number": 27
    },
    {
        "ulcer_type": "eju_houqi",
        "chinese_name": "颚疔（后期）",
        "location": "头面部",
        "location_detail": "麻栓已脱，疮口溃开，新肉内生，疮水不多，新内红活，收口即愈",
        "category": "疔",
        "page_number": 28
    },
    {
        "ulcer_type": "chunju",
        "chinese_name": "唇疔",
        "location": "头面部",
        "location_detail": "上下唇部的疔疮",
        "category": "疔",
        "clinical_features": "凡生于唇部的疔疮，统称为唇疔，又称为鱼口疔，生于口唇内里膜反唇疔，生于左右口角称口角唇疔，其特点是：初起如粟，择痛不快，逐渐肿胀，唇部外翻，并可因难，伴有寒热",
        "morphology": {
            "color": "红肿热痛，重者至面颊",
            "size": "初起如粟",
            "pain": "择痛不快"
        },
        "treatment_principle": "清热解毒，提脓",
        "internal_treatment": {
            "formulas": [
                {"name": "同印堂疔"},
                {"name": "五味消毒饮加减，黄连解毒汤，配服嗽秋丸，西黄丸"}
            ]
        },
        "external_treatment": {
            "topical": [
                {"name": "油调膏", "usage": "玉露散外敷"},
                {"name": "麻栓不脱", "usage": "用九一丹，八二丹，提毒散草提毒"}
            ]
        },
        "page_number": 28
    },
    {
        "ulcer_type": "chunju_zhoukou",
        "chinese_name": "唇疔（颚口疔）",
        "location": "头面部",
        "location_detail": "疔症于右颚口唇上方，有一粟米大脓头，其形旦小，但根深且硬，根盘虽坚，肿势塞延上唇及右侧面颊，开合因难",
        "category": "疔",
        "page_number": 29
    },
    {
        "ulcer_type": "chunju_zhongqi",
        "chinese_name": "唇疔（中期）",
        "location": "头面部",
        "location_detail": "右侧唇疔，疮口溃开，如胜不多，新内红活，生长较好",
        "category": "疔",
        "page_number": 29
    },
    {
        "ulcer_type": "dicangju",
        "chinese_name": "地仓疔",
        "location": "头面部",
        "location_detail": "地仓穴处",
        "category": "疔",
        "clinical_features": "疔生于地仓穴处，称为地仓疔，可向周围扩散，甚开口困难",
        "morphology": {
            "color": "左侧面颊（相当于地仓穴处）生疔",
            "size": "麻栓破溃，麻栓未落，肿汗溃散手术口，毒郁外泄"
        },
        "treatment_principle": "同颚疔",
        "page_number": 29
    },
    {
        "ulcer_type": "eju_other",
        "chinese_name": "颚疔",
        "location": "头面部",
        "location_detail": "生于颚部的疔疮",
        "category": "疔",
        "page_number": 30
    },
    {
        "ulcer_type": "eju_alt",
        "chinese_name": "颚疔",
        "location": "头面部",
        "location_detail": "右侧唇下颚部起一粟粒样脓出，其位虽小，宜进边界较多，按之有波动感，为麻毒已成，肿势不到",
        "category": "疔",
        "page_number": 30
    },
    {
        "ulcer_type": "zhijiagouju",
        "chinese_name": "指甲沟疔",
        "location": "上肢",
        "location_detail": "手指甲沟处",
        "category": "疔",
        "clinical_features": "又称蛇毒、天蛇头、天蛇头，水蛇头、蛇头疔。其特点是：发手指甲沟，因其皮内压膨胀，故成脓后多向外溃破，成脓迟者，扩散后可沿腱鞘引流，以致手指全部出现成膜胀不宜，甚至波动有发痛",
        "morphology": {
            "color": "赤红至滞涨满者，下垂郁血",
            "size": "图示脓在足初始，可正常血白，内脓张满高处"
        },
        "treatment_principle": "清热解毒",
        "internal_treatment": {
            "formulas": [{"name": "仙方活命饮加减"}]
        },
        "external_treatment": {
            "topical": [
                {"name": "一致膏", "usage": "金黄散外敷"},
                {"name": "成膜切开引流", "usage": "外敷一致膏"}
            ]
        },
        "page_number": 31
    },
    {
        "ulcer_type": "shetouding",
        "chinese_name": "蛇头疔",
        "location": "上肢",
        "location_detail": "手指甲沟之疔疮",
        "category": "疔",
        "page_number": 32
    },
    {
        "ulcer_type": "shetouju_alt",
        "chinese_name": "蛇头疔（腹肿）",
        "location": "上肢",
        "location_detail": "图示蛇头疔腹肿，指滑麻满迅赤，黄白相杂，麻栓粗糙，脓头郁闭，内脓张满角膜",
        "category": "疔",
        "page_number": 33
    },
    {
        "ulcer_type": "shetouju_jiangu",
        "chinese_name": "蛇头疔（合并骨疔）",
        "location": "上肢",
        "location_detail": "图示蛇头疔腹肿脓，发于右食指中节，治疗不当，逐新加剧，并多及筋膜，若不及时治疗，势必损及筋膜",
        "category": "疔",
        "page_number": 33
    },
]


def create_seed_data():
    """生成种子数据"""
    output_file = Path(__file__).parent.parent / "data" / "seed_data" / "ulcer_knowledge.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ULCER_TYPES, f, ensure_ascii=False, indent=2)

    print(f"✅ 成功生成 {len(ULCER_TYPES)} 条疮疡知识数据")
    print(f"📁 文件位置: {output_file}")
    return output_file


if __name__ == "__main__":
    create_seed_data()
