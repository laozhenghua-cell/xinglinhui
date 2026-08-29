"""辨证论治核心 —— 按「病种 × 阶段 × 证型」出方"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Disease, Formula, Syndrome, TreatmentRule
from ..schemas import (
    DifferentiateIn,
    DifferentiateOut,
    FormulaOut,
    MatchDomain,
    MatchFormulaIn,
    MatchFormulaOut,
    MatchFormulaResponse,
    MatchSyndrome,
    MatchSyndromeIn,
    MatchSyndromeResponse,
    MatchSyndromeScore,
    SyndromeOut,
    TreatmentRecommendIn,
    TreatmentRecommendOut,
)

router = APIRouter(prefix="/api/v1/treatment", tags=["treatment"])

# 证型 → 病机关键词(用于文琢之经验方的精准排序)
_SYNDROME_PATHOGEN: dict[str, list[str]] = {
    "寒湿凝滞": ["寒湿", "寒", "冷"],
    "湿热下注": ["湿热", "湿"],
    "血瘀阻络": ["血瘀", "瘀"],
    "正虚酿脓": ["虚", "酿脓", "托里"],
    "阴虚内热": ["阴虚", "阴"],
    "气血两虚": ["气血", "虚"],
    "正虚邪恋": ["虚", "邪恋"],
    "火毒炽盛": ["火毒", "热毒", "火"],
    "热盛肉腐": ["热", "毒", "腐"],
    "余毒未清": ["余毒", "毒"],
    "肝郁胃热": ["肝郁", "胃热"],
    "痰火凝结": ["痰", "火"],
    "风热犯表": ["风热", "风"],
}

# 三阶段对应治法与原则(成脓期按病种大类区分)
def _stage_advice(stage: str, category: str = None, is_yang: bool = True) -> str:
    if stage == "初起":
        return "疮疡初起,邪未成脓,宜「消法」消散。内服清热解毒、活血消肿之剂,外敷消肿散结之药,使肿疡消散于无形。"
    if stage == "溃后":
        if is_yang:
            return "溃后气血已伤,宜「补法」扶正。内服补益气血之剂,外用生肌收口之药,促进疮口愈合。"
        return "阴证溃后气血更虚,宜「温补」气血。内服温补之剂,外用生肌收口之药,促进疮口愈合。"
    # 成脓期:按病种大类区分治则
    if category == "疔":
        return "疔疮成脓,宜清热解毒、透脓拔毒(可加皂角刺、穿山甲),严禁挤压、忌过早切开,防走黄。"
    if category == "脱疽":
        return "脱疽成脓,宜清热解毒、活血通络,忌大切开,保肢为要。"
    if not is_yang:
        return "阴证酿脓,宜「温托」透脓托毒,忌寒凉凝滞,不宜过早切开。"
    return "脓已形成,宜「托法」透脓托毒。内服透托之剂,必要时切开排脓,务使脓毒外泄,不可过早补益以免闭门留寇。"


@router.post("/recommend", response_model=TreatmentRecommendOut)
async def recommend(body: TreatmentRecommendIn, db: AsyncSession = Depends(get_db)):
    """给定病种 + 阶段 + 证型,返回内治方 + 外治 + 调护"""
    disease = await db.get(Disease, body.disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail="病种不存在")

    syndrome = None
    if body.syndrome_id:
        syndrome = await db.get(Syndrome, body.syndrome_id)

    stmt = (
        select(TreatmentRule)
        .options(
            selectinload(TreatmentRule.syndrome),
            selectinload(TreatmentRule.formula),
        )
        .where(
            TreatmentRule.disease_id == body.disease_id,
            TreatmentRule.stage == body.stage,
        )
    )
    result = await db.execute(stmt)
    rules = list(result.scalars().all())

    # 优先匹配证型,次选该阶段通用规则(syndrome_id 为空);证型无规则时回退到该阶段全部规则
    if body.syndrome_id:
        matched = [r for r in rules if r.syndrome_id == body.syndrome_id]
        matched += [r for r in rules if r.syndrome_id is None]
        if not matched:
            matched = rules
    else:
        matched = [r for r in rules if r.syndrome_id is None]

    # 去重,证型细分规则(is_specific)优先展示
    seen, dedup = set(), []
    for r in sorted(matched, key=lambda x: (not x.is_specific, x.id)):
        if r.id not in seen:
            seen.add(r.id)
            dedup.append(r)

    summary = _stage_advice(body.stage, disease.category, disease.is_yang)
    if syndrome:
        summary = f"{disease.name} · {syndrome.name}({syndrome.yin_yang}证) · {body.stage}期。{summary}"

    external_formulas = await _external_formula_refs(body.stage, disease.is_yang, db)
    experience_formulas = await _experience_formula_refs(disease, syndrome, db)

    return TreatmentRecommendOut(
        disease=disease,
        stage=body.stage,
        syndrome=syndrome,
        rules=dedup,
        external_formulas=external_formulas,
        experience_formulas=experience_formulas,
        summary=summary,
    )


async def _experience_formula_refs(disease: Disease, syndrome, db: AsyncSession) -> list[FormulaOut]:
    """文琢之《中医外科经验论集》内服经验方:按病名/别名/大类 + 证型病机关键词匹配。"""
    kws = [disease.name, disease.category] + [a for a in (disease.aliases or []) if a]
    # 证型 → 病机关键词(用于在命中病种内进一步精准排序)
    patho_kws = _SYNDROME_PATHOGEN.get(syndrome.name, []) if syndrome else []

    stmt = (
        select(Formula)
        .where(
            Formula.source == "《中医外科经验论集》",
            Formula.usage_type.in_(["内服", "内服外用"]),
        )
        .order_by(Formula.id)
    )
    result = await db.execute(stmt)
    formulas = list(result.scalars().all())

    matched = []
    for f in formulas:
        text = (f.name or "") + (f.indication or "")
        if any(k and k in text for k in kws):
            matched.append(f)

    # 排序:方名命中病名 > 适应证命中病名 > 命中证型病机,取前 6
    def _score(f: Formula) -> int:
        name_hit = any(k and k in (f.name or "") for k in kws)
        ind_hit = any(k and k in (f.indication or "") for k in kws)
        patho_hit = any(k and k in (f.indication or "") for k in patho_kws)
        return (4 if name_hit else 0) + (2 if ind_hit else 0) + (1 if patho_hit else 0)

    matched.sort(key=lambda f: (_score(f), f.id), reverse=True)
    return [FormulaOut.model_validate(f) for f in matched[:6]]


async def _external_formula_refs(stage: str, is_yang: bool, db: AsyncSession) -> list[FormulaOut]:
    """马培之《外科传薪集》外治方参考:按消/托/补阶段匹配,阴证优先温通方。"""
    method = {"初起": "消", "成脓": "托", "溃后": "补"}.get(stage)
    if not method:
        return []
    stmt = (
        select(Formula)
        .where(
            Formula.source == "《外科传薪集》",
            Formula.usage_type.in_(["外用", "内服外用"]),
            Formula.method == method,
        )
        .order_by(Formula.id)
    )
    result = await db.execute(stmt)
    formulas = list(result.scalars().all())

    # 阴证:温通方(阳和解凝膏/回阳散/黑敷药等)排前;阳证:寒凉围药在前
    def _is_warm(f: Formula) -> bool:
        text = (f.indication or "") + (f.name or "")
        return any(k in text for k in ("阴", "寒", "漫肿", "不红", "不热", "鹤膝", "回阳", "温", "阳和", "黑敷", "皮色不变"))

    if not is_yang:
        formulas.sort(key=lambda f: (not _is_warm(f), f.id))
    else:
        formulas.sort(key=lambda f: (_is_warm(f), f.id))

    # 只取最贴切的前 8 首,避免列表过长
    return [FormulaOut.model_validate(f) for f in formulas[:8]]


# 各证型的精准辨证关键词(与前端四诊选项一致),舌/苔/脉权重高、症状权重低
_SYNDROME_KEYWORDS: dict[str, list[str]] = {
    "火毒炽盛": ["舌红", "苔黄", "脉数", "红肿热痛", "口渴", "发热", "便结", "溲赤"],
    "热盛肉腐": ["舌红", "苔黄燥", "脉洪数", "红肿热痛", "发热", "口渴"],
    "余毒未清": ["舌红", "脉数", "腐肉不脱", "红肿热痛"],
    "正虚邪恋": ["舌淡", "脉细弱", "脓水清稀", "腐肉不脱", "新肉不生", "神疲乏力", "面色无华"],
    "气血两虚": ["舌淡", "苔薄白", "脉细弱", "疮口不敛", "神疲乏力", "面色无华"],
    "湿热下注": ["舌红", "苔黄腻", "脉滑数", "红肿热痛", "纳呆"],
    "寒湿凝滞": ["舌淡", "苔薄白", "脉沉细", "发凉麻木", "畏寒"],
    "血瘀阻络": ["舌紫暗", "舌有瘀斑", "脉涩", "刺痛固定"],
    "正虚酿脓": ["舌淡", "苔薄白", "脉细弱", "漫肿", "脓成不溃", "神疲乏力", "畏寒"],
    "肝郁胃热": ["舌红", "苔黄", "脉弦数", "红肿热痛"],
    "痰火凝结": ["舌淡红", "苔薄白", "脉弦"],
    "阴虚内热": ["舌红", "苔少", "脉细数", "潮热盗汗"],
    "风热犯表": ["舌红", "苔黄", "脉浮数", "发热", "口渴"],
}


def _kw_weight(kw: str) -> int:
    """舌/苔/脉为辨证主征,权重高;症状为佐证,权重低"""
    return 3 if kw.startswith(("舌", "苔", "脉")) else 1


def _score(syndrome: Syndrome, symptoms: list[str]) -> int:
    keywords = _SYNDROME_KEYWORDS.get(syndrome.name, [])
    return sum(_kw_weight(k) for k in keywords if k in symptoms)


def _matched(syndrome: Syndrome, symptoms: list[str]) -> list[str]:
    keywords = _SYNDROME_KEYWORDS.get(syndrome.name, [])
    return [k for k in keywords if k in symptoms]


# 阴阳通用证型:虚证(溃后)与血瘀,阳证阴证皆可见,不按阴阳硬过滤
_UNIVERSAL_SYNDROMES = {"气血两虚", "正虚邪恋", "血瘀阻络"}

# 跨阶段证型:火毒炽盛既见于初起(阳证初起),又见于成脓(脱疽热毒型/疔疮走黄/糖尿病坏疽)
_CROSS_STAGE_SYNDROMES = {"火毒炽盛": {"初起", "成脓"}}


@router.post("/differentiate", response_model=DifferentiateOut)
async def differentiate(body: DifferentiateIn, db: AsyncSession = Depends(get_db)):
    """辨证导航:病种专属——只返回该病种有论治规则的证型;分型病种不按阴阳/阶段,直接给病机分型"""
    result = await db.execute(select(Syndrome).order_by(Syndrome.id))
    all_syn = list(result.scalars().all())

    # 分型病种(脱疽/瘰疬/冻疮/乳岩/丹毒/臁疮/褥疮):不辨阴阳阶段,直接给该病种分型
    differentiation = None
    if body.disease_id:
        disease = await db.get(Disease, body.disease_id)
        differentiation = disease.differentiation if disease else None

    if body.disease_id and differentiation == "分型":
        # 该病种 stage=分型 的规则 → 证型
        rst = select(TreatmentRule.syndrome_id).where(
            TreatmentRule.disease_id == body.disease_id,
            TreatmentRule.stage == "分型",
            TreatmentRule.syndrome_id.isnot(None),
        )
        ids = list(dict.fromkeys((await db.execute(rst)).scalars().all()))
        syndromes = [s for s in all_syn if s.id in ids]
    else:
        # 消托补病种:病种专属 + 阶段/阴阳过滤
        if body.disease_id:
            rst = select(TreatmentRule.syndrome_id).where(
                TreatmentRule.disease_id == body.disease_id,
                TreatmentRule.syndrome_id.isnot(None),
            )
            if body.stage:
                rst = rst.where(TreatmentRule.stage == body.stage)
            valid_ids = set((await db.execute(rst)).scalars().all())
            if valid_ids:
                all_syn = [s for s in all_syn if s.id in valid_ids]

        syndromes = []
        for s in all_syn:
            # 阶段过滤(跨阶段证型特殊处理)
            if body.stage:
                if s.name in _CROSS_STAGE_SYNDROMES:
                    if body.stage not in _CROSS_STAGE_SYNDROMES[s.name]:
                        continue
                elif s.stage != body.stage:
                    continue
            # 阴阳过滤(通用证型对阴阳都开放)
            if body.yin_yang and s.yin_yang != body.yin_yang and s.name not in _UNIVERSAL_SYNDROMES:
                continue
            syndromes.append(s)

    if body.symptoms:
        syndromes.sort(key=lambda s: _score(s, body.symptoms), reverse=True)

    suggestion = ""
    if not syndromes:
        suggestion = "未匹配到证型,请核对阴阳与阶段的选择。"
    elif body.symptoms:
        top = syndromes[0]
        matched = _matched(top, body.symptoms)
        if matched:
            suggestion = f"最符合的证型为「{top.name}」({top.yin_yang}证),依据:{'、'.join(matched)}。请结合舌脉与全身症状复核。"
        else:
            suggestion = f"最符合的证型为「{top.name}」({top.yin_yang}证),请补充舌脉症状以进一步确认。"
    else:
        suggestion = f"共 {len(syndromes)} 个候选证型,请进一步补充症状以缩小范围。"

    return DifferentiateOut(
        matched_syndromes=[SyndromeOut.model_validate(s) for s in syndromes],
        suggestion=suggestion,
    )


# ---------- 方证对应(按证选方)—— 非疮疡方(骨伤/杂病)也有门可入,辨证不按病 ----------
# 每域一套辨证维度:证候 key → 关键词 → 反查方(与疮疡辨证同构,只是维度不同)
MATCH_DOMAINS: list[MatchDomain] = [
    MatchDomain(domain="骨伤", label="骨伤科", syndromes=[
        MatchSyndrome(key="跌打骨伤", label="跌打骨伤", desc="跌打损伤、骨折、骨断、刀斧金刃伤(瘀血证)"),
        MatchSyndrome(key="风寒湿痹", label="风寒湿痹", desc="风寒湿痹、关节冷痛、四肢麻木、鹤膝风(痹证)"),
        MatchSyndrome(key="筋骨疼痛", label="筋骨疼痛", desc="周身筋骨疼痛、手足酸软、诸痛(痛证)"),
        MatchSyndrome(key="中风偏瘫", label="中风偏瘫", desc="半身不遂、瘫痪、中风、惊风(风证)"),
    ]),
    MatchDomain(domain="杂病", label="内科杂病", syndromes=[
        MatchSyndrome(key="脾胃虚弱", label="脾胃虚弱", desc="消化不良、胃弱食少"),
        MatchSyndrome(key="胃脘积聚", label="胃脘积聚", desc="胃癌、积聚"),
        MatchSyndrome(key="哮证", label="哮证", desc="哮喘、盐哮、奶哮"),
        MatchSyndrome(key="痔疮便血", label="痔疮便血", desc="痔核、肠风下血、漏管"),
        MatchSyndrome(key="疯犬咬伤", label="疯犬咬伤", desc="疯犬/狂犬咬伤"),
        MatchSyndrome(key="小儿疳疾", label="小儿疳疾", desc="疳疾、疳积"),
        MatchSyndrome(key="汤火伤", label="汤火伤", desc="汤火烫伤"),
        MatchSyndrome(key="其他杂证", label="其他杂证", desc="象皮肿、臭虫、舌长、痘疹入目"),
    ]),
]

# 证候 key → 命中关键词(在适应证/功效中做子串匹配)
MATCH_KEYWORDS: dict[str, list[str]] = {
    "跌打骨伤": ["跌打", "损伤", "骨折", "骨断", "接骨", "刀斧", "金刃", "见血", "瘀", "骨碎"],
    "风寒湿痹": ["风寒", "湿痹", "痹", "关节", "冷痛", "麻木", "鹤膝", "痼冷"],
    "筋骨疼痛": ["筋骨疼痛", "疼痛", "诸痛", "酸软"],
    "中风偏瘫": ["半身不遂", "瘫痪", "左瘫右痪", "中风", "惊风", "母猪风", "痿废"],
    "脾胃虚弱": ["消化不良", "胃弱", "食少", "健胃", "健脾"],
    "胃脘积聚": ["胃癌", "积聚"],
    "哮证": ["哮", "喘"],
    "痔疮便血": ["痔", "便血", "肠风", "漏", "瘘"],
    "疯犬咬伤": ["疯犬", "狂犬", "犬咬", "犬伤"],
    "小儿疳疾": ["疳"],
    "汤火伤": ["汤火", "烫", "火伤"],
    "其他杂证": ["象皮", "臭虫", "舌长", "痘", "目"],
}

# 证候 key → 四诊/表现关键词(勾选后自动评分证候,舌/苔/脉权重高)
MATCH_SYMPTOMS: dict[str, list[str]] = {
    "跌打骨伤": ["舌紫暗", "舌有瘀斑", "脉涩", "跌打外伤", "肿胀青紫", "疼痛拒按", "瘀斑"],
    "风寒湿痹": ["舌淡", "苔白", "脉沉细", "脉迟", "关节冷痛", "遇寒加重", "得温则减", "肢体麻木", "畏寒"],
    "风湿热痹": ["舌红", "苔黄腻", "脉滑数", "关节红肿", "灼热", "发热"],
    "筋骨疼痛": ["周身酸痛", "手足酸软", "劳则加重", "筋骨疼痛"],
    "中风偏瘫": ["半身不遂", "口眼歪斜", "言语不利", "肢体麻木", "瘫痪", "头晕"],
    "脾胃虚弱": ["舌淡", "苔白", "脉弱", "食少", "纳呆", "腹胀", "便溏", "神疲乏力"],
    "胃脘积聚": ["消瘦", "胃脘", "积聚", "呕恶", "纳差", "胃癌"],
    "哮证": ["苔白滑", "苔黄", "脉滑", "喘息", "喉中痰鸣", "咳嗽"],
    "痔疮便血": ["舌红", "苔黄腻", "脉滑数", "便血", "痔核脱出", "肛门灼热", "便秘"],
    "疯犬咬伤": ["疯犬咬伤", "犬咬", "狂犬", "咬伤史"],
    "小儿疳疾": ["消瘦", "面黄", "腹大", "纳呆", "疳积"],
    "汤火伤": ["汤火伤", "烫伤", "烧伤", "火伤"],
    "其他杂证": ["象皮肿", "臭虫", "舌长", "痘疹", "目"],
}


def _formula_match(formula: Formula, keywords: list[str]) -> tuple[int, list[str]]:
    """在适应证 + 功效中命中关键词,返回(得分, 命中词)。"""
    haystack = f"{formula.indication or ''} {formula.function or ''}"
    matched = [k for k in keywords if k and k in haystack]
    return len(matched), matched


def _symptom_weight(kw: str) -> int:
    """舌/苔/脉为辨证主征,权重高;症状为佐证,权重低。"""
    return 3 if kw.startswith(("舌", "苔", "脉")) else 1


@router.get("/match-options", response_model=list[MatchDomain])
async def match_options() -> list[MatchDomain]:
    """按证选方的证候选项(骨伤/杂病各一套辨证维度,含四诊关键词)。"""
    out: list[MatchDomain] = []
    for md in MATCH_DOMAINS:
        syndromes = [
            MatchSyndrome(key=s.key, label=s.label, desc=s.desc, symptoms=MATCH_SYMPTOMS.get(s.key, []))
            for s in md.syndromes
        ]
        out.append(MatchDomain(domain=md.domain, label=md.label, syndromes=syndromes))
    return out


@router.post("/match-syndrome", response_model=MatchSyndromeResponse)
async def match_syndrome(body: MatchSyndromeIn) -> MatchSyndromeResponse:
    """四诊驱动辨证:勾选症状/舌脉 → 自动评分并排序证候(与疮疡辨证同构)。"""
    scored: list[MatchSyndromeScore] = []
    for md in MATCH_DOMAINS:
        if body.domain and md.domain != body.domain:
            continue
        for s in md.syndromes:
            kws = MATCH_SYMPTOMS.get(s.key, [])
            matched = [k for k in kws if k in body.symptoms]
            if not matched:
                continue
            score = sum(_symptom_weight(k) for k in matched)
            scored.append(MatchSyndromeScore(
                key=s.key, label=s.label, desc=s.desc, score=score, matched=matched,
            ))

    scored.sort(key=lambda x: (-x.score, x.key))

    suggestion = ""
    if not body.symptoms:
        suggestion = "请勾选四诊/表现,系统将自动辨证并给出最可能证候。"
    elif not scored:
        suggestion = "未匹配到证候,请补充或更换四诊表现。"
    else:
        top = scored[0]
        basis = "、".join(top.matched)
        suggestion = f"最可能为「{top.label}」,依据:{basis}。请结合整体情况复核。"
        if len(scored) > 1:
            suggestion += f" 次选:{'、'.join(x.label for x in scored[1:3])}。"

    return MatchSyndromeResponse(matched=scored, suggestion=suggestion)


@router.post("/match-formula", response_model=MatchFormulaResponse)
async def match_formula(body: MatchFormulaIn, db: AsyncSession = Depends(get_db)):
    """方证对应:由证候反查方(含马钱子方毒性警示)。"""
    domains: set[str] = set()
    keywords: list[str] = []
    for key in body.keys:
        if key not in MATCH_KEYWORDS:
            continue
        keywords.extend(MATCH_KEYWORDS[key])
        # 由 key 反推病域(用于汇总提示)
        for md in MATCH_DOMAINS:
            if any(s.key == key for s in md.syndromes):
                domains.add(md.domain)

    stmt = select(Formula)
    if body.domain:
        stmt = stmt.where(Formula.domain == body.domain)
    elif domains:
        stmt = stmt.where(Formula.domain.in_(domains))
    result = await db.execute(stmt)
    formulas = list(result.scalars().all())

    items: list[MatchFormulaOut] = []
    for f in formulas:
        score, matched = _formula_match(f, keywords)
        if score > 0:
            items.append(MatchFormulaOut(formula=FormulaOut.model_validate(f), matched=matched, score=score))

    items.sort(key=lambda x: (x.score, x.formula.id), reverse=True)

    summary = ""
    if not body.keys:
        summary = "请选择证候(病机)以反查相应方剂。"
    elif not items:
        summary = "未命中方剂,请更换或放宽证候选择。"
    else:
        top = items[0]
        summary = f"共命中 {len(items)} 首方,最贴合者为「{top.formula.name}」({top.formula.domain or '—'})。马钱子(番木鳖)类方有大毒,须炮制减毒、严格控量、孕妇忌服。"

    return MatchFormulaResponse(items=items, summary=summary)
