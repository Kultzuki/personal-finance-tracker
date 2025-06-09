import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(test_config=None):
    """Application factory function"""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)

    # Set up login manager
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Register blueprints
    from app.routes import auth, charts, goals, main, transactions

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(goals.bp)
    app.register_blueprint(charts.bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
