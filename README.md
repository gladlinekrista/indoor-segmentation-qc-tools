# 🏠 Indoor Segmentation QC Tools

Quality-control tooling and annotation standards for **polygon segmentation datasets** (e.g., indoor scenes labelled as `Floor`, `Wall`, `Others`). It automatically catches the boundary errors that quietly damage training data.

> **Topics:** `computer-vision` `semantic-segmentation` `data-quality` `annotation` `cvat` `shapely` `yolo`

All sample data is synthetic. No real images or client data.

---

## Why this matters
In segmentation, annotation **boundaries** decide model quality. Three errors are especially common where regions meet (e.g., Wall ↔ Floor):

| Error | Meaning | Effect on training |
|---|---|---|
| **Overlap** | Two classes cover the same pixels | Contradictory labels |
| **Gap** | Pixels belong to no region | Unlabelled/ambiguous areas |
| **Invalid polygon** | < 3 points or zero area | Corrupt or useless label |

At tens of thousands of annotations, manual spot-checking misses these. This tool checks every file.

## The tool: `check_overlaps.py`
Reads YOLO-seg label files (`class x1 y1 ... xn yn`, normalised) and reports per file:
- **OVERLAP** between different classes above a tolerance
- **GAP** (unlabelled fraction), if you set `--max-gap`
- **INVALID** polygons

It returns exit code 1 on any issue, so it can gate a CI pipeline or a dataset hand-off.

```bash
pip install -r requirements.txt
python check_overlaps.py sample_labels --max-gap 0.01
```
```
✓ clean_scene.txt
✗ gap_scene.txt
    GAP 20.00% of image unlabelled (limit 1.00%)
✗ invalid_scene.txt
    INVALID line 1: needs >= 3 (x, y) points
✗ overlap_scene.txt
    OVERLAP Wall(line 1) x Floor(line 2): 10.00% of image
```
`pytest` runs the test suite.

## Annotation standards (the workflow this supports)
1. **Class definitions:** `Floor` = walkable surfaces; `Wall` = walls/partitions; `Others` = furniture, posts, equipment, obstacles.
2. **AI-assisted first pass:** use SAM-style interactors in CVAT to generate initial masks.
3. **Manual refinement:** fix vertices on thin or complex geometry (railings, bed frames, corners).
4. **Interpolate, then verify:** propagate across frames, then correct drift. Interpolation never replaces review.
5. **Automated QC:** run `check_overlaps.py` before a batch is accepted.

## My role
> **[Edit to match]** Annotation and quality control for segmentation datasets (CVAT, AI-assisted tools, manual refinement), and author of these QC tools.

## Tech stack
Python · Shapely · pytest · CVAT (annotation) · YOLO-seg label format
