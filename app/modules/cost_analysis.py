"""
Cost Analysis Module
─────────────────────
  Total Cost   = Fixed Cost + Variable Cost × Quantity
  Profit       = Revenue − Total Cost
  Profit Margin = (Profit / Revenue) × 100 %

Supports multiple alternatives and crossover-point analysis.
"""
from __future__ import annotations

import numpy as np
from typing import List, Dict, Any


def _total_cost(fc: float, vc: float, qty: float) -> float:
    return fc + vc * qty


def analyze_costs(data: Dict) -> Dict[str, Any]:
    """
    Analyse costs and profits for one or more alternatives.

    Expected input keys
    -------------------
    alternatives : list of
        { name, fixed_cost, variable_cost_per_unit, selling_price, production_qty }
    quantity_range : [min, max, step]   (default 0-10000, step 500)
    """
    alternatives = data.get('alternatives', [])
    qty_range    = data.get('quantity_range', [0, 10000, 500])
    q_min, q_max, q_step = qty_range
    quantities   = np.arange(q_min, q_max + q_step, q_step).tolist()

    results   = []
    chart_data: Dict = {
        'quantities':   [round(q, 0) for q in quantities],
        'total_costs':  {},
        'revenues':     {},
        'profits':      {},
    }

    for alt in alternatives:
        name = alt['name']
        fc   = alt['fixed_cost']
        vc   = alt['variable_cost_per_unit']
        sp   = alt.get('selling_price', 0)
        qty  = alt.get('production_qty', q_max)

        tc      = _total_cost(fc, vc, qty)
        revenue = sp * qty
        profit  = revenue - tc
        margin  = (profit / revenue * 100) if revenue > 0 else 0

        chart_data['total_costs'][name] = [round(_total_cost(fc, vc, q), 2) for q in quantities]
        chart_data['revenues'][name]    = [round(sp * q, 2)               for q in quantities]
        chart_data['profits'][name]     = [round(sp * q - _total_cost(fc, vc, q), 2) for q in quantities]

        results.append({
            'name':           name,
            'fixed_cost':     fc,
            'variable_cost':  vc,
            'selling_price':  sp,
            'production_qty': qty,
            'total_cost':     round(tc, 2),
            'revenue':        round(revenue, 2),
            'profit':         round(profit, 2),
            'profit_margin':  round(margin, 2),
            'cost_per_unit':  round(tc / qty, 2) if qty > 0 else 0,
        })

    best = max(results, key=lambda r: r['profit']) if results else None

    # Crossover points between every pair
    crossovers = []
    for i in range(len(alternatives)):
        for j in range(i + 1, len(alternatives)):
            a1, a2 = alternatives[i], alternatives[j]
            dv = a1['variable_cost_per_unit'] - a2['variable_cost_per_unit']
            if abs(dv) > 1e-10:
                q = (a2['fixed_cost'] - a1['fixed_cost']) / dv
                if q >= 0:
                    crossovers.append({
                        'between':          f"{a1['name']} vs {a2['name']}",
                        'quantity':         round(q, 0),
                        'cost_at_crossover': round(_total_cost(a1['fixed_cost'],
                                                               a1['variable_cost_per_unit'], q), 2),
                    })

    return {
        'results':          results,
        'chart_data':       chart_data,
        'best_alternative': best,
        'crossovers':       crossovers,
    }
