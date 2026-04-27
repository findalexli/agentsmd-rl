# feat: add clarvia-aeo-check — score MCP servers for agent-readiness before installing

Source: [sickn33/antigravity-awesome-skills#402](https://github.com/sickn33/antigravity-awesome-skills/pull/402)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/clarvia-aeo-check/SKILL.md`

## What to add / change

# Pull Request Description

Adds the community skill `clarvia-aeo-check`, a maintainer-reviewed recommendation for scoring MCP servers and related tools for agent-readiness before installation.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

N/A

## Quality Bar Checklist ✅

- [x] **Standards**: Reviewed against the repository contributor standards and security guardrails.
- [x] **Metadata**: `SKILL.md` frontmatter is present in the submitted file.
- [x] **Risk Label**: `risk: safe` is declared.
- [x] **Triggers**: The skill is explicitly targeted at pre-install evaluation workflows.
- [x] **Security**: N/A (not an offensive skill).
- [x] **Safety scan**: The PR adds setup guidance and will be validated by CI / docs security checks on merge path.
- [x] **Automated Skill Review**: Required for `SKILL.md` changes and expected to run after fork approval.
- [x] **Local Test**: Example usage and setup are included for local verification.
- [x] **Repo Checks**: Source-only PR; repository CI will validate the change.
- [x] **Source-Only PR**: No generated registry artifacts are included.
- [x] **Credits**: Source links are included in the PR body.
- [x] **Maintainer Edits**: Enabled.

## New Skill: `clarvia-aeo-check`

**Category:** tool-quality  
**Risk:** safe  
**Tools:** Claude Code, Cursor, Windsurf, Cline

### What it does

Before adding any MCP server, API, or CLI to an agent workflow, use Clarvia to score its **AEO (Agent Expe

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
