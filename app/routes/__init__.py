from flask import Blueprint

app_views = Blueprint('app_views', __name__)

from app.routes import quiz_routes
from app.routes import user_routes
from app.routes import auth_routes
