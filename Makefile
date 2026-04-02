.PHONY: help build up down restart logs ps clean deploy k8s-apply k8s-delete

help:
	@echo "Video Slicer - 可用命令"
	@echo "======================"
	@echo "make build         - 构建 Docker 镜像"
	@echo "make up           - 启动所有服务 (docker-compose)"
	@echo "make down         - 停止所有服务"
	@echo "make restart      - 重启所有服务"
	@echo "make logs         - 查看日志"
	@echo "make ps           - 查看容器状态"
	@echo "make clean        - 清理容器和数据"
	@echo "make deploy       - 部署到 Kubernetes"
	@echo "make k8s-delete   - 删除 Kubernetes 部署"

# Docker Compose 命令
build:
	docker build -t video-slicer:latest .

up:
	docker-compose up -d
	@echo "等待服务启动..."
	@sleep 10
	@docker-compose ps

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-worker:
	docker-compose logs -f celery-worker

ps:
	docker-compose ps

clean:
	docker-compose down -v
	rm -rf uploads/* uploads/.* 2>/dev/null || true

# Kubernetes 部署
k8s-apply:
	./deploy.sh

k8s-delete:
	kubectl delete namespace video-slicer

k8s-status:
	kubectl get all -n video-slicer

k8s-logs-api:
	kubectl logs -n video-slicer -l app=video-slicer-api -f

k8s-logs-worker:
	kubectl logs -n video-slicer -l app=video-slicer-celery-worker -f

k8s-scale-api:
	kubectl scale deployment video-slicer-api -n video-slicer --replicas=3

k8s-scale-worker:
	kubectl scale deployment video-slicer-celery-worker -n video-slicer --replicas=4