"""Assignment Theory routes."""
from flask import Blueprint, render_template, request, jsonify
from ..modules.assignment import analyze_assignment
from ..modules.ai_advisor import generate_recommendations
from ..models.project     import Project
from ..models.analysis    import Analysis
from ..extensions         import db

assignment_bp = Blueprint('assignment', __name__)


@assignment_bp.route('/')
def index():
    return render_template('assignment/index.html', projects=Project.query.all())


@assignment_bp.route('/solve', methods=['POST'])
def solve():
    data = request.get_json(silent=True) or {}
    if not data.get('cost_matrix'):
        return jsonify({'error': 'cost_matrix is required.'}), 400
    try:
        result         = analyze_assignment(data)
        result['recs'] = generate_recommendations('assignment', result)
        pid = data.get('project_id')
        if pid:
            a = Analysis(project_id=pid, module='assignment', title='Assignment Analysis')
            a.set_input(data); a.set_result(result)
            db.session.add(a); db.session.commit()
            result['analysis_id'] = a.id
        return jsonify(result)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
