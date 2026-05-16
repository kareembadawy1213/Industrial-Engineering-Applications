"""
Transportation Problem Solver
──────────────────────────────
Three initial feasible solution methods:
  1. North-West Corner Method (NWC)
  2. Least Cost Method        (LCM)
  3. Vogel's Approximation Method (VAM)

All three are compared so the user can choose the best starting point.
"""
from __future__ import annotations
from typing import List, Dict, Any
import copy


# ── Helper: balance supply == demand ─────────────────────────────────────────

def _balance(supply: List[float], demand: List[float],
             costs: List[List[float]]):
    """Add a dummy supplier or dummy destination to balance the problem."""
    sup  = list(supply)
    dem  = list(demand)
    cost = [list(row) for row in costs]

    ts, td = sum(sup), sum(dem)
    if ts > td:
        dem.append(ts - td)
        for row in cost:
            row.append(0)
    elif td > ts:
        sup.append(td - ts)
        cost.append([0] * len(dem))
    return sup, dem, cost


def _total(alloc, costs):
    return sum(alloc[i][j] * costs[i][j]
               for i in range(len(alloc))
               for j in range(len(alloc[0])))


# ── Method 1: North-West Corner ──────────────────────────────────────────────

def north_west_corner(supply, demand, costs) -> Dict[str, Any]:
    sup, dem, cost = _balance(supply, demand, costs)
    m, n = len(sup), len(dem)
    alloc = [[0] * n for _ in range(m)]
    s, d  = sup[:], dem[:]
    steps = []
    i = j = 0

    while i < m and j < n:
        a = min(s[i], d[j])
        alloc[i][j] = a
        steps.append({'row': i, 'col': j, 'amount': a})
        s[i] -= a;  d[j] -= a
        if s[i] == 0 and d[j] == 0:
            i += 1;  j += 1
        elif s[i] == 0:
            i += 1
        else:
            j += 1

    return {
        'method':     'North-West Corner',
        'allocation': alloc,
        'total_cost': round(_total(alloc, cost), 2),
        'steps':      steps,
        'supply':     sup,
        'demand':     dem,
        'costs':      cost,
    }


# ── Method 2: Least Cost Method ──────────────────────────────────────────────

def least_cost_method(supply, demand, costs) -> Dict[str, Any]:
    sup, dem, cost = _balance(supply, demand, costs)
    m, n = len(sup), len(dem)
    alloc = [[0] * n for _ in range(m)]
    s, d  = sup[:], dem[:]
    row_done = [False] * m
    col_done = [False] * n
    steps = []

    while not all(row_done) and not all(col_done):
        best_val = float('inf')
        bi = bj = -1
        for i in range(m):
            if row_done[i]:
                continue
            for j in range(n):
                if col_done[j]:
                    continue
                if cost[i][j] < best_val:
                    best_val, bi, bj = cost[i][j], i, j
        if bi == -1:
            break

        a = min(s[bi], d[bj])
        alloc[bi][bj] = a
        steps.append({'row': bi, 'col': bj, 'amount': a, 'cost': cost[bi][bj]})
        s[bi] -= a;  d[bj] -= a
        if s[bi] == 0:
            row_done[bi] = True
        if d[bj] == 0:
            col_done[bj] = True

    return {
        'method':     'Least Cost Method',
        'allocation': alloc,
        'total_cost': round(_total(alloc, cost), 2),
        'steps':      steps,
        'supply':     sup,
        'demand':     dem,
        'costs':      cost,
    }


# ── Method 3: Vogel's Approximation Method ────────────────────────────────────

def vogel_approximation(supply, demand, costs) -> Dict[str, Any]:
    sup, dem, cost = _balance(supply, demand, costs)
    m, n = len(sup), len(dem)
    alloc = [[0] * n for _ in range(m)]
    s, d  = sup[:], dem[:]
    row_done = [False] * m
    col_done = [False] * n
    steps = []

    def row_pen(i):
        vals = sorted(cost[i][j] for j in range(n) if not col_done[j])
        return (vals[1] - vals[0]) if len(vals) >= 2 else (vals[0] if vals else 0)

    def col_pen(j):
        vals = sorted(cost[i][j] for i in range(m) if not row_done[i])
        return (vals[1] - vals[0]) if len(vals) >= 2 else (vals[0] if vals else 0)

    iters = 0
    while not all(row_done) and not all(col_done):
        iters += 1
        if iters > m * n * 10:
            break

        r_pens = [(row_pen(i), i) for i in range(m) if not row_done[i]]
        c_pens = [(col_pen(j), j) for j in range(n) if not col_done[j]]

        best_r = max(r_pens, key=lambda x: x[0]) if r_pens else (-1, -1)
        best_c = max(c_pens, key=lambda x: x[0]) if c_pens else (-1, -1)

        if best_r[0] >= best_c[0]:
            i = best_r[1]
            j = min((j for j in range(n) if not col_done[j]), key=lambda j: cost[i][j])
        else:
            j = best_c[1]
            i = min((i for i in range(m) if not row_done[i]), key=lambda i: cost[i][j])

        a = min(s[i], d[j])
        alloc[i][j] = a
        steps.append({'row': i, 'col': j, 'amount': a, 'cost': cost[i][j]})
        s[i] -= a;  d[j] -= a
        if s[i] == 0:
            row_done[i] = True
        if d[j] == 0:
            col_done[j] = True

    return {
        'method':     "Vogel's Approximation Method",
        'allocation': alloc,
        'total_cost': round(_total(alloc, cost), 2),
        'steps':      steps,
        'supply':     sup,
        'demand':     dem,
        'costs':      cost,
    }


# ── Main entry point ─────────────────────────────────────────────────────────

def solve_transportation(data: Dict) -> Dict[str, Any]:
    """
    Solve a transportation problem with all three methods and compare.

    Input keys: supply (list), demand (list), costs (2-D list)
    Optional:   supplier_names, destination_names
    """
    supply = data['supply']
    demand = data['demand']
    costs  = data['costs']

    nwc = north_west_corner(supply, demand, costs)
    lcm = least_cost_method(supply, demand, costs)
    vam = vogel_approximation(supply, demand, costs)

    comparison = {
        'North-West Corner':         nwc['total_cost'],
        'Least Cost Method':         lcm['total_cost'],
        "Vogel's Approximation":     vam['total_cost'],
    }
    best_name = min(comparison, key=comparison.get)

    return {
        'north_west_corner': nwc,
        'least_cost':        lcm,
        'vogel':             vam,
        'comparison':        comparison,
        'best_method':       best_name,
        'best_cost':         comparison[best_name],
        'supplier_names':    data.get('supplier_names', [f'S{i+1}' for i in range(len(supply))]),
        'destination_names': data.get('destination_names', [f'D{j+1}' for j in range(len(demand))]),
    }
