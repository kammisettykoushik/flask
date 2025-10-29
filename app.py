from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from monitor.screenshot import start_screenshot_thread
from datetime import datetime
import requests


app = Flask(__name__)
app.secret_key = 'secret-key-example'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitoring.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

USERS = {"admin": "admin123", "employee": "emp123"}

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    location = db.Column(db.String(200))
    login_time = db.Column(db.DateTime, nullable=False)
    logout_time = db.Column(db.DateTime)
    session_duration = db.Column(db.Integer)  # duration in seconds
    
    def __repr__(self):
        return f'<Session {self.username} - {self.login_time}>'


def get_user_ip():
    """Get the user's IP address, handling proxies"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        return request.remote_addr or request.environ.get('REMOTE_ADDR', 'Unknown')

def get_location_from_ip(ip_address):
    """Get location from IP address using ip-api.com (free, no key required)"""
    try:
        response = requests.get(f'https://ipinfo.io/json/{ip_address}', timeout=3)
        data = response.json()
        if data.get('status') == 'success':
            return f"{data.get('city', 'Unknown')}, {data.get('regionName', 'Unknown')}, {data.get('country', 'Unknown')}"
        return "Location unavailable"
    except Exception as e:
        print(f"Location lookup error: {e}")
        return "Location unavailable"




@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username in USERS and USERS[username] == password:
        session['username'] = username
        
        # Capture login metadata
        ip_address = get_user_ip()
        location = get_location_from_ip(ip_address)
        login_time = datetime.now()
        
        # Create new session record in database
        user_session = UserSession(
            username=username,
            ip_address=ip_address,
            location=location,
            login_time=login_time
        )
        db.session.add(user_session)
        db.session.commit()
        
        # Store session ID for logout tracking
        session['session_id'] = user_session.id
        
        print(f"[+] User {username} logged in from {ip_address} ({location})")
        
        if username == "employee":
            start_screenshot_thread()
            return redirect(url_for('dashboard'))
        if username == "admin":
            start_screenshot_thread()
            return redirect(url_for('admin_panel'))
    else:
        return render_template('login.html', error="Invalid credentials")



@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    return render_template('dashboard.html', user=session['username'])

@app.route('/admin')
def admin_panel():
    if session.get('username') != "admin":
        return redirect('/')
    return render_template('admin_panel.html')


@app.route('/logout')
def logout():
    if 'session_id' in session:
        # Update session record with logout time and duration
        user_session = UserSession.query.get(session['session_id'])
        if user_session and not user_session.logout_time:
            user_session.logout_time = datetime.now()
            user_session.session_duration = int(
                (user_session.logout_time - user_session.login_time).total_seconds()
            )
            db.session.commit()
            print(f"[+] User {user_session.username} logged out. Duration: {user_session.session_duration} seconds")
    
    session.pop('username', None)
    session.pop('session_id', None)
    return redirect('/')

@app.route('/admin/sessions')
def view_sessions():
    if session.get('username') != "admin":
        return redirect('/')
    
    # Get all sessions ordered by most recent first
    all_sessions = UserSession.query.order_by(UserSession.login_time.desc()).all()
    return render_template('session_logs.html', sessions=all_sessions)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates the database and tables
        print("[+] Database initialized")
    app.run(debug=True)

