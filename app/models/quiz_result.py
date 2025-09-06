from app import db
from app.utils.timezone_utils import utc_now


class QuizResult(db.Model):
    """Quiz Results Model"""
    __tablename__ = 'quizresult'

    id = db.Column(db.Integer, primary_key=True)
    quiz_score = db.Column(db.Integer, default=0.0)
    created_at = db.Column(db.DateTime, default=utc_now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
