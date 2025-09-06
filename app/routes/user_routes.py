"""User endpoints"""
from app.models.user import User
from app.routes import app_views
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user
from werkzeug.security import check_password_hash


@app_views.route('/register', methods=["GET", "POST"], strict_slashes=False)
def register():
    """register user"""
    from app.services.user_service import create_user
    from app import db

    if request.method == "POST":
        # Input validation
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        user_name = request.form.get('user_name', '').strip()
        password = request.form.get('password', '')

        # Validate required fields
        if not all([first_name, last_name, user_name, password]):
            flash("All fields are required", "error")
            return render_template('register.html')

        # Check if username already exists
        existing_user = db.session.query(User).filter_by(user_name=user_name).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return render_template('register.html')

        # Validate password length
        if len(password) < 6:
            flash("Password must be at least 6 characters long", "error")
            return render_template('register.html')

        try:
            create_user(request.form)
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('app_views.login'))
        except Exception:
            flash("An error occurred during registration. Please try again.", "error")
            return render_template('register.html')

    return render_template('register.html')


@app_views.route('/login', methods=["GET", "POST"], strict_slashes=False)
def login():
    """login user"""
    from app import db

    if request.method == 'POST':
        username = request.form.get('user_name', '').strip()
        password = request.form.get('password', '')

        # Input validation
        if not username or not password:
            flash("Username and password are required", "error")
            return render_template('login.html')

        try:
            user = db.session.query(User).filter_by(user_name=username).first()
            if user and check_password_hash(user.password_hash, str(password)):
                login_user(user)
                flash(f"Welcome back, {user.first_name}!", "success")
                return redirect(url_for('app_views.quiz'))
            else:
                flash("Invalid username or password", "error")
        except Exception:
            flash("An error occurred during login. Please try again.", "error")

    return render_template('login.html')
