from flask import Flask, render_template
from flask_login import LoginManager
from models import db, User
from config import Config
from routes.auth import auth_bp
from routes.user import user_bp
from routes.tutor import tutor_bp
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'abc123' 
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(tutor_bp, url_prefix='/tutor')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint to verify system status"""
    health = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "app": "ok",
            "database": "unknown",
            "llm_api": "unknown"
        }
    }
    
    # Check database
    try:
        db.session.execute('SELECT 1')
        health["components"]["database"] = "ok"
    except Exception as e:
        health["components"]["database"] = "error"
        health["status"] = "degraded"
    
    # Check LLM API
    from services.llm_service import LLMService
    llm = LLMService()
    try:
        response = llm._call_llm("Hello, are you working?")
        if response:
            health["components"]["llm_api"] = "ok"
        else:
            health["components"]["llm_api"] = "degraded"
            health["status"] = "degraded"
    except Exception as e:
        health["components"]["llm_api"] = "error"
        health["status"] = "degraded"
    
    return jsonify(health)
# Create the database tables
with app.app_context():
    if not os.path.exists(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')):
        db.create_all()
        
        # Create initial skills if needed
        from models import Skill
        if Skill.query.count() == 0:
            initial_skills = [
                Skill(name='Python', description='Python programming language'),
                Skill(name='JavaScript', description='JavaScript programming language'),
                Skill(name='Data Science', description='Data analysis and machine learning'),
                Skill(name='Web Development', description='HTML, CSS, and web frameworks')
            ]
            db.session.add_all(initial_skills)
            db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)