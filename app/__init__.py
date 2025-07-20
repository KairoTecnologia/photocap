from flask import Flask
from flask_session import Session
import os

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutos
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Configuração da pasta de uploads
    app.config['UPLOAD_FOLDER'] = 'uploads'
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Inicializar extensões
    Session(app)
    
    # Registrar blueprints
    from app.routes import auth, dashboard, events, search
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(search.bp)
    
    return app 