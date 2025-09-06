"""Quiz business logic"""
from app.models.question import Questions
from app.models.quiz_session import QuizSession
from app.utils.timezone_utils import utc_now
from flask_login import current_user


def get_questions():
    """get all questions from db"""
    from app import db
    return db.session.query(Questions).all()


def start_quiz_session(time_limit_minutes=30):
    """Start a new timed quiz session for the current user"""
    if not current_user or not current_user.is_authenticated:
        raise ValueError("User must be authenticated to start quiz")

    session = QuizSession.create_new_session(
        user_id=current_user.id,
        time_limit_minutes=time_limit_minutes
    )

    return session


def get_active_quiz_session():
    """Get the current active quiz session for the user"""
    if not current_user or not current_user.is_authenticated:
        return None

    return QuizSession.get_active_session(current_user.id)


def validate_session_time(session):
    """Check if session is still valid (not expired)"""
    if not session:
        return False, "No active quiz session"

    if session.is_expired:
        # Auto-timeout expired sessions
        from app import db
        session.timeout_session()
        db.session.commit()
        return False, "Quiz time has expired"

    return True, "Session is valid"


def get_quiz_score(form_data, results, session=None):
    """mark quiz, return score and store in db with timing validation"""
    from app import db
    from app.models.quiz_result import QuizResult

    # Validate current_user is authenticated
    if not current_user or not current_user.is_authenticated:
        raise ValueError("User must be authenticated to score quiz")

    # Validate session timing
    if session:
        is_valid, message = validate_session_time(session)
        if not is_valid:
            # Session expired - return partial score based on current answers
            counter = calculate_score(form_data, results)
            session.timeout_session(score=counter, total_questions=len(results))
            db.session.commit()
            raise TimeoutError(message)

    if not results:
        return 0

    if not form_data:
        return 0

    # Calculate score
    counter = calculate_score(form_data, results)

    # Complete the session if provided
    if session:
        session.complete_session(score=counter, total_questions=len(results))

    # Update quiz result record
    qr = db.session.query(QuizResult).filter_by(user_id=current_user.id).first()

    if qr is None:
        # Create new quiz result if none exists
        qr = QuizResult()
        qr.user_id = current_user.id
        qr.quiz_score = counter
        db.session.add(qr)
    else:
        # Update existing quiz result
        qr.quiz_score = counter

    db.session.commit()
    return counter


def calculate_score(form_data, results):
    """Calculate quiz score from form data and questions"""
    question_map = {q.id: q.answer for q in results}
    counter = 0

    for id_str, ans in form_data.items():
        try:
            # Validate that id is a valid integer
            question_id = int(id_str)

            # Check if question exists and answer matches (case-insensitive, stripped)
            if (question_id in question_map and
                question_map[question_id].strip().lower() == ans.strip().lower()):
                counter += 1
        except (ValueError, TypeError):
            # Skip invalid form data entries
            continue

    return counter


def create_questions(question, answer):
    """create questions and save to db"""
    from app import db

    # Input validation
    if not question or not answer:
        raise ValueError("Question and answer cannot be empty")

    if len(question.strip()) < 5:
        raise ValueError("Question must be at least 5 characters long")

    if len(answer.strip()) < 1:
        raise ValueError("Answer cannot be empty")

    q = Questions()
    q.question = question.strip()
    q.answer = answer.strip()
    db.session.add(q)
    db.session.commit()


def edit_question(question_id, new_question=None, new_answer=None):
    """edit question"""
    from app import db

    if not question_id:
        raise ValueError("Question ID is required")

    question = db.session.query(Questions).filter_by(id=question_id).first()
    if not question:
        raise ValueError("Question not found")

    if new_question:
        if len(new_question.strip()) < 5:
            raise ValueError("Question must be at least 5 characters long")
        question.question = new_question.strip()

    if new_answer:
        if len(new_answer.strip()) < 1:
            raise ValueError("Answer cannot be empty")
        question.answer = new_answer.strip()

    db.session.commit()
    return question


def delete_question(question_id):
    """deletes question"""
    from app import db

    if not question_id:
        raise ValueError("Question ID is required")

    question = db.session.query(Questions).filter_by(id=question_id).first()
    if not question:
        raise ValueError("Question not found")

    db.session.delete(question)
    db.session.commit()
    return True
