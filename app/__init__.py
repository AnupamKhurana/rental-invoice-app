"""Application factory and initialization."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    # Import and register blueprints
    from app.routes import (
        main_bp, tenant_bp, landlord_bp, 
        property_bp, lease_bp, invoice_bp, auth_bp
    )
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tenant_bp, url_prefix='/tenant')
    app.register_blueprint(landlord_bp, url_prefix='/landlord')
    app.register_blueprint(property_bp, url_prefix='/property')
    app.register_blueprint(lease_bp, url_prefix='/lease')
    app.register_blueprint(invoice_bp, url_prefix='/invoice')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Flask-Login user loader (must be registered after app is created)
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Landlord
        return Landlord.query.get(int(user_id))
    
    return app
