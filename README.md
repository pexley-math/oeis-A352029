# OEIS A352029 -- Number of Minimalist Polyomino Containers

Solver code, data, and figures for [OEIS A352029](https://oeis.org/A352029).

## The Problem

a(n) = the number of distinct free polyominoes with exactly A327094(n) cells that contain all free n-ominoes as subshapes (under translation, rotation, and reflection). These are the *minimalist containers* -- the smallest polyominoes that universally contain every n-omino, counted up to free equivalence. The input to the problem -- the number of free n-ominoes -- is [A000105](https://oeis.org/A000105). The container size is given by [A327094](https://oeis.org/A327094). The problem dates to T. R. Dawson's Minimum Common Superform question (*Fairy Chess Review* Vol. 5 No. 4, 1942).

## Results

**Known terms (proved by prior authors):**

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **a(n)** | 1 | 1 | 2 | 2 | 2 | 14 | 204 |
| **Pieces** | 1 | 1 | 2 | 5 | 12 | 35 | 108 |
| **Container size** | 1 | 2 | 4 | 6 | 9 | 12 | 17 |

Terms a(1) through a(7) were established by John Mason (2022).

**New proved term (this work):**

| n | 8 |
|:---:|:---:|
| **a(n)** | **7** |
| **Pieces** | 369 |
| **Container size** | 20 |

Proved by exhaustive SAT enumeration over all 36 valid bounding box partitions. All 7 minimalist containers are in bounding boxes 4 x 8 (6 solutions) and 5 x 8 (1 solution). Every container independently verified by two verifiers with disjoint code paths (matrix-based and complex-number orientations), both checking containment and local optimality.

**Lower bound:** a(9) >= 111 (111 distinct 26-cell containers found across 4 partitions).

## Method

Boolean satisfiability (SAT) enumeration with Counter-Example Guided Abstraction Refinement (CEGAR). For each valid bounding box (H, W), the solver encodes universal containment as SAT, then enumerates all solutions by iterative blocking and canonicalization under D_4 equivalence.

- **CEGAR:** Start with only the 20 hardest-to-place pieces (fewest valid placements). Verify candidates against all 369 pieces outside the solver. Add failed constraints lazily. Reduces formula size 10-100x and gives 10-50x speedup on satisfiable partitions.
- **Partition decomposition:** All valid (H, W) bounding boxes enumerated. Border-touching and no-gap constraints restrict search within each partition; the union over all partitions is complete. Mathematical pruning (triple-piece overhead, spanning tree bound) eliminates infeasible partitions.
- **Lex-leader symmetry breaking:** Vertical flip, horizontal flip, 180-degree rotation, and 90-degree rotation (square grids) eliminate symmetric duplicates.
- **Dual-solver selection:** Glucose 4.2 for SAT-expected partitions, CaDiCaL 1.9.5 with aggressive restarts for UNSAT-expected near-square partitions (aspect ratio > 0.6, slack <= 2). For n=8 all partitions have high slack so Glucose handles all 36; the dual-solver strategy activates at n >= 9.

## Running the Solver

**Requirements:** Python 3.8+, python-sat

```bash
pip install python-sat

# Prove a(8) = 7 (takes ~45 seconds on 8 cores)
python code/solve_a352029.py --n 8 --workers 8

# Verify known terms n=3..8
python code/solve_a352029.py --verify

# Run specific term
python code/solve_a352029.py --n 6 --workers 4
```

**Verify all proofs** (two independent verifiers, no shared code paths):

```bash
python code/verify_v1.py 8    # matrix-based orientations
python code/verify_v2.py 8    # complex-number orientations
```

## Files

| File | Description |
|------|-------------|
| `code/solve_a352029.py` | SAT+CEGAR enumeration solver |
| `code/verify_v1.py` | Independent verifier #1 (containment + local optimality) |
| `code/verify_v2.py` | Independent verifier #2 (containment + local optimality) |
| `code/generate-figures.py` | Publication figure generator |
| `research/solver-results.json` | Machine-readable results with solutions |
| `research/solver-run-log.txt` | Reviewer-grade proof of solver run |
| `submission/a352029-n8-figures.pdf` | Publication figures (all 7 containers for n=8) |
| `submission/a352029-paper.pdf` | Standalone paper |

## Prior Art and Acknowledgments

The sequence A352029 was created by John Mason (2022) with data through a(7) = 204. The companion sequence [A327094](https://oeis.org/A327094) (minimum container sizes) was created by Peter Kagey (2019). The problem generalises T. R. Dawson's 1942 Minimum Common Superform question for pentominoes (*Fairy Chess Review* Vol. 5 No. 4) to arbitrary n.

This work was inspired by the [OEIS](https://oeis.org/) and the community of contributors who maintain it.

## Hardware

AMD Ryzen 5 5600 (6-core / 12-thread), 16 GB RAM.

## License

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) -- Peter Exley, 2026.

This work is freely available. If you find it useful, a citation or acknowledgment is appreciated but not required.

## Links

- **OEIS A352029** (this sequence): https://oeis.org/A352029
- **A327094** (minimum container size): https://oeis.org/A327094
- **A000105** (free polyomino count): https://oeis.org/A000105
- T. R. Dawson, *Fairy Chess Review* Vol. 5 No. 4, 1942 -- original MCS problem. Archive: [The Problemist](https://www.theproblemist.org/mags.pl?type=fcr&page=volumes) (Vol. 5 covers 1942-1945).
- Puzzle Zapper, [Polyomino Common Superforms](https://puzzlezapper.com/aom/mathrec/polycover.html) -- secondary source on Dawson's 1942 problem.
