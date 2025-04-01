import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///learning_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'pdf'}
    LLM_API_URL = os.environ.get('LLM_API_URL') or 'http://localhost:11434/api/generate'
    LLM_MODEL = os.environ.get('LLM_MODEL') or 'llama3.2:3b'
    LLM_MAX_TOKENS = os.environ.get('LLM_MAX_TOKENS') or 2048
    LLM_TEMPERATURE = os.environ.get('LLM_TEMPERATURE') or 0.7