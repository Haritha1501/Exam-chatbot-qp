import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Basic App Config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')
    
    # DB Directory & Database URL
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Render provides DATABASE_URL starting with postgres:// - SQLAlchemy requires postgresql://
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url or f"sqlite:///{os.path.join(BASE_DIR, 'exam_bot.sqlite3')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload Config
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB max limit
    ALLOWED_EXTENSIONS = {'pdf'}

    # Gemini API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
