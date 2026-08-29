#!/bin/bash

# 生产环境启动脚本
set -e

echo "=========================================="
echo "🚀 启动中医疮疡远程协作平台（生产环境）"
echo "=========================================="

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker未安装"
    exit 1
fi

# 检查配置文件
if [ ! -f docker-compose.prod.yml ]; then
    echo "❌ 错误: docker-compose.prod.yml 不存在"
    exit 1
fi

# 生成种子数据（如果不存在）
if [ ! -f backend/data/seed_data/ulcer_knowledge.json ]; then
    echo "📊 生成疮疡知识库种子数据..."
    cd backend
    python3 scripts/generate_seed_data.py
    cd ..
fi

# 启动服务
echo ""
echo "🔨 构建并启动所有容器..."
docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo "⏳ 等待服务启动（15秒）..."
sleep 15

# 导入知识库
echo ""
echo "📚 导入疮疡知识库..."
docker exec ulcer_backend_prod python scripts/seed_knowledge.py

# 显示容器状态
echo ""
echo "=========================================="
echo "📋 容器状态："
echo "=========================================="
docker compose -f docker-compose.prod.yml ps

# 检查健康状态
echo ""
echo "🏥 健康检查..."
sleep 5
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health || echo "000")

if [ "$HEALTH_STATUS" = "200" ]; then
    echo "✅ 后端服务健康"
else
    echo "⚠️  后端服务可能未就绪（状态码: $HEALTH_STATUS）"
fi

echo ""
echo "=========================================="
echo "🎉 启动完成！"
echo "=========================================="
echo ""
echo "📍 本地访问: http://localhost"
echo "📚 API文档:  http://localhost/api/docs"
echo ""
echo "🔍 查看日志:"
echo "   docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 停止服务:"
echo "   docker compose -f docker-compose.prod.yml down"
echo ""
echo "=========================================="
