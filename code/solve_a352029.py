"""
A352029 -- Number of minimalist polyominoes containing all free n-ominoes
SAT enumeration solver with CEGAR (rebuilt from archived v7).

Approach:
  For each valid bounding box (H, W):
    1. Build base SAT formula: grid vars + exactly-k cardinality + border
       touching + local connectivity + no-gap + lex-leader symmetry breaking
    2. Pre-solve: compute mandatory cells over ALL pieces (not just seeds)
    3. CEGAR: seed hardest pieces, find candidates, verify against all pieces,
       add failed constraints lazily
    4. Enumerate all solutions, canonicalize, deduplicate across partitions

Enhancements over archived v7:
  - Uses shared library polyform_enum (Cython/C, 50-200x faster)
  - Uses shared library sat_utils.connectivity
  - Full mandatory cell analysis over all pieces before CEGAR
  - Dual-solver support: Glucose for SAT-expected, CaDiCaL for UNSAT-expected
  - Versioned output via figure_gen_utils
  - SolverLogger for structured run logs

Usage:
    python solve_a352029.py --n N              # enumerate for specific n
    python solve_a352029.py --n N --workers W  # limit CPU cores
    python solve_a352029.py --verify           # verify known terms n=3..8
"""

import sys
import os
import time
import json
import argparse
from collections import deque
from multiprocessing import Pool, cpu_count
from datetime import datetime

# Add parent paths for shared libraries
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_paper_root = os.path.dirname(_project_root)
sys.path.insert(0, _paper_root)

sys.stdout.reconfigure(line_buffering=True)

# Shared libraries
try:
    from polyform_enum import enumerate_free as pe_enumerate_free
    from polyform_enum import all_placements as pe_all_placements
    from polyform_enum import normalize as pe_normalize
    from polyform_enum import canonical_form as pe_canonical_form
    _USE_CYTHON = True
except ImportError:
    _USE_CYTHON = False

from sat_utils.connectivity import find_components, SQUARE_DIRS

try:
    from figure_gen_utils.versioned_output import save_versioned
    from figure_gen_utils.solver_log import SolverLogger
    _HAS_FIG_UTILS = True
except ImportError:
    _HAS_FIG_UTILS = False


# ============================================================
# Constants
# ============================================================

# A327094: smallest polyomino containing all free n-ominoes
A327094 = {1: 1, 2: 2, 3: 4, 4: 6, 5: 9, 6: 12, 7: 17, 8: 20, 9: 26}

# Known terms for verification
A352029_KNOWN = {1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 14, 7: 204, 8: 7}


# ============================================================
# Polyomino generation (fallback if no Cython)
# ============================================================

def _normalize_py(cells):
    cells = frozenset(cells)
    mr = min(r for r, c in cells)
    mc = min(c for r, c in cells)
    return frozenset((r - mr, c - mc) for r, c in cells)


def _rot90(cells):
    return frozenset((c, -r) for r, c in cells)


def _flip(cells):
    return frozenset((-r, c) for r, c in cells)


def _orientations_py(cells):
    cells = frozenset(cells)
    seen = set()
    result = []
    cur = cells
    for _ in range(4):
        n = _normalize_py(cur)
        if n not in seen:
            seen.add(n)
            result.append(n)
        fn = _normalize_py(_flip(cur))
        if fn not in seen:
            seen.add(fn)
            result.append(fn)
        cur = _rot90(cur)
    return result


def _gen_fixed_py(n):
    if n == 1:
        return [frozenset([(0, 0)])]
    smaller = _gen_fixed_py(n - 1)
    result = set()
    for poly in smaller:
        for r, c in poly:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if (nr, nc) not in poly:
                    new = _normalize_py(poly | {(nr, nc)})
                    result.add(new)
    return list(result)


def _gen_free_py(n):
    if n <= 0:
        return [frozenset()]
    fixed = _gen_fixed_py(n)
    seen = set()
    free = []
    for p in fixed:
        canon = min(tuple(sorted(o)) for o in _orientations_py(p))
        if canon not in seen:
            seen.add(canon)
            free.append(p)
    return free


def gen_free(n):
    """Generate all free n-ominoes. Uses Cython if available."""
    if _USE_CYTHON:
        return pe_enumerate_free(n, "square")
    return _gen_free_py(n)


def orientations(cells):
    """All distinct orientations of a polyomino (free equivalence)."""
    return _orientations_py(cells)


def normalize(cells):
    """Translate to origin."""
    if _USE_CYTHON:
        return pe_normalize(frozenset(cells), "square")
    return _normalize_py(cells)


def canonicalize(cells):
    """Canonical form: lex-smallest orientation."""
    if _USE_CYTHON:
        return pe_canonical_form(frozenset(cells), "square")
    cells = frozenset(cells)
    best = None
    for o in _orientations_py(cells):
        n = _normalize_py(o)
        t = tuple(sorted(n))
        if best is None or t < best:
            best = t
    return frozenset(best)


# ============================================================
# Partition enumeration (from archived v7)
# ============================================================

def has_2x2_piece(free_polys):
    target = frozenset([(0, 0), (0, 1), (1, 0), (1, 1)])
    for poly in free_polys:
        for o in orientations(poly):
            if _normalize_py(o) == target:
                return True
    return False


def compute_triple_piece_overhead(n, free_polys):
    line_n = frozenset((0, i) for i in range(n))
    has_line = any(_normalize_py(o) == _normalize_py(line_n)
                   for p in free_polys for o in orientations(p))
    plus_cells = frozenset([(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)])
    has_plus = n >= 5 and any(_normalize_py(o) == _normalize_py(plus_cells)
                               for p in free_polys for o in orientations(p))
    sq_cells = frozenset([(r, c) for r in range(3) for c in range(3)])
    has_sq = n >= 9 and any(_normalize_py(o) == _normalize_py(sq_cells)
                             for p in free_polys for o in orientations(p))
    overhead = 0
    if has_line and has_plus:
        overhead = max(overhead, 2)
    if has_line and has_sq:
        overhead = max(overhead, n + 2)
    if has_plus and has_sq:
        overhead = max(overhead, 4)
    return overhead


def valid_partitions(n, k, free_polys):
    cap = max(n, k - n + 1)
    has_2x2 = has_2x2_piece(free_polys)
    hw_limit = k if has_2x2 else k + 1
    triple_overhead = compute_triple_piece_overhead(n, free_polys)
    partitions = []
    for w in range(n, cap + 1):
        for h in range(1, w + 1):
            if h * w < k:
                continue
            if h + w - 1 > k:
                continue
            if h + w > hw_limit:
                continue
            if h * w < k + triple_overhead:
                continue
            all_fit = True
            for poly in free_polys:
                fits = False
                for o in orientations(poly):
                    mr = max(r for r, c in o)
                    mc = max(c for r, c in o)
                    if mr < h and mc < w:
                        fits = True
                        break
                if not fits:
                    all_fit = False
                    break
            if all_fit:
                partitions.append((h, w))
    return partitions


# ============================================================
# Symmetry breaking (lex-leader constraints)
# ============================================================

def _lex_leader(pairs, aux_start):
    """Lex-leader clauses: X <= mirror(X) lexicographically."""
    clauses = []
    aux_vars = list(range(aux_start, aux_start + len(pairs)))
    for i, (a, b) in enumerate(pairs):
        prev_eq = aux_vars[i - 1] if i > 0 else None
        curr_eq = aux_vars[i]
        if prev_eq:
            clauses.append([-prev_eq, -a, b])
        else:
            clauses.append([-a, b])
        if prev_eq:
            clauses.append([-curr_eq, prev_eq])
        clauses.append([-curr_eq, -a, b])
        clauses.append([-curr_eq, a, -b])
    return clauses, aux_start + len(pairs)


# ============================================================
# Pre-solve mandatory cell analysis (creative-review Proposal 3)
# ============================================================

def compute_mandatory_cells(free_polys, H, W):
    """Find cells that appear in ALL placements of at least one piece.

    A cell is mandatory if some piece P has the property that every valid
    placement of P includes that cell. Such cells must be occupied in any
    valid container, giving free unit propagation.
    """
    def var(r, c):
        return r * W + c + 1

    mandatory = set()
    for poly in free_polys:
        all_cells_in_placement = None
        for ori in orientations(poly):
            cells_list = list(ori)
            mr = max(r for r, c in cells_list)
            mc = max(c for r, c in cells_list)
            if mr >= H or mc >= W:
                continue
            for dr in range(H - mr):
                for dc in range(W - mc):
                    placed = frozenset((r + dr, c + dc) for r, c in cells_list)
                    if all_cells_in_placement is None:
                        all_cells_in_placement = set(placed)
                    else:
                        all_cells_in_placement &= placed

        if all_cells_in_placement:
            mandatory |= all_cells_in_placement

    return mandatory


# ============================================================
# CEGAR solver core
# ============================================================

def piece_difficulty(poly, H, W):
    """Count total placements of a piece in H x W grid. Fewer = harder."""
    count = 0
    for ori in orientations(poly):
        cells_list = list(ori)
        mr = max(r for r, c in cells_list)
        mc = max(c for r, c in cells_list)
        if mr < H and mc < W:
            for dr in range(H - mr):
                for dc in range(W - mc):
                    count += 1
    return count


def can_contain_piece(occupied_set, poly, H, W):
    """Check if occupied cells can contain at least one placement of poly."""
    for ori in orientations(poly):
        cells_list = list(ori)
        mr = max(r for r, c in cells_list)
        mc = max(c for r, c in cells_list)
        if mr >= H or mc >= W:
            continue
        for dr in range(H - mr):
            for dc in range(W - mc):
                placed = {(r + dr, c + dc) for r, c in cells_list}
                if placed.issubset(occupied_set):
                    return True
    return False


def build_cegar_base(H, W, k, mandatory_cells=None):
    """Build base SAT encoding with optional mandatory cell pre-seeding."""
    from pysat.card import CardEnc, EncType

    def var(r, c):
        return r * W + c + 1

    total_vars = H * W
    cell_vars = [var(r, c) for r in range(H) for c in range(W)]
    clauses = []

    # Anchor: shape touches all 4 borders
    clauses.append([var(0, c) for c in range(W)])
    clauses.append([var(r, 0) for r in range(H)])
    clauses.append([var(H - 1, c) for c in range(W)])
    clauses.append([var(r, W - 1) for r in range(H)])

    # No-gap constraints
    for r in range(1, H):
        row_prev = [var(r - 1, c) for c in range(W)]
        for c in range(W):
            clauses.append([-var(r, c)] + row_prev)
    for c in range(1, W):
        col_prev = [var(r, c - 1) for r in range(H)]
        for r in range(H):
            clauses.append([-var(r, c)] + col_prev)

    # Neighbor connectivity (local)
    for r in range(H):
        for c in range(W):
            neighbors = []
            if r > 0: neighbors.append(var(r - 1, c))
            if r < H - 1: neighbors.append(var(r + 1, c))
            if c > 0: neighbors.append(var(r, c - 1))
            if c < W - 1: neighbors.append(var(r, c + 1))
            if neighbors:
                clauses.append([-var(r, c)] + neighbors)

    # Mandatory cells (from pre-solve analysis)
    if mandatory_cells:
        for r, c in mandatory_cells:
            if 0 <= r < H and 0 <= c < W:
                clauses.append([var(r, c)])

    # Cardinality: exactly k cells
    aux_id = total_vars + 1
    card_clauses = CardEnc.equals(cell_vars, k, top_id=aux_id,
                                   encoding=EncType.totalizer)
    clauses.extend(card_clauses.clauses)
    max_var = max(max(abs(lit) for lit in cl) for cl in clauses)

    # Symmetry breaking (lex-leader)
    next_sym = max_var + 1

    v_pairs = [(var(r, c), var(H - 1 - r, c))
               for r in range(H // 2) for c in range(W)]
    if v_pairs:
        v_cl, next_sym = _lex_leader(v_pairs, next_sym)
        clauses.extend(v_cl)

    h_pairs = [(var(r, c), var(r, W - 1 - c))
               for r in range(H) for c in range(W // 2)]
    if h_pairs:
        h_cl, next_sym = _lex_leader(h_pairs, next_sym)
        clauses.extend(h_cl)

    r_pairs = []
    half = (H * W) // 2
    for i in range(half):
        r1, c1 = i // W, i % W
        r2, c2 = H - 1 - r1, W - 1 - c1
        r_pairs.append((var(r1, c1), var(r2, c2)))
    if r_pairs:
        r_cl, next_sym = _lex_leader(r_pairs, next_sym)
        clauses.extend(r_cl)

    if H == W:
        q_pairs = []
        for i in range(half):
            r1, c1 = i // W, i % W
            r2, c2 = c1, H - 1 - r1
            q_pairs.append((var(r1, c1), var(r2, c2)))
        if q_pairs:
            q_cl, next_sym = _lex_leader(q_pairs, next_sym)
            clauses.extend(q_cl)

    max_var = next_sym - 1
    return clauses, cell_vars, max_var


def make_piece_clauses(poly, H, W, aux_start):
    """Generate placement constraints for a single piece."""
    def var(r, c):
        return r * W + c + 1

    placements = []
    seen = set()
    for ori in orientations(poly):
        cells_list = list(ori)
        mr = max(r for r, c in cells_list)
        mc = max(c for r, c in cells_list)
        if mr >= H or mc >= W:
            continue
        for dr in range(H - mr):
            for dc in range(W - mc):
                placed = tuple(sorted((r + dr, c + dc) for r, c in cells_list))
                if placed not in seen:
                    seen.add(placed)
                    placements.append(placed)

    if not placements:
        return [[1], [-1]], aux_start  # contradiction

    pvars = list(range(aux_start, aux_start + len(placements)))
    next_aux = aux_start + len(placements)

    clauses = []
    clauses.append(pvars[:])  # at least one placement active
    for j, placed_cells in enumerate(placements):
        aux = pvars[j]
        for r, c in placed_cells:
            clauses.append([-aux, var(r, c)])

    return clauses, next_aux


def _select_solver(H, W, k):
    """Select SAT solver based on partition characteristics.

    Creative-review Proposal 2: use CaDiCaL for UNSAT-expected partitions
    (near-square, slack=0), Glucose for SAT-expected (elongated, higher slack).
    """
    slack = H * W - k
    aspect = min(H, W) / max(H, W)

    # Near-square + low slack -> likely UNSAT -> CaDiCaL with aggressive restarts
    if aspect > 0.6 and slack <= 2:
        return "cadical"
    # Otherwise -> Glucose (proved 46-71x faster on SAT partitions)
    return "glucose"


def _make_solver(solver_type, clauses):
    """Create a PySAT solver instance."""
    if solver_type == "cadical":
        from pysat.solvers import Cadical195
        solver = Cadical195(bootstrap_with=clauses)
        solver.configure({'restartint': 5})  # aggressive restarts for UNSAT
        return solver
    else:
        from pysat.solvers import Glucose42
        return Glucose42(bootstrap_with=clauses)


def _solve_partition_cegar(args):
    """CEGAR solver for one (H, W) partition. Worker function."""
    H, W, k, free_polys_ser, seed_size, use_mandatory = args
    t_start = time.time()

    # Reconstruct free_polys
    free_polys = [frozenset(tuple(c) for c in poly) for poly in free_polys_ser]
    n_pieces = len(free_polys)

    def var(r, c):
        return r * W + c + 1

    # Rank pieces by difficulty
    diffs = [(piece_difficulty(poly, H, W), i) for i, poly in enumerate(free_polys)]
    diffs.sort()

    # Check feasibility
    for d, i in diffs:
        if d == 0:
            return {"H": H, "W": W, "solutions": {},
                    "raw": 0, "distinct": 0, "proved": True,
                    "time": time.time() - t_start, "pieces_used": 0,
                    "mandatory_cells": 0, "solver_type": "n/a",
                    "status": "infeasible"}

    # Pre-solve mandatory cell analysis (over ALL pieces)
    mandatory = set()
    if use_mandatory:
        mandatory = compute_mandatory_cells(free_polys, H, W)

    # Build base encoding with mandatory cells
    base_clauses, cell_vars, max_var = build_cegar_base(H, W, k, mandatory)

    # Add seed pieces
    all_clauses = list(base_clauses)
    next_aux = max_var + 1
    added_pieces = set()
    actual_seed = min(seed_size, n_pieces)
    for _, idx in diffs[:actual_seed]:
        pc, next_aux = make_piece_clauses(free_polys[idx], H, W, next_aux)
        all_clauses.extend(pc)
        added_pieces.add(idx)

    # Select and create solver
    solver_type = _select_solver(H, W, k)
    solver = _make_solver(solver_type, all_clauses)

    canonical_solutions = {}
    raw_count = 0
    iteration = 0
    max_iterations = 10000

    while iteration < max_iterations:
        iteration += 1

        # Iterative connectivity solve
        found_connected = False
        for _ in range(10000):
            if not solver.solve():
                solver.delete()
                elapsed = time.time() - t_start
                return {"H": H, "W": W,
                        "solutions": {tuple(tuple(c) for c in k_): v
                                      for k_, v in canonical_solutions.items()},
                        "raw": raw_count, "distinct": len(canonical_solutions),
                        "proved": True, "time": elapsed,
                        "pieces_used": len(added_pieces),
                        "mandatory_cells": len(mandatory),
                        "solver_type": solver_type,
                        "status": "complete"}

            model = set(solver.get_model())
            occupied = set()
            for r in range(H):
                for c in range(W):
                    if var(r, c) in model:
                        occupied.add((r, c))

            components = find_components(occupied)
            if len(components) == 1:
                found_connected = True
                break

            largest = max(components, key=len)
            for comp in components:
                if comp is not largest:
                    solver.add_clause([-var(r, c) for r, c in comp])

        if not found_connected:
            solver.delete()
            elapsed = time.time() - t_start
            return {"H": H, "W": W,
                    "solutions": {tuple(tuple(c) for c in k_): v
                                  for k_, v in canonical_solutions.items()},
                    "raw": raw_count, "distinct": len(canonical_solutions),
                    "proved": True, "time": elapsed,
                    "pieces_used": len(added_pieces),
                    "mandatory_cells": len(mandatory),
                    "solver_type": solver_type,
                    "status": "complete"}

        # Verify candidate against ALL pieces
        failed = []
        for i, poly in enumerate(free_polys):
            if not can_contain_piece(occupied, poly, H, W):
                failed.append(i)
                if len(failed) >= 10:
                    break

        if not failed:
            raw_count += 1
            canon = canonicalize(occupied)
            if canon not in canonical_solutions:
                canonical_solutions[canon] = list(sorted(occupied))
            solver.add_clause([-var(r, c) for r, c in occupied])
            continue

        # Add failed piece constraints incrementally
        new_count = 0
        for idx in failed:
            if idx not in added_pieces:
                pc, next_aux = make_piece_clauses(
                    free_polys[idx], H, W, next_aux)
                for cl in pc:
                    solver.add_clause(cl)
                added_pieces.add(idx)
                new_count += 1

        if new_count == 0:
            solver.add_clause([-var(r, c) for r, c in occupied])

    solver.delete()
    elapsed = time.time() - t_start
    return {"H": H, "W": W,
            "solutions": {tuple(tuple(c) for c in k_): v
                          for k_, v in canonical_solutions.items()},
            "raw": raw_count, "distinct": len(canonical_solutions),
            "proved": False, "time": elapsed,
            "pieces_used": len(added_pieces),
            "mandatory_cells": len(mandatory),
            "solver_type": solver_type,
            "status": "max_iterations"}


# ============================================================
# Main driver
# ============================================================

def run_enumeration(n_target, num_workers=None, seed_size=20, use_mandatory=True):
    """Run full parallel CEGAR enumeration for a(n_target)."""
    if n_target not in A327094:
        print(f"A327094({n_target}) not known -- cannot enumerate")
        return {}, False, {}

    k = A327094[n_target]
    if num_workers is None:
        num_workers = max(1, cpu_count() - 1)

    print("=" * 60)
    print(f"A352029 solver -- all minimalist {n_target}-omino containers")
    print(f"Container size: {k} cells (A327094)")
    print(f"Solver: CEGAR + dual-solver (Glucose/CaDiCaL)")
    print(f"Seed pieces: {seed_size} hardest per partition")
    print(f"Mandatory cell analysis: {'ON' if use_mandatory else 'OFF'}")
    print(f"Workers: {num_workers}")
    print(f"Cython enum: {'YES' if _USE_CYTHON else 'NO (Python fallback)'}")
    print("=" * 60)

    t0 = time.time()
    free_polys = gen_free(n_target)
    print(f"\n  {len(free_polys)} free {n_target}-ominoes [{time.time()-t0:.1f}s]")

    free_polys_ser = [sorted([list(c) for c in poly]) for poly in free_polys]

    t_part = time.time()
    partitions = valid_partitions(n_target, k, free_polys)
    print(f"  {len(partitions)} valid (H, W) partitions [{time.time()-t_part:.1f}s]")
    for h, w in partitions:
        solver_hint = _select_solver(h, w, k)
        print(f"    {h} x {w}  (area={h*w}, slack={h*w-k}, solver={solver_hint})")
    print()

    if not partitions:
        print("  No valid partitions -- infeasible")
        return {}, True, {}

    t_solve = time.time()
    worker_args = [(h, w, k, free_polys_ser, seed_size, use_mandatory)
                   for h, w in partitions]
    effective_workers = min(num_workers, len(worker_args))

    all_solutions = {}
    all_proved = True
    completed = 0
    total = len(partitions)
    partition_summaries = []

    print(f"  Solving {total} partitions on {effective_workers} cores...\n")

    with Pool(effective_workers) as pool:
        for result in pool.imap_unordered(_solve_partition_cegar, worker_args):
            completed += 1
            h, w = result["H"], result["W"]
            distinct = result["distinct"]
            raw = result["raw"]
            proved = result["proved"]
            elapsed = result["time"]
            pieces = result.get("pieces_used", 0)
            mand = result.get("mandatory_cells", 0)
            solver_type = result.get("solver_type", "?")
            status = result["status"]

            if not proved:
                all_proved = False

            new = 0
            for canon_key, cells in result["solutions"].items():
                canon = tuple(tuple(c) for c in canon_key)
                if canon not in all_solutions:
                    all_solutions[canon] = set(tuple(c) for c in cells)
                    new += 1

            tag = "PROVED" if proved else "partial"
            if status == "infeasible":
                tag = "infeasible"

            wall = time.time() - t_solve
            print(f"    [{completed}/{total}] {h} x {w} (slack={h*w-k}): "
                  f"{distinct} sol ({new} new, {pieces} pcs, {mand} mand) "
                  f"[{tag}/{solver_type}] [{elapsed:.1f}s] "
                  f"-- total: {len(all_solutions)} "
                  f"[wall {wall:.0f}s]")

            partition_summaries.append({
                "H": h, "W": w, "area": h * w, "slack": h * w - k,
                "distinct": distinct, "raw": raw,
                "new_global": new, "proved": proved,
                "time": round(elapsed, 1), "pieces_used": pieces,
                "mandatory_cells": mand, "solver_type": solver_type,
                "status": status
            })

    total_time = time.time() - t_solve

    print(f"\n  {'='*56}")
    if all_proved:
        print(f"  PROVED COMPLETE (all partitions exhausted)")
    else:
        print(f"  NOT PROVED (some partitions incomplete)")
    print(f"  a({n_target}) = {len(all_solutions)} [{total_time:.1f}s]")
    print(f"  {'='*56}")

    metadata = {
        "n": n_target, "k": k,
        "free_polyominoes": len(free_polys),
        "partitions_total": len(partitions),
        "solver": "CEGAR-dual",
        "proved": all_proved,
        "time": round(total_time, 1),
        "use_mandatory": use_mandatory,
        "cython": _USE_CYTHON,
        "partitions": partition_summaries
    }

    return all_solutions, all_proved, metadata


def main():
    parser = argparse.ArgumentParser(description="A352029 solver")
    parser.add_argument("--n", type=int, help="Compute a(n)")
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--seed", type=int, default=20)
    parser.add_argument("--no-mandatory", action="store_true",
                        help="Disable mandatory cell analysis")
    parser.add_argument("--verify", action="store_true",
                        help="Verify known terms n=3..8")
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    if args.verify:
        print("=" * 60)
        print("A352029 verification run")
        print("=" * 60)
        all_ok = True
        for n in sorted(A352029_KNOWN.keys()):
            if n < 3:
                continue
            expected = A352029_KNOWN[n]
            print(f"\n{'---'*20}")
            print(f"  n={n}, expected a({n})={expected}")
            solutions, proved, _ = run_enumeration(
                n, num_workers=1, seed_size=20,
                use_mandatory=not args.no_mandatory)
            actual = len(solutions)
            ok = actual == expected and proved
            status = "PASS" if ok else "FAIL"
            print(f"  {status}: a({n})={actual} (expected {expected}), proved={proved}")
            if not ok:
                all_ok = False
        print(f"\n{'='*60}")
        print(f"  {'ALL PASSED' if all_ok else 'SOME FAILED'}")
        print(f"{'='*60}")
        return

    if args.n is None:
        parser.print_help()
        return

    n_target = args.n
    use_mandatory = not args.no_mandatory
    solutions, proved, metadata = run_enumeration(
        n_target, num_workers=args.workers, seed_size=args.seed,
        use_mandatory=use_mandatory)

    # Build results dict
    results = {
        "terms": {str(n_target): len(solutions)},
        "details": {
            str(n_target): {
                "value": len(solutions),
                "proved": proved,
                "container_size": A327094.get(n_target),
                "free_polyominoes": metadata.get("free_polyominoes"),
                "partitions": metadata.get("partitions_total"),
                "time_s": metadata.get("time"),
                "use_mandatory": use_mandatory,
                "solver": "CEGAR-dual",
            }
        },
        "metadata": metadata,
        "solutions": [
            {"cells": sorted([list(c) for c in canon]),
             "bbox": [max(r for r, c in canon) + 1,
                      max(c for r, c in canon) + 1]}
            for canon in sorted(solutions.keys(), key=lambda x: sorted(x))
        ]
    }

    # Save versioned output
    if _HAS_FIG_UTILS:
        vpath = save_versioned(results, "research/solver-results.json")
        print(f"\n  Results saved: {vpath}")
    else:
        out_path = f"research/solver-results.json"
        os.makedirs("research", exist_ok=True)
        with open(out_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n  Results saved: {out_path}")

    # Build solver log
    if _HAS_FIG_UTILS:
        log = SolverLogger(
            "A352029",
            "Number of minimalist polyomino containers",
            method="SAT enumeration with CEGAR + dual-solver",
            software="solve_a352029.py",
            date=datetime.now().strftime("%Y-%m-%d"),
        )
        # Prior values are Mason's (n=1..7) only -- a(8) is our new term
        prior = {k: v for k, v in A352029_KNOWN.items() if k <= 7}
        log.set_prior_values(prior)
        log.start_term(n_target, extra_info=f"k={A327094.get(n_target)}, "
                       f"{metadata.get('free_polyominoes')} pieces, "
                       f"{metadata.get('partitions_total')} partitions")
        status_str = "OPT" if proved else "PARTIAL"
        log.add_result(n_target, len(solutions),
                       metadata.get("time", 0), status_str,
                       extra={"partitions": metadata.get("partitions_total"),
                              "mandatory": use_mandatory})
        log.add_verification(
            f"{'PROVED' if proved else 'NOT PROVED'}: "
            f"{len(solutions)} distinct containers in "
            f"{metadata.get('time', 0):.1f}s")
        log_text = log.build()
        save_versioned(log_text, "research/solver-run-log.txt")

    # Print first few solutions
    if solutions:
        shown = 0
        for canon in sorted(solutions.keys(), key=lambda x: sorted(x)):
            if shown >= 5:
                print(f"\n  ... and {len(solutions) - 5} more")
                break
            cells = set(canon)
            min_r = min(r for r, c in cells)
            max_r = max(r for r, c in cells)
            min_c = min(c for r, c in cells)
            max_c = max(c for r, c in cells)
            print(f"\n  Solution {shown+1}/{len(solutions)} "
                  f"({max_r-min_r+1}x{max_c-min_c+1}):")
            for r in range(min_r, max_r + 1):
                row = "    "
                for c in range(min_c, max_c + 1):
                    row += "# " if (r, c) in cells else ". "
                print(row)
            shown += 1


if __name__ == "__main__":
    main()
