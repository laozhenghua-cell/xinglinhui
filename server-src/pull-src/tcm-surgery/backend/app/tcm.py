"""中医常识与毒性分级工具(不删原书毒药,只做安全提示)。"""
from typing import Optional

# 剧毒药:内服可致命,须极慎
TOXIC_LETHAL = ("信石", "砒", "斑蝥", "红娘子", "水银", "轻粉", "巴豆")
# 有毒药:须炮制减毒、严格控量
TOXIC_CAUTION = (
    "马钱子", "番木鳖", "木鳖", "雄黄", "蟾酥", "川乌", "草乌", "闹羊花", "朱砂",
    "黄丹", "铅粉", "密陀僧", "铜绿", "胆矾", "硫黄", "藤黄",
)


def classify_toxicity(composition: str, usage_type: str = "") -> Optional[str]:
    """按组成分级:剧毒 / 有毒 / None(普通)。"""
    comp = composition or ""
    if any(k in comp for k in TOXIC_LETHAL):
        return "剧毒"
    if any(k in comp for k in TOXIC_CAUTION):
        return "有毒"
    return None


def build_warnings(composition: str, indication: str = "", usage_type: str = "") -> str:
    """根据组成/适应证生成禁忌警示(保留原书特色,只叠加安全提示)。"""
    comp = composition or ""
    ind = indication or ""
    parts: list[str] = []

    if "马钱子" in comp or "番木鳖" in comp or "木鳖" in comp:
        parts.append("马钱子(番木鳖/木鳖)有大毒,须炮制减毒、严格控量、中病即止")
    if any(k in ind for k in ("疯犬", "狂犬", "犬咬", "犬伤")):
        parts.append("疯犬咬伤必须立即到正规机构全程接种狂犬疫苗,本方仅为辅助、不可替代疫苗")
    if classify_toxicity(comp) == "剧毒":
        parts.append("含剧毒药(信石/斑蝥/轻粉等),内服须由经验医师严格控制剂量、严禁超量")
    if usage_type and "外用" in usage_type:
        parts.append("仅供外用,切勿内服")
    if parts:
        parts.append("孕妇忌服")

    return "。".join(parts) + "。" if parts else ""
