"""
Assignment Theory Module – Hungarian Method
────────────────────────────────────────────
Uses scipy.optimize.linear_sum_assignment (Jonker-Volgenant algorithm).
Supports minimisation and maximisation, square and non-square matrices.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import List, Dict, Any, Optional


def hungarian_method(
    cost_matrix: List[List[float]],
    minimize: bool = True,
    row_labels: Optional[List[str]] = None,
    col_labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Solve the assignment problem using the Hungarian algorithm.

    Parameters
    ----------
    cost_matrix : 2-D list (n_rows × n_cols)
    minimize    : True → minimise cost, False → maximise
    row_labels  : names for rows (workers / machines)
    col_labels  : names for columns (tasks / jobs)

    Returns
    -------
    dict with assignments list, total cost, annotated result matrix.
    """
    mat = np.array(cost_matrix, dtype=float)
    n_rows, n_cols = mat.shape

    if row_labels is None:
        row_labels = [f'Worker {i+1}' for i in range(n_rows)]
    if col_labels is None:
        col_labels = [f'Task {j+1}' for j in range(n_cols)]

    # For maximisation negate; scipy expects a minimisation problem
    work = -mat if not minimize else mat.copy()

    row_ind, col_ind = linear_sum_assignment(work)

    assignments = []
    total_cost  = 0.0
    for r, c in zip(row_ind, col_ind):
        if r < n_rows and c < n_cols:
            v = float(mat[r, c])
            total_cost += v
            assignments.append({
                'row':       int(r),
                'col':       int(c),
                'row_label': row_labels[r],
                'col_label': col_labels[c],
                'cost':      v,
            })

    assigned_set = {(a['row'], a['col']) for a in assignments}
    result_matrix = [
        [{'value': cost_matrix[i][j], 'assigned': (i, j) in assigned_set}
         for j in range(n_cols)]
        for i in range(n_rows)
    ]

    return {
        'assignments':   assignments,
        'total_cost':    round(total_cost, 2),
        'minimize':      minimize,
        'result_matrix': result_matrix,
        'row_labels':    row_labels,
        'col_labels':    col_labels,
        'n_rows':        n_rows,
        'n_cols':        n_cols,
    }


def analyze_assignment(data: Dict) -> Dict[str, Any]:
    """
    Main assignment analysis entry point.

    Input keys: cost_matrix, minimize (bool), row_labels, col_labels
    """
    result = hungarian_method(
        data['cost_matrix'],
        minimize=data.get('minimize', True),
        row_labels=data.get('row_labels'),
        col_labels=data.get('col_labels'),
    )

    # Naïve sequential cost for comparison (worker-i → task-i)
    matrix = data['cost_matrix']
    n = min(len(matrix), len(matrix[0]) if matrix else 0)
    naive = sum(matrix[i][i] for i in range(n))
    result['naive_cost']             = round(naive, 2)
    result['savings_vs_sequential']  = round(naive - result['total_cost'], 2)

    return result
