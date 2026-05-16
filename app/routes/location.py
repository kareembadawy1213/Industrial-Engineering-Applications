"""Plant Location routes."""
from flask import Blueprint, render_template, request, jsonify
from ..modules.plant_location import analyze_plant_location
from ..modules.ai_advisor     import generate_recommendations
from ..models.project         import Project
from ..models.analysis        import Analysis
from ..extensions             import db

location_bp = Blueprint('location', __name__)


@location_bp.route('/')
def index():
    return render_template('location/index.html', projects=Project.query.all())


@location_bp.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json(silent=True) or {}
    if not data.get('locations') and not data.get('cost_locations'):
        return jsonify({'error': 'Location data is required.'}), 400
    try:
        result         = analyze_plant_location(data)
        result['recs'] = generate_recommendations('location', result)
        pid = data.get('project_id')
        if pid:
            a = Analysis(project_id=pid, module='location', title='Plant Location Analysis')
            a.set_input(data); a.set_result(result)
            db.session.add(a); db.session.commit()
            result['analysis_id'] = a.id
        return jsonify(result)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
