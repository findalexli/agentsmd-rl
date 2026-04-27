"""Behavioral checks for sciagent-skills-enhance-add-read-group-extraction (markdown_authoring task).

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
    text = _read('skills/genomics-bioinformatics/pysam-genomic-files/SKILL.md')
    assert 'description: "Read/write SAM/BAM/CRAM alignments, VCF/BCF variants, FASTA/FASTQ sequences. Region queries, coverage/pileup analysis, variant filtering, read group extraction. Python wrapper for htslib' in text, "expected to find: " + 'description: "Read/write SAM/BAM/CRAM alignments, VCF/BCF variants, FASTA/FASTQ sequences. Region queries, coverage/pileup analysis, variant filtering, read group extraction. Python wrapper for htslib'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/pysam-genomic-files/SKILL.md')
    assert '| Read group filter returns 0 reads | RG tag missing or wrong ID specified | Verify RG tag exists: `read.has_tag("RG")`; list available RGs from `bam.header.get("RG", [])` |' in text, "expected to find: " + '| Read group filter returns 0 reads | RG tag missing or wrong ID specified | Verify RG tag exists: `read.has_tag("RG")`; list available RGs from `bam.header.get("RG", [])` |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/pysam-genomic-files/SKILL.md')
    assert 'print(f"  ID: {rg_dict[\'ID\']}, Sample: {rg_dict.get(\'SM\', \'N/A\')}, Library: {rg_dict.get(\'LB\', \'N/A\')}, Platform: {rg_dict.get(\'PL\', \'N/A\')}")' in text, "expected to find: " + 'print(f"  ID: {rg_dict[\'ID\']}, Sample: {rg_dict.get(\'SM\', \'N/A\')}, Library: {rg_dict.get(\'LB\', \'N/A\')}, Platform: {rg_dict.get(\'PL\', \'N/A\')}")'[:80]

