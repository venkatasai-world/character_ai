"""
AI Character App - Main Application Entry Point
"""
import os
from flask import Flask
from flask_login import LoginManager
from models import db, User
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    # IMPORTANT:
    # If SQLALCHEMY_DATABASE_URI uses a *relative* sqlite path (e.g. sqlite:///ai_character.db),
    # the DB file location depends on the current working directory. That makes characters
    # "disappear" when you restart/run the app from a different folder.
    db_uri = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///ai_character.db')
    if db_uri.startswith('sqlite:///'):
        # Strip sqlite:/// and resolve relative paths against the project root.
        db_path = db_uri.replace('sqlite:///', '', 1)
        if db_path and not os.path.isabs(db_path):
            abs_db_path = os.path.abspath(os.path.join(app.root_path, db_path))
            db_uri = f"sqlite:///{abs_db_path}"
    # Flask-SQLAlchemy + SQLAlchemy on Windows generally expects forward slashes in the URL.
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri.replace('\\', '/')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    
    # Initialize extensions
    db.init_app(app)
    
    # Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.characters import characters_bp
    from routes.chat import chat_bp
    from routes.profile import profile_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(characters_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(profile_bp)
    
    # Create database tables and seed data
    with app.app_context():
        db.create_all()
        seed_default_stickers(app)
    
    return app


def seed_default_stickers(app):
    """Seed default sticker files based on what's in static/stickers/"""
    from models import Sticker
    import os
    
    sticker_dir = os.path.join(app.root_path, 'static', 'stickers')
    os.makedirs(sticker_dir, exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'uploads'), exist_ok=True)
    
    # Check if any stickers exist in folder
    if os.path.exists(sticker_dir):
        sticker_files = [f for f in os.listdir(sticker_dir) 
                        if f.lower().endswith(('.png', '.gif', '.jpg', '.jpeg', '.webp'))]
        for filename in sticker_files:
            if not Sticker.query.filter_by(filename=filename).first():
                name = os.path.splitext(filename)[0].replace('_', ' ').title()
                sticker = Sticker(name=name, filename=filename, category='general')
                db.session.add(sticker)
        db.session.commit()


# Create the app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
