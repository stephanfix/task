#!/bin/bash

echo "========================================="
echo "Task Manager - Restart Helper"
echo "========================================="

DATA_DIR="/Users/stephanfix/workspace/task/data"

# Check what needs to be done
echo ""
echo "Select restart scenario:"
echo "1. Quick restart (Minikube running, just restart pods)"
echo "2. Minikube restart (restart Minikube with mount)"
echo "3. Code changed (rebuild images and restart)"
echo "4. Full redeploy (delete and recreate everything)"
echo "5. Status check only"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "=== Quick Restart ==="
        kubectl rollout restart deployment/user-service -n task-manager
        kubectl rollout restart deployment/task-service -n task-manager
        kubectl rollout restart deployment/frontend -n task-manager
        kubectl get pods -n task-manager -w
        ;;
    
    2)
        echo ""
        echo "=== Restarting Minikube ==="
        minikube stop
        minikube start --mount --mount-string="$DATA_DIR:/host-data"
        
        echo "Verifying mount..."
        if minikube ssh "ls /host-data/user_service && ls /host-data/task_service" > /dev/null 2>&1; then
            echo "✓ Mount verified"
        else
            echo "✗ Mount failed!"
            exit 1
        fi
        
        echo "Checking pods..."
        kubectl get pods -n task-manager
        ;;
    
    3)
        echo ""
        echo "=== Rebuilding Images ==="
        
        # Point to Minikube Docker
        eval $(minikube docker-env)
        
        echo "Building user-service..."
        cd user_service
        docker build -t user-service:latest .
        
        echo "Building task-service..."
        cd ../task_service
        docker build -t task-service:latest .
        
        echo "Building frontend..."
        cd ../frontend
        docker build -t frontend:latest .
        
        cd ..
        
        echo "Restarting deployments..."
        kubectl rollout restart deployment/user-service -n task-manager
        kubectl rollout restart deployment/task-service -n task-manager
        kubectl rollout restart deployment/frontend -n task-manager
        
        echo "Waiting for rollout..."
        kubectl rollout status deployment/user-service -n task-manager
        kubectl rollout status deployment/task-service -n task-manager
        kubectl rollout status deployment/frontend -n task-manager
        
        kubectl get pods -n task-manager
        ;;
    
    4)
        echo ""
        echo "=== Full Redeploy ==="
        read -p "⚠️  This will delete everything in Minikube. Continue? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Cancelled."
            exit 0
        fi
        
        echo "Deleting Minikube..."
        minikube delete
        
        echo "Starting Minikube..."
        minikube start --mount --mount-string="$DATA_DIR:/host-data"
        
        echo "Configuring Docker..."
        eval $(minikube docker-env)
        
        echo "Building images..."
        cd user_service && docker build -t user-service:latest . && cd ..
        cd task_service && docker build -t task-service:latest . && cd ..
        cd frontend && docker build -t frontend:latest . && cd ..
        
        echo "Deploying to Kubernetes..."
        kubectl apply -f kubernetes/namespace.yaml
        kubectl apply -f kubernetes/persistent-volumes.yaml
        kubectl apply -f kubernetes/user-service/
        kubectl apply -f kubernetes/task-service/
        kubectl apply -f kubernetes/frontend/
        
        echo "Waiting for pods..."
        kubectl wait --for=condition=available --timeout=120s deployment --all -n task-manager
        
        kubectl get pods -n task-manager
        ;;
    
    5)
        echo ""
        echo "=== Status Check ==="
        
        echo ""
        echo "Docker:"
        docker ps > /dev/null 2>&1 && echo "✓ Docker is running" || echo "✗ Docker is NOT running"
        
        echo ""
        echo "Minikube:"
        minikube status
        
        echo ""
        echo "Mount verification:"
        if minikube ssh "ls /host-data" > /dev/null 2>&1; then
            echo "✓ Host mount is active"
            minikube ssh "ls -la /host-data"
        else
            echo "✗ Host mount is NOT active"
        fi
        
        echo ""
        echo "Pods:"
        kubectl get pods -n task-manager
        
        echo ""
        echo "Services:"
        kubectl get svc -n task-manager
        
        echo ""
        echo "PVCs:"
        kubectl get pvc -n task-manager
        
        echo ""
        echo "Database files:"
        ls -lh "$DATA_DIR/user_service/" 2>/dev/null || echo "No user service data"
        ls -lh "$DATA_DIR/task_service/" 2>/dev/null || echo "No task service data"
        ;;
    
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "Done!"
echo "========================================="
echo ""
echo "To access the application:"
echo "  minikube service frontend -n task-manager"
echo ""
echo "To view logs:"
echo "  kubectl logs -n task-manager -l app=user-service -f"
echo "  kubectl logs -n task-manager -l app=task-service -f"