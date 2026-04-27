# docs: document GEO SuperSeries/SubSeries handling

Source: [jaechang-hits/SciAgent-Skills#14](https://github.com/jaechang-hits/SciAgent-Skills/pull/14)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/genomics-bioinformatics/geo-database/SKILL.md`

## What to add / change

## Summary
- Add Key Concepts section explaining SuperSeries vs SubSeries in GEO, with a snippet that resolves SubSeries accessions via `gse.metadata["relation"]`.
- Add Best Practice # 6 mandating SubSeries resolution after every GSE load so the actual sample data is not silently dropped.
- Add a Troubleshooting row for the empty `gse.gsms` symptom that occurs when a SuperSeries is downloaded directly.

## Motivation
The existing GEO skill covered GSE/GPL/GSM/GDS record types but had no guidance on multi-assay submissions that use a SuperSeries to aggregate SubSeries. Agents loading a SuperSeries accession would silently get metadata with zero samples.

## Test plan
- [x] `pixi run test` — 4093 passed

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
