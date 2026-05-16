"""
AI Advisor Module
──────────────────
Rule-based + heuristic intelligence that examines analysis results and
returns actionable recommendations displayed on the frontend.

Each recommendation is a dict:
  { type: 'success'|'info'|'warning'|'danger',
    title: str, message: str, priority: 'high'|'medium'|'low' }
"""
from __future__ import annotations
import numpy as np
from typing import List, Dict, Any


# ── PERT / CPM ────────────────────────────────────────────────────────────────

def _pert_recs(result: Dict) -> List[Dict]:
    recs = []
    table    = result.get('table', [])
    cp       = result.get('critical_path', [])
    duration = result.get('project_duration', 1) or 1

    if len(cp) > 6:
        recs.append({'type': 'warning', 'priority': 'high',
                     'title': 'Complex Critical Path',
                     'message': f'The critical path spans {len(cp)} activities. '
                                'Apply resource levelling or fast-tracking to reduce schedule risk.'})

    high_slack = [a for a in table if a.get('slack', 0) > duration * 0.25]
    if high_slack:
        names = ', '.join(a['name'] for a in high_slack[:3])
        recs.append({'type': 'info', 'priority': 'medium',
                     'title': 'Resource Reallocation Opportunity',
                     'message': f'Activities {names} have >25% slack. '
                                'Shift their resources to critical-path activities to accelerate the project.'})

    if result.get('use_pert'):
        stats = result.get('pert_stats', {})
        std   = stats.get('project_std_dev', 0)
        cv    = (std / duration) * 100
        if cv > 30:
            recs.append({'type': 'danger', 'priority': 'high',
                         'title': 'High Schedule Uncertainty',
                         'message': f'Coefficient of Variation = {cv:.1f}%. '
                                    'Add a 20%+ contingency buffer and identify risk-mitigation actions.'})
        elif cv > 15:
            recs.append({'type': 'warning', 'priority': 'medium',
                         'title': 'Moderate Schedule Risk',
                         'message': f'CV = {cv:.1f}%. A 10% time contingency is advisable.'})

    if not recs:
        recs.append({'type': 'success', 'priority': 'low',
                     'title': 'Schedule Looks Healthy',
                     'message': 'No major risk flags detected. Monitor critical-path activities throughout execution.'})
    return recs


# ── Plant Location ────────────────────────────────────────────────────────────

def _location_recs(result: Dict) -> List[Dict]:
    recs = []

    wfr = result.get('weighted_factor_rating', {})
    if wfr:
        ranked = wfr.get('ranked', [])
        if len(ranked) >= 2:
            diff = ranked[0][1] - ranked[1][1]
            if diff < 5:
                recs.append({'type': 'warning', 'priority': 'high',
                             'title': 'Very Close Scores',
                             'message': f'{ranked[0][0]} leads by only {diff:.1f} points. '
                                        'Consider a site visit or additional qualitative factors before deciding.'})
            else:
                recs.append({'type': 'success', 'priority': 'low',
                             'title': f'Clear Recommendation: {ranked[0][0]}',
                             'message': f'{ranked[0][0]} outscores the next best by {diff:.1f} points.'})

    cc = result.get('cost_comparison', {})
    if cc:
        if cc.get('crossovers'):
            recs.append({'type': 'info', 'priority': 'medium',
                         'title': 'Cost Crossover Points Exist',
                         'message': 'The cost ranking changes at certain production volumes. '
                                    'Verify your target volume before finalising the location.'})
        recs.append({'type': 'info', 'priority': 'medium',
                     'title': f"Cost Winner: {cc.get('best_location', '—')}",
                     'message': f"{cc.get('best_location')} has the lowest total cost at your target volume."})
    return recs


# ── Cost Analysis ─────────────────────────────────────────────────────────────

def _cost_recs(result: Dict) -> List[Dict]:
    recs = []
    for alt in result.get('results', []):
        m = alt.get('profit_margin', 0)
        if m < 10:
            recs.append({'type': 'danger', 'priority': 'high',
                         'title': f'Thin Margin: {alt["name"]}',
                         'message': f'Profit margin is only {m:.1f}%. Investigate variable-cost reduction or a price increase.'})
        elif m < 20:
            recs.append({'type': 'warning', 'priority': 'medium',
                         'title': f'Below-Average Margin: {alt["name"]}',
                         'message': f'{m:.1f}% margin is below the typical 20-30% industrial benchmark.'})

    best = result.get('best_alternative')
    if best:
        recs.append({'type': 'success', 'priority': 'low',
                     'title': f'Best Alternative: {best["name"]}',
                     'message': f'Profit = ${best["profit"]:,.2f} ({best["profit_margin"]:.1f}% margin).'})
    return recs


# ── Transportation ────────────────────────────────────────────────────────────

def _transport_recs(result: Dict) -> List[Dict]:
    recs = []
    comp       = result.get('comparison', {})
    best_name  = result.get('best_method', '')
    best_cost  = result.get('best_cost', 0)

    if comp:
        worst = max(comp.values())
        if worst > 0:
            saving_pct = (worst - best_cost) / worst * 100
            recs.append({'type': 'success', 'priority': 'high',
                         'title': f'Best Method: {best_name}',
                         'message': f'Saves {saving_pct:.1f}% vs the costliest method '
                                    f'(${worst - best_cost:,.2f} saved).'})

    recs.append({'type': 'info', 'priority': 'medium',
                 'title': 'Verify Optimality',
                 'message': 'Apply the MODI (Modified Distribution) method to confirm '
                            'the initial solution is globally optimal.'})
    return recs


# ── Break-Even ────────────────────────────────────────────────────────────────

def _bep_recs(result: Dict) -> List[Dict]:
    recs = []
    bep  = result.get('bep', {})
    cm_r = bep.get('contribution_margin_ratio', 0)
    bep_u = bep.get('bep_units', 0)

    if cm_r < 25:
        recs.append({'type': 'danger', 'priority': 'high',
                     'title': 'Low Contribution Margin',
                     'message': f'CM Ratio = {cm_r:.1f}%. Explore ways to reduce variable costs or raise the selling price.'})
    elif cm_r > 55:
        recs.append({'type': 'success', 'priority': 'low',
                     'title': 'Strong Contribution Margin',
                     'message': f'CM Ratio = {cm_r:.1f}% — excellent pricing / cost structure.'})
    else:
        recs.append({'type': 'info', 'priority': 'low',
                     'title': f'CM Ratio: {cm_r:.1f}%',
                     'message': 'Within normal range. Continuously monitor variable costs for improvement opportunities.'})

    recs.append({'type': 'info', 'priority': 'medium',
                 'title': 'Track Safety Margin Monthly',
                 'message': f'Break-even is {bep_u:,.0f} units. '
                            'Measure your safety margin (actual − BEP) regularly.'})
    return recs


# ── Assignment ────────────────────────────────────────────────────────────────

def _assignment_recs(result: Dict) -> List[Dict]:
    recs = []
    savings = result.get('savings_vs_sequential', 0)
    tc      = result.get('total_cost', 1) or 1
    assignments = result.get('assignments', [])

    if savings > 0:
        recs.append({'type': 'success', 'priority': 'high',
                     'title': 'Savings Found',
                     'message': f'Hungarian method saves {savings:,.2f} units '
                                f'({savings/tc*100:.1f}%) vs sequential assignment.'})

    costs = [a['cost'] for a in assignments]
    if costs:
        cv = np.std(costs) / np.mean(costs) * 100 if np.mean(costs) > 0 else 0
        if cv > 50:
            recs.append({'type': 'warning', 'priority': 'medium',
                         'title': 'Unbalanced Workload',
                         'message': f'Assignment costs vary significantly (CV={cv:.0f}%). '
                                    'Review whether this workload imbalance is acceptable.'})

    recs.append({'type': 'info', 'priority': 'low',
                 'title': 'Reassign Periodically',
                 'message': 'Re-run this analysis whenever worker skills or task requirements change.'})
    return recs


# ── Plant Layout ──────────────────────────────────────────────────────────────

def _layout_recs(result: Dict) -> List[Dict]:
    recs = []

    ft = result.get('from_to', {})
    if ft:
        mvs = ft.get('movements', [])
        if mvs:
            top = mvs[0]
            recs.append({'type': 'warning', 'priority': 'high',
                         'title': 'Highest Movement Cost Pair',
                         'message': f'{top["from"]} ↔ {top["to"]} costs ${top["cost"]:,.2f}. '
                                    'Place these departments adjacent to minimise transport.'})

    rc = result.get('rel_chart', {})
    if rc:
        a_pairs = [p for p in rc.get('pairs', []) if p['relationship'] == 'A']
        x_pairs = [p for p in rc.get('pairs', []) if p['relationship'] == 'X']
        if a_pairs:
            names = ', '.join(f"{p['dept1']}–{p['dept2']}" for p in a_pairs[:2])
            recs.append({'type': 'success', 'priority': 'high',
                         'title': 'Must-Be-Adjacent Pairs',
                         'message': f'Ensure these are neighbours in your layout: {names}.'})
        if x_pairs:
            names = ', '.join(f"{p['dept1']}–{p['dept2']}" for p in x_pairs[:2])
            recs.append({'type': 'danger', 'priority': 'high',
                         'title': 'Incompatible Departments',
                         'message': f'Keep these departments separated: {names}.'})
    return recs


# ── Public router ─────────────────────────────────────────────────────────────

_HANDLERS = {
    'pert':       _pert_recs,
    'location':   _location_recs,
    'cost':       _cost_recs,
    'transport':  _transport_recs,
    'break_even': _bep_recs,
    'assignment': _assignment_recs,
    'layout':     _layout_recs,
}


def generate_recommendations(module: str, result: Dict) -> List[Dict]:
    """
    Return a list of recommendation dicts for the given module result.
    Falls back to a generic success message if no handler exists.
    """
    handler = _HANDLERS.get(module)
    if not handler:
        return [{'type': 'info', 'priority': 'low',
                 'title': 'Analysis Complete',
                 'message': 'Review the results above for insights.'}]
    try:
        return handler(result)
    except Exception:
        return [{'type': 'info', 'priority': 'low',
                 'title': 'Analysis Complete',
                 'message': 'Analysis completed successfully.'}]
