"""
PERT / CPM routes.
GET  /pert/          → input form
POST /pert/analyze   → JSON API (receives activities, returns results)
GET  /pert/result/<id> → saved result view
"""
from flask import Blueprint, render_template, request, jsonify
from ..modules.pert_cpm  import analyze_pert_cpm
from ..modules.ai_advisor import generate_recommendations
from ..models.project    import Project
from ..models.analysis   import Analysis
from ..extensions        import db

pert_bp = Blueprint('pert', __name__)


@pert_bp.route('/')
def index():
    projects = Project.query.order_by(Project.name).all()
    return render_template('pert/index.html', projects=projects)


@pert_bp.route('/analyze', methods=['POST'])
def analyze():
    data       = request.get_json(silent=True) or {}
    activities = data.get('activities', [])
    use_pert   = bool(data.get('use_pert', False))
    project_id = data.get('project_id')

    if not activities:
        return jsonify({'error': 'No activities provided.'}), 400

    try:
        result          = analyze_pert_cpm(activities, use_pert)
        result['recs']  = generate_recommendations('pert', result)

        if project_id:
            a = Analysis(project_id=project_id, module='pert',
                         title=f"PERT/CPM – {len(activities)} activities")
            a.set_input({'activities': activities, 'use_pert': use_pert})
            a.set_result(result)
            db.session.add(a)
            db.session.commit()
            result['analysis_id'] = a.id

        return jsonify(result)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@pert_bp.route('/result/<int:aid>')
def result(aid: int):
    analysis = Analysis.query.get_or_404(aid)
    return render_template('pert/result.html', analysis=analysis,
                           result=analysis.get_result())
