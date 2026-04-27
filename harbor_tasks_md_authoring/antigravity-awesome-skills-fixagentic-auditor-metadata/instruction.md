# Fix/agentic auditor metadata

Source: [sickn33/antigravity-awesome-skills#353](https://github.com/sickn33/antigravity-awesome-skills/pull/353)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/advanced-evaluation/SKILL.md`
- `skills/agentic-actions-auditor/SKILL.md`

## What to add / change

This PR fixes metadata validation errors in skills/agentic-actions-auditor/SKILL.md. I have added the mandatory risk, source, date_added, and author fields to the frontmatter and corrected the YAML syntax for the multi-line description using a folded scalar (>). This ensures the skill is correctly parsed by the project's automated registry tools.
​Change Classification
- ​[ ] Skill PR
- ​[x] Docs PR
- ​[ ] Infra PR
​Issue Link (Optional)
​No open issue — proactive documentation accuracy fix to resolve npm run validate warnings.
​Quality Bar Checklist ✅
​All items must be checked before merging.
​[x] Standards: I have read docs/contributors/quality-bar.md and docs/contributors/security-guardrails.md.
​[x] Metadata: The SKILL.md frontmatter is valid (checked with npm run validate).
​- [x] Risk Label: I have assigned the correct risk: tag.
​- [x] Triggers: The "When to use" section is clear and specific.
- ​[x] Security: If this is an offensive skill, I included the "Authorized Use Only" disclaimer. (N/A — docs-only PR)
- ​[x] Safety scan: I ran npm run security:docs.
- ​[x] Automated Skill Review: I checked the skill-review GitHub Actions result.
​- [x] Local Test: I have verified the skill works locally.
- ​[x] Repo Checks: I ran npm run validate:references.
​- [x] Source-Only PR: I did not manually include generated registry artifacts (CATALOG.md, data/*.json).
- ​[x] Credits: I have added the source credit (N/A — docs-only).
- ​[x] Maintainer Edits: I ena

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
