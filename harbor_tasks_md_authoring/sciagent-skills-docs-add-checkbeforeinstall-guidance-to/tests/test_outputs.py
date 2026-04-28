"""Behavioral checks for sciagent-skills-docs-add-checkbeforeinstall-guidance-to (markdown_authoring task).

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
    text = _read('CLAUDE.md')
    assert '- [ ] **Check-before-install**: Prerequisites sections for CLI executables include a note telling the agent to run `command -v <tool>` first and skip the install commands if the tool is already presen' in text, "expected to find: " + '- [ ] **Check-before-install**: Prerequisites sections for CLI executables include a note telling the agent to run `command -v <tool>` first and skip the install commands if the tool is already presen'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/bcftools-variant-manipulation/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v bcftools` first and skip the install commands below i' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v bcftools` first and skip the install commands below i'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/bedtools-genomic-intervals/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v bedtools` first and skip the install commands below i' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v bedtools` first and skip the install commands below i'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/biopython-sequence-analysis/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v python` first and skip the install commands below if ' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v python` first and skip the install commands below if '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/bwa-mem2-dna-aligner/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v bwa-mem2` first and skip the install commands below i' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v bwa-mem2` first and skip the install commands below i'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/cnvkit-copy-number/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v cnvkit.py` first and skip the install commands below ' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v cnvkit.py` first and skip the install commands below '[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/etetoolkit/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v python` first and skip the install commands below if ' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v python` first and skip the install commands below if '[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/fastp-fastq-preprocessing/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v fastp` first and skip the install commands below if i' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v fastp` first and skip the install commands below if i'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/featurecounts-rna-counting/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v featureCounts` first and skip the install commands be' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v featureCounts` first and skip the install commands be'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/gatk-variant-calling/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v gatk` first and skip the install commands below if it' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v gatk` first and skip the install commands below if it'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/homer-motif-analysis/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v findMotifsGenome.pl` first and skip the install comma' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v findMotifsGenome.pl` first and skip the install comma'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/macs3-peak-calling/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v macs3` first and skip the install commands below if i' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v macs3` first and skip the install commands below if i'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/multiqc-qc-reports/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v multiqc` first and skip the install commands below if' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v multiqc` first and skip the install commands below if'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/plink2-gwas-analysis/SKILL.md')
    assert '> **Check before installing**: The tool may already be available (e.g., inside a `pixi` / `conda` env). Always run `command -v plink2` first and skip the install block if it returns a path. When execu' in text, "expected to find: " + '> **Check before installing**: The tool may already be available (e.g., inside a `pixi` / `conda` env). Always run `command -v plink2` first and skip the install block if it returns a path. When execu'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/plink2-gwas-analysis/SKILL.md')
    assert 'wget https://s3.amazonaws.com/plink2-assets/alpha6/plink2_linux_avx2_20241112.zip' in text, "expected to find: " + 'wget https://s3.amazonaws.com/plink2-assets/alpha6/plink2_linux_avx2_20241112.zip'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/plink2-gwas-analysis/SKILL.md')
    assert '# wget https://s3.amazonaws.com/plink2-assets/alpha6/plink2_mac_20241112.zip' in text, "expected to find: " + '# wget https://s3.amazonaws.com/plink2-assets/alpha6/plink2_mac_20241112.zip'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/prokka-genome-annotation/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v prokka` first and skip the install commands below if ' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v prokka` first and skip the install commands below if '[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/salmon-rna-quantification/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v salmon` first and skip the install commands below if ' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v salmon` first and skip the install commands below if '[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/samtools-bam-processing/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v samtools` first and skip the install commands below i' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v samtools` first and skip the install commands below i'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/snpeff-variant-annotation/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v snpEff` first and skip the install commands below if ' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v snpEff` first and skip the install commands below if '[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/genomics-bioinformatics/star-rna-seq-aligner/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v STAR` first and skip the install commands below if it' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v STAR` first and skip the install commands below if it'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/nextflow-workflow-engine/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v nextflow` first and skip the install commands below i' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v nextflow` first and skip the install commands below i'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/scientific-computing/snakemake-workflow-engine/SKILL.md')
    assert '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v snakemake` first and skip the install commands below ' in text, "expected to find: " + '> **Check before installing**: The tool may already be available in the current environment (e.g., inside a `pixi` / `conda` env). Run `command -v snakemake` first and skip the install commands below '[:80]

