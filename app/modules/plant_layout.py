"""
Plant Layout Optimization Module
──────────────────────────────────
Two analysis methods:
  1. REL Chart  – closeness relationship analysis (A/E/I/O/U/X ratings)
  2. From-To Chart – flow × distance movement cost analysis

Also generates a simple grid layout visualisation.
"""
from __future__ import annotations

import math
from typing import List, Dict, Any, Optional

# Closeness relationship values (higher = more desirable to be adjacent)
REL_VALUES = {'A': 6, 'E': 5, 'I': 4, 'O': 3, 'U': 2, 'X': 1}
REL_LABELS = {
    'A': 'Absolutely Necessary',
    'E': 'Especially Important',
    'I': 'Important',
    'O': 'Ordinary Closeness',
    'U': 'Unimportant',
    'X': 'Undesirable',
}


# ── REL Chart analysis ───────────────────────────────────────────────────────

def rel_chart_analysis(departments: List[str], rel_matrix: Dict) -> Dict[str, Any]:
    """
    Analyse department closeness ratings.

    rel_matrix : { dept_A: { dept_B: 'A'/'E'/'I'/'O'/'U'/'X' } }
    """
    pairs = []
    for i, d1 in enumerate(departments):
        for j, d2 in enumerate(departments):
            if i >= j:
                continue
            rel = (rel_matrix.get(d1, {}).get(d2)
                   or rel_matrix.get(d2, {}).get(d1, 'U'))
            pairs.append({
                'dept1':        d1,
                'dept2':        d2,
                'relationship': rel,
                'value':        REL_VALUES.get(rel, 2),
                'label':        REL_LABELS.get(rel, ''),
            })

    pairs.sort(key=lambda x: x['value'], reverse=True)

    summary = {k: 0 for k in REL_VALUES}
    for p in pairs:
        summary[p['relationship']] = summary.get(p['relationship'], 0) + 1

    # Adjacency score per department
    dept_scores: Dict[str, float] = {d: 0.0 for d in departments}
    for p in pairs:
        dept_scores[p['dept1']] += p['value']
        dept_scores[p['dept2']] += p['value']

    ranked_depts = sorted(dept_scores.items(), key=lambda x: x[1], reverse=True)

    return {
        'pairs':        pairs,
        'summary':      summary,
        'departments':  departments,
        'dept_scores':  dept_scores,
        'ranked_depts': ranked_depts,
    }


# ── From-To Chart analysis ───────────────────────────────────────────────────

def from_to_chart_analysis(
    departments: List[str],
    flow_matrix: List[List[float]],
    distance_matrix: List[List[float]],
) -> Dict[str, Any]:
    """
    Compute total movement cost = Σ (flow × distance).

    flow_matrix     : trips/loads per period between departments
    distance_matrix : physical distances between departments
    """
    n = len(departments)
    total_cost = 0.0
    movements  = []

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            f = flow_matrix[i][j] if i < len(flow_matrix) and j < len(flow_matrix[i]) else 0
            dist = distance_matrix[i][j] if i < len(distance_matrix) and j < len(distance_matrix[i]) else 1
            if f > 0:
                cost = f * dist
                total_cost += cost
                movements.append({
                    'from':     departments[i],
                    'to':       departments[j],
                    'flow':     f,
                    'distance': dist,
                    'cost':     round(cost, 2),
                })

    movements.sort(key=lambda x: x['cost'], reverse=True)

    dept_costs: Dict[str, float] = {d: 0.0 for d in departments}
    for m in movements:
        dept_costs[m['from']] = dept_costs.get(m['from'], 0) + m['cost']

    return {
        'total_cost':     round(total_cost, 2),
        'movements':      movements,
        'dept_costs':     {k: round(v, 2) for k, v in dept_costs.items()},
        'departments':    departments,
    }


# ── Grid layout generator ────────────────────────────────────────────────────

def _make_grid(departments: List[str]) -> Dict:
    n    = len(departments)
    cols = max(2, math.ceil(math.sqrt(n)))
    rows = math.ceil(n / cols)
    grid = [[None] * cols for _ in range(rows)]
    for idx, dept in enumerate(departments):
        grid[idx // cols][idx % cols] = dept
    return {'grid': grid, 'rows': rows, 'cols': cols}


# ── Main entry point ─────────────────────────────────────────────────────────

def analyze_plant_layout(data: Dict) -> Dict[str, Any]:
    """
    Run REL chart and/or From-To analysis depending on supplied data.

    Required input key: departments (list of strings)
    Optional:
        rel_matrix    → triggers REL chart analysis
        flow_matrix + distance_matrix → triggers From-To analysis
    """
    departments = data['departments']
    results: Dict[str, Any] = {'departments': departments}

    if data.get('rel_matrix'):
        results['rel_chart'] = rel_chart_analysis(departments, data['rel_matrix'])

    if data.get('flow_matrix') and data.get('distance_matrix'):
        results['from_to'] = from_to_chart_analysis(
            departments, data['flow_matrix'], data['distance_matrix']
        )

    results.update(_make_grid(departments))
    return results
