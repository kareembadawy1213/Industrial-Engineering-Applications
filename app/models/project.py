"""
Project model – represents a factory / engineering project saved by the user.
Each project can have multiple Analysis records attached to it.
"""
from datetime import datetime
from ..extensions import db


class Project(db.Model):
    __tablename__ = 'projects'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    company     = db.Column(db.String(200), nullable=True)
    industry    = db.Column(db.String(100), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One project → many analyses
    analyses = db.relationship(
        'Analysis', backref='project', lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self) -> dict:
        return {
            'id':             self.id,
            'name':           self.name,
            'description':    self.description,
            'company':        self.company,
            'industry':       self.industry,
            'created_at':     self.created_at.isoformat(),
            'analysis_count': len(self.analyses),
        }

    def __repr__(self) -> str:
        return f'<Project {self.name}>'
