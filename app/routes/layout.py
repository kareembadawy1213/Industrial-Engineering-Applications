"""Plant Layout routes."""
from flask import Blueprint, render_template, request, jsonify
from ..modules.plant_layout import analyze_plant_layout
from ..modules.ai_advisor   import generate_recommendations
from ..models.project       import Project
from ..models.analysis      import Analysis
from ..extensions           import db

layout_bp = Blueprint('layout', __name__)


@layout_bp.route('/')
def index():
    return render_template('layout/index.html', projects=Project.query.all())


@layout_bp.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json(silent=True) or {}
    if not data.get('departments'):
        return jsonify({'error': 'At least one department is required.'}), 400
    try:
        result         = analyze_plant_layout(data)
        result['recs'] = generate_recommendations('layout', result)
        pid = data.get('project_id')
        if pid:
            a = Analysis(project_id=pid, module='layout', title='Plant Layout Analysis')
            a.set_input(data); a.set_result(result)
            db.session.add(a); db.session.commit()
            result['analysis_id'] = a.id
        return jsonify(result)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
