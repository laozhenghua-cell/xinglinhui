# 统一辨证中心 — 工程规格(DX v1)

## 目标
在知识总库(kb_* 8 表,3532 行)之上新增跨专科"统一辨证中心":输入症状/四诊 → 病种、证型、方剂、医案/要诀/引药 全链路推荐 + DeepSeek 综合报告 + 辨证记录回溯;四模块辨证页接入总库关联与 AI 增强;儿科静态辨证升级为交互式。

## 后端规格(platform/backend)
### 新增 app/models/dx.py
- DxRecord: id UUID, module(不限/anorectal/surgery/pediatrics/alchemy), input(JSONB), result(JSONB), ip_hash, ua_hash, created_at

### 新增 app/api/v1/dx.py(免鉴权,prefix /api/v1/dx)
1. POST /dx/analyze
   入参:{symptoms: list[str], tongue: str?, pulse: str?, local: str?, systemic: str?, detail: str?, module: str?(可选,默认不限), use_ai: bool=true}
   流程:
   a. KB 证型匹配:对 kb_syndromes 全表(或 module 过滤)打分——关键词在 name/aliases/summary/tongue_pulse/local_signs/systemic_signs/extra.required_symptoms 中命中计分(名称命中权重高,症状命中次之),取前 5,返回 hit 证据(命中的词)
   b. KB 病种匹配:kb_diseases 在 name/aliases/characteristics/differential/location 打分,取前 5
   c. 方剂推荐:对匹配到的证型/病种,在 kb_formulas 中按其 indication/function/name/extra(肛肠的 disease_types/syndrome_type)匹配,分组返回(每组带 module 标签、来源专科),每专科≤8
   d. 关联内容:kb_cases(disease/syndrome 名命中,≤5)、kb_tips(category 与病/证名模糊命中,≤5)、kb_dulong(disease 关键词命中,≤5)
   e. AI 综合(use_ai 且 settings.DEEPSEEK_API_KEY 非空):构造 prompt(包含上面匹配结果摘要 + 用户输入)调用 DeepSeek(复用 app/services/deepseek_service.py 或 surgery_ai 的配置,不要新写 key 读取),要求返回 JSON {syndrome_analysis, disease_suggestion, formula_suggestion, precautions, confidence};AI 失败时静默降级为规则结果
   f. 存 DxRecord(IP/UA 加盐哈希同 visits 模式)并返回 {record_id, syndromes:[], diseases:[], formulas:{module:[...]}, related:{cases,tips,dulong}, ai:{...}|null}
2. GET /dx/records?limit=20:按 ip_hash+ua_hash 过滤返回本设备最近记录(公开模式无账号,按设备回溯);GET /dx/records/{id} 详情
3. GET /dx/quick?q=:给前端"症状快速联想"(从 kb_syndromes.summary、kb_diseases.characteristics、symptom_dictionary 表抽词,简单 ILIKE 即可)

### main.py 挂载;models 注册;复用既有 get_db。

## 前端规格(platform/web)
1. src/api/dx.js 接口封装
2. src/views/dx/DxCenter.vue(路由 /dx):
   - 输入区:专科范围(el-select 不限/四专科)、症状多选(常用症状 chips,点选)+ 自定义输入、舌象/脉象/局部/全身(el-input)、自由描述(textarea)、AI 开关
   - 提交 → 结果区:证型排名(分数+命中证据)、病种排名、方剂推荐(按专科分组卡片,点击跳 /kb/formulas/:id)、医案/要诀/引药关联(跳 /kb 详情)、AI 报告卡片(可折叠)
   - 右侧/底部:"本设备近期辨证记录"列表(点开回显结果)
3. 路由 /dx 加入 router(mode='dx');门户 PortalHome 加"辨证中心"入口(第 6 张卡片或与知识总库并列);Layout 顶部菜单加"辨证中心"
4. 模块增强:
   - 儿科 Bianzheng.vue:顶部加"AI 智能辨证"按钮 → router.push('/dx?module=pediatrics')(用 query 预选专科)
   - 疮疡 DiagnosisView.vue 与肛肠 Diagnosis.vue:结果区加一行"在总库查看相关方剂/医案"链接 → /kb/search?q=<证型或病名>
   - 丹药 AssistHomeView/ProfessionalFlowView:结果方名加"总库详情"链接 → /kb/formulas?q=<方名>
5. npm run build 必须通过。

## 验收
- 后端 py_compile 通过;服务器部署后:POST /dx/analyze 用"咳嗽 发热 脉浮数"(module=pediatrics)与"肛周红肿热痛"(anorectal)各测一次,返回证型/方剂非空,AI 报告有内容或优雅降级
- 前端 build 通过;/dx 页面公网 200;儿科辨证页按钮跳转正确
