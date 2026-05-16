"""Break-Even Analysis routes."""
from flask import Blueprint, render_template, request, jsonify
from ..modules.break_even import analyze_break_even
from ..modules.ai_advisor import generate_recommendations
from ..models.project     import Project
from ..models.analysis    import Analysis
from ..extensions         import db

break_even_bp = Blueprint('break_even', __name__)


@break_even_bp.route('/')
def index():
    return render_template('break_even/index.html', projects=Project.query.all())


@break_even_bp.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json(silent=True) or {}
    required = ('fixed_cost', 'variable_cost_per_unit', 'selling_price')
    if not all(k in data for k in required):
        return jsonify({'error': 'fixed_cost, variable_cost_per_unit, and selling_price are required.'}), 400
    try:
        result         = analyze_break_even(data)
        if 'error' in result:
            return jsonify(result), 400
        result['recs'] = generate_recommendations('break_even', result)
        pid = data.get('project_id')
        if pid:
            a = Analysis(project_id=pid, module='break_even', title='Break-Even Analysis')
            a.set_input(data); a.set_result(result)
            db.session.add(a); db.session.commit()
            result['analysis_id'] = a.id
        return jsonify(result)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
