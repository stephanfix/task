# ============================================
# run_prod.sh - Run in production mode
#!/bin/bash

echo "🚀 Starting Task Manager in PRODUCTION mode"
echo "============================================="

# Set environment
export FLASK_ENV=production

# Check for production secrets
if [ -z "$SECRET_KEY" ]; then
    echo "❌ ERROR: SECRET_KEY not set!"
    echo "Set it with: export SECRET_KEY=your-secret-key"
    exit 1
fi

# Start services (same as above but with production env)
# ... (similar to dev script)


# ============================================
# stop_all.sh - Stop all services
#!/bin/bash

echo "🛑 Stopping all Task Manager services..."

# Kill processes on specific ports
lsof -ti:5001 | xargs kill -9 2>/dev/null
lsof -ti:5002 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "✅ All services stopped!"


# ============================================
# Make scripts executable:
# chmod +x run_dev.sh run_prod.sh stop_all.sh