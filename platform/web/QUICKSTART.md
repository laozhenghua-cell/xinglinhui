# 快速开始

## 前置要求

- Node.js 18+
- npm 或 yarn

## 安装步骤

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

浏览器访问: http://localhost:3000

**注意**: 后端服务需要在 http://localhost:8000 运行

### 3. 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录

## 测试账号

如果后端已配置演示账号:
- 邮箱: `demo@tcm.com`
- 密码: `demo123456`

或注册新账号使用。

## 主要功能入口

登录后可访问:

1. **工作台** (`/dashboard`) - 数据概览与快捷操作
2. **患者管理** (`/patients`) - 患者档案管理
3. **智能诊断** (`/diagnosis`) - AI图像诊断（核心功能）
4. **新建就诊** (`/consultations/new`) - 创建就诊记录
5. **知识库** (`/knowledge`) - 中医药知识查询
6. **收费管理** (`/billing`) - 开单收费
7. **库存管理** (`/inventory`) - 药品库存

## AI图像诊断使用流程

1. 进入 **智能诊断** 页面
2. 点击上传区域，选择"拍照"或"从相册选择"
3. 如使用拍照，允许浏览器访问摄像头
4. 选择图像类型（舌象/痔疮/肛裂/肛瘘等）
5. 可选填写伴随症状
6. 点击"开始AI分析"
7. 查看AI诊断结果（疾病判断、证型、治疗方案、危险信号）
8. 可将结果保存到患者就诊记录

## 故障排查

### 无法连接后端

检查:
- 后端服务是否在 `http://localhost:8000` 运行
- 浏览器控制台是否有CORS错误
- `vite.config.js` 中的 proxy 配置是否正确

### 摄像头无法访问

确保:
- 使用HTTPS或localhost
- 浏览器允许摄像头权限
- 设备有可用摄像头

### 构建失败

尝试:
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Docker部署

```bash
# 构建镜像
docker build -t zhilou-frontend .

# 运行容器
docker run -d -p 80:80 --name zhilou-frontend zhilou-frontend
```

访问 http://localhost

## 开发建议

1. 使用Chrome DevTools进行调试
2. 安装Vue DevTools浏览器插件
3. 检查Network面板查看API请求
4. 使用响应式设计模式测试移动端

## 技术支持

遇到问题请检查:
1. README.md 中的详细文档
2. 浏览器控制台错误信息
3. 网络请求响应状态码
4. 后端API日志
