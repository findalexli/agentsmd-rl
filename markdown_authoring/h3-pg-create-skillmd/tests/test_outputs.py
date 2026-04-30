"""Behavioral checks for h3-pg-create-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/h3-pg")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/SKILL.md')
    assert '- `h3_get_resolution_from_tile_zoom(z, [max_h3_resolution=15], [min_h3_resolution], [hex_edge_pixels=44], [tile_size=512])` — returns optimal H3 resolution for XYZ tile zoom level `z`, targeting hexag' in text, "expected to find: " + '- `h3_get_resolution_from_tile_zoom(z, [max_h3_resolution=15], [min_h3_resolution], [hex_edge_pixels=44], [tile_size=512])` — returns optimal H3 resolution for XYZ tile zoom level `z`, targeting hexag'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/SKILL.md')
    assert 'description: PostgreSQL bindings for H3 hexagonal grid system. Use when working with H3 cells in Postgres, including spatial indexing, geometry/geography integration, and raster analysis.' in text, "expected to find: " + 'description: PostgreSQL bindings for H3 hexagonal grid system. Use when working with H3 cells in Postgres, including spatial indexing, geometry/geography integration, and raster analysis.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/SKILL.md')
    assert '**Antimeridian gotcha:** Cells crossing 180° are split into valid polygons. `ST_Centroid` of a split polygon may fall outside the cell — use `h3::geometry` for centroids instead.' in text, "expected to find: " + '**Antimeridian gotcha:** Cells crossing 180° are split into valid polygons. `ST_Centroid` of a split polygon may fall outside the cell — use `h3::geometry` for centroids instead.'[:80]

