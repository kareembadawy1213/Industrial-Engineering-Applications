"""
File handler utility – validates and parses uploaded CSV / Excel files
into Python dicts that the IE modules can consume.
"""
from __future__ import annotations
import os
import io
import pandas as pd
from werkzeug.utils import secure_filename
from typing import Dict, Any

ALLOWED = {'csv', 'xlsx', 'xls'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


def save_upload(file, upload_folder: str) -> str:
    """Save an uploaded file and return its path."""
    fname = secure_filename(file.filename)
    path  = os.path.join(upload_folder, fname)
    file.save(path)
    return path


def read_dataframe(path: str) -> pd.DataFrame:
    """Read a CSV or Excel file into a pandas DataFrame."""
    ext = path.rsplit('.', 1)[-1].lower()
    if ext == 'csv':
        return pd.read_csv(path)
    return pd.read_excel(path)


def parse_activities_from_df(df: pd.DataFrame) -> list:
    """
    Parse a PERT/CPM activities table.
    Expected columns: name, predecessors, duration
                      OR optimistic, most_likely, pessimistic
    """
    activities = []
    for _, row in df.iterrows():
        act: Dict[str, Any] = {'name': str(row.get('name', row.get('activity', '')))}
        preds_raw = row.get('predecessors', row.get('predecessor', ''))
        if pd.isna(preds_raw) or str(preds_raw).strip() in ('', '-', 'None'):
            act['predecessors'] = []
        else:
            act['predecessors'] = [p.strip() for p in str(preds_raw).split(',') if p.strip()]

        for col in ('duration', 'optimistic', 'most_likely', 'pessimistic'):
            if col in df.columns and not pd.isna(row.get(col)):
                act[col] = float(row[col])
        activities.append(act)
    return activities


def parse_cost_matrix_from_df(df: pd.DataFrame) -> list:
    """Parse a cost matrix (rows = workers, cols = tasks)."""
    return df.values.tolist()
