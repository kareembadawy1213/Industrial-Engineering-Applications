"""
Best Plant Location Analysis Module
────────────────────────────────────
Two complementary methods:
  1. Weighted Factor Rating  – qualitative factors scored & weighted
  2. Cost Comparison         – fixed + variable costs at varying volumes
"""
from __future__ import annotations
from typing import List, Dict, Any


# ── Method 1: Weighted Factor Rating ─────────────────────────────────────────

def weighted_factor_rating(locations: List[str], factors: List[Dict]) -> Dict[str, Any]:
    """
    Weighted Factor Rating (WFR) method.

    Parameters
    ----------
    locations : list of location names
    factors   : list of dicts
        { 'name': str, 'weight': float (0-100), 'scores': { location_name: score } }
        Scores are typically on a 0-100 scale.

    Returns
    -------
    dict with weighted scores, ranking, detail table, and recommendation.
    """
    # Normalise weights so they sum to 100
    total_w = sum(f['weight'] for f in factors) or 1
    if abs(total_w - 100) > 0.01:
        factors = [{**f, 'weight': f['weight'] / total_w * 100} for f in factors]

    totals: Dict[str, float] = {loc: 0.0 for loc in locations}
    detail = []
    for fac in factors:
        row: Dict = {'factor': fac['name'], 'weight': round(fac['weight'], 2)}
        for loc in locations:
            raw      = fac['scores'].get(loc, 0)
            weighted = fac['weight'] / 100 * raw
            totals[loc] += weighted
            row[f'{loc}_score']    = raw
            row[f'{loc}_weighted'] = round(weighted, 2)
        detail.append(row)

    scores  = {loc: round(v, 2) for loc, v in totals.items()}
    ranked  = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best    = ranked[0][0] if ranked else None

    return {
        'method':         'Weighted Factor Rating',
        'scores':         scores,
        'ranked':         ranked,
        'recommendation': best,
        'detail':         detail,
        'locations':      locations,
        'factors':        [f['name'] for f in factors],
    }


# ── Method 2: Cost Comparison ────────────────────────────────────────────────

def cost_comparison(locations: List[Dict], production_volumes: List[float]) -> Dict[str, Any]:
    """
    Compare total costs (FC + VC × Q) across locations at given volumes.

    Parameters
    ----------
    locations         : list of { 'name', 'fixed_cost', 'variable_cost_per_unit' }
    production_volumes: list of quantities to evaluate

    Returns
    -------
    dict with cost table, chart data, crossover points, and best location.
    """
    table      = []
    chart_data: Dict[str, List[float]] = {loc['name']: [] for loc in locations}

    for vol in production_volumes:
        row: Dict = {'volume': vol}
        for loc in locations:
            total = loc['fixed_cost'] + loc['variable_cost_per_unit'] * vol
            row[loc['name']]               = round(total, 2)
            chart_data[loc['name']].append(round(total, 2))
        table.append(row)

    # Best location at maximum volume
    max_vol  = max(production_volumes)
    max_costs = {loc['name']: loc['fixed_cost'] + loc['variable_cost_per_unit'] * max_vol
                 for loc in locations}
    best = min(max_costs, key=max_costs.get)

    # Crossover points between every pair
    crossovers = []
    for i in range(len(locations)):
        for j in range(i + 1, len(locations)):
            l1, l2 = locations[i], locations[j]
            dv = l1['variable_cost_per_unit'] - l2['variable_cost_per_unit']
            if abs(dv) > 1e-10:
                q = (l2['fixed_cost'] - l1['fixed_cost']) / dv
                if q > 0:
                    crossovers.append({
                        'between':  f"{l1['name']} & {l2['name']}",
                        'quantity': round(q, 0),
                    })

    return {
        'method':                'Cost Comparison',
        'table':                 table,
        'chart_data':            chart_data,
        'volumes':               production_volumes,
        'best_location':         best,
        'costs_at_max_volume':   {k: round(v, 2) for k, v in max_costs.items()},
        'crossovers':            crossovers,
        'locations':             [loc['name'] for loc in locations],
    }


# ── Combined entry point ─────────────────────────────────────────────────────

def analyze_plant_location(data: Dict) -> Dict[str, Any]:
    """
    Run Weighted Factor Rating and/or Cost Comparison depending on
    what data is supplied, then return combined results and recommendations.
    """
    results: Dict[str, Any] = {}

    if data.get('weighted_factors'):
        results['weighted_factor_rating'] = weighted_factor_rating(
            data['locations'], data['weighted_factors']
        )

    if data.get('cost_locations'):
        volumes = data.get('production_volumes') or list(range(0, 10001, 1000))
        results['cost_comparison'] = cost_comparison(data['cost_locations'], volumes)

    recs = []
    if 'weighted_factor_rating' in results:
        recs.append(f"Weighted Factor Rating recommends: "
                    f"{results['weighted_factor_rating']['recommendation']}")
    if 'cost_comparison' in results:
        recs.append(f"Cost Comparison recommends: "
                    f"{results['cost_comparison']['best_location']}")
    results['recommendations'] = recs
    return results
