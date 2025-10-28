from dotenv import load_dotenv
load_dotenv('.env.development')  # Load environment variables
# task_service/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import requests
import traceback
import sys
from config import get_config 

app = Flask(__name__)

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(get_config(env))
get_config(env).init_app(app)

# Setup CORS with configured origins
CORS(app, origins=app.config['CORS_ORIGINS'])

# Database configuration
DATABASE = os.getenv('DATABASE', '/app/data/tasks.db')

# USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:5001')
# Replaced with config value
USER_SERVICE_URL = app.config['USER_SERVICE_URL']

print(f"=== TASK SERVICE STARTING ===", file=sys.stderr)
print(f"DATABASE: {DATABASE}", file=sys.stderr)
print(f"USER_SERVICE_URL: {USER_SERVICE_URL}", file=sys.stderr)

def ensure_data_directory():
    """Ensure the data directory exists"""
    db_dir = os.path.dirname(DATABASE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"Created directory: {db_dir}", file=sys.stderr)

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
    """Initialize the database with required tables"""
    print("Initializing database...", file=sys.stderr)
    ensure_data_directory()
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                due_date TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!", file=sys.stderr)
        print(f"Database location: {DATABASE}", file=sys.stderr)
    except Exception as e:
        print(f"ERROR initializing database: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes probes"""
    try:
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()
        
        try:
            response = requests.get(f'{USER_SERVICE_URL}/health', timeout=2)
            user_service_healthy = response.status_code == 200
        except:
            user_service_healthy = False
        
        return jsonify({
            'status': 'healthy',
            'service': 'task-service',
            'dependencies': {
                'user-service': 'healthy' if user_service_healthy else 'unhealthy'
            },
            'timestamp': datetime.now().isoformat()
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'task-service',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/api/tasks', methods=['GET', 'POST', 'OPTIONS'])
def tasks():
    """Get all tasks for a user or create a new task"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if request.method == 'GET':
        print("=== GET TASKS REQUEST ===", file=sys.stderr)
        try:
            user_id = request.args.get('user_id')
            print(f"User ID: {user_id}", file=sys.stderr)
            
            if not user_id:
                return jsonify({'error': 'user_id is required'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            tasks = cursor.fetchall()
            conn.close()
            
            print(f"Found {len(tasks)} tasks", file=sys.stderr)
            
            tasks_list = []
            for task in tasks:
                tasks_list.append({
                    'id': task['id'],
                    'user_id': task['user_id'],
                    'title': task['title'],
                    'description': task['description'],
                    'priority': task['priority'],
                    'status': task['status'],
                    'due_date': task['due_date'],
                    'created_at': task['created_at'],
                    'updated_at': task['updated_at']
                })
            
            return jsonify({'tasks': tasks_list}), 200
            
        except Exception as e:
            print(f"GET TASKS ERROR: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    
    elif request.method == 'POST':
        print("=== CREATE TASK REQUEST ===", file=sys.stderr)
        print(f"Content-Type: {request.content_type}", file=sys.stderr)
        print(f"Raw data: {request.data}", file=sys.stderr)
        
        try:
            data = request.get_json()
            print(f"Parsed JSON: {data}", file=sys.stderr)
            
            if not data:
                print("ERROR: No JSON data provided", file=sys.stderr)
                return jsonify({'error': 'No JSON data provided'}), 400
            
            user_id = data.get('user_id')
            title = data.get('title')
            description = data.get('description', '')
            priority = data.get('priority', 'medium')
            status = data.get('status', 'pending')
            due_date = data.get('due_date')
            
            print(f"Extracted - User ID: {user_id}, Title: {title}, Priority: {priority}, Status: {status}", file=sys.stderr)
            
            if not user_id:
                print("ERROR: user_id is missing", file=sys.stderr)
                return jsonify({'error': 'user_id is required'}), 400
            
            if not title:
                print("ERROR: title is missing", file=sys.stderr)
                return jsonify({'error': 'title is required'}), 400
            
            print("Opening database connection...", file=sys.stderr)
            conn = get_db_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            print(f"Timestamp: {now}", file=sys.stderr)
            
            print("Executing INSERT...", file=sys.stderr)
            cursor.execute('''
                INSERT INTO tasks (user_id, title, description, priority, status, due_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, title, description, priority, status, due_date, now, now))
            
            print("Committing...", file=sys.stderr)
            conn.commit()
            task_id = cursor.lastrowid
            conn.close()
            
            print(f"✓ Task created successfully: ID={task_id}", file=sys.stderr)
            
            return jsonify({
                'message': 'Task created successfully',
                'task': {
                    'id': task_id,
                    'user_id': user_id,
                    'title': title,
                    'description': description,
                    'priority': priority,
                    'status': status,
                    'due_date': due_date
                }
            }), 201
            
        except Exception as e:
            print(f"CREATE TASK ERROR: {str(e)}", file=sys.stderr)
            print(f"Exception type: {type(e).__name__}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def task_detail(task_id):
    """Get, update, or delete a specific task"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            task = cursor.fetchone()
            conn.close()
            
            if task:
                return jsonify({
                    'task': {
                        'id': task['id'],
                        'user_id': task['user_id'],
                        'title': task['title'],
                        'description': task['description'],
                        'priority': task['priority'],
                        'status': task['status'],
                        'due_date': task['due_date'],
                        'created_at': task['created_at'],
                        'updated_at': task['updated_at']
                    }
                }), 200
            else:
                return jsonify({'error': 'Task not found'}), 404
                
        except Exception as e:
            print(f"Get task error: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return jsonify({'error': 'Internal server error'}), 500
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            update_fields = []
            values = []
            
            if 'title' in data:
                update_fields.append('title = ?')
                values.append(data['title'])
            if 'description' in data:
                update_fields.append('description = ?')
                values.append(data['description'])
            if 'priority' in data:
                update_fields.append('priority = ?')
                values.append(data['priority'])
            if 'status' in data:
                update_fields.append('status = ?')
                values.append(data['status'])
            if 'due_date' in data:
                update_fields.append('due_date = ?')
                values.append(data['due_date'])
            
            update_fields.append('updated_at = ?')
            values.append(datetime.now().isoformat())
            
            values.append(task_id)
            
            query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount == 0:
                conn.close()
                return jsonify({'error': 'Task not found'}), 404
            
            conn.close()
            
            return jsonify({'message': 'Task updated successfully'}), 200
            
        except Exception as e:
            print(f"Update task error: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return jsonify({'error': 'Internal server error'}), 500
    
    elif request.method == 'DELETE':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                conn.close()
                return jsonify({'error': 'Task not found'}), 404
            
            conn.close()
            
            return jsonify({'message': 'Task deleted successfully'}), 200
            
        except Exception as e:
            print(f"Delete task error: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/tasks/stats/<int:user_id>', methods=['GET'])
def task_stats(user_id):
    """Get task statistics for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ?', (user_id,))
        total_tasks = cursor.fetchone()['count']
        
        cursor.execute('SELECT status, COUNT(*) as count FROM tasks WHERE user_id = ? GROUP BY status', (user_id,))
        status_counts = cursor.fetchall()
        
        by_status = {}
        for row in status_counts:
            by_status[row['status']] = row['count']
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM tasks 
            WHERE user_id = ? AND due_date < ? AND status != 'completed'
        ''', (user_id, datetime.now().isoformat()))
        overdue_tasks = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'total_tasks': total_tasks,
            'by_status': by_status,
            'overdue_tasks': overdue_tasks
        }), 200
        
    except Exception as e:
        print(f"Stats error: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return jsonify({'error': 'Internal server error'}), 500

# if __name__ == '__main__':
#     print(f"Starting task service...", file=sys.stderr)
#     print(f"Database path: {DATABASE}", file=sys.stderr)
#     print(f"User service URL: {USER_SERVICE_URL}", file=sys.stderr)
#     init_db()
#     app.run(host='0.0.0.0', port=5002, debug=True)

if __name__ == '__main__':
    init_db()
    print(f"🚀 Task Service starting in {env} mode")
    print(f"📊 Database: {app.config['DATABASE_PATH']}")
    print(f"🔧 Debug: {app.config['DEBUG']}")
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )