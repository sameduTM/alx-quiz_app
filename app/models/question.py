from app import db
from app.utils.timezone_utils import utc_now


class Questions(db.Model):
    """Model for quiz questions"""
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False)
    answer = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
