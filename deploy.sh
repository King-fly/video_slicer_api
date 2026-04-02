#!/bin/bash
set -e

NAMESPACE="video-slicer"
IMAGE_NAME="video-slicer"
REGISTRY="${DOCKER_REGISTRY:-localhost:5000}"

echo "========================================"
echo "Video Slicer 部署脚本"
echo "========================================"

# 检查必要的工具
command -v kubectl >/dev/null 2>&1 || { echo "kubectl 未安装"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "docker 未安装"; exit 1; }

# 1. 构建镜像
echo "[1/6] 构建 Docker 镜像..."
docker build -t ${IMAGE_NAME}:latest .
docker tag ${IMAGE_NAME}:latest ${REGISTRY}/${IMAGE_NAME}:latest

# 2. 推送镜像 (可选)
if [ "$PUSH_IMAGE" = "true" ]; then
    echo "[2/6] 推送镜像到仓库..."
    docker push ${REGISTRY}/${IMAGE_NAME}:latest
fi

# 3. 创建命名空间
echo "[3/6] 创建 Kubernetes 命名空间..."
kubectl apply -f k8s/00-namespace.yaml

# 4. 部署配置
echo "[4/6] 部署配置 (Secret & ConfigMap)..."
kubectl apply -f k8s/01-secret.yaml
kubectl apply -f k8s/02-configmap.yaml
kubectl apply -f k8s/05-pvc.yaml

# 5. 部署服务
echo "[5/6] 部署服务..."
kubectl apply -f k8s/10-redis.yaml
kubectl apply -f k8s/20-api.yaml
kubectl apply -f k8s/30-celery.yaml
kubectl apply -f k8s/40-ingress.yaml

# 6. 等待部署完成
echo "[6/6] 等待服务启动..."
echo "等待 Redis..."
kubectl wait --for=condition=ready pod -l app=redis -n ${NAMESPACE} --timeout=120s || true

echo "等待 API 服务..."
kubectl wait --for=condition=available deployment/video-slicer-api -n ${NAMESPACE} --timeout=180s || true

echo "等待 Celery Worker..."
kubectl wait --for=condition=available deployment/video-slicer-celery-worker -n ${NAMESPACE} --timeout=180s || true

# 显示状态
echo ""
echo "========================================"
echo "部署完成！"
echo "========================================"
echo ""
echo "检查服务状态:"
kubectl get pods -n ${NAMESPACE}
echo ""
echo "服务访问:"
echo "  API: http://video-slicer.example.com"
echo "  (需要配置 DNS 或使用 port-forward)"
echo ""
echo "Port Forward 方式访问:"
echo "  kubectl port-forward -n ${NAMESPACE} svc/video-slicer-api 8000:80"