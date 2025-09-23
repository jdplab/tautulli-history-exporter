#!/usr/bin/env python3
"""
Tautulli History Exporter

A modern, production-ready Flask web application for exporting watch history from Tautulli
with comprehensive security, beautiful UI, and advanced filtering capabilities.

Features:
- Secure authentication with password management
- Multi-layered security (rate limiting, CSRF protection, secure headers)
- Modern responsive UI with dark/light theme support
- Advanced data filtering and CSV export capabilities
- Production-ready Docker deployment
- Comprehensive error handling and logging

Author: Jonathan Polansky (with AI assistance)
License: MIT
Version: 2.0.0
"""

import os
from flask import Flask, render_template, redirect, url_for, flash, session, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import requests
import csv
from io import StringIO
import logging
import secrets
from sqlalchemy import text

app = Flask(__name__)

# Security Configuration
# Generate secure secret key if not provided
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
# Database connection - defaults to SQLite for development
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tautulli_exporter.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CSRF Protection
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit for CSRF tokens

# Session Security - secure cookies in production only
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS access to session cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
# Default session timeout: 8 hours (480 minutes)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=int(os.environ.get('SESSION_TIMEOUT', 480)))

# Security Headers
if os.environ.get('SECURITY_HEADERS', 'true').lower() == 'true':
    # Content Security Policy - allows Bootstrap CSS/JS from CDN
    csp = {
        'default-src': "'self'",  # Only allow resources from same origin by default
        'script-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net",  # Allow Bootstrap JS
        'style-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net",   # Allow Bootstrap CSS
        'font-src': "'self' https://cdn.jsdelivr.net",                   # Allow Bootstrap fonts
        'img-src': "'self' data:",                                       # Allow images and data URIs
        'connect-src': "'self' https://cdn.jsdelivr.net"                 # Allow AJAX to CDN
    }
    Talisman(app, 
             force_https=False,  # Set to True when using HTTPS in production
             strict_transport_security=True,
             content_security_policy=csp)

# Rate Limiting with Redis storage
redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
limiter = Limiter(
    app,
    key_func=get_remote_address,  # Rate limit by client IP address
    default_limits=[f"{os.environ.get('RATE_LIMIT', 100)} per minute"],  # Default: 100 requests/minute
    storage_uri=redis_url
)

# Logging Configuration
if os.environ.get('FLASK_ENV') == 'production':
    logging.basicConfig(level=logging.INFO)
    app.logger.info('Tautulli History Exporter starting in production mode')

# Initialize database
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    must_change_password = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Configuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tautulli_url = db.Column(db.String(255), nullable=True)
    api_key = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Helper Functions
def is_logged_in():
    """
    Check if a user is currently logged in.
    
    Returns:
        bool: True if user is logged in (user_id in session), False otherwise
    """
    return 'user_id' in session

def get_configuration():
    """
    Get or create the application configuration from database.
    
    Returns:
        Configuration: The configuration object containing Tautulli URL and API key
    """
    config = Configuration.query.first()
    if not config:
        config = Configuration()
        db.session.add(config)
        db.session.commit()
    return config

def test_tautulli_connection(url, api_key):
    """
    Test connection to Tautulli API by attempting to get server info.
    
    Args:
        url (str): The Tautulli server URL
        api_key (str): The Tautulli API key
        
    Returns:
        tuple: (success: bool, message: str) indicating connection status and result message
    """
    try:
        if not url.endswith('/'):
            url += '/'
        
        test_url = f"{url}api/v2"
        params = {
            'apikey': api_key,
            'cmd': 'get_server_info'
        }
        
        response = requests.get(test_url, params=params, timeout=10)
        data = response.json()
        
        if data.get('response', {}).get('result') == 'success':
            return True, "Connection successful!"
        else:
            return False, "API returned error: " + str(data.get('response', {}).get('message', 'Unknown error'))
    
    except requests.exceptions.RequestException as e:
        return False, f"Connection failed: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_tautulli_users(url, api_key):
    """
    Retrieve list of users from Tautulli API.
    
    Args:
        url (str): The Tautulli server URL
        api_key (str): The Tautulli API key
        
    Returns:
        list: List of user dictionaries containing user_id and friendly_name,
              or empty list if request fails
    """
    try:
        if not url.endswith('/'):
            url += '/'
        
        api_url = f"{url}api/v2"
        params = {
            'apikey': api_key,
            'cmd': 'get_user_names'
        }
        
        response = requests.get(api_url, params=params, timeout=10)
        data = response.json()
        
        if data.get('response', {}).get('result') == 'success':
            return data.get('response', {}).get('data', [])
        else:
            return []
    
    except Exception as e:
        app.logger.error(f"Error getting users: {e}")
        return []

def get_user_history(url, api_key, user_id, start_date=None, end_date=None, media_type=None, length=25):
    """
    Get user watch history from Tautulli with optional filtering.
    
    Args:
        url (str): The Tautulli server URL
        api_key (str): The Tautulli API key
        user_id (str): The user ID to get history for
        start_date (str, optional): Start date filter in YYYY-MM-DD format
        end_date (str, optional): End date filter in YYYY-MM-DD format
        media_type (str, optional): Media type filter (movie, episode, track, etc.)
        length (int, optional): Maximum number of items to return. Defaults to 25
        
    Returns:
        list: List of history items with media information and watch statistics,
              or empty list if request fails
    """
    try:
        if not url.endswith('/'):
            url += '/'
        
        api_url = f"{url}api/v2"
        all_history_items = []
        
        # For requests larger than 1000 items, we need to paginate
        # Tautulli typically limits responses to around 1000 items per request
        if length > 1000:
            # Use pagination to get large datasets
            page_size = 1000
            start = 0
            
            while len(all_history_items) < length:
                items_to_fetch = min(page_size, length - len(all_history_items))
                
                params = {
                    'apikey': api_key,
                    'cmd': 'get_history',
                    'user_id': user_id,
                    'start': start,
                    'length': items_to_fetch
                }
                
                if media_type:
                    params['media_type'] = media_type
                
                response = requests.get(api_url, params=params, timeout=30)
                data = response.json()
                
                if data.get('response', {}).get('result') != 'success':
                    break
                
                page_items = data.get('response', {}).get('data', {}).get('data', [])
                
                # If we got no items, we've reached the end
                if not page_items:
                    break
                
                all_history_items.extend(page_items)
                start += len(page_items)
                
                # If we got fewer items than requested, we've reached the end
                if len(page_items) < items_to_fetch:
                    break
            
            history_items = all_history_items[:length]
        else:
            # For smaller requests, use the existing logic
            api_length = length
            if start_date or end_date:
                # Get more data to ensure we have enough after filtering
                api_length = min(length * 4, 1000)  # Get 4x requested amount, max 1000
            
            params = {
                'apikey': api_key,
                'cmd': 'get_history',
                'user_id': user_id,
                'length': api_length
            }
            
            if media_type:
                params['media_type'] = media_type
            
            response = requests.get(api_url, params=params, timeout=30)
            data = response.json()
            
            if data.get('response', {}).get('result') == 'success':
                history_items = data.get('response', {}).get('data', {}).get('data', [])
            else:
                return []
        
        # Apply server-side date filtering if dates are specified
        if start_date or end_date:
            filtered_items = []
            
            # Convert date strings to timestamps for comparison
            start_timestamp = None
            end_timestamp = None
            
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                start_timestamp = int(start_dt.timestamp())
                
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
                end_timestamp = int(end_dt.timestamp())
            
            # Filter items by date
            for item in history_items:
                item_date = int(item.get('date', 0))
                
                # Check if item falls within date range
                if start_timestamp and item_date < start_timestamp:
                    continue
                if end_timestamp and item_date > end_timestamp:
                    continue
                    
                filtered_items.append(item)
            
            # Return only the requested number of items after filtering
            return filtered_items[:length]
        else:
            # No date filtering, return as requested
            return history_items[:length]
    
    except Exception as e:
        app.logger.error(f"Error getting history: {e}")
        return []

# Routes
@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if user.must_change_password:
        return redirect(url_for('change_password'))
    
    config = get_configuration()
    if not config.tautulli_url or not config.api_key:
        flash('Please configure Tautulli settings first.', 'warning')
        return redirect(url_for('configuration'))
    
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Prevent brute force attacks
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session.permanent = True
            
            # Log successful login
            app.logger.info(f'Successful login for user: {username} from IP: {get_remote_address()}')
            
            if user.must_change_password:
                return redirect(url_for('change_password'))
            else:
                return redirect(url_for('index'))
        else:
            # Log failed login attempt
            app.logger.warning(f'Failed login attempt for user: {username} from IP: {get_remote_address()}')
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/change_password', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Prevent password change abuse
def change_password():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    forced_change = user.must_change_password
    
    if request.method == 'POST':
        # For voluntary password changes, require current password
        if not forced_change:
            current_password = request.form.get('current_password', '')
            if not check_password_hash(user.password_hash, current_password):
                flash('Current password is incorrect', 'error')
                return render_template('change_password.html', forced_change=forced_change)
        
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('change_password.html', forced_change=forced_change)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('change_password.html', forced_change=forced_change)
        
        # Additional password strength validation
        if new_password.lower() in ['password', '123456', 'admin', user.username.lower()]:
            flash('Password is too common. Please choose a stronger password.', 'error')
            return render_template('change_password.html', forced_change=forced_change)
        
        user.password_hash = generate_password_hash(new_password)
        user.must_change_password = False
        db.session.commit()
        
        app.logger.info(f'Password changed for user: {user.username} from IP: {get_remote_address()}')
        flash('Password changed successfully!', 'success')
        
        if forced_change:
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    
    return render_template('change_password.html', forced_change=forced_change)

@app.route('/configuration', methods=['GET', 'POST'])
def configuration():
    """
    Configuration management route for Tautulli connection settings.
    
    Handles both GET (display form) and POST (save settings) requests.
    Allows authenticated users to configure Tautulli URL and API key.
    
    Returns:
        GET: Rendered configuration.html template with current config
        POST: Redirect to configuration page after saving settings
        
    Redirects:
        To login page if user is not authenticated
    """
    if not is_logged_in():
        return redirect(url_for('login'))
    
    config = get_configuration()
    
    if request.method == 'POST':
        config.tautulli_url = request.form['tautulli_url'].strip()
        config.api_key = request.form['api_key'].strip()
        config.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Configuration saved successfully!', 'success')
        return redirect(url_for('configuration'))
    
    return render_template('configuration.html', config=config)

@app.route('/test_connection', methods=['POST'])
def test_connection():
    """
    AJAX endpoint to test Tautulli server connection.
    
    Validates connection to Tautulli server using provided URL and API key.
    Returns JSON response indicating success/failure status.
    
    Form Parameters:
        tautulli_url (str): Tautulli server URL to test
        api_key (str): API key for authentication
        
    Returns:
        JSON: {'success': bool, 'message': str} - Connection test result
    """
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    url = request.form['tautulli_url'].strip()
    api_key = request.form['api_key'].strip()
    
    success, message = test_tautulli_connection(url, api_key)
    return jsonify({'success': success, 'message': message})

@app.route('/get_users')
def get_users():
    """
    AJAX endpoint to retrieve Tautulli user list.
    
    Fetches all users from configured Tautulli server for filtering purposes.
    Returns JSON response with user data or error message.
    
    Returns:
        JSON: {'success': bool, 'users': list, 'message': str} - User list or error
    """
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    config = get_configuration()
    if not config.tautulli_url or not config.api_key:
        return jsonify({'success': False, 'message': 'Tautulli not configured'})
    
    users = get_tautulli_users(config.tautulli_url, config.api_key)
    return jsonify({'success': True, 'users': users})

@app.route('/get_history', methods=['POST'])
def get_history():
    """
    AJAX endpoint to retrieve filtered user history from Tautulli.
    
    Fetches watch history for specified user with optional filters for
    date range, media type, and result limit.
    
    Form Parameters:
        user_id (str): Tautulli user ID (required)
        start_date (str): Start date filter (YYYY-MM-DD format, optional)
        end_date (str): End date filter (YYYY-MM-DD format, optional)
        media_type (str): Media type filter (optional)
        length (int): Number of results to return (default: 25)
        
    Returns:
        JSON: {'success': bool, 'history': list, 'message': str} - History data or error
    """
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    config = get_configuration()
    if not config.tautulli_url or not config.api_key:
        return jsonify({'success': False, 'message': 'Tautulli not configured'})
    
    user_id = request.form.get('user_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    media_type = request.form.get('media_type')
    length = int(request.form.get('length', 25))
    
    # Validate export limit
    if length > 10000:
        return jsonify({'success': False, 'message': 'Export limit is 10,000 items maximum'})
    
    if not user_id:
        return jsonify({'success': False, 'message': 'User ID required'})
    
    # Validate date range
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                return jsonify({'success': False, 'message': 'Start date must be before or equal to end date'})
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format'})
    
    history = get_user_history(config.tautulli_url, config.api_key, user_id, start_date, end_date, media_type, length)
    return jsonify({'success': True, 'history': history})

@app.route('/export_csv', methods=['POST'])
def export_csv():
    """
    Export watch history data to CSV file.
    
    Generates a CSV file from provided history data with formatted columns
    including date, user, title, media type, duration, completion percentage,
    status, and IP address.
    
    JSON Parameters:
        history (list): Array of history objects to export
        
    Returns:
        CSV file download or JSON error response
        
    CSV Columns:
        - Date: Formatted timestamp of watch event
        - User: Friendly username
        - Title: Show/movie title with episode info
        - Media Type: Type of media (movie, episode, etc.)
        - Duration (min): Playback duration in minutes
        - Percent Complete: Completion percentage
        - Status: Finished/Stopped/Unknown
        - IP Address: Client IP address
    """
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    history_data = request.json.get('history', [])
    
    if not history_data:
        return jsonify({'success': False, 'message': 'No data to export'})
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Headers
    headers = ['Date', 'User', 'Title', 'Media Type', 'Duration (min)', 'Percent Complete', 'Status', 'IP Address']
    writer.writerow(headers)
    
    # Data rows
    for item in history_data:
        date = datetime.fromtimestamp(int(item.get('date', 0))).strftime('%Y-%m-%d %H:%M:%S') if item.get('date') else ''
        user = item.get('friendly_name', '')
        title = f"{item.get('grandparent_title', '')} - {item.get('title', '')}" if item.get('grandparent_title') else item.get('title', '')
        media_type = item.get('media_type', '')
        duration = round(int(item.get('duration', 0)) / 60, 1) if item.get('duration') else 0
        percent_complete = f"{item.get('percent_complete', 0)}%"
        
        # Format watched status
        watched_status = int(item.get('watched_status', 0))
        status_text = 'Finished' if watched_status == 1 else 'Stopped' if watched_status == 0 else 'Unknown'
        
        ip_address = item.get('ip_address', '')
        
        writer.writerow([date, user, title, media_type, duration, percent_complete, status_text, ip_address])
    
    # Create response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=tautulli_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/logout')
def logout():
    """
    User logout route.
    
    Clears user session and redirects to login page.
    
    Returns:
        Redirect to login page
    """
    session.clear()
    return redirect(url_for('login'))

# Health check endpoint for monitoring
@app.route('/health')
@limiter.exempt
def health_check():
    """
    Health check endpoint for application monitoring.
    
    Tests database connectivity and returns application status.
    Exempt from rate limiting for monitoring systems.
    
    Returns:
        JSON: Status information with HTTP 200 (healthy) or 503 (unhealthy)
        
    Response Format:
        {
            'status': 'healthy'|'unhealthy',
            'timestamp': ISO format timestamp,
            'version': Application version,
            'error': Error message (if unhealthy)
        }
    """
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    except Exception as e:
        app.logger.error(f'Health check failed: {str(e)}')
        return jsonify({
            'status': 'unhealthy',
            'error': 'Database connection failed',
            'timestamp': datetime.utcnow().isoformat()
        }), 503

# Security headers for all responses
@app.after_request
def set_security_headers(response):
    """
    Add security headers to all HTTP responses.
    
    Applies standard security headers to enhance application security
    unless disabled via SECURITY_HEADERS environment variable.
    
    Args:
        response (Flask.Response): The response object to modify
        
    Returns:
        Flask.Response: Modified response with security headers
        
    Headers Added:
        - X-Content-Type-Options: nosniff
        - X-Frame-Options: DENY
        - X-XSS-Protection: 1; mode=block
        - Referrer-Policy: strict-origin-when-cross-origin
    """
    if os.environ.get('SECURITY_HEADERS', 'true').lower() == 'true':
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 Not Found errors.
    
    Args:
        error: The error object (unused)
        
    Returns:
        Rendered error template with 404 status code
    """
    return render_template('error.html', 
                         title='Page Not Found',
                         message='The requested page could not be found.'), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 Internal Server errors.
    
    Logs the error and rolls back database session to prevent corruption.
    
    Args:
        error: The error object
        
    Returns:
        Rendered error template with 500 status code
    """
    app.logger.error(f'Internal server error: {str(error)}')
    db.session.rollback()
    return render_template('error.html',
                         title='Internal Server Error', 
                         message='An internal error occurred. Please try again later.'), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    """
    Handle 429 Rate Limit Exceeded errors.
    
    Args:
        e: The rate limit error object
        
    Returns:
        Rendered error template with 429 status code
    """
    return render_template('error.html',
                         title='Rate Limit Exceeded',
                         message='Too many requests. Please wait before trying again.'), 429

# Initialize database and create default user
def create_tables():
    """
    Initialize database tables and create default admin user.
    
    Creates all database tables defined by SQLAlchemy models and
    ensures a default admin user exists for initial application access.
    
    Default User:
        - Username: admin
        - Password: admin (must be changed on first login)
        - must_change_password: True
    """
    with app.app_context():
        db.create_all()
        
        # Create default admin user if none exists
        if not User.query.first():
            default_user = User(
                username='admin',
                password_hash=generate_password_hash('admin'),
                must_change_password=True
            )
            db.session.add(default_user)
            db.session.commit()

if __name__ == '__main__':
    create_tables()
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0')