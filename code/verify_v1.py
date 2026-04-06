"""
Independent verifier #1 for A352029.

Reads solver-results.json, independently checks:
1. Each container has exactly k = A327094(n) cells
2. Each container is connected
3. Every free n-omino fits inside each container
4. Local optimality: removing any cell breaks connectivity or containment
5. All containers are distinct under free polyomino equivalence

Uses its OWN polyomino generation and placement code (no solver imports).
Coordinate system: (row, col), 4-connected square grid.

Usage:
    python verify_v1.py [max_n]   # verify up to max_n (default 8)
"""

import sys
import os
import json
from collections import deque

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

A327094 = {1: 1, 2: 2, 3: 4, 4: 6, 5: 9, 6: 12, 7: 17, 8: 20, 9: 26}
A352029_KNOWN = {1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 14, 7: 204, 8: 7}

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# === Polyomino generation (independent implementation) ===

def _norm(cells):
    """Normalize: translate so min row and min col are 0."""
    fs = frozenset(cells)
    mr = min(r for r, _ in fs)
    mc = min(c for _, c in fs)
    return frozenset((r - mr, c - mc) for r, c in fs)


def _all_orientations(cells):
    """Generate all 8 orientations (4 rotations x 2 reflections).
    Uses matrix transformations, NOT the solver's _rot90/_flip."""
    fs = frozenset(cells)
    results = set()
    # 4 rotations
    cur = fs
    for _ in range(4):
        results.add(_norm(cur))
        results.add(_norm(frozenset((-r, c) for r, c in cur)))  # reflect
        cur = frozenset((c, -r) for r, c in cur)  # rotate 90 CW
    return list(results)


def _canonical(cells):
    """Canonical form: lex-smallest among all orientations."""
    best = None
    for ori in _all_orientations(cells):
        t = tuple(sorted(ori))
        if best is None or t < best:
            best = t
    return frozenset(best)


def generate_free_polyominoes(n):
    """Generate all free n-ominoes via incremental growth + canonical dedup."""
    if n == 1:
        return [frozenset([(0, 0)])]
    smaller = generate_free_polyominoes(n - 1)
    # Grow all fixed (n-1)-ominoes by one cell
    grown = set()
    for poly in smaller:
        for ori in _all_orientations(poly):  # all fixed orientations
            for r, c in ori:
                for dr, dc in DIRS:
                    nr, nc = r + dr, c + dc
                    if (nr, nc) not in ori:
                        new = _norm(ori | {(nr, nc)})
                        grown.add(new)
    # Dedup under free equivalence
    seen = set()
    free = []
    for p in grown:
        c = _canonical(p)
        ct = tuple(sorted(c))
        if ct not in seen:
            seen.add(ct)
            free.append(p)
    return free


# === Verification functions ===

def is_connected(cells):
    """BFS connectivity check."""
    if len(cells) <= 1:
        return True
    cells = set(cells)
    start = next(iter(cells))
    visited = {start}
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        for dr, dc in DIRS:
            nb = (r + dr, c + dc)
            if nb in cells and nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return len(visited) == len(cells)


def piece_fits_in(container_set, piece):
    """Check if piece fits in container under any orientation and translation."""
    for ori in _all_orientations(piece):
        cells = list(ori)
        mr = max(r for r, _ in cells)
        mc = max(c for _, c in cells)
        for dr in range(-min(r for r, _ in cells),
                         max(r for r, _ in container_set) - mr + 1):
            for dc in range(-min(c for _, c in cells),
                             max(c for _, c in container_set) - mc + 1):
                placed = {(r + dr, c + dc) for r, c in cells}
                if placed.issubset(container_set):
                    return True
    return False


def check_local_optimality(container_set, free_polys):
    """For each cell, check that removing it breaks connectivity or containment."""
    for cell in container_set:
        reduced = container_set - {cell}
        if not is_connected(reduced):
            continue  # removal disconnects -> cell is needed
        # Check if all pieces still fit
        all_fit = True
        for poly in free_polys:
            if not piece_fits_in(reduced, poly):
                all_fit = False
                break
        if all_fit:
            return False, cell  # cell is removable -> NOT locally optimal
    return True, None


def verify_n(n, solutions_data):
    """Verify all solutions for a given n."""
    k = A327094[n]
    free_polys = generate_free_polyominoes(n)
    expected_count = A352029_KNOWN.get(n)

    print(f"\n  n={n}: k={k}, {len(free_polys)} free {n}-ominoes, "
          f"expected a({n})={expected_count}")

    if len(solutions_data) == 0 and expected_count == 0:
        print(f"    PASS: 0 solutions (expected 0)")
        return True

    errors = []
    canonicals = set()

    for i, sol in enumerate(solutions_data):
        cells = frozenset(tuple(c) for c in sol["cells"])

        # Check 1: cell count
        if len(cells) != k:
            errors.append(f"    FAIL sol {i}: {len(cells)} cells (expected {k})")
            continue

        # Check 2: connectivity
        if not is_connected(cells):
            errors.append(f"    FAIL sol {i}: disconnected")
            continue

        # Check 3: all pieces fit
        for j, poly in enumerate(free_polys):
            if not piece_fits_in(cells, poly):
                errors.append(f"    FAIL sol {i}: piece {j} does not fit")
                break

        # Check 4: local optimality
        is_opt, removable = check_local_optimality(cells, free_polys)
        if not is_opt:
            errors.append(f"    FAIL sol {i}: cell {removable} removable "
                          f"(NOT locally optimal)")

        # Check 5: canonical dedup
        canon = _canonical(cells)
        ct = tuple(sorted(canon))
        if ct in canonicals:
            errors.append(f"    FAIL sol {i}: duplicate canonical form")
        canonicals.add(ct)

    actual = len(canonicals)
    if expected_count is not None and actual != expected_count:
        errors.append(f"    FAIL: count mismatch: got {actual}, expected {expected_count}")

    if errors:
        for e in errors:
            print(e)
        return False

    print(f"    PASS: {actual} solutions verified "
          f"(cells={k}, connected, all pieces fit, locally optimal, unique)")
    return True


def main():
    max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 8

    results_path = os.path.join(_project_root, "research", "solver-results.json")
    if not os.path.exists(results_path):
        print(f"ERROR: {results_path} not found")
        sys.exit(1)

    with open(results_path) as f:
        data = json.load(f)

    print("=" * 60)
    print("A352029 Independent Verifier #1")
    print("=" * 60)

    # For each n in known range, load results and verify
    all_ok = True
    for n in range(3, max_n + 1):
        n_str = str(n)
        if n_str in data.get("terms", {}):
            solutions = data.get("solutions", [])
            if not verify_n(n, solutions):
                all_ok = False
        elif n in A352029_KNOWN:
            # Need to run solver for this n -- just check known value
            print(f"\n  n={n}: no solver data in results file, skipping")

    print(f"\n{'='*60}")
    print(f"  {'ALL PASSED' if all_ok else 'SOME FAILED'}")
    print(f"{'='*60}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
