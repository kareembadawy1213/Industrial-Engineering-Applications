"""
Break-Even Point Analysis Module
──────────────────────────────────
  Contribution Margin (CM) = Selling Price − Variable Cost per Unit
  CM Ratio                 = CM / Selling Price
  BEP (units)              = Fixed Cost / CM
  BEP (revenue)            = Fixed Cost / CM Ratio

Supports single-product and multi-product (weighted-average) break-even.
"""
from __future__ import annotations

import numpy as np
from typing import Dict, List, Any, Optional


def calculate_break_even(fc: float, vc: float, sp: float) -> Dict[str, Any]:
    """Compute single-product break-even statistics."""
    if sp <= vc:
        return {'error': 'Selling price must be greater than variable cost per unit.'}

    cm     = sp - vc
    cm_r   = cm / sp
    bep_u  = fc / cm
    bep_r  = fc / cm_r

    return {
        'bep_units':                 round(bep_u, 2),
        'bep_revenue':               round(bep_r, 2),
        'contribution_margin':       round(cm, 2),
        'contribution_margin_ratio': round(cm_r * 100, 2),
        'fixed_cost':                fc,
        'variable_cost_per_unit':    vc,
        'selling_price':             sp,
    }


def _chart_data(fc: float, vc: float, sp: float, max_qty: Optional[float]) -> Dict[str, Any]:
    """Generate x/y series for the break-even chart."""
    bep = calculate_break_even(fc, vc, sp)
    if 'error' in bep:
        return bep

    max_q = max_qty or bep['bep_units'] * 2.5
    qs    = np.linspace(0, max_q, 120).tolist()

    return {
        'quantities':   [round(q, 2)                   for q in qs],
        'total_costs':  [round(fc + vc * q, 2)         for q in qs],
        'revenues':     [round(sp * q, 2)               for q in qs],
        'fixed_costs':  [fc]  * len(qs),
        'profits':      [round(sp * q - fc - vc * q, 2) for q in qs],
        'bep_units':    bep['bep_units'],
        'bep_revenue':  bep['bep_revenue'],
    }


def analyze_break_even(data: Dict) -> Dict[str, Any]:
    """
    Main break-even analysis entry point.

    Input keys: fixed_cost, variable_cost_per_unit, selling_price
    Optional:   max_quantity, products (list for multi-product BEP)
    """
    fc = data['fixed_cost']
    vc = data['variable_cost_per_unit']
    sp = data['selling_price']

    bep = calculate_break_even(fc, vc, sp)
    if 'error' in bep:
        return bep

    chart = _chart_data(fc, vc, sp, data.get('max_quantity'))

    # Sample profit table at 50 %, BEP, 150 %, 200 % of BEP
    bep_u = bep['bep_units']
    target_profits = []
    for factor, label in [(0.5, '50% of BEP'), (1.0, 'Break-Even'), (1.5, '150% of BEP'), (2.0, '200% of BEP')]:
        qty = bep_u * factor
        rev = sp * qty
        tc  = fc + vc * qty
        target_profits.append({
            'label':      label,
            'quantity':   round(qty, 0),
            'revenue':    round(rev, 2),
            'total_cost': round(tc,  2),
            'profit':     round(rev - tc, 2),
        })

    return {
        'bep':            bep,
        'chart_data':     chart,
        'target_profits': target_profits,
    }
