"""
Character Routes - Create, Edit, Delete AI Characters
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Character
from werkzeug.utils import secure_filename

characters_bp = Blueprint('characters', __name__, url_prefix='/characters')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

PERSONALITY_OPTIONS = [
    'friendly', 'mysterious', 'humorous', 'serious', 'romantic',
    'adventurous', 'wise', 'playful', 'dramatic', 'caring'
]

SPEAKING_STYLES = [
    'casual', 'formal', 'poetic', 'technical', 'slang', 
    'old-english', 'philosophical', 'enthusiastic', 'sarcastic', 'gentle'
]

@characters_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        personality = request.form.get('personality', 'friendly')
        background_story = request.form.get('background_story', '').strip()
        speaking_style = request.form.get('speaking_style', 'casual')
        color_accent = request.form.get('color_accent', '#7c3aed')
        
        if not name:
            flash('Character name is required.', 'error')
            return render_template('characters/create.html', 
                                   personalities=PERSONALITY_OPTIONS,
                                   speaking_styles=SPEAKING_STYLES)
        
        character = Character(
            user_id=current_user.id,
            name=name,
            personality=personality,
            background_story=background_story,
            speaking_style=speaking_style,
            color_accent=color_accent
        )
        
        # Handle avatar upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"char_{current_user.id}_{name.replace(' ', '_')}_{file.filename}")
                upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_path, exist_ok=True)
                file.save(os.path.join(upload_path, filename))
                character.avatar = filename
        
        db.session.add(character)
        db.session.commit()
        
        flash(f'Character "{name}" created successfully! 🎭', 'success')
        return redirect(url_for('chat.chat_page', character_id=character.id))
    
    return render_template('characters/create.html',
                           personalities=PERSONALITY_OPTIONS,
                           speaking_styles=SPEAKING_STYLES)


@characters_bp.route('/edit/<int:character_id>', methods=['GET', 'POST'])
@login_required
def edit(character_id):
    character = Character.query.filter_by(id=character_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        character.name = request.form.get('name', character.name).strip()
        character.personality = request.form.get('personality', character.personality)
        character.background_story = request.form.get('background_story', character.background_story)
        character.speaking_style = request.form.get('speaking_style', character.speaking_style)
        character.color_accent = request.form.get('color_accent', character.color_accent)
        
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"char_{current_user.id}_{character.name.replace(' ', '_')}_{file.filename}")
                upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_path, exist_ok=True)
                file.save(os.path.join(upload_path, filename))
                character.avatar = filename
        
        db.session.commit()
        flash(f'Character "{character.name}" updated! ✅', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('characters/edit.html', character=character,
                           personalities=PERSONALITY_OPTIONS,
                           speaking_styles=SPEAKING_STYLES)


@characters_bp.route('/delete/<int:character_id>', methods=['POST'])
@login_required
def delete(character_id):
    character = Character.query.filter_by(id=character_id, user_id=current_user.id).first_or_404()
    name = character.name
    db.session.delete(character)
    db.session.commit()
    flash(f'Character "{name}" deleted. 🗑️', 'info')
    return redirect(url_for('main.dashboard'))


@characters_bp.route('/toggle-online/<int:character_id>', methods=['POST'])
@login_required
def toggle_online(character_id):
    character = Character.query.filter_by(id=character_id, user_id=current_user.id).first_or_404()
    character.is_online = not character.is_online
    db.session.commit()
    return jsonify({'is_online': character.is_online})
