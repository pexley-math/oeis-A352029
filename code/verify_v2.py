"""
Independent verifier #2 for A352029.

COMPLETELY DISJOINT code path from solver and verifier #1.
Uses complex-number coordinates for rotations/reflections instead of
matrix-based transforms. Different BFS iteration order (reversed neighbors).
Different canonicalization (sorted tuples compared as strings).

Reads solver-results.json, independently checks:
1. Cell count = A327094(n)
2. Connected (BFS with reversed neighbor order)
3. All free n-ominoes fit (complex-number orientation computation)
4. Local optimality (removing any single cell invalidates container)
5. All containers are distinct canonical forms

Usage:
    python verify_v2.py [max_n]
"""

import sys
import os
import json
from collections import deque

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

A327094 = {1: 1, 2: 2, 3: 4, 4: 6, 5: 9, 6: 12, 7: 17, 8: 20, 9: 26}
A352029_KNOWN = {1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 14, 7: 204, 8: 7}


# === Complex-number based polyomino operations ===
# Each cell (r, c) maps to complex number r + c*1j
# Rotation 90 CW: multiply by -1j (i.e., z -> -1j * z)
# Reflection: conjugate (i.e., z -> z.conjugate())

def _cells_to_complex(cells):
    return frozenset(complex(r, c) for r, c in cells)


def _complex_to_cells(zs):
    return frozenset((int(round(z.real)), int(round(z.imag))) for z in zs)


def _cnorm(zs):
    """Normalize complex set: translate so min real and min imag are 0."""
    mr = min(z.real for z in zs)
    mc = min(z.imag for z in zs)
    offset = complex(mr, mc)
    return frozenset(z - offset for z in zs)


def _c_orientations(cells):
    """All 8 orientations via complex multiplication and conjugation."""
    zs = _cells_to_complex(cells)
    results = set()
    cur = zs
    for _ in range(4):
        n = _cnorm(cur)
        results.add(n)
        # Reflect: conjugate
        ref = frozenset(z.conjugate() for z in cur)
        results.add(_cnorm(ref))
        # Rotate 90 CW: multiply by -1j
        cur = frozenset(-1j * z for z in cur)
    return [_complex_to_cells(o) for o in results]


def _c_canonical(cells):
    """Canonical form via complex-number orientations, string comparison."""
    best = None
    for ori in _c_orientations(cells):
        # Use string representation of sorted tuples for comparison
        # This is intentionally different from verifier #1's tuple comparison
        key = str(sorted(ori))
        if best is None or key < best[0]:
            best = (key, frozenset(ori))
    return best[1]


# === Polyomino generation (via complex numbers) ===

def _gen_free_complex(n):
    """Generate free n-ominoes using complex-number growth."""
    CDIRS = [1+0j, -1+0j, 0+1j, 0-1j]
    if n == 1:
        return [frozenset([(0, 0)])]

    # Generate fixed polyominoes
    if n == 1:
        fixed = [frozenset([0+0j])]
    else:
        prev_free = _gen_free_complex(n - 1)
        # Expand each free polyomino through all orientations to get fixed
        fixed_set = set()
        for poly in prev_free:
            for ori in _c_orientations(poly):
                zs = _cells_to_complex(ori)
                nzs = _cnorm(zs)
                for z in nzs:
                    for d in CDIRS:
                        nb = z + d
                        if nb not in nzs:
                            new = _cnorm(nzs | {nb})
                            fixed_set.add(new)
        # Convert to cell tuples and dedup as free
        seen = set()
        result = []
        for zs in fixed_set:
            cells = _complex_to_cells(zs)
            canon = _c_canonical(cells)
            key = str(sorted(canon))
            if key not in seen:
                seen.add(key)
                result.append(cells)
        return result

    return []


# === Verification (disjoint implementation) ===

def _bfs_connected(cells):
    """BFS connectivity with REVERSED neighbor order (disjoint from v1)."""
    if len(cells) <= 1:
        return True
    cell_set = set(cells)
    start = min(cell_set)  # different start selection than v1
    visited = {start}
    queue = deque([start])
    # Reversed direction order
    rdirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    while queue:
        r, c = queue.popleft()
        for dr, dc in rdirs:
            nb = (r + dr, c + dc)
            if nb in cell_set and nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return len(visited) == len(cell_set)


def _piece_fits(container, piece):
    """Check if piece fits using complex-number orientations."""
    cs = set(container)
    for ori in _c_orientations(piece):
        cells = list(ori)
        for anchor in cs:
            # Try placing first cell of ori at each container cell
            base = cells[0]
            dr, dc = anchor[0] - base[0], anchor[1] - base[1]
            placed = {(r + dr, c + dc) for r, c in cells}
            if placed.issubset(cs):
                return True
    return False


def _check_local_opt(container, free_polys):
    """Local optimality: each cell is essential."""
    cs = set(container)
    for cell in cs:
        reduced = cs - {cell}
        if not _bfs_connected(reduced):
            continue  # articulation point
        all_fit = True
        for poly in free_polys:
            if not _piece_fits(reduced, poly):
                all_fit = False
                break
        if all_fit:
            return False, cell
    return True, None


def verify_n(n, solutions_data):
    """Verify solutions for n."""
    k = A327094[n]
    free_polys = _gen_free_complex(n)
    expected = A352029_KNOWN.get(n)

    print(f"\n  n={n}: k={k}, {len(free_polys)} free {n}-ominoes, "
          f"expected={expected}")

    errors = []
    canon_set = set()

    for i, sol in enumerate(solutions_data):
        cells = frozenset(tuple(c) for c in sol["cells"])

        if len(cells) != k:
            errors.append(f"    FAIL sol {i}: {len(cells)} cells != {k}")
            continue

        if not _bfs_connected(cells):
            errors.append(f"    FAIL sol {i}: disconnected")
            continue

        for j, poly in enumerate(free_polys):
            if not _piece_fits(cells, poly):
                errors.append(f"    FAIL sol {i}: piece {j} no fit")
                break

        is_opt, removable = _check_local_opt(cells, free_polys)
        if not is_opt:
            errors.append(f"    FAIL sol {i}: {removable} removable")

        canon = _c_canonical(cells)
        ckey = str(sorted(canon))
        if ckey in canon_set:
            errors.append(f"    FAIL sol {i}: duplicate")
        canon_set.add(ckey)

    actual = len(canon_set)
    if expected is not None and actual != expected:
        errors.append(f"    FAIL: count {actual} != expected {expected}")

    if errors:
        for e in errors:
            print(e)
        return False

    print(f"    PASS: {actual} verified (k={k}, connected, fits, optimal, unique)")
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
    print("A352029 Independent Verifier #2 (complex-number coords)")
    print("=" * 60)

    all_ok = True
    for n in range(3, max_n + 1):
        n_str = str(n)
        if n_str in data.get("terms", {}):
            solutions = data.get("solutions", [])
            if not verify_n(n, solutions):
                all_ok = False

    print(f"\n{'='*60}")
    print(f"  {'ALL PASSED' if all_ok else 'SOME FAILED'}")
    print(f"{'='*60}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
