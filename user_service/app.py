# user_service/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import uuid
import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Database setup
DATABASE = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with user table"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Simple password hashing (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

# Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'user-service',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/api/users/register', methods=['POST'])
def register_user():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ('username', 'email', 'password')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Basic validation
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        if '@' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        conn = get_db_connection()
        
        # Check if user already exists
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({'error': 'Username or email already exists'}), 409
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        created_at = datetime.datetime.now().isoformat()
        
        conn.execute(
            'INSERT INTO users (id, username, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)',
            (user_id, username, email, password_hash, created_at)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user_id,
                'username': username,
                'email': email,
                'created_at': created_at
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/users/login', methods=['POST'])
def login_user():
    """Authenticate a user"""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ('username', 'password')):
            return jsonify({'error': 'Username and password required'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? OR email = ?',
            (username, username)
        ).fetchone()
        
        if not user or not verify_password(password, user['password_hash']):
            conn.close()
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Update last login
        last_login = datetime.datetime.now().isoformat()
        conn.execute(
            'UPDATE users SET last_login = ? WHERE id = ?',
            (last_login, user['id'])
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'last_login': last_login
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/users/profile/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Get user profile by ID"""
    try:
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, username, email, created_at, last_login FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at'],
                'last_login': user['last_login']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/users', methods=['GET'])
def list_users():
    """List all users (for development/admin purposes)"""
    try:
        conn = get_db_connection()
        users = conn.execute(
            'SELECT id, username, email, created_at, last_login FROM users ORDER BY created_at DESC'
        ).fetchall()
        conn.close()
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at'],
                'last_login': user['last_login']
            })
        
        return jsonify({'users': user_list}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Run the service
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"Starting User Service on port {port}")
    print(f"Health check: http://localhost:{port}/health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)