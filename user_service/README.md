# User Service

A simple Flask-based microservice for user management.

## Features

- User registration
- User authentication (login)
- User profile retrieval
- Health check endpoint
- SQLite database for data persistence

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the service:
```bash
python app.py
```

The service will start on port 5001 by default.

## API Endpoints

- `GET /health` - Health check
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `GET /api/users/profile/<user_id>` - Get user profile
- `GET /api/users` - List all users (dev/admin)

## Testing

Run the test script to verify the service:
```bash
python test_service.py
```

## Environment Variables

- `PORT` - Service port (default: 5001)
- `DEBUG` - Enable debug mode (default: True)

## Next Steps

- Add JWT token authentication
- Implement bcrypt for password hashing
- Add input validation and sanitization
- Add logging
- Add database migrations