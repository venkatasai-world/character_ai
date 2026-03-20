"""
Main Routes - Landing Page, Dashboard
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from models import Character, ChatHistory

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    characters = Character.query.filter_by(user_id=current_user.id).order_by(Character.created_at.desc()).all()
    
    # Stats
    total_messages = ChatHistory.query.filter_by(user_id=current_user.id).count()
    
    # Last active character
    last_chat = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).first()
    last_character = None
    if last_chat:
        last_character = Character.query.get(last_chat.character_id)
    
    return render_template('dashboard.html', 
                           characters=characters,
                           total_messages=total_messages,
                           last_character=last_character)
