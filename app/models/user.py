from app import db
from app.utils.timezone_utils import utc_now
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    quiz_results = db.relationship('QuizResult', backref='user')

    def set_password(self, password):
        """set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """check if password matches"""
        return check_password_hash(self.password_hash, password)
