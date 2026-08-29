# 痔漏辅助诊疗系统 - Backend

基于 FastAPI 的肛肠科中西医结合诊疗管理系统后端服务。

## 技术栈

- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL (AsyncPG + SQLAlchemy 2.0)
- **缓存**: Redis
- **AI服务**: 
  - DeepSeek API (文本辨证论治)
  - Qwen-VL-Max (多模态图像分析)
- **认证**: JWT (python-jose)
- **文件上传**: aiofiles
- **PDF生成**: reportlab

## 功能模块

### 核心功能
- ✅ 多租户架构 (tenant_id)
- ✅ 用户认证与权限管理 (JWT)
- ✅ 患者管理 (Patient CRUD)
- ✅ 诊疗记录 (Consultation + AI辨证)
- ✅ 处方管理 (Prescription)
- ✅ 随访管理 (Followup scheduling)

### AI诊断
- ✅ **图像分析**: Qwen-VL-Max 多模态分析肛肠病变图片
  - 支持: 痔疮、肛裂、肛瘘、肛周脓肿、直肠脱垂、肛周湿疹、尖锐湿疣、舌象
  - 返回: 疾病判断、分型分级、中医辨证、治疗方案、方药建议
- ✅ **辨证论治**: DeepSeek 文本辨证分析
  - 八纲辨证、脏腑辨证、气血津液辨证
  - 生成: 诊断、证型、治则、方药、外治法、针灸、调护

### 业务管理
- ✅ **收费管理**: 收费项目、账单、收款、日营收统计
- ✅ **库存管理**: 药品、批次、入库/出库、库存预警
- ✅ **知识库**: 肛肠中药、方剂、病例、预防指南

### 统计分析
- ✅ 概览统计 (患者、诊疗、收入、库存告警)
- ✅ 趋势分析 (日诊疗量、日营收)
- ✅ 疾病分型分布

## 快速开始

### 1. 安装依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入数据库连接、AI API Key 等
```

必填配置:
- `DATABASE_URL`: PostgreSQL 连接字符串
- `SECRET_KEY`: JWT 密钥 (生产环境必须修改)
- `DEEPSEEK_API_KEY`: DeepSeek API 密钥
- `QWEN_API_KEY`: 通义千问 API 密钥

### 3. 初始化数据库

```bash
# 确保 PostgreSQL 已启动并创建数据库
createdb zhilou_db

# 运行应用会自动创建表
uvicorn app.main:app --reload
```

### 4. 运行开发服务器

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问:
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 5. 初始化测试数据 (可选)

```bash
# 初始化收费项目
python scripts/seed_charge_items.py

# 初始化知识库 (中药、方剂)
python scripts/seed_knowledge.py

# 创建演示账户
python scripts/init_demo.py
```

## API 端点

### 认证 `/api/v1/auth`
- `POST /login` - 登录
- `POST /register` - 注册 (自动创建租户)
- `GET /me` - 获取当前用户信息

### 患者 `/api/v1/patients`
- `GET /` - 患者列表
- `POST /` - 创建患者
- `GET /{id}` - 患者详情
- `PUT /{id}` - 更新患者

### 诊疗 `/api/v1/consultations`
- `GET /` - 诊疗记录列表
- `POST /` - 创建诊疗记录
- `GET /{id}` - 诊疗详情
- `POST /{id}/ai-diagnosis` - 触发AI辨证诊断

### 图像分析 `/api/v1/vision`
- `POST /analyze-image` - 上传并分析临床图片
- `GET /history/{patient_id}` - 患者图像历史
- `POST /compare` - 对比前后图片

### 收费 `/api/v1/billing`
- `/charge-items` - 收费项目管理
- `/bills` - 账单管理
- `/payments` - 收款记录
- `/revenue` - 营收统计

### 库存 `/api/v1/inventory`
- `/medicines` - 药品管理
- `/stock-in` - 入库
- `/stock-out` - 出库
- `/alerts` - 库存告警
- `/stats` - 库存统计

### 知识库 `/api/v1/knowledge`
- `/herbs` - 中药库
- `/formulas` - 方剂库
- `/cases` - 病例库
- `/prevention` - 预防指南

### 统计 `/api/v1/stats`
- `/overview` - 概览统计
- `/trends` - 趋势分析

### 随访 `/api/v1/followup`
- `GET /` - 随访列表
- `POST /` - 创建随访
- `GET /today` - 今日随访
- `POST /{id}/complete` - 完成随访

## Docker 部署

```bash
# 构建镜像
docker build -t zhilou-backend .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db \
  -e DEEPSEEK_API_KEY=your-key \
  -e QWEN_API_KEY=your-key \
  --name zhilou-backend \
  zhilou-backend
```

## 数据库模型

### 核心表
- `tenants` - 租户/诊所
- `users` - 用户 (医生、收银员等)
- `patients` - 患者
- `consultations` - 诊疗记录
- `prescriptions` - 处方
- `followups` - 随访计划

### 业务表
- `bills`, `bill_items`, `bill_payments` - 收费
- `medicines`, `medicine_batches`, `stock_transactions` - 库存
- `images` - 临床图片及AI分析结果

### 知识库表
- `anorectal_herbs` - 肛肠中药
- `anorectal_formulas` - 肛肠方剂
- `anorectal_cases` - 病例
- `prevention_guides` - 预防指南

## 开发说明

### 添加新的 API 路由

1. 在 `app/api/v1/` 创建路由文件
2. 在 `app/main.py` 中 import 并 include_router
3. 如需数据模型，在 `app/models/` 添加
4. 如需请求/响应 schema，在 `app/schemas/` 添加

### AI 服务扩展

- **视觉分析**: 修改 `app/services/vision_ai.py` 中的 prompt
- **文本辨证**: 修改 `app/services/deepseek_service.py` 中的 prompt

### 数据库迁移

使用 Alembic 管理数据库变更:

```bash
# 生成迁移
alembic revision --autogenerate -m "describe changes"

# 执行迁移
alembic upgrade head
```

## 许可证

内部项目 - 版权所有
