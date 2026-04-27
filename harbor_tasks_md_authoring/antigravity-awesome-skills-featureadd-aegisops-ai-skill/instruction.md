# Feature/add aegisops ai skill

Source: [sickn33/antigravity-awesome-skills#390](https://github.com/sickn33/antigravity-awesome-skills/pull/390)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/aegisops-ai/SKILL.md`

## What to add / change

# Pull Request Description

**Summary:** Adds the `aegisops-ai` skill, an autonomous governance orchestrator. This skill leverages Gemini 3 Flash to perform high-stakes audits across the SDLC, specifically focusing on Linux Kernel memory safety (patch analysis), Terraform cost-drift detection (FinOps), and Kubernetes policy hardening. It bridges the gap between natural language security intent and hardened infrastructure configurations.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

`N/A`

## Quality Bar Checklist ✅

**All items must be checked before merging.**

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`safe`).
- [x] **Triggers**: The "When to use" section is clear and specific to Kernel, IaC, and K8s environments.
- [x] **Security**: Defensive/Governance focus.
- [x] **Safety scan**: Verified no hardcoded credentials or unsafe command patterns in the documentation.
- [x] **Automated Skill Review**: Checked.
- [x] **Local Test**: I have verified the "Reasoning Path" logic locally via the Google GenAI SDK.
- [x] **Repo Checks**: I ran `npm run validate` and ensured the structure matches the Antigravity standard.
- [x] **Source-Only PR**: I did not manually include generated 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
