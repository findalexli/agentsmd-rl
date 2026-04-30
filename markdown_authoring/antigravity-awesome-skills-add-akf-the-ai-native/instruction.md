# Add AKF — The AI Native File Format skill

Source: [sickn33/antigravity-awesome-skills#406](https://github.com/sickn33/antigravity-awesome-skills/pull/406)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/akf-trust-metadata/SKILL.md`

## What to add / change

AKF is the AI native file format — EXIF for AI.

Stamps every file with trust scores, source provenance, and compliance metadata (~15 tokens of JSON, 20+ formats).

Works with Antigravity, Claude Code, Codex, Cursor, and all SKILL.md-compatible agents.

- `pip install akf`
- https://akf.dev
- https://github.com/HMAKT99/AKF

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

None.

## Quality Bar Checklist ✅

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`none`, `safe`, `critical`, `offensive`, or `unknown` for legacy/unclassified content).
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Security**: If this is an _offensive_ skill, I included the "Authorized Use Only" disclaimer.
- [x] **Safety scan**: If this PR adds or modifies `SKILL.md` command guidance, remote/network examples, or token-like strings, I ran `npm run security:docs` (or equivalent hardening check) and addressed any findings.
- [x] **Automated Skill Review**: If this PR changes `SKILL.md`, I checked the `skill-review` GitHub Actions result and addressed any actionable feedback.
- [x] **Local Test**: I have verified the skill works locally.
- [x] **Repo Checks**: I ran `npm run validate:references` if my change affec

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
