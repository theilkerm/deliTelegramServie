from flask import Flask
import logging
from config import config
from app.models import db
from app.auth import init_auth

def create_app(config_name='default'):
    """Application factory function."""
    app = Flask(__name__)
    
    # Set application name
    app.name = "Deli Telegram Notification Service"
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize database
    db.init_app(app)
    
    # Initialize authentication
    init_auth(app)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(message)s'
    )
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
