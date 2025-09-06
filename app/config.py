import os
import secrets


class Config:
    """Base Config class"""

    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    # database settings
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API settings
    API_KEY = os.environ.get('API_KEY') or secrets.token_hex(32)

    # CSRF Protection (optional - currently disabled)
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'False').lower() == 'true'
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or secrets.token_hex(32)
