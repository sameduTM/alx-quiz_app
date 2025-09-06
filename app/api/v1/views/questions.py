"""Get all the questions"""
from app.services import quiz_service
from app.api.v1.views import api_bp
from flask import Response
from flask_login import login_required
from collections import OrderedDict
import json


@api_bp.route('/get_questions')
@login_required
def get_questions():
    questions = quiz_service.get_questions()
    question_map = [
        OrderedDict([
            ("_id", q.id),
            ("question", q.question)
        ])
        for q in questions
    ]
    return Response(json.dumps(question_map, indent=2), mimetype='application/json')
