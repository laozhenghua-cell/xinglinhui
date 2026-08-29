# 痔漏辅助诊疗系统 - 前端

肛肠科智能临床管理平台前端应用

## 技术栈

- **框架**: Vue 3 + Vite
- **UI组件**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **图表**: ECharts
- **工具库**: @vueuse/core

## 核心功能

### 1. 患者管理
- 患者信息录入与管理
- 患者档案查询
- 就诊历史追踪
- 随访记录管理

### 2. 智能诊断
- **AI图像诊断** - 核心功能
  - 支持摄像头拍照和相册上传
  - 多种图像类型识别（舌象、痔疮、肛裂、脓肿、肛瘘等）
  - AI视觉分析与辨证论治
  - 结构化诊断报告
  - 危险信号预警
- 四诊合参
- 症状辨证

### 3. 就诊管理
- 新建就诊记录
- 病种与证型选择
- AI辨证论治
- 处方自动生成
- 影像资料管理

### 4. 知识库
- 中药数据库（功效、归经、禁忌）
- 方剂查询（组成、主治、用法）
- 临床医案
- 预防保健指南

### 5. 收费管理
- 收费项目配置
- 开单收费
- 多种支付方式
- 收入统计与报表

### 6. 库存管理
- 药品信息管理
- 入库/出库操作
- 批次与有效期追踪
- 库存预警（低库存、即将过期、已过期）

## 开发

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

后端API需在 http://localhost:8000 运行

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## Docker部署

### 构建镜像

```bash
docker build -t zhilou-frontend .
```

### 运行容器

```bash
docker run -p 80:80 zhilou-frontend
```

## 项目结构

```
frontend/
├── public/              # 静态资源
│   └── favicon.svg
├── src/
│   ├── api/            # API接口封装
│   │   ├── index.js    # Axios实例与拦截器
│   │   ├── auth.js     # 认证接口
│   │   ├── patients.js
│   │   ├── consultations.js
│   │   ├── vision.js   # AI图像诊断
│   │   ├── knowledge.js
│   │   ├── billing.js
│   │   └── inventory.js
│   ├── components/     # 可复用组件
│   │   └── ImageUploader.vue  # 图像上传/拍照组件
│   ├── data/          # 静态数据
│   │   └── anorectal-syndromes.js  # 病种与证型数据
│   ├── router/        # 路由配置
│   ├── stores/        # Pinia状态管理
│   │   └── auth.js
│   ├── views/         # 页面组件
│   │   ├── Layout.vue
│   │   ├── Login.vue
│   │   ├── Dashboard.vue
│   │   ├── Patients.vue
│   │   ├── PatientDetail.vue
│   │   ├── ConsultationNew.vue
│   │   ├── Knowledge.vue
│   │   ├── Settings.vue
│   │   ├── diagnosis/
│   │   │   └── ImageDiagnosis.vue  # AI图像诊断页面
│   │   ├── billing/
│   │   │   └── BillingMain.vue
│   │   └── inventory/
│   │       └── InventoryMain.vue
│   ├── App.vue
│   ├── main.js
│   └── style.css      # 全局样式
├── index.html
├── vite.config.js
├── package.json
├── Dockerfile
└── nginx.conf
```

## API对接

前端通过 `/api/v1` 前缀访问后端API，开发环境由Vite代理，生产环境由Nginx代理。

主要API端点：
- `/api/v1/auth/*` - 认证
- `/api/v1/patients/*` - 患者管理
- `/api/v1/consultations/*` - 就诊记录
- `/api/v1/vision/analyze-image` - AI图像诊断
- `/api/v1/knowledge/*` - 知识库
- `/api/v1/billing/*` - 收费管理
- `/api/v1/inventory/*` - 库存管理

## 响应式设计

系统支持桌面和移动设备访问：
- 桌面：完整功能，侧边栏导航
- 移动：自适应布局，可折叠侧边栏，触摸优化

## 浏览器支持

- Chrome/Edge (推荐)
- Firefox
- Safari
- 移动浏览器（支持摄像头访问）

## 注意事项

1. **摄像头权限**：AI图像诊断需要浏览器摄像头权限，HTTPS环境下效果最佳
2. **网络要求**：AI分析需要稳定的后端连接
3. **图片大小**：上传图片限制10MB以内

## License

MIT
