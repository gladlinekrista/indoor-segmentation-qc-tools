"""QC for polygon segmentation labels (YOLO-seg .txt format, normalised coordinates).

Line format:  <class_id> x1 y1 x2 y2 ... xn yn
Checks per file:
  1. OVERLAP: polygons of DIFFERENT classes covering the same area (e.g. Wall over Floor)
  2. GAP:     fraction of the image not covered by any polygon (for fully-labelled scenes)
  3. INVALID: polygons with < 3 points or zero area
Exit code 1 if any issue is found, so it can run in CI.
"""
import argparse
import sys
from itertools import combinations
from pathlib import Path

from shapely.geometry import Polygon
from shapely.ops import unary_union

DEFAULT_CLASSES = {0: "Floor", 1: "Wall", 2: "Others"}


def load_polygons(path: Path):
    polys, invalid = [], []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        parts = line.split()
        if not parts:
            continue
        try:
            cls, coords = int(parts[0]), list(map(float, parts[1:]))
        except ValueError:
            invalid.append((n, "non-numeric values"))
            continue
        if len(coords) < 6 or len(coords) % 2:
            invalid.append((n, "needs >= 3 (x, y) points"))
            continue
        poly = Polygon(zip(coords[0::2], coords[1::2]))
        if not poly.is_valid:
            poly = poly.buffer(0)                      # repair self-intersections
        if poly.area == 0:
            invalid.append((n, "zero area"))
            continue
        polys.append((n, cls, poly))
    return polys, invalid


def check_file(path: Path, names: dict, overlap_tol: float, max_gap: float):
    polys, invalid = load_polygons(path)
    issues = [f"INVALID line {n}: {why}" for n, why in invalid]
    for (n1, c1, p1), (n2, c2, p2) in combinations(polys, 2):
        if c1 == c2:
            continue
        inter = p1.intersection(p2).area
        if inter > overlap_tol:
            issues.append(
                f"OVERLAP {names.get(c1, c1)}(line {n1}) x {names.get(c2, c2)}(line {n2}): "
                f"{inter * 100:.2f}% of image"
            )
    if polys and max_gap is not None:
        gap = 1.0 - unary_union([p for _, _, p in polys]).intersection(Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])).area
        if gap > max_gap:
            issues.append(f"GAP {gap * 100:.2f}% of image unlabelled (limit {max_gap * 100:.2f}%)")
    return issues


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("labels_dir", type=Path)
    ap.add_argument("--overlap-tol", type=float, default=0.0005, help="max allowed cross-class overlap (fraction of image)")
    ap.add_argument("--max-gap", type=float, default=None, help="max unlabelled fraction; omit to skip gap check")
    args = ap.parse_args(argv)

    files = sorted(args.labels_dir.glob("*.txt"))
    bad = 0
    for f in files:
        issues = check_file(f, DEFAULT_CLASSES, args.overlap_tol, args.max_gap)
        if issues:
            bad += 1
            print(f"✗ {f.name}")
            for i in issues:
                print("   ", i)
        else:
            print(f"✓ {f.name}")
    print(f"\n{len(files)} files checked, {bad} with issues")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
