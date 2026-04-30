# feat: add ai-native-cli skill

Source: [sickn33/antigravity-awesome-skills#317](https://github.com/sickn33/antigravity-awesome-skills/pull/317)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/ai-native-cli/SKILL.md`

## What to add / change

# Pull Request Description

Adds the **ai-native-cli** skill -- a design spec with 98 rules for building CLI tools that AI agents can safely use. Covers structured JSON output, error handling, input contracts, safety guardrails, exit codes, and agent self-description across three certification levels (Agent-Friendly, Agent-Ready, Agent-Native).

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Quality Bar Checklist

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`safe` -- read-only spec/guideline, no destructive operations).
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Security**: Not an offensive skill; no disclaimer needed.
- [x] **Safety scan**: No shell commands, network access, or credential examples that require security review.
- [x] **Local Test**: Verified the skill content is accurate and complete.
- [x] **Repo Checks**: No docs/workflow/infra changes in this PR.
- [x] **Source-Only PR**: No generated registry artifacts included.
- [x] **Credits**: Source linked in SKILL.md frontmatter.
- [x] **Maintainer Edits**: Enabled.

## Details

- **Name**: ai-native-cli
- **Risk**: safe (read-only design specification)
- **Source**: https://github.com/ChaosRealmsAI/agent-cli-spec
- **Validation**: `n

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
