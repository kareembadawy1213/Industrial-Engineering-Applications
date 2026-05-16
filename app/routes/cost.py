"""Cost Analysis routes."""
from flask import Blueprint, render_template, request, jsonify
from ..modules.cost_analysis import analyze_costs
from ..modules.ai_advisor    import generate_recommendations
from ..models.project        import Project
from ..models.analysis       import Analysis
from ..extensions            import db

cost_bp = Blueprint('cost', __name__)


@cost_bp.route('/')
def index():
    return render_template('cost/index.html', projects=Project.query.all())


@cost_bp.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json(silent=True) or {}
    if not data.get('alternatives'):
        return jsonify({'error': 'At least one cost alternative is required.'}), 400
    try:
        result         = analyze_costs(data)
        result['recs'] = generate_recommendations('cost', result)
        pid = data.get('project_id')
        if pid:
            a = Analysis(project_id=pid, module='cost', title='Cost Analysis')
            a.set_input(data); a.set_result(result)
            db.session.add(a); db.session.commit()
            result['analysis_id'] = a.id
        return jsonify(result)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
