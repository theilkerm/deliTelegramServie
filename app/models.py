"""
Database models for the Telegram Notifier Service
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Association table for many-to-many relationship between services and chats
service_chat_association = db.Table('service_chat_association',
    db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True),
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'), primary_key=True)
)

class Service(db.Model):
    """Service model for managing notification services."""
    __tablename__ = 'service'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    label = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Many-to-many relationship with chats
    authorized_chats = db.relationship('Chat', secondary=service_chat_association, 
                                     backref=db.backref('services', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Service {self.name}>'
    
    def to_dict(self):
        """Convert service to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'label': self.label or '',
            'description': self.description or '',
            'api_key': self.api_key,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d') if self.updated_at else None,
            'authorized_chat_ids': [chat.id for chat in self.authorized_chats]
        }

class MessageEvent(db.Model):
    """Message event model for tracking notification history."""
    __tablename__ = 'message_event'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    message_content = db.Column(db.Text, nullable=False)
    telegram_message_id = db.Column(db.Integer, nullable=True)
    success = db.Column(db.Boolean, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    service = db.relationship('Service', backref='message_events')
    chat = db.relationship('Chat', backref='message_events')
    
    def __repr__(self):
        return f'<MessageEvent {self.id}: {self.service.name if self.service else "Unknown"} -> {self.chat.title if self.chat else "Unknown"}>'
    
    def to_dict(self):
        """Convert message event to dictionary."""
        return {
            'id': self.id,
            'service_name': self.service.name if self.service else 'Unknown',
            'chat_title': self.chat.title if self.chat else 'Unknown',
            'message_content': self.message_content,
            'telegram_message_id': self.telegram_message_id,
            'success': self.success,
            'error_message': self.error_message,
            'sent_at': self.sent_at.strftime('%Y-%m-%d %H:%M:%S') if self.sent_at else None
        }

class Chat(db.Model):
    """Chat model for managing Telegram chats."""
    __tablename__ = 'chat'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.BigInteger, unique=True, nullable=False)  # Telegram chat ID
    title = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(100), nullable=True)
    chat_type = db.Column(db.String(20), nullable=False, default='private')
    label = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_tester = db.Column(db.Boolean, default=False)  # Mark chats for testing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Chat {self.title}>'
    
    def to_dict(self):
        """Convert chat to dictionary."""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'title': self.title,
            'username': self.username or '',
            'chat_type': self.chat_type,
            'label': self.label or '',
            'description': self.description or '',
            'is_tester': self.is_tester,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d') if self.updated_at else None
        }
