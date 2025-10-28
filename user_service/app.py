# Enable config loading from .env files
from dotenv import load_dotenv
load_dotenv('.env.development')  # Load environment variables
# user_service/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import os
from datetime import datetime
import traceback
import sys
from config import get_config  # .env config loader

app = Flask(__name__)

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(get_config(env))
get_config(env).init_app(app)

# Setup CORS with configured origins
CORS(app, origins=app.config['CORS_ORIGINS'])

# Database setup
DATABASE = os.environ.get('DATABASE', 'users.db')

# Ensure the database file exists
def ensure_data_directory():
    db_dir = os.path.dirname(DATABASE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

# def get_db():
#     """Get database connection using config"""
#     conn = sqlite3.connect(app.config['DATABASE_PATH'])
#     conn.row_factory = sqlite3.Row
#     return conn

def get_db_connection():
    """Get database connection using config"""
    try:
        conn = sqlite3.connect(app.config['DATABASE_PATH'])
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"ERROR connecting to database: {e}", file=sys.stderr)
        raise

def init_db():
    """Initialize the database with user table"""
    print("Initializing database...", file=sys.stderr)
    ensure_data_directory()
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP,
            last_login TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully!", file=sys.stderr)

def hash_password(password):
    """Simple password hashing (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

# Routes
@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for Kubernetes probes.
    Returns 200 if service is healthy.
    """
    try:
        # Test database connection
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'service': 'user-service',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'user-service',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503  # 503 = Service Unavailable

@app.route('/api/users/register', methods=['POST', 'OPTIONS'])
def register_user():
    """Register a new user"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
    
    print("=== REGISTER REQUEST ===", file=sys.stderr)
    print(f"Content-Type: {request.content_type}", file=sys.stderr)
    print(f"Raw data: {request.data}", file=sys.stderr)

    try:
        data = request.get_json()
        print(f"Parsed JSON: {data}", file=sys.stderr)

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
        
        print(f"Username: {username}, Email: {email}", file=sys.stderr)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Hash password
        password_hash = hash_password(password)
        
        # Explicitly set created_at to avoid SQLite DEFAULT issues
        created_at = datetime.now().isoformat()
        
        # Insert new user
        cursor.execute(
            'INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
            (username, email, password_hash, created_at)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        print(f"User created successfully: ID={user_id}", file=sys.stderr)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user_id,
                'username': username,
                'email': email
            }
        }), 201
        
    except sqlite3.IntegrityError as e:
        print(f"IntegrityError: {str(e)}", file=sys.stderr)
        return jsonify({'error': 'Username or email already exists'}), 409
        
    except Exception as e:
        print(f"EXCEPTION: {str(e)}", file=sys.stderr)
        print(f"Exception type: {type(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/users/login', methods=['POST', 'OPTIONS'])
def login_user():
    """Authenticate a user"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
    
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
        last_login = datetime.now().isoformat()
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
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/users/profile/<int:user_id>', methods=['GET'])
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
        print(f"Profile error: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
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
        print(f"List users error: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_db()
    print(f"🚀 User Service starting in {env} mode")
    print(f"📊 Database: {app.config['DATABASE_PATH']}")
    print(f"🔧 Debug: {app.config['DEBUG']}")
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )