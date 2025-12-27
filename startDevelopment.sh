#!/bin/bash
# run_dev.sh - Run in development mode

echo "🚀 Starting Task Manager in DEVELOPMENT mode"
echo "=============================================="

# Set environment
export FLASK_ENV=development

# Start user service
echo "📦 Starting User Service on port 5001..."
cd user_service
python app.py &
USER_PID=$!
cd ..

# Wait a bit for user service to start
sleep 2

# Start task service
echo "📦 Starting Task Service on port 5002..."
cd task_service
python app.py &
TASK_PID=$!
cd ..

# Wait a bit for services to start
sleep 2

# Start frontend
echo "🎨 Starting Frontend on port 3000..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ All services started!"
echo "   User Service: http://localhost:5001"
echo "   Task Service: http://localhost:5002"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "echo 'Stopping services...'; kill $USER_PID $TASK_PID $FRONTEND_PID; exit" INT
wait