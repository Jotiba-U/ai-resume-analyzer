import os
from flask import Flask
from dotenv import load_dotenv
from .routes import main
from .user_routes import user
from .admin_routes import admin
from .utils import init_db

load_dotenv()

def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-secret-key")
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'txt'}

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db()

    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(user)

    return app
