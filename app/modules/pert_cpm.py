"""
PERT / CPM Analysis Module
───────────────────────────
CPM  – Critical Path Method   (deterministic single durations)
PERT – Program Evaluation and Review Technique (3-point probabilistic durations)

Key formulas
  PERT expected time : te = (a + 4m + b) / 6
  PERT variance      : σ² = ((b − a) / 6)²
  Forward pass       : ES_j = max(EF of predecessors),  EF_j = ES_j + te_j
  Backward pass      : LF_j = min(LS of successors),    LS_j = LF_j − te_j
  Total slack        : TF_j = LS_j − ES_j   (= 0 on critical path)
"""
from __future__ import annotations

import numpy as np
import networkx as nx
from collections import defaultdict
from typing import List, Dict, Any


# ── PERT helpers ─────────────────────────────────────────────────────────────

def pert_expected(a: float, m: float, b: float):
    """Return (expected_time, variance, std_dev) for a PERT activity."""
    te  = (a + 4 * m + b) / 6.0
    var = ((b - a) / 6.0) ** 2
    return te, var, np.sqrt(var)


# ── Graph construction ────────────────────────────────────────────────────────

def _build_graph(activities: List[Dict]) -> nx.DiGraph:
    """
    Build an Activity-on-Node (AON) directed graph.

    Each activity dict must have:
        name         : str
        duration     : float   (CPM) or computed PERT expected time
        predecessors : list[str]  (empty → depends only on START)
    """
    G = nx.DiGraph()
    G.add_node('START', duration=0)
    G.add_node('END',   duration=0)

    known = {a['name'] for a in activities}

    for act in activities:
        G.add_node(act['name'], duration=act.get('duration', 0))

    for act in activities:
        preds = [p for p in act.get('predecessors', []) if p in known]
        if not preds:
            G.add_edge('START', act['name'])
        else:
            for p in preds:
                G.add_edge(p, act['name'])

    for node in list(G.nodes):
        if node not in ('START', 'END') and G.out_degree(node) == 0:
            G.add_edge(node, 'END')

    return G


# ── Forward / Backward pass ──────────────────────────────────────────────────

def _forward(G: nx.DiGraph):
    ES: Dict[str, float] = defaultdict(float)
    EF: Dict[str, float] = defaultdict(float)
    for node in nx.topological_sort(G):
        if node == 'START':
            continue
        preds = list(G.predecessors(node))
        ES[node] = max((EF[p] for p in preds), default=0.0)
        EF[node] = ES[node] + G.nodes[node].get('duration', 0)
    return dict(ES), dict(EF)


def _backward(G: nx.DiGraph, EF: Dict):
    project_end = EF.get('END', 0.0)
    LF: Dict[str, float] = defaultdict(lambda: project_end)
    LS: Dict[str, float] = defaultdict(lambda: project_end)
    LF['END'] = LS['END'] = project_end

    for node in reversed(list(nx.topological_sort(G))):
        if node == 'END':
            continue
        succs = list(G.successors(node))
        LF[node] = min((LS[s] for s in succs), default=project_end)
        LS[node] = LF[node] - G.nodes[node].get('duration', 0)

    return dict(LS), dict(LF)


# ── Main entry point ─────────────────────────────────────────────────────────

def analyze_pert_cpm(activities: List[Dict], use_pert: bool = False) -> Dict[str, Any]:
    """
    Perform full PERT / CPM analysis.

    Parameters
    ----------
    activities : list of dicts
        Required keys per activity:
            name, predecessors, duration  (CPM)
            OR name, predecessors, optimistic, most_likely, pessimistic  (PERT)
    use_pert : bool
        When True compute expected durations from the 3-point estimates.

    Returns
    -------
    dict with keys: table, project_duration, critical_path,
                    critical_activities, use_pert, pert_stats
    """
    processed: List[Dict] = []
    for raw in activities:
        act = dict(raw)
        if use_pert and all(k in act for k in ('optimistic', 'most_likely', 'pessimistic')):
            te, var, std = pert_expected(act['optimistic'], act['most_likely'], act['pessimistic'])
            act.update(duration=te, variance=var, std_dev=std)
        processed.append(act)

    G = _build_graph(processed)

    # Push updated durations onto graph nodes
    for act in processed:
        if act['name'] in G.nodes:
            G.nodes[act['name']]['duration'] = act.get('duration', 0)

    ES, EF = _forward(G)
    LS, LF = _backward(G, EF)

    project_duration = EF.get('END', 0.0)

    slack   = {n: LS[n] - ES[n] for n in G.nodes if n not in ('START', 'END')}
    critical = [n for n, s in slack.items() if abs(s) < 1e-6]

    # Build result table
    table = []
    for act in processed:
        name = act['name']
        row: Dict[str, Any] = {
            'name':         name,
            'duration':     round(act.get('duration', 0), 2),
            'predecessors': act.get('predecessors', []),
            'es':           round(ES.get(name, 0), 2),
            'ef':           round(EF.get(name, 0), 2),
            'ls':           round(LS.get(name, 0), 2),
            'lf':           round(LF.get(name, 0), 2),
            'slack':        round(slack.get(name, 0), 2),
            'critical':     name in critical,
        }
        if use_pert:
            row.update(
                optimistic=act.get('optimistic', 0),
                most_likely=act.get('most_likely', 0),
                pessimistic=act.get('pessimistic', 0),
                variance=round(act.get('variance', 0), 4),
                std_dev=round(act.get('std_dev', 0), 4),
            )
        table.append(row)

    # PERT project-level statistics
    pert_stats: Dict = {}
    if use_pert:
        cp_vars  = [act.get('variance', 0) for act in processed if act['name'] in critical]
        tot_var  = sum(cp_vars)
        proj_std = np.sqrt(tot_var)
        pert_stats = {
            'total_variance':    round(tot_var, 4),
            'project_std_dev':   round(proj_std, 4),
            'expected_duration': round(project_duration, 2),
        }

    # Retrieve one critical path sequence (START→END traversal)
    critical_path_seq: List[str] = []
    try:
        for path in nx.all_simple_paths(G, 'START', 'END'):
            inner = [n for n in path if n not in ('START', 'END')]
            if all(n in critical for n in inner):
                critical_path_seq = inner
                break
    except Exception:
        critical_path_seq = critical

    return {
        'table':              table,
        'project_duration':   round(project_duration, 2),
        'critical_path':      critical_path_seq,
        'critical_activities': critical,
        'use_pert':           use_pert,
        'pert_stats':         pert_stats,
    }
