#!/usr/bin/env python3
"""
Telegram Notifier Service - Main Application Entry Point
"""

import os
from app import create_app

# Create the Flask application
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Get configuration
    debug = app.config.get('DEBUG', False)
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting Deli Telegram Notification Service...")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Debug: {debug}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    
    # Run the application
    app.run(host=host, port=port, debug=debug)
