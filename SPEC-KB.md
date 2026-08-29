# 统一共用知识总库 — 工程规格(KB v1)

## 目标
把四专科内容集中为一套共享 PG 表 + 统一检索 + 前端"知识总库"中心。
现有平台:https://tcm.llixz.cn(1 后端 FastAPI+PG16 docker + 1 前端 Vue3+EP,4 模块)。

## 数据源盘点
| 内容 | 疮疡 surgery | 痔漏 anorectal | 儿科 pediatrics | 丹药 alchemy |
|---|---|---|---|---|
| 方剂 | surgery_formulas 508 | anorectal_formulas 75 | JSON 45 | JSON 34 |
| 中药 | (组成内嵌) | anorectal_herbs 72 | — | 引药 245(独立表) |
| 病种 | surgery_diseases 107 | disease_types(JSONB,从方剂/医案提取) | 8 症(入证型) | — |
| 证型 | surgery_syndromes 13 | syndrome_rules 38 | JSON 8 | — |
| 医案 | surgery_cases 40 + expert_cases 40 | anorectal_cases 14 + medical_cases 7 | JSON 32 | — |
| 要诀/训诫 | clinical_tips 59 | safety_rules 67 / prevention_guides 6 | JSON 159 | — |
| 术语 | — | — | — | JSON 48 |
| 引药 | — | — | — | JSON 245 |

本地已提取:kb-data/pediatrics.json、kb-data/alchemy.json(规范化结构:module/origin_id/name/aliases/composition/...)

## 后端规格(platform/backend)
新增 `app/models/kb.py`(全部带 `module` 字段: surgery|anorectal|pediatrics|alchemy)与 `app/api/v1/kb.py`:
1. 表:kb_formulas / kb_herbs / kb_diseases / kb_syndromes / kb_cases / kb_tips / kb_terms / kb_dulong
   - 通用列:id(UUID)、module、origin_id(源标识,唯一约束 (module, origin_id))、created_at;其余见下
   - kb_formulas: name, aliases(JSONB), source, category, composition(JSONB [{name,dose}]), function, indication, usage, method, formula_type, contraindications, modifications, preparation, toxicity, extra(JSONB)
   - kb_herbs: name, pinyin, aliases(JSONB), category, properties(性味), meridians(JSONB), effects, indications, contraindications, dosage, usage_notes, extra
   - kb_diseases: name, aliases(JSONB), category, location, morphology, characteristics, differential, prognosis, western_equiv, source, is_dangerous, extra
   - kb_syndromes: name, aliases(JSONB), yin_yang, stage, local_signs, systemic_signs, tongue_pulse, summary, extra
   - kb_cases: title, disease, syndrome, patient_info, chief_complaint, history, treatment, effect, source, expert_name, category, extra
   - kb_tips: category, content, source, extra
   - kb_terms: term, definition, source, extra
   - kb_dulong: section, n(int), disease, guide
2. API(免鉴权,前缀 /api/v1/kb):
   - GET /kb/stats:各表计数 + 按 module 计数
   - GET /kb/formulas?q&module&category&page&size(统一方剂,含 aliases/composition)
   - GET /kb/herbs /kb/diseases /kb/syndromes /kb/cases /kb/tips /kb/terms /kb/dulong(同参数模式)
   - GET /kb/{type}/{id}:详情
   - GET /kb/search?q=&type=:跨类型全文检索(q 匹配 name/aliases/source/indication/content/term 等,ILIKE,每类返回前 20 条,带类型标签);支持 type 过滤
   - GET /kb/linked?type=&id=:返回与该条内容相关的其他类型条目(按名称/别名/组成药物名匹配,简单启发式即可)
3. 迁移脚本 `scripts/migrate_kb.py`(幂等:按 (module, origin_id) upsert):
   - 从 PG:surgery_formulas→kb_formulas(composition 文本按 、和,切分 {name,dose})、surgery_diseases、surgery_syndromes、surgery_cases(+expert_cases 合并,expert_name 区分)、surgery_clinical_tips→kb_tips、surgery_expert_experiences→kb_tips(category 名家经验)
   - 从 PG:anorectal_formulas(JSONB composition→标准 composition)、anorectal_herbs、anorectal_cases(+medical_cases)、syndrome_rules→kb_syndromes(读表结构后适配)、safety_rules/prevention_guides→kb_tips、disease_types JSONB 提取去重→kb_diseases
   - 从 JSON:kb-data/pediatrics.json、kb-data/alchemy.json 直接导入
   - 从 surgery_formulas.composition 提取去重中药名→kb_herbs(module=surgery, source=方剂组成提取)
   - 输出每类对账
4. main.py 挂载 kb 路由;models 注册进 metadata(create_all 自动建表)

## 前端规格(platform/web)
1. 路由 /kb:知识总库(独立于 4 模块,Layout 可复用或轻量顶栏):
   - /kb(首页:8 类内容计数卡片 + 搜索框)
   - /kb/formulas /kb/herbs /kb/diseases /kb/syndromes /kb/cases /kb/tips /kb/terms /kb/dulong(列表页:搜索+专科筛选+分页)
   - /kb/{type}/:id 详情页(展示 extra 字段;composition 表格)
2. 门户首页"知识总库"入口卡片(第 5 张);导航加"知识总库"。
3. 各模块知识页加"在知识总库中检索"链接(小改动,可放在列表页顶部)。
4. 统一搜索框放知识总库首页与门户顶部(搜索跳 /kb/search?q=...)。
5. `npm run build` 必须通过。

## 验收
- migrate_kb.py 在服务器执行后 /kb/stats 计数与盘点表一致(方剂 508+75+45+34=662、中药 72+提取数、病 107+提取、证 13+38+8、案 40+40+14+7+32、诀 59+67+6+159、术语 48、引药 245)
- 前端 build 通过;搜索跨专科命中;上线后旧模块功能不回退
