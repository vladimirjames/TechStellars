from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import base64
import io
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB

# Create uploads directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        fullname TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        image_name TEXT,
        crop_type TEXT,
        disease_name TEXT,
        confidence REAL,
        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def create_user(username, email, password, fullname):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, email, password, fullname) VALUES (?, ?, ?, ?)',
                    (username, email, password, fullname))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def save_detection(user_id, image_name, crop_type, disease_name, confidence):
    conn = get_db_connection()
    conn.execute('INSERT INTO detections (user_id, image_name, crop_type, disease_name, confidence) VALUES (?, ?, ?, ?, ?)',
                 (user_id, image_name, crop_type, disease_name, confidence))
    conn.commit()
    conn.close()

def get_user_detections(user_id):
    conn = get_db_connection()
    detections = conn.execute('SELECT * FROM detections WHERE user_id = ? ORDER BY detected_at DESC LIMIT 10', 
                             (user_id,)).fetchall()
    conn.close()
    return detections

# Simple disease database
disease_info = {
    'Healthy': {
        'symptoms': ['Green leaves', 'No spots or discoloration', 'Normal growth'],
        'prevention': ['Regular watering', 'Proper spacing', 'Balanced fertilizer'],
        'treatment': ['No treatment needed', 'Continue good practices']
    },
    'Early Blight': {
        'symptoms': ['Brown spots with concentric rings', 'Yellowing leaves', 'Leaf drop'],
        'prevention': ['Crop rotation', 'Fungicide spray', 'Remove infected leaves'],
        'treatment': ['Copper-based fungicide', 'Remove affected parts', 'Improve air circulation']
    },
    'Late Blight': {
        'symptoms': ['Dark water-soaked spots', 'White mold underside', 'Rapid plant collapse'],
        'prevention': ['Avoid overhead watering', 'Use resistant varieties', 'Proper spacing'],
        'treatment': ['Destroy infected plants', 'Apply systemic fungicide', 'Quarantine area']
    },
    'Powdery Mildew': {
        'symptoms': ['White powdery spots', 'Leaf distortion', 'Reduced growth'],
        'prevention': ['Good air circulation', 'Avoid crowding', 'Morning watering'],
        'treatment': ['Sulfur spray', 'Baking soda solution', 'Milk spray']
    }
}

def simple_disease_detection(image_data, crop_type):
    """Mock disease detection - in real app, replace with AI model"""
    # Simple mock detection based on filename/content length
    # This is where you'd add real image processing
    import random
    diseases = ['Healthy', 'Early Blight', 'Late Blight', 'Powdery Mildew']
    weights = [0.6, 0.2, 0.15, 0.05]  # Higher probability for healthy
    
    disease = random.choices(diseases, weights=weights)[0]
    confidence = round(random.uniform(75, 95), 1)
    
    return disease, confidence

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crop Disease Detector</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .card { backdrop-filter: blur(10px); background: rgba(255,255,255,0.9); }
        </style>
    </head>
    <body class="d-flex align-items-center">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card shadow-lg">
                        <div class="card-body text-center p-5">
                            <h1 class="display-4 text-success mb-4">🌱 Crop Doctor</h1>
                            <p class="lead mb-4">AI-powered plant disease detection made simple</p>
                            <div class="d-grid gap-3">
                                <a href="/register" class="btn btn-success btn-lg">Get Started</a>
                                <a href="/login" class="btn btn-outline-success btn-lg">Login</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        fullname = request.form['fullname']
        
        if get_user_by_username(username):
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))
        
        if create_user(username, email, password, fullname):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed!', 'error')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - Crop Doctor</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-dark bg-success">
            <div class="container">
                <a class="navbar-brand" href="/">🌱 Crop Doctor</a>
            </div>
        </nav>
        
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card shadow">
                        <div class="card-body p-4">
                            <h3 class="text-center mb-4">👤 Register</h3>
                            
                            {% with messages = get_flashed_messages(with_categories=true) %}
                                {% if messages %}
                                    {% for category, message in messages %}
                                        <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }}">
                                            {{ message }}
                                        </div>
                                    {% endfor %}
                                {% endif %}
                            {% endwith %}
                            
                            <form method="POST">
                                <div class="mb-3">
                                    <label class="form-label">Full Name</label>
                                    <input type="text" name="fullname" class="form-control" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Username</label>
                                    <input type="text" name="username" class="form-control" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" name="email" class="form-control" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Password</label>
                                    <input type="password" name="password" class="form-control" required>
                                </div>
                                <button type="submit" class="btn btn-success w-100 btn-lg">Register</button>
                            </form>
                            
                            <div class="text-center mt-3">
                                <a href="/login">Already have an account? Login here</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user_by_username(username)
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['fullname'] = user['fullname']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - Crop Doctor</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-dark bg-success">
            <div class="container">
                <a class="navbar-brand" href="/">🌱 Crop Doctor</a>
            </div>
        </nav>
        
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card shadow">
                        <div class="card-body p-4">
                            <h3 class="text-center mb-4">🔐 Login</h3>
                            
                            {% with messages = get_flashed_messages(with_categories=true) %}
                                {% if messages %}
                                    {% for category, message in messages %}
                                        <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }}">
                                            {{ message }}
                                        </div>
                                    {% endfor %}
                                {% endif %}
                            {% endwith %}
                            
                            <form method="POST">
                                <div class="mb-3">
                                    <label class="form-label">Username</label>
                                    <input type="text" name="username" class="form-control" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Password</label>
                                    <input type="password" name="password" class="form-control" required>
                                </div>
                                <button type="submit" class="btn btn-success w-100 btn-lg">Login</button>
                            </form>
                            
                            <div class="text-center mt-3">
                                <a href="/register">Don't have an account? Register here</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    detections = get_user_detections(session['user_id'])
    
    detection_rows = ''
    for detection in detections:
        badge_class = 'success' if detection['disease_name'] == 'Healthy' else 'danger'
        detection_rows += f'''
        <tr>
            <td>{detection['crop_type'].title()}</td>
            <td><span class="badge bg-{badge_class}">{detection['disease_name']}</span></td>
            <td>{detection['confidence']}%</td>
            <td>{detection['detected_at'][:16]}</td>
        </tr>
        '''
    
    if not detection_rows:
        detection_rows = '<tr><td colspan="4" class="text-center">No detections yet. <a href="/detect">Start detecting!</a></td></tr>'
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - Crop Doctor</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-dark bg-success">
            <div class="container">
                <a class="navbar-brand" href="/">🌱 Crop Doctor</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/dashboard">Dashboard</a>
                    <a class="nav-link" href="/detect">Detect</a>
                    <a class="nav-link" href="/logout">Logout ({session["fullname"]})</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <div class="card shadow">
                        <div class="card-body">
                            <h2>Welcome, {session['fullname']}! 👋</h2>
                            <p class="lead">Plant disease detection made simple</p>
                            
                            <a href="/detect" class="btn btn-success btn-lg mb-4">🌿 Detect Disease</a>
                            
                            <h4>Recent Detections</h4>
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Crop Type</th>
                                            <th>Disease</th>
                                            <th>Confidence</th>
                                            <th>Date</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {detection_rows}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No image selected!', 'error')
            return redirect(request.url)
        
        file = request.files['image']
        crop_type = request.form.get('crop_type', 'tomato')
        
        if file.filename == '':
            flash('No image selected!', 'error')
            return redirect(request.url)
        
        if file:
            # Save file
            filename = f"{session['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Mock disease detection
            disease, confidence = simple_disease_detection(file.read(), crop_type)
            save_detection(session['user_id'], filename, crop_type, disease, confidence)
            
            info = disease_info.get(disease, disease_info['Healthy'])
            
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Results - Crop Doctor</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="bg-light">
                <nav class="navbar navbar-expand-lg navbar-dark bg-success">
                    <div class="container">
                        <a class="navbar-brand" href="/">🌱 Crop Doctor</a>
                        <div class="navbar-nav ms-auto">
                            <a class="nav-link" href="/dashboard">Dashboard</a>
                            <a class="nav-link" href="/detect">Detect</a>
                            <a class="nav-link" href="/logout">Logout</a>
                        </div>
                    </div>
                </nav>
                
                <div class="container mt-4">
                    <div class="row justify-content-center">
                        <div class="col-md-10">
                            <div class="card shadow">
                                <div class="card-body">
                                    <h3 class="text-center">🔍 Detection Results</h3>
                                    
                                    <div class="row mt-4">
                                        <div class="col-md-6 text-center">
                                            <img src="/{filepath}" alt="Plant image" class="img-fluid rounded" style="max-height: 300px;">
                                        </div>
                                        <div class="col-md-6">
                                            <div class="alert alert-{'success' if disease == 'Healthy' else 'danger'}">
                                                <h4>{disease}</h4>
                                                <p class="mb-0">Confidence: <strong>{confidence}%</strong></p>
                                            </div>
                                            
                                            <h5>🔍 Symptoms:</h5>
                                            <ul>
                                                {"".join([f'<li>{s}</li>' for s in info['symptoms']])}
                                            </ul>
                                        </div>
                                    </div>
                                    
                                    <div class="row mt-4">
                                        <div class="col-md-6">
                                            <div class="card">
                                                <div class="card-header bg-warning">🛡️ Prevention</div>
                                                <div class="card-body">
                                                    <ul>
                                                        {"".join([f'<li>{p}</li>' for p in info['prevention']])}
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="card">
                                                <div class="card-header bg-info text-white">💊 Treatment</div>
                                                <div class="card-body">
                                                    <ul>
                                                        {"".join([f'<li>{t}</li>' for t in info['treatment']])}
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="text-center mt-4">
                                        <a href="/detect" class="btn btn-success">🔄 Analyze Another</a>
                                        <a href="/dashboard" class="btn btn-outline-success">📊 Dashboard</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            '''
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Detect Disease - Crop Doctor</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-dark bg-success">
            <div class="container">
                <a class="navbar-brand" href="/">🌱 Crop Doctor</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/dashboard">Dashboard</a>
                    <a class="nav-link" href="/detect">Detect</a>
                    <a class="nav-link" href="/logout">Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card shadow">
                        <div class="card-body">
                            <h3 class="text-center">🌿 Detect Plant Disease</h3>
                            
                            <form method="POST" enctype="multipart/form-data">
                                <div class="mb-3">
                                    <label class="form-label">Crop Type</label>
                                    <select name="crop_type" class="form-select">
                                        <option value="tomato">Tomato</option>
                                        <option value="potato">Potato</option>
                                        <option value="corn">Corn</option>
                                        <option value="general">General</option>
                                    </select>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Plant Image</label>
                                    <input type="file" name="image" class="form-control" accept="image/*" required>
                                    <div class="form-text">Upload a clear photo of plant leaves, stems, or fruits</div>
                                </div>
                                
                                <button type="submit" class="btn btn-success w-100 btn-lg">🔍 Analyze Image</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)