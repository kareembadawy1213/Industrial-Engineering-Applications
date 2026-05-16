"""
Main routes – landing page, dashboard, project management, and global API stats.
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ..models.project  import Project
from ..models.analysis import Analysis
from ..extensions import db
from sqlalchemy import func

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/dashboard')
def dashboard():
    projects        = Project.query.order_by(Project.created_at.desc()).limit(6).all()
    total_projects  = Project.query.count()
    total_analyses  = Analysis.query.count()
    module_stats    = db.session.query(
        Analysis.module, func.count(Analysis.id).label('cnt')
    ).group_by(Analysis.module).all()

    return render_template(
        'dashboard.html',
        projects=projects,
        total_projects=total_projects,
        total_analyses=total_analyses,
        module_stats=module_stats,
    )


# ── Project CRUD ──────────────────────────────────────────────────────────────

@main_bp.route('/projects', methods=['GET'])
def projects():
    all_projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=all_projects)


@main_bp.route('/projects/new', methods=['POST'])
def new_project():
    name        = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    company     = request.form.get('company', '').strip()
    industry    = request.form.get('industry', '').strip()

    if not name:
        flash('Project name is required.', 'danger')
        return redirect(url_for('main.projects'))

    proj = Project(name=name, description=description, company=company, industry=industry)
    db.session.add(proj)
    db.session.commit()
    flash(f'Project "{name}" created successfully.', 'success')
    return redirect(url_for('main.projects'))


@main_bp.route('/projects/<int:pid>/delete', methods=['POST'])
def delete_project(pid: int):
    proj = Project.query.get_or_404(pid)
    db.session.delete(proj)
    db.session.commit()
    flash(f'Project "{proj.name}" deleted.', 'warning')
    return redirect(url_for('main.projects'))


# ── API endpoints ─────────────────────────────────────────────────────────────

@main_bp.route('/api/stats')
def api_stats():
    module_stats = db.session.query(
        Analysis.module, func.count(Analysis.id).label('cnt')
    ).group_by(Analysis.module).all()
    return jsonify({
        'total_projects':  Project.query.count(),
        'total_analyses':  Analysis.query.count(),
        'module_stats':    {m: c for m, c in module_stats},
    })


@main_bp.route('/api/projects')
def api_projects():
    return jsonify([p.to_dict() for p in Project.query.order_by(Project.created_at.desc()).all()])
