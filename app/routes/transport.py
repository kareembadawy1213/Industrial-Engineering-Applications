"""Transportation Problem routes."""
from flask import Blueprint, render_template, request, jsonify
from ..modules.transportation import solve_transportation
from ..modules.ai_advisor     import generate_recommendations
from ..models.project         import Project
from ..models.analysis        import Analysis
from ..extensions             import db

transport_bp = Blueprint('transport', __name__)


@transport_bp.route('/')
def index():
    return render_template('transport/index.html', projects=Project.query.all())


@transport_bp.route('/solve', methods=['POST'])
def solve():
    data = request.get_json(silent=True) or {}
    if not data.get('supply') or not data.get('demand') or not data.get('costs'):
        return jsonify({'error': 'supply, demand, and costs are all required.'}), 400
    try:
        result         = solve_transportation(data)
        result['recs'] = generate_recommendations('transport', result)
        pid = data.get('project_id')
        if pid:
            a = Analysis(project_id=pid, module='transport', title='Transportation Analysis')
            a.set_input(data); a.set_result(result)
            db.session.add(a); db.session.commit()
            result['analysis_id'] = a.id
        return jsonify(result)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
