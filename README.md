# 杏林汇 · 中医专科辅助诊疗系统

汇聚肛肠痔漏、外科疮疡、儿科、丹药研究四大中医专科的**智能诊疗平台**(线上 https://tcm.llixz.cn):

- **知识总库**:方剂 670 / 中药 1960 / 病种 115 / 证型 59 / 医案 133 / 要诀 310 / 术语 48 / 引药 245(全部可原文溯源);
- **统一辨证中心**:四科原版辨证引擎(儿科程氏八症/疮疡消托补分期/痔漏结构化置信度/丹药红旗问诊)+ DeepSeek/Qwen AI + 拍照辨病;
- **门诊工作流**:四诊录入 → AI 辨证 → 处方 → 处方 PDF → 随访提醒 → 数据导出;
- **学苑**:学习路径/自测/AI 助教;全开放免登录、设备级隐私;
- **工程底座**:AI 模型网关(成本计量/熔断)、可观测性(/metrics)、混合语义检索(向量重排)、CI/CD。

## 目录
- `platform/backend`:FastAPI + PostgreSQL + Redis(SQLAlchemy 2.0 async)
- `platform/web`:Vue3 + Element Plus(Vite)
- `deploy/`:部署脚本与 nginx 配置
- `docs/`:建设方案(世界级路线图 P1-P4)、架构模块化方案
- `kb-data/`:儿科/丹药知识提取数据
- `server-src/`:四个原版系统的源码快照(参考)

## 本地运行
```bash
# 后端
cd platform/backend && pip install -r requirements.txt
cp .env.example .env   # 配置数据库与 AI 密钥
uvicorn app.main:app --port 8000
# 前端
cd platform/web && npm install && npm run dev
```

> 全开放平台,内容仅供临床参考与教学研究;丹药等毒性药品严禁自行配制服用。
