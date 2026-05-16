"""
Flask extensions initialized here so they can be imported by both
app/__init__.py and models without circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
