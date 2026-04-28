# docs: add nemo-curator-docs Claude Code skill

Source: [NVIDIA-NeMo/Curator#1825](https://github.com/NVIDIA-NeMo/Curator/pull/1825)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/nemo-curator-docs/SKILL.md`

## What to add / change

## Description

Adds a Claude Code agent skill at `.claude/skills/nemo-curator-docs/SKILL.md` that encodes the NeMo Curator Fern authoring workflow. The skill guides agents through add/update/remove operations against the versioned `fern/versions/vXX.YY/pages/` + `vXX.YY.yml` layout, and covers Fern-native components (no GitHub-callout conversion), the `{{ variable }}` substitution pipeline, frontmatter schema, `fern check` / preview / publish steps, and a ship checklist for cutting new trains. Modeled on the Dynamo docs skill but adapted to NeMo Curator's `fern/`-only setup (the legacy `docs/` tree is deprecated).

## Usage

N/A — tooling-only change. The skill activates when an agent is asked to modify NeMo Curator documentation.

## Checklist
- [x] I am familiar with the [Contributing Guide](https://github.com/NVIDIA-NeMo/Curator/blob/main/CONTRIBUTING.md).
- [ ] New or Existing tests cover these changes.
- [x] The documentation is up to date with these changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
