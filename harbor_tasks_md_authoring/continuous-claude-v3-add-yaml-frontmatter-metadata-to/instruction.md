# Add YAML frontmatter metadata to skill docs

Source: [parcadei/Continuous-Claude-v3#118](https://github.com/parcadei/Continuous-Claude-v3/pull/118)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/commit/SKILL.md`
- `.claude/skills/continuity_ledger/SKILL.md`
- `.claude/skills/create_handoff/SKILL.md`
- `.claude/skills/debug/SKILL.md`
- `.claude/skills/describe_pr/SKILL.md`
- `.claude/skills/discovery-interview/SKILL.md`
- `.claude/skills/loogle-search/SKILL.md`
- `.claude/skills/plan-agent/SKILL.md`
- `.claude/skills/recall/SKILL.md`
- `.claude/skills/remember/SKILL.md`
- `.claude/skills/repo-research-analyst/SKILL.md`
- `.claude/skills/resume_handoff/SKILL.md`
- `.claude/skills/system_overview/SKILL.md`
- `.claude/skills/tldr-deep/SKILL.md`
- `.claude/skills/tldr-overview/SKILL.md`
- `.claude/skills/tldr-router/SKILL.md`
- `.claude/skills/tldr-stats/SKILL.md`
- `.claude/skills/tour/SKILL.md`
- `.claude/skills/validate-agent/SKILL.md`

## What to add / change

This adds frontmatter to a number of the skills that were missing them completely or were only partially implemented.
This references #116

<!-- greptile_comment -->

<h3>Greptile Summary</h3>


- Adds YAML frontmatter metadata with required `name` and `description` fields to 19 skill documentation files that were missing this metadata, fixing skill loading issues in the codex system
- Standardizes the frontmatter format across all skill files to ensure consistent loading behavior and proper skill registration
- Addresses Issue #116 where skills with invalid or missing YAML frontmatter were being skipped during loading

<h3>Important Files Changed</h3>


| Filename | Overview |
|----------|----------|
| `.claude/skills/*/SKILL.md` files | Added missing YAML frontmatter with required `name` and `description` fields to fix skill loading validation errors |

<h3>Confidence score: 5/5</h3>


- This PR is safe to merge with minimal risk as it only adds metadata without changing any functional code
- Score reflects the straightforward nature of adding required YAML frontmatter fields - these are purely metadata additions that fix a loading issue
- No files require special attention as all changes follow the same pattern of adding standardized frontmatter metadata

<h3>Sequence Diagram</h3>

```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant SkillActivation as "Skill Activation Hook"
    participant SkillParser as "Skill Parser"
    participant S

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
