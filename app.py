import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.DEBUG)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
app.secret_key = os.environ.get("SESSION_SECRET")
app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

with app.app_context():
    import models
    import routes
    
# app.py (Example)
# ... your imports (Flask, SQLAlchemy, os, etc.)

# Import the Vercel WSGI handler
from serverless_wsgi import handle_request
db = SQLAlchemy()
app = Flask(__name__)
# ... your config lines (SECRET_KEY, SQLALCHEMY_DATABASE_URI) ...

# Initialize db and login_manager
db.init_app(app)
login_manager.init_app(app)
# ----------------------------------------------------
# FINAL LINES for VercEL deployment:
# If you run locally, use the original app.run() lines
# If deploying to Vercel, this handles the startup:
app = VercelWSGI(app) # <--- WRAP YOUR FLASK APP

# You might need to adjust based on how your app is structured
# but VercelApp handles the WSGI connection.
def handler(event, context):
    """Entry point for the serverless function."""
    from serverless_wsgi import handle_request
    
    # We must call the handler function with the Flask application object
    return handle_request(app, event, context)