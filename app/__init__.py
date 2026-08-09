from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.database import init_db
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for frontend requests (e.g. from Vercel)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize DB (creates tables on SQLite or PostgreSQL automatically)
    init_db(app)

    # Register Blueprints
    from app.routes.upload import upload_bp
    from app.routes.analysis import analysis_bp
    from app.routes.chat import chat_bp
    
    app.register_blueprint(upload_bp, url_prefix='/api/v1')
    app.register_blueprint(analysis_bp, url_prefix='/api/v1')
    app.register_blueprint(chat_bp, url_prefix='/api/v1')

    # Serve Frontend
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        return app.send_static_file(path)

    return app
