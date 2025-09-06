"""Quiz endpoints"""
from app.routes import app_views
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.services import quiz_service
from datetime import datetime, timezone


@app_views.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    """take quiz with timing"""
    from app.services.quiz_service import get_quiz_score, start_quiz_session, get_active_quiz_session, validate_session_time

    questions = quiz_service.get_questions()
    if not questions:
        flash("No questions available at the moment.", "warning")
        return render_template('questions.html', questions=[])

    if request.method == 'POST':
        # Handle quiz submission
        form_data = request.form
        session = get_active_quiz_session()

        try:
            # Validate session is still active
            if session:
                is_valid, message = validate_session_time(session)
                if not is_valid:
                    flash(f"Quiz submission failed: {message}", "error")
                    return redirect(url_for('app_views.quiz_results', score=0, timeout=True))

            score = get_quiz_score(form_data, questions, session)
            return redirect(url_for('app_views.quiz_results', score=score))

        except TimeoutError as e:
            flash(f"Time expired! {str(e)}", "warning")
            # Calculate partial score for timeout scenario
            from app.services.quiz_service import calculate_score
            partial_score = calculate_score(form_data, questions)
            return redirect(url_for('app_views.quiz_results', score=partial_score, timeout=True))
        except Exception as e:
            flash(f"An error occurred while calculating your score: {str(e)}", "error")
            return render_template('questions.html', questions=questions)

    # GET request - start new quiz session
    try:
        # Start a new timed session (30 minutes default)
        session = start_quiz_session(time_limit_minutes=30)
        return render_template('questions_timed.html',
                             questions=questions,
                             session=session.to_dict(),
                             time_limit_seconds=session.time_limit_minutes * 60)
    except Exception as e:
        flash(f"Error starting quiz: {str(e)}", "error")
        return redirect(url_for('app_views.home'))


@app_views.route('/quiz_results', methods=["GET"])
@login_required
def quiz_results():
    """Get quiz results with timing info"""
    score = request.args.get('score', 0, type=int)
    timeout = request.args.get('timeout', False, type=bool)
    return render_template('results.html', score=score, timeout=timeout)


@app_views.route('/quiz_status', methods=["GET"])
@login_required
def quiz_status():
    """API endpoint to get current quiz session status"""
    session = quiz_service.get_active_quiz_session()

    if not session:
        return jsonify({'error': 'No active quiz session'}), 404

    # Check if session has expired
    is_valid, message = quiz_service.validate_session_time(session)
    if not is_valid:
        return jsonify({
            'expired': True,
            'message': message,
            'session': session.to_dict()
        })

    return jsonify({
        'expired': False,
        'session': session.to_dict(),
        'time_remaining': session.time_remaining_seconds
    })


@app_views.route('/quiz/abandon', methods=["POST"])
@login_required
def abandon_quiz():
    """Abandon current quiz session"""
    from app import db

    session = quiz_service.get_active_quiz_session()
    if session:
        session.abandon_session()
        db.session.commit()
        flash("Quiz session abandoned.", "info")

    return redirect(url_for('app_views.home'))
