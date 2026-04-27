# feat: add kotler and osterwalder strategic business skills

Source: [sickn33/antigravity-awesome-skills#525](https://github.com/sickn33/antigravity-awesome-skills/pull/525)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/kotler-macro-analyzer/SKILL.md`
- `skills/osterwalder-canvas-architect/SKILL.md`

## What to add / change

# Pull Request Description

## Summary
This PR introduces a new category of skills focused on **Strategic Business and Economic Analysis**. As a 4th-year Software Engineering student at **Kyiv School of Economics (KSE)**, I’ve designed these skills to bridge the gap between rigorous economic frameworks and AI automation

While the repository has a strong technical foundation, these tools allow agentic workflows to handle high-level strategy (Kotler/Osterwalder) with the precision expected in professional software engineering

### Added Skills:
* **`kotler-macro-analyzer`**: A strategic audit tool based on Kotler’s methodology. It performs data-driven PESTEL analysis and maps trends to a SWOT matrix using real-time research
* **`osterwalder-canvas-architect`**: An iterative consultant skill for building logically consistent 9-block Business Model Canvases

## Change Classification
- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Quality Bar Checklist ✅

- [x] **Standards**: I have read the quality and security guardrails.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: Assigned `safe` tag.
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Limitations**: Included sections explaining that these skills do not replace expert review.
- [x] **Local Test**: Verified in my local Claude Code environment.
- [x] **Source-Only PR**: No generated registry artifacts included.


## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
