"""Behavioral checks for sciagent-skills-docs-document-geo-superseriessubseries-handl (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sciagent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/geo-database/SKILL.md')
    assert '6. **Always resolve SubSeries before analysis**: After loading any GSE, inspect `gse.metadata.get("relation", [])` for `"SuperSeries of: ..."` entries. If present, iterate every referenced SubSeries a' in text, "expected to find: " + '6. **Always resolve SubSeries before analysis**: After loading any GSE, inspect `gse.metadata.get("relation", [])` for `"SuperSeries of: ..."` entries. If present, iterate every referenced SubSeries a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/geo-database/SKILL.md')
    assert 'Multi-assay or multi-batch submissions (e.g., RNA-seq + ATAC-seq) are organized as a **SuperSeries** GSE that references one or more **SubSeries** GSEs. Each SubSeries holds its own samples, platform,' in text, "expected to find: " + 'Multi-assay or multi-batch submissions (e.g., RNA-seq + ATAC-seq) are organized as a **SuperSeries** GSE that references one or more **SubSeries** GSEs. Each SubSeries holds its own samples, platform,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/geo-database/SKILL.md')
    assert '| GSE has no samples / empty `gse.gsms` | Accession is a SuperSeries | Parse `gse.metadata["relation"]` for `SuperSeries of:` entries and download each SubSeries |' in text, "expected to find: " + '| GSE has no samples / empty `gse.gsms` | Accession is a SuperSeries | Parse `gse.metadata["relation"]` for `SuperSeries of:` entries and download each SubSeries |'[:80]

