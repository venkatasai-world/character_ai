"""
Profile Routes - View and Edit User Profile
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import db, User
from werkzeug.utils import secure_filename

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def view():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        language = request.form.get('language', 'en')
        
        if name:
            current_user.name = name
        current_user.language = language
        
        # Handle avatar upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"user_{current_user.id}_{file.filename}")
                upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_path, exist_ok=True)
                file.save(os.path.join(upload_path, filename))
                current_user.avatar = filename
        
        db.session.commit()
        flash('Profile updated successfully! ✅', 'success')
        return redirect(url_for('profile.view'))
    
    return render_template('profile.html')


@profile_bp.route('/update-language', methods=['POST'])
@login_required
def update_language():
    data = request.get_json()
    language = data.get('language', 'en')
    current_user.language = language
    db.session.commit()
    return jsonify({'success': True, 'language': language})
