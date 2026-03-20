"""
Chat Routes - AI Chat with characters, stickers, voice
"""
import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Character, ChatHistory, Sticker
from utils.ai import get_ai_response, get_sticker_response

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')


@chat_bp.route('/<int:character_id>')
@login_required
def chat_page(character_id):
    character = Character.query.filter_by(id=character_id, user_id=current_user.id).first_or_404()
    
    # Get user's characters for sidebar
    characters = Character.query.filter_by(user_id=current_user.id).order_by(Character.created_at.desc()).all()
    
    # Get chat history
    messages = ChatHistory.query.filter_by(
        character_id=character_id,
        user_id=current_user.id
    ).order_by(ChatHistory.timestamp.asc()).all()
    
    # Get stickers
    stickers = Sticker.query.all()
    sticker_files = []
    sticker_dir = os.path.join(current_app.root_path, 'static', 'stickers')
    if os.path.exists(sticker_dir):
        sticker_files = [f for f in os.listdir(sticker_dir) 
                        if f.lower().endswith(('.png', '.gif', '.jpg', '.jpeg', '.webp'))]
    
    return render_template('chat/chat.html',
                           character=character,
                           characters=characters,
                           messages=messages,
                           sticker_files=sticker_files)


@chat_bp.route('/send/<int:character_id>', methods=['POST'])
@login_required
def send_message(character_id):
    character = Character.query.filter_by(id=character_id, user_id=current_user.id).first_or_404()
    
    data = request.get_json()
    message_text = data.get('message', '').strip()
    message_type = data.get('type', 'text')
    user_language = data.get('language', current_user.language or 'en')
    
    if not message_text:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Save user message
    user_msg = ChatHistory(
        character_id=character_id,
        user_id=current_user.id,
        role='user',
        message_type=message_type,
        content=message_text
    )
    db.session.add(user_msg)
    db.session.flush()
    
    # Get chat history for context
    history = ChatHistory.query.filter_by(
        character_id=character_id,
        user_id=current_user.id
    ).order_by(ChatHistory.timestamp.asc()).limit(20).all()
    
    # Generate AI response
    if message_type == 'sticker':
        ai_text = get_sticker_response(character, history, message_text, user_name=current_user.name)
    else:
        ai_text = get_ai_response(
            character,
            history,
            message_text,
            user_name=current_user.name,
            target_language=user_language
        )
    
    # Save AI response
    ai_msg = ChatHistory(
        character_id=character_id,
        user_id=current_user.id,
        role='model',
        message_type='text',
        content=ai_text
    )
    db.session.add(ai_msg)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user_message': user_msg.to_dict(),
        'ai_message': ai_msg.to_dict()
    })


@chat_bp.route('/clear/<int:character_id>', methods=['POST'])
@login_required
def clear_chat(character_id):
    character = Character.query.filter_by(id=character_id, user_id=current_user.id).first_or_404()
    ChatHistory.query.filter_by(character_id=character_id, user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'success': True})


@chat_bp.route('/export/<int:character_id>')
@login_required
def export_chat(character_id):
    """Export chat as text"""
    character = Character.query.filter_by(id=character_id, user_id=current_user.id).first_or_404()
    messages = ChatHistory.query.filter_by(
        character_id=character_id,
        user_id=current_user.id
    ).order_by(ChatHistory.timestamp.asc()).all()
    
    lines = [f"Chat with {character.name}\n{'='*50}\n"]
    for msg in messages:
        role = current_user.name if msg.role == 'user' else character.name
        lines.append(f"[{msg.timestamp.strftime('%Y-%m-%d %H:%M')}] {role}: {msg.content}")
    
    content = '\n'.join(lines)
    
    from flask import Response
    return Response(
        content,
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment; filename=chat_{character.name}.txt'}
    )
