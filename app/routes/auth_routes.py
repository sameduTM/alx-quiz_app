"""Auth endpoints"""
from app.routes import app_views
from flask import redirect, url_for
from flask_login import logout_user, login_required


@app_views.route('/')
def home():
    """Home page"""
    from flask import render_template
    return render_template('home.html')


@app_views.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('app_views.login'))
