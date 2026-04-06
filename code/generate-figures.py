"""Generate publication figures for A352029.

Reads solver-results.json and produces Typst figures showing
all minimalist containers for our new term a(8) = 7.
"""

import sys
import os
import json
import glob

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_paper_root = os.path.dirname(_project_root)
sys.path.insert(0, _paper_root)

from figure_gen_utils.document_builder import DocumentBuilder


def find_solutions_file():
    """Find the latest solver-results file with solutions."""
    files = sorted(glob.glob(
        os.path.join(_project_root, "research", "solver-results-*.json")),
        reverse=True)
    for f in files:
        with open(f) as fh:
            d = json.load(fh)
        if "solutions" in d and len(d["solutions"]) > 0:
            return f, d
    # Fallback to stable name
    stable = os.path.join(_project_root, "research", "solver-results.json")
    with open(stable) as fh:
        return stable, json.load(fh)


def main():
    os.chdir(_project_root)

    src_path, data = find_solutions_file()
    solutions = data.get("solutions", [])
    n_target = data.get("metadata", {}).get("n", 8)
    k = data.get("metadata", {}).get("k", 20)

    if not solutions:
        print("No solutions found in results file")
        return

    print(f"Generating figures for a({n_target}) = {len(solutions)} "
          f"from {src_path}")

    doc = DocumentBuilder(
        title="A352029: Number of Minimalist Polyomino Containers",
        description=(
            "a(n) = number of distinct free polyominoes of minimum size "
            "A327094(n) containing all free n-ominoes"
        ),
        sequence_line="1, 1, 2, 2, 2, 14, 204, 7",
        author="Peter Exley",
        date="April 2026",
    )

    doc.set_binary_legend(
        ["Occupied", "Empty"],
        ["#4A90D9", "#F0F0F0"],
    )

    for i, sol in enumerate(solutions):
        cells_list = sol["cells"]
        cells_set = set(tuple(c) for c in cells_list)
        bbox = sol["bbox"]
        rows, cols = bbox[0], bbox[1]

        doc.add_binary_figure(
            cells=cells_set,
            bbox_rows=rows,
            bbox_cols=cols,
            n=n_target,
            k=k,
            status="PROVED",
            method=f"CEGAR + Glucose 4.2",
            mode="container",
            detail_text=f"Solution {i+1}/{len(solutions)}, "
                        f"{rows} x {cols} bounding box",
        )

    output_path = "submission/a352029-n8-figures.typ"
    os.makedirs("submission", exist_ok=True)
    doc.generate(output_path)
    print(f"Generated: {output_path}")

    # Try to compile
    try:
        doc.compile()
        print(f"Compiled to PDF")
    except Exception as e:
        print(f"Compilation skipped: {e}")


if __name__ == "__main__":
    main()
