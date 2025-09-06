from app import db
from app.utils.timezone_utils import utc_now, ensure_utc, seconds_between
from datetime import timedelta
from sqlalchemy import Enum


class QuizSession(db.Model):
    """Model for tracking quiz sessions with timing"""
    __tablename__ = 'quiz_session'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=utc_now, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    time_limit_minutes = db.Column(db.Integer, default=30, nullable=False)  # Default 30 minutes
    status = db.Column(
        Enum('active', 'completed', 'timeout', 'abandoned', name='session_status'),
        default='active',
        nullable=False
    )
    score = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)

    # Relationships
    user = db.relationship('User', backref=db.backref('quiz_sessions', lazy=True))

    def __init__(self, user_id, time_limit_minutes=30):
        self.user_id = user_id
        self.time_limit_minutes = time_limit_minutes
        self.start_time = utc_now()
        self.status = 'active'

    @property
    def expiry_time(self):
        """Calculate when the quiz expires"""
        if self.start_time is None:
            return None
        start_time_aware = ensure_utc(self.start_time)
        if start_time_aware is None:
            return None
        return start_time_aware + timedelta(minutes=self.time_limit_minutes)

    @property
    def time_remaining_seconds(self):
        """Get remaining time in seconds"""
        if self.status != 'active':
            return 0

        now = utc_now()
        expiry = self.expiry_time

        if expiry is None or now >= expiry:
            return 0

        return int((expiry - now).total_seconds())

    @property
    def time_elapsed_seconds(self):
        """Get elapsed time in seconds"""
        now = utc_now()
        return seconds_between(self.start_time, now)

    @property
    def is_expired(self):
        """Check if quiz session has expired"""
        if self.status != 'active':
            return True

        expiry = self.expiry_time
        return expiry is not None and utc_now() >= expiry

    @property
    def progress_percentage(self):
        """Calculate progress as percentage (time elapsed / total time)"""
        elapsed = self.time_elapsed_seconds
        total_time = self.time_limit_minutes * 60

        if total_time == 0:
            return 100

        progress = (elapsed / total_time) * 100
        return min(100, max(0, progress))

    def complete_session(self, score=0, total_questions=0):
        """Mark session as completed"""
        self.end_time = utc_now()
        self.status = 'completed'
        self.score = score
        self.total_questions = total_questions

    def timeout_session(self, score=0, total_questions=0):
        """Mark session as timed out"""
        self.end_time = utc_now()
        self.status = 'timeout'
        self.score = score
        self.total_questions = total_questions

    def abandon_session(self):
        """Mark session as abandoned"""
        self.end_time = utc_now()
        self.status = 'abandoned'

    @classmethod
    def get_active_session(cls, user_id):
        """Get active quiz session for user"""
        return cls.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()

    @classmethod
    def create_new_session(cls, user_id, time_limit_minutes=30):
        """Create a new quiz session for user"""
        from app import db

        # End any existing active sessions
        active_session = cls.get_active_session(user_id)
        if active_session:
            active_session.abandon_session()
            db.session.commit()

        # Create new session
        session = cls(user_id=user_id, time_limit_minutes=time_limit_minutes)
        db.session.add(session)
        db.session.commit()

        return session

    def to_dict(self):
        """Convert session to dictionary for JSON responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'time_limit_minutes': self.time_limit_minutes,
            'status': self.status,
            'score': self.score,
            'total_questions': self.total_questions,
            'time_remaining_seconds': self.time_remaining_seconds,
            'time_elapsed_seconds': self.time_elapsed_seconds,
            'is_expired': self.is_expired,
            'progress_percentage': self.progress_percentage,
            'expiry_time': self.expiry_time.isoformat() if self.expiry_time else None
        }

    def __repr__(self):
        return f'<QuizSession {self.id}: User {self.user_id}, Status: {self.status}>'
