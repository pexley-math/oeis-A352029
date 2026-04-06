# A352029 -- Number of Minimalist Polyomino Containers

Computational results for OEIS sequence [A352029](https://oeis.org/A352029).

a(n) = the number of distinct free polyominoes of minimum size A327094(n) cells
that contain all free n-ominoes as subshapes.

## Known Terms

| n | a(n) | Container size | Free n-ominoes | Method |
|---|------|---------------|----------------|--------|
| 1 | 1 | 1 | 1 | trivial |
| 2 | 1 | 2 | 1 | trivial |
| 3 | 2 | 4 | 2 | SAT enum |
| 4 | 2 | 6 | 5 | SAT enum |
| 5 | 2 | 9 | 12 | SAT enum |
| 6 | 14 | 12 | 35 | SAT enum |
| 7 | 204 | 17 | 108 | SAT enum |
| 8 | **7** | 20 | 369 | **SAT enum (CEGAR)** |

a(8) = 7 is our new contribution, proved by exhaustive enumeration.

## Method

SAT enumeration with CEGAR (Counter-Example Guided Abstraction Refinement).
For each valid bounding box (H, W), the solver:
1. Builds a SAT formula encoding: exactly k cells, connectivity, border-touching,
   lex-leader symmetry breaking, and piece-containment constraints
2. Uses CEGAR to add piece constraints lazily (start with 20 hardest pieces)
3. Enumerates all solutions, canonicalizes under free polyomino equivalence
4. Deduplicates across all bounding box partitions

Backend: Glucose 4.2 for SAT-expected partitions, CaDiCaL 1.9.5 for UNSAT.
Independently verified by two verifiers with disjoint code paths.

## Files

- `code/solve_a352029.py` -- Main solver
- `code/verify_v1.py` -- Independent verifier #1 (matrix orientations)
- `code/verify_v2.py` -- Independent verifier #2 (complex-number orientations)
- `code/generate-figures.py` -- Figure generator
- `research/solver-results.json` -- Proved terms and solution data
- `submission/a352029-n8-figures.pdf` -- Publication figures for a(8)

## License

CC BY 4.0
