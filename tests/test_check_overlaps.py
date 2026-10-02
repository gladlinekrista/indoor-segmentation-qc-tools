from pathlib import Path

from check_overlaps import check_file, DEFAULT_CLASSES

S = Path(__file__).parent.parent / "sample_labels"


def run(name, max_gap=0.01):
    return check_file(S / name, DEFAULT_CLASSES, 0.0005, max_gap)


def test_clean_scene_passes():
    assert run("clean_scene.txt") == []


def test_overlap_detected():
    issues = run("overlap_scene.txt")
    assert any(i.startswith("OVERLAP Wall") and "10.00%" in i for i in issues)


def test_gap_detected():
    assert any(i.startswith("GAP") and "20.00%" in i for i in run("gap_scene.txt"))


def test_invalid_polygon_detected():
    assert any(i.startswith("INVALID") for i in run("invalid_scene.txt"))
