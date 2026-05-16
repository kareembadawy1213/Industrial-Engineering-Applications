"""
Application factory for the IE Platform Flask app.
All blueprints and extensions are registered here.
"""
import os
from flask import Flask
from config import config
from .extensions import db, migrate


def create_app(config_name: str = 'default') -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # ── Ensure required directories exist ──────────────────────────────────
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'instance'), exist_ok=True)

    # ── Initialize extensions ───────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)

    # Ensure the database tables exist when the app starts under gunicorn
    with app.app_context():
        db.create_all()

    # ── Register blueprints ─────────────────────────────────────────────────
    from .routes.main import main_bp
    from .routes.pert import pert_bp
    from .routes.location import location_bp
    from .routes.cost import cost_bp
    from .routes.transport import transport_bp
    from .routes.break_even import break_even_bp
    from .routes.assignment import assignment_bp
    from .routes.layout import layout_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(pert_bp,        url_prefix='/pert')
    app.register_blueprint(location_bp,    url_prefix='/location')
    app.register_blueprint(cost_bp,        url_prefix='/cost')
    app.register_blueprint(transport_bp,   url_prefix='/transport')
    app.register_blueprint(break_even_bp,  url_prefix='/break-even')
    app.register_blueprint(assignment_bp,  url_prefix='/assignment')
    app.register_blueprint(layout_bp,      url_prefix='/layout')

    return app
