import os
import logging
from dotenv import load_dotenv

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.DEBUG)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

# 1. Initialize Extensions Globally (without passing the app)
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    """Application factory function to create and configure the Flask app."""
    
    app = Flask(__name__)

    # 2. APPLICATION CONFIGURATION (Reads Environment Variables with defaults)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", 
        "sqlite:///finance.db"  # Default to SQLite for local development
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", 
        "dev-secret-key-please-change-in-production"  # Default for development
    )
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # CSRF Protection (Flask-WTF handles this automatically with SECRET_KEY)
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["WTF_CSRF_TIME_LIMIT"] = None  # No time limit for CSRF tokens
    
    # 3. Apply Middleware and Initialize Extensions
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = "login"
    login_manager.login_message_category = "info"

    # 4. Import and register routes within app context
    with app.app_context():
        import models  # Import models to register them with SQLAlchemy
        from routes import register_routes
        register_routes(app)  # Register all routes
        
        # Create all database tables (for development only)
        # In production, use Flask-Migrate instead
        db.create_all()
    
    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)