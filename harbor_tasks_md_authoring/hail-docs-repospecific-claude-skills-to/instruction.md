# [docs] Repo-specific claude skills to help with batch and batch-dev activities

Source: [hail-is/hail#15351](https://github.com/hail-is/hail/pull/15351)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/hail-batch-dev.md`
- `.claude/skills/hail-batch.md`

## What to add / change

## Change Description

Adds two markdown files to help claude interact with the batch service in both general, and dev-specific ways.

In a claude session within the hail repo, these can be triggered with 
- `/hail-batch` - general purpose instructions for interacting with the batch service
- `/hail-batch-dev` - additional instructions specific to interacting with the batch service during development

## Security Assessment

- This change cannot impact the Hail Batch instance as deployed by Broad Institute in GCP

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
