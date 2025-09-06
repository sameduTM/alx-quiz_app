"""User management logic"""
from app import db
from werkzeug.security import check_password_hash


def create_user(form_data):
    """creates User model"""
    from app.models.user import User

    user = User()

    user.first_name = form_data.get('first_name')
    user.last_name = form_data.get('last_name')
    user.user_name = form_data.get('user_name')
    # Use set_password method which handles password hashing
    user.set_password(form_data.get('password'))

    db.session.add(user)
    db.session.commit()

def get_user(username, password):
    """get user given username and password"""
    from app.models.user import User
    user = db.session.query(User).filter_by(user_name=username).first()
    if user and check_password_hash(user.password_hash, password):
        return user
