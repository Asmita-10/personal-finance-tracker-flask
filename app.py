import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
# Correct import for the serverless handler
from serverless_wsgi import handle_request 

logging.basicConfig(level=logging.DEBUG)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

# 1. Initialize Extensions Globally (without passing the app)
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()


def create_app():
    """Application factory function to create and configure the Flask app."""
    
    app = Flask(__name__)

    # 2. APPLICATION CONFIGURATION (Reads Environment Variables)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") # Use SECRET_KEY for all Flask security
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # 3. Apply Middleware and Initialize Extensions
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = "login"
    login_manager.login_message_category = "info"

    # 4. Import Routes (MUST BE DONE AFTER APP AND EXTENSIONS ARE DEFINED)
    # This must be a simple import call. routes.py should not execute code that relies on the app context immediately.
    import routes
    
    return app

# ----------------------------------------------------
# SERVERLESS ENTRY POINT SETUP
# ----------------------------------------------------

# Create the application instance once at the global level
app = create_app()

# Delete the incorrect and confusing wrapper
# app = VercelWSGI(app) <--- DELETE THIS LINE

def handler(event, context):
    """
    Primary entry point for the Vercel Serverless Function.
    The 'serverless_wsgi' package executes the application using this handler.
    """
    # Call the imported handle_request function with our Flask app instance
    return handle_request(app, event, context)

with app.app_context():
    # Safely import the modules
    import routes
    import models
    db.create_all()