import React, { useState, useEffect } from 'react';
import { User, CheckCircle, Clock, AlertCircle, Plus, Edit3, Trash2, LogOut, UserPlus, LogIn } from 'lucide-react';

// const API_BASE = {
//   users: 'http://localhost:5001/api',
//   tasks: 'http://localhost:5002/api'
// };

// Configuration management - read from environment variables
const API_BASE = {
  users: process.env.REACT_APP_USER_SERVICE_URL || 'http://localhost:6001/api',
  tasks: process.env.REACT_APP_TASK_SERVICE_URL || 'http://localhost:6002/api'
};

const APP_ENV = process.env.REACT_APP_ENVIRONMENT || 'development';

// Configuration display component for debugging
const ConfigInfo = ({ show }) => {
  if (!show) return null;
  
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
      <h3 className="font-semibold text-blue-900 mb-2">🔧 Configuration</h3>
      <div className="text-sm text-blue-800 space-y-1">
        <p><strong>Environment:</strong> {APP_ENV}</p>
        <p><strong>User Service:</strong> {API_BASE.users}</p>
        <p><strong>Task Service:</strong> {API_BASE.tasks}</p>
      </div>
    </div>
  );
};

const TaskManagementApp = () => {
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true); // Start with loading true
  const [error, setError] = useState('');
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [filter, setFilter] = useState('all');
  const [showConfig, setShowConfig] = useState(false);
  
  // Auth Forms State
  // Added Sept 27 when file replaced
  const [authForm, setAuthForm] = useState({
    username: '',
    email: '',
    password: '',
    isLogin: true
  });

  // Task Form State
  const [taskForm, setTaskForm] = useState({
    title: '',
    description: '',
    priority: 'medium',
    status: 'pending',
    due_date: ''
  });

  const [stats, setStats] = useState({
    total_tasks: 0,
    by_status: {},
    overdue_tasks: 0
  });

  // Authentication persistence functions
  const saveUserSession = (userData) => {
    localStorage.setItem('taskAppUser', JSON.stringify(userData));
    setUser(userData);
  };

  const loadUserSession = () => {
    try {
      const savedUser = localStorage.getItem('taskAppUser');
      if (savedUser) {
        const userData = JSON.parse(savedUser);
        // Verify the user still exists by making a quick API call
        verifyUserSession(userData);
      } else {
        setLoading(false);
      }
    } catch (error) {
      console.error('Error loading user session:', error);
      localStorage.removeItem('taskAppUser');
      setLoading(false);
    }
  };

  const verifyUserSession = async (userData) => {
    try {
      const response = await fetch(`${API_BASE.users}/users/profile/${userData.id}`);
      if (response.ok) {
        setUser(userData);
      } else {
        // User no longer exists, clear session
        localStorage.removeItem('taskAppUser');
      }
    } catch (error) {
      console.error('Error verifying user session:', error);
      // Keep user logged in even if verification fails (offline scenario)
      setUser(userData);
    } finally {
      setLoading(false);
    }
  };

  const clearUserSession = () => {
    localStorage.removeItem('taskAppUser');
    setUser(null);
    setTasks([]);
    setStats({ total_tasks: 0, by_status: {}, overdue_tasks: 0 });
  };

  // Load user session on app initialization
  useEffect(() => {
    loadUserSession();
  }, []);

  // Load tasks when user changes
  useEffect(() => {
    if (user) {
      loadTasks();
      loadStats();
    }
  }, [user]);
  // FIX 6: Note on potential race condition with loading state
  const showError = (message) => {
    setError(message);
    setTimeout(() => setError(''), 5000);
  };

  // Authentication Functions
  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const endpoint = authForm.isLogin ? '/users/login' : '/users/register';
      const payload = authForm.isLogin 
        ? { username: authForm.username, password: authForm.password }
        : { username: authForm.username, email: authForm.email, password: authForm.password };

      const response = await fetch(`${API_BASE.users}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok) {
        saveUserSession(data.user); // Save to localStorage
        setAuthForm({ username: '', email: '', password: '', isLogin: true });
      } else {
        showError(data.error || 'Authentication failed');
      }
    } catch (error) {
      showError('Unable to connect to user service. Make sure it\'s running on port 5001.');
    }
    
    setLoading(false);
  };

  const logout = () => {
    clearUserSession();
  };

  // Task Functions (unchanged)
  const loadTasks = async () => {
    try {
      const response = await fetch(`${API_BASE.tasks}/tasks?user_id=${user.id}`);
      const data = await response.json();
      
      if (response.ok) {
        setTasks(data.tasks || []);
      } else {
        showError('Failed to load tasks');
      }
    } catch (error) {
      showError('Unable to connect to task service. Make sure it\'s running on port 5002.');
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE.tasks}/tasks/stats/${user.id}`);
      const data = await response.json();
      
      if (response.ok) {
        setStats(data);
      } else {
        // FIX 4: Show error if stats loading fails
        showError('Failed to load stats');
      }
    } catch (error) {
      console.error('Failed to load stats');
    }
  };

  const handleTaskSubmit = async (e) => {
    e.preventDefault();
    console.log('🚀 Form submitted!'); // ADD THIS
    console.log('Task form data:', taskForm); // ADD THIS
    console.log('User ID:', user.id); // ADD THIS

    setLoading(true);

    try {
      const payload = {
        ...taskForm,
        user_id: user.id,
        due_date: taskForm.due_date || null
      };

      console.log('📦 Payload:', payload); // ADD THIS

      const url = editingTask 
        ? `${API_BASE.tasks}/tasks/${editingTask.id}`
        : `${API_BASE.tasks}/tasks`;

      console.log('📦 Payload:', payload); // ADD THIS
      
      const method = editingTask ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      console.log('📨 Response status:', response.status); // ADD THIS

      const data = await response.json();
      console.log('📥 Response data:', data); // ADD THIS

      if (response.ok) {
        await loadTasks();
        await loadStats();
        setShowTaskForm(false);
        setEditingTask(null);
        setTaskForm({ title: '', description: '', priority: 'medium', status: 'pending', due_date: '' });
      } else {
        showError(data.error || 'Failed to save task');
      }
    } catch (error) {
      console.error('❌ Error:', error); // ADD THIS
      showError('Unable to connect to task service');
    }

    setLoading(false);
  };

  const deleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;

    try {
      const response = await fetch(`${API_BASE.tasks}/tasks/${taskId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await loadTasks();
        await loadStats();
      } else {
        showError('Failed to delete task');
      }
    } catch (error) {
      showError('Unable to connect to task service');
    }
  };

  const editTask = (task) => {
    setEditingTask(task);
    setTaskForm({
      title: task.title,
      description: task.description || '',
      priority: task.priority,
      status: task.status,
      due_date: task.due_date ? task.due_date.split('T')[0] : ''
    });
    setShowTaskForm(true);
  };

  const toggleTaskStatus = async (task) => {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    
    try {
      const response = await fetch(`${API_BASE.tasks}/tasks/${task.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        await loadTasks();
        await loadStats();
      }
    } catch (error) {
      showError('Failed to update task');
    }
  };

  // Filter tasks
  const filteredTasks = tasks.filter(task => {
    if (filter === 'all') return true;
    return task.status === filter;
  });

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'medium': return 'text-blue-600 bg-blue-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'in_progress': return <Clock className="w-5 h-5 text-blue-600" />;
      default: return <AlertCircle className="w-5 h-5 text-gray-600" />;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString();
  };

  // Show loading spinner while checking authentication
  if (loading && !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Login/Register Form
  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <User className="w-12 h-12 text-indigo-600 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900">Task Manager</h1>
            <p className="text-gray-600">Microservices Demo Application</p>
            {APP_ENV === 'development' && (
              <span className="inline-block mt-2 px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">
                Development Mode
              </span>
            )}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {APP_ENV === 'development' && (
            <button
              onClick={() => setShowConfig(!showConfig)}
              className="w-full mb-4 text-sm text-blue-600 hover:text-blue-800"
            >
              {showConfig ? '🔽 Hide' : '▶️ Show'} Configuration
            </button>
          )}

          <ConfigInfo show={showConfig} />

          <form onSubmit={handleAuth} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <input
                type="text"
                value={authForm.username}
                onChange={(e) => setAuthForm({...authForm, username: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>

            {/* {!authForm.isLogin && (
              // <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <input
                type="text"
                value={authForm.username}
                onChange={(e) => setAuthForm({...authForm, username: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div> */}

            {!authForm.isLogin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={authForm.email}
                  onChange={(e) => setAuthForm({...authForm, email: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                value={authForm.password}
                onChange={(e) => setAuthForm({...authForm, password: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50 flex items-center justify-center"
        >
              {loading ? (
                'Loading...'
              ) : authForm.isLogin ? (
                <>
                  <LogIn className="w-4 h-4 mr-2" />
                  Sign In
                </>
              ) : (
                <>
                  <UserPlus className="w-4 h-4 mr-2" />
                  Sign Up
                </>
              )}
            </button>
          </form>

          <div className="mt-4 text-center">
            <button
              onClick={() => setAuthForm({...authForm, isLogin: !authForm.isLogin})}
              className="text-indigo-600 hover:text-indigo-800"
            >
              {authForm.isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Main Application (rest remains the same)
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Task Manager</h1>
              <p className="text-gray-600">Welcome, {user.username}!</p>
            </div>
            <button
              onClick={logout}
              className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 flex items-center"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </button>
          </div>
        </div>
      </header>

      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Total Tasks</h3>
            <p className="text-3xl font-bold text-indigo-600">{stats.total_tasks}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Pending</h3>
            <p className="text-3xl font-bold text-yellow-600">{stats.by_status.pending || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Completed</h3>
            <p className="text-3xl font-bold text-green-600">{stats.by_status.completed || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Overdue</h3>
            <p className="text-3xl font-bold text-red-600">{stats.overdue_tasks}</p>
          </div>
        </div>

        {/* Controls */}
        <div className="flex justify-between items-center mb-6">
          <div className="flex space-x-2">
            {['all', 'pending', 'in_progress', 'completed'].map(status => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-4 py-2 rounded-md ${
                  filter === status 
                    ? 'bg-indigo-600 text-white' 
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
              </button>
            ))}
          </div>

          <button
            onClick={() => setShowTaskForm(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Task
          </button>
        </div>

        {/* Task List */}
        <div className="bg-white rounded-lg shadow">
          {filteredTasks.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-500">No tasks found. Create your first task!</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredTasks.map(task => (
                <div key={task.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <button
                          onClick={() => toggleTaskStatus(task)}
                          className="mr-3"
                        >
                          {getStatusIcon(task.status)}
                        </button>
                        <h3 className={`text-lg font-medium ${
                          task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'
                        }`}>
                          {task.title}
                        </h3>
                        <span className={`ml-3 px-2 py-1 text-xs rounded-full ${getPriorityColor(task.priority)}`}>
                          {task.priority}
                        </span>
                      </div>
                      
                      {task.description && (
                        <p className="text-gray-600 mb-2">{task.description}</p>
                      )}
                      
                      <div className="flex items-center text-sm text-gray-500 space-x-4">
                        <span>Status: {task.status.replace('_', ' ')}</span>
                        {task.due_date && (
                          <span>Due: {formatDate(task.due_date)}</span>
                        )}
                        <span>Created: {formatDate(task.created_at)}</span>
                      </div>
                    </div>
                    
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => editTask(task)}
                        className="p-2 text-gray-600 hover:text-indigo-600"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteTask(task.id)}
                        className="p-2 text-gray-600 hover:text-red-600"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Task Form Modal */}
      {showTaskForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">
              {editingTask ? 'Edit Task' : 'Create New Task'}
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  value={taskForm.title}
                  onChange={(e) => setTaskForm({...taskForm, title: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={taskForm.description}
                  onChange={(e) => setTaskForm({...taskForm, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows="3"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    value={taskForm.priority}
                    onChange={(e) => setTaskForm({...taskForm, priority: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    value={taskForm.status}
                    onChange={(e) => setTaskForm({...taskForm, status: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="pending">Pending</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Due Date
                </label>
                <input
                  type="date"
                  value={taskForm.due_date}
                  onChange={(e) => setTaskForm({...taskForm, due_date: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowTaskForm(false);
                    setEditingTask(null);
                    setTaskForm({ title: '', description: '', priority: 'medium', status: 'pending', due_date: '' });
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                {/* FIX 3: Use type="submit" for task form submit button, remove onClick */}
                <button
                  onClick={handleTaskSubmit}
                  disabled={loading}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
                >
                  {loading ? 'Saving...' : editingTask ? 'Update Task' : 'Create Task'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskManagementApp;