# docs: add check-before-install guidance to skill Prerequisites

Source: [jaechang-hits/SciAgent-Skills#13](https://github.com/jaechang-hits/SciAgent-Skills/pull/13)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `skills/genomics-bioinformatics/bcftools-variant-manipulation/SKILL.md`
- `skills/genomics-bioinformatics/bedtools-genomic-intervals/SKILL.md`
- `skills/genomics-bioinformatics/biopython-sequence-analysis/SKILL.md`
- `skills/genomics-bioinformatics/bwa-mem2-dna-aligner/SKILL.md`
- `skills/genomics-bioinformatics/cnvkit-copy-number/SKILL.md`
- `skills/genomics-bioinformatics/etetoolkit/SKILL.md`
- `skills/genomics-bioinformatics/fastp-fastq-preprocessing/SKILL.md`
- `skills/genomics-bioinformatics/featurecounts-rna-counting/SKILL.md`
- `skills/genomics-bioinformatics/gatk-variant-calling/SKILL.md`
- `skills/genomics-bioinformatics/homer-motif-analysis/SKILL.md`
- `skills/genomics-bioinformatics/macs3-peak-calling/SKILL.md`
- `skills/genomics-bioinformatics/multiqc-qc-reports/SKILL.md`
- `skills/genomics-bioinformatics/plink2-gwas-analysis/SKILL.md`
- `skills/genomics-bioinformatics/prokka-genome-annotation/SKILL.md`
- `skills/genomics-bioinformatics/salmon-rna-quantification/SKILL.md`
- `skills/genomics-bioinformatics/samtools-bam-processing/SKILL.md`
- `skills/genomics-bioinformatics/snpeff-variant-annotation/SKILL.md`
- `skills/genomics-bioinformatics/star-rna-seq-aligner/SKILL.md`
- `skills/scientific-computing/nextflow-workflow-engine/SKILL.md`
- `skills/scientific-computing/snakemake-workflow-engine/SKILL.md`

## What to add / change

## Summary
- Adds a **Check before installing** note to 20 SKILL.md Prerequisites sections (plink2, fastp, macs3, bwa-mem2, STAR, GATK, featureCounts, snpEff, cnvkit, bcftools, salmon, MultiQC, BioPython, Prokka, HOMER, bedtools, samtools, ete, snakemake, nextflow) telling the agent to `command -v <tool>` first and prefer `pixi run <tool>` inside pixi projects.
- plink2 skill additionally wraps its install block in an `if command -v plink2` guard as a canonical example.
- Adds the rule to the `CLAUDE.md` quality checklist so future skills follow it.

## Motivation
Agents were blindly re-running the install steps in skills even when the executable was already present (typically inside a pixi env), wasting time and risking clobbering working installs.

## Test plan
- [x] `pixi run test` — 4093 passed
- [x] Spot-checked fastp and plink2 Prerequisites sections render correctly
- [x] `grep -l "Check before installing" skills/` returns all 20 expected files

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
