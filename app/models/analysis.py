"""
Analysis model – stores the input parameters and computed results
for every IE module run (PERT, location, cost, transport, etc.).
"""
import json
from datetime import datetime
from ..extensions import db

# Valid module identifiers
MODULE_CHOICES = ['pert', 'location', 'cost', 'transport', 'break_even', 'assignment', 'layout']


class Analysis(db.Model):
    __tablename__ = 'analyses'

    id          = db.Column(db.Integer, primary_key=True)
    project_id  = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    module      = db.Column(db.String(50), nullable=False)   # one of MODULE_CHOICES
    title       = db.Column(db.String(200), nullable=True)
    # Store as JSON text columns for portability with SQLite
    input_data  = db.Column(db.Text, nullable=False, default='{}')
    result_data = db.Column(db.Text, nullable=True,  default='{}')
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # ── helpers ─────────────────────────────────────────────────────────────
    def get_input(self) -> dict:
        try:
            return json.loads(self.input_data) if self.input_data else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_result(self) -> dict:
        try:
            return json.loads(self.result_data) if self.result_data else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_input(self, data: dict) -> None:
        self.input_data = json.dumps(data, default=str)

    def set_result(self, data: dict) -> None:
        self.result_data = json.dumps(data, default=str)

    def to_dict(self) -> dict:
        return {
            'id':          self.id,
            'project_id':  self.project_id,
            'module':      self.module,
            'title':       self.title,
            'input_data':  self.get_input(),
            'result_data': self.get_result(),
            'created_at':  self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f'<Analysis {self.module} project={self.project_id}>'
