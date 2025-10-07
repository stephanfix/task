#!/bin/bash

echo "========================================="
echo "Quick Deploy to Kubernetes"
echo "========================================="

# Check Minikube is running
if ! minikube status > /dev/null 2>&1; then
    echo "✗ Minikube is not running!"
    echo "Start with: minikube start --mount --mount-string=\"/Users/stephanfix/workspace/task/data:/host-data\""
    exit 1
fi

echo "✓ Minikube is running"

# Point to Minikube Docker
eval $(minikube docker-env)
echo "✓ Docker environment configured"

# Build images
echo ""
echo "Building images..."

echo "  - user-service"
cd user_service
docker build -t user-service:latest . > /dev/null
cd ..

echo "  - task-service"
cd task_service
docker build -t task-service:latest . > /dev/null
cd ..

echo "  - frontend"
cd frontend
docker build -t frontend:latest . > /dev/null
cd ..

echo "✓ Images built"

# Deploy to Kubernetes
echo ""
echo "Deploying to Kubernetes..."

kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/persistent-volumes.yaml
kubectl apply -f kubernetes/user-service/
kubectl apply -f kubernetes/task-service/
kubectl apply -f kubernetes/frontend/

echo "✓ Resources deployed"

# Wait for rollout
echo ""
echo "Waiting for deployments..."
kubectl wait --for=condition=available --timeout=120s deployment/user-service -n task-manager 2>/dev/null
kubectl wait --for=condition=available --timeout=120s deployment/task-service -n task-manager 2>/dev/null
kubectl wait --for=condition=available --timeout=120s deployment/frontend -n task-manager 2>/dev/null

echo ""
echo "========================================="
echo "Deployment Status"
echo "========================================="
kubectl get pods -n task-manager
echo ""
kubectl get pvc -n task-manager
echo ""
kubectl get svc -n task-manager

echo ""
echo "========================================="
echo "Access Application"
echo "========================================="
echo "Run: minikube service frontend -n task-manager"