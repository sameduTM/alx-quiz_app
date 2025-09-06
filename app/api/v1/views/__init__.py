from flask import Blueprint

api_bp = Blueprint('api_bp', __name__)

from app.api.v1.views import questions
from app.api.v1.views import session
