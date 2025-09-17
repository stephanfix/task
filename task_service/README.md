# Task Service

A Flask-based microservice for task management that communicates with the User Service.

## Features

- Full CRUD operations for tasks
- Task filtering by status and priority
- Task statistics and analytics
- User validation through User Service
- Health checks with dependency status
- SQLite database with proper indexing

## Setup

1. **Make sure User Service is running first** (on port 5001)

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the service:
```bash
python app.py
```

The service will start on port 5002 by default.

## API Endpoints

- `GET /health` - Health check with dependency status
- `GET /api/tasks?user_id=<id>` - Get tasks for user (with optional filters)
- `POST /api/tasks` - Create new task
- `GET /api/tasks/<task_id>` - Get specific task
- `PUT /api/tasks/<task_id>` - Update task
- `DELETE /api/tasks/<task_id>` - Delete task
- `GET /api/tasks/stats/<user_id>` - Get task statistics for user

## Task Properties

- `title` (required) - Task title
- `description` - Task description
- `status` - One of: pending, in_progress, completed, cancelled
- `priority` - One of: low, medium, high, urgent
- `due_date` - ISO format datetime string
- `user_id` (required) - ID of the user who owns the task

## Testing

Run the test script to verify the service:
```bash
python test_service.py
```

This will create a test user and perform various task operations.

## Microservice Communication

The Task Service communicates with the User Service to:
- Verify users exist before creating tasks
- Check User Service health status

## Environment Variables

- `PORT` - Service port (default: 5002)
- `DEBUG` - Enable debug mode (default: True)
- `USER_SERVICE_URL` - URL of User Service (default: http://localhost:5001)

## Next Steps

- Add JWT token validation
- Implement task categories
- Add task search functionality
- Add file attachments
- Implement task sharing between users