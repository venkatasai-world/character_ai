"""
Database Models for AI Character App
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(255), default='default_avatar.png')
    language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(256), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    characters = db.relationship('Character', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        from datetime import timedelta
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def __repr__(self):
        return f'<User {self.email}>'


class Character(db.Model):
    """AI Character model"""
    __tablename__ = 'characters'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    personality = db.Column(db.String(50), default='friendly')
    background_story = db.Column(db.Text, nullable=True)
    speaking_style = db.Column(db.String(50), default='casual')
    avatar = db.Column(db.String(255), default='default_char.png')
    color_accent = db.Column(db.String(20), default='#7c3aed')
    is_online = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('ChatHistory', backref='character', lazy=True, cascade='all, delete-orphan')
    
    def get_system_prompt(self):
        """Generate system prompt for Gemini based on character personality"""
        return f"""You are {self.name}, an AI character with the following traits:

Personality: {self.personality}
Background: {self.background_story or 'A mysterious AI character'}
Speaking Style: {self.speaking_style}

Important rules:
- Always stay in character as {self.name}
- Match the personality and speaking style described above
- Keep responses engaging and conversational
- If the user speaks in a different language, respond in the same language
- You can occasionally use emojis to express emotions
- If the user asks "why", "because", "how", or "explain", include a short reasoning/explanation (1-3 sentences) before the answer.
- When addressing the user, use their name if it is provided to you in the system instructions.
- Keep responses concise but meaningful (2-4 sentences usually; explanations can be slightly longer when the user asks "why/how").
"""
    
    def __repr__(self):
        return f'<Character {self.name}>'


class ChatHistory(db.Model):
    """Chat message history"""
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'user' or 'model'
    message_type = db.Column(db.String(10), default='text')  # 'text' or 'sticker'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp.strftime('%H:%M')
        }
    
    def __repr__(self):
        return f'<ChatHistory {self.role}: {self.content[:50]}>'


class Sticker(db.Model):
    """Sticker model"""
    __tablename__ = 'stickers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), default='general')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Sticker {self.name}>'
