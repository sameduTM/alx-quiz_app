import os
from app.config import Config
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    from app.routes import app_views
    from app.api.v1.views import api_bp
    from app.models.user import User

    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Set login view
    login_manager.login_view = "app_views.login"  # type: ignore

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Debug mode should be set via environment variable in production
    app.debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Register blueprints
    app.register_blueprint(app_views)
    app.register_blueprint(api_bp)

    return app
