"""Session management API endpoints"""
from app.services import quiz_service
from app.api.v1.views import api_bp
from flask import jsonify, request
from flask_login import login_required, current_user
from app.utils.timezone_utils import utc_now


@api_bp.route('/session/status', methods=['GET'])
@login_required
def get_session_status():
    """Get current quiz session status"""
    try:
        session = quiz_service.get_active_quiz_session()

        if not session:
            return jsonify({
                'success': False,
                'error': 'No active quiz session found',
                'session': None
            }), 404

        # Check if session has expired
        is_valid, message = quiz_service.validate_session_time(session)

        return jsonify({
            'success': True,
            'session': session.to_dict(),
            'is_valid': is_valid,
            'message': message,
            'server_time': utc_now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get session status: {str(e)}'
        }), 500


@api_bp.route('/session/heartbeat', methods=['POST'])
@login_required
def session_heartbeat():
    """Keep session alive and sync time with server"""
    try:
        session = quiz_service.get_active_quiz_session()

        if not session:
            return jsonify({
                'success': False,
                'error': 'No active quiz session'
            }), 404

        # Validate session is still active
        is_valid, message = quiz_service.validate_session_time(session)

        if not is_valid:
            return jsonify({
                'success': False,
                'expired': True,
                'message': message,
                'session': session.to_dict()
            })

        return jsonify({
            'success': True,
            'expired': False,
            'time_remaining': session.time_remaining_seconds,
            'server_time': utc_now().isoformat(),
            'session': session.to_dict()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Heartbeat failed: {str(e)}'
        }), 500


@api_bp.route('/session/create', methods=['POST'])
@login_required
def create_session():
    """Create a new quiz session"""
    try:
        data = request.get_json() or {}
        time_limit = data.get('time_limit_minutes', 30)

        # Validate time limit
        if not isinstance(time_limit, int) or time_limit < 1 or time_limit > 180:
            return jsonify({
                'success': False,
                'error': 'Time limit must be between 1 and 180 minutes'
            }), 400

        session = quiz_service.start_quiz_session(time_limit_minutes=time_limit)

        return jsonify({
            'success': True,
            'message': 'Quiz session created successfully',
            'session': session.to_dict()
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create session: {str(e)}'
        }), 500


@api_bp.route('/session/abandon', methods=['POST'])
@login_required
def abandon_session():
    """Abandon current quiz session"""
    try:
        from app import db

        session = quiz_service.get_active_quiz_session()

        if not session:
            return jsonify({
                'success': False,
                'error': 'No active quiz session to abandon'
            }), 404

        session.abandon_session()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Quiz session abandoned successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to abandon session: {str(e)}'
        }), 500


@api_bp.route('/session/extend', methods=['POST'])
@login_required
def extend_session():
    """Extend current quiz session time (admin only feature)"""
    try:
        from app import db

        data = request.get_json() or {}
        additional_minutes = data.get('additional_minutes', 5)

        # Validate extension time
        if not isinstance(additional_minutes, int) or additional_minutes < 1 or additional_minutes > 30:
            return jsonify({
                'success': False,
                'error': 'Additional time must be between 1 and 30 minutes'
            }), 400

        session = quiz_service.get_active_quiz_session()

        if not session:
            return jsonify({
                'success': False,
                'error': 'No active quiz session to extend'
            }), 404

        # Extend the session
        session.time_limit_minutes += additional_minutes
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Session extended by {additional_minutes} minutes',
            'session': session.to_dict()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to extend session: {str(e)}'
        }), 500
