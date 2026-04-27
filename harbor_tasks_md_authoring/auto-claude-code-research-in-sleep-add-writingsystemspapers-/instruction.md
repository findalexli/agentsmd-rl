# Add writing-systems-papers skill for systems conference papers

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#125](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/125)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/writing-systems-papers/SKILL.md`

## What to add / change

## Summary

Adds a new `writing-systems-papers` skill for paragraph-level structural guidance when writing 10–12 page systems papers targeting OSDI, SOSP, ASPLOS, NSDI, and EuroSys.

### Contents
- `skills/writing-systems-papers/SKILL.md` (184 lines)
  - Page allocation per section
  - Paragraph templates with authoritative sources
  - 4 writing patterns (Gap Analysis, Observation-Driven, Contribution List, Thesis Formula)
  - Conference differences table (USENIX/ACM formats)
  - Pre-submission checklist
  - Academic integrity requirements

### Authoritative Sources
Levin & Redell (SOSP PC Chairs), Irene Zhang (MSR/UW, SOSP/OSDI PC), Gernot Heiser (UNSW, seL4), Timothy Roscoe (ETH Zürich), Yi Ding, hzwer/WritingAIPaper

### Boundary with Existing Skills

| Existing Skill | Scope | This Skill |
|---------------|-------|------------|
| `paper-write` | General paper generation workflow, LaTeX output, citation verification | No overlap — this skill provides structural blueprints only |
| `paper-slides` | Conference presentations (Beamer+PPTX) | No overlap — already complete |
| `paper-poster` | Conference posters | No overlap |
| `paper-plan` | Research outline | Complementary — use paper-plan first, then this for structure |

### Why Not Duplicate paper-slides?
ARIS already has `paper-slides` (570 lines) fully covering conference presentations. No need to duplicate. The companion AI-Research-SKILLs PR includes `presenting-conference-talks` as an independent implementation for th

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
