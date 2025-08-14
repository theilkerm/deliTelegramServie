"""
Authentication module for admin access
"""

from functools import wraps
from flask import request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
import os

def init_auth(app):
    """Initialize authentication with the Flask app."""
    app.secret_key = app.config.get('SECRET_KEY') or os.urandom(24)
    
    # Set session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

def login_required(f):
    """Decorator to require login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def is_authenticated():
    """Check if user is authenticated."""
    return session.get('authenticated', False)

def authenticate_user(username, password):
    """Authenticate user credentials."""
    # Get admin credentials from environment variables
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_password_hash = os.environ.get('ADMIN_PASSWORD_HASH')
    
    # If no password hash is set, use default 'admin' password
    if not admin_password_hash:
        admin_password_hash = generate_password_hash('admin')
    
    if username == admin_username and check_password_hash(admin_password_hash, password):
        session['authenticated'] = True
        session['username'] = username
        session.permanent = True
        return True
    return False

def logout_user():
    """Logout the current user."""
    session.pop('authenticated', None)
    session.pop('username', None)

def get_current_user():
    """Get current authenticated user info."""
    if is_authenticated():
        return {
            'username': session.get('username'),
            'authenticated': True
        }
    return None
