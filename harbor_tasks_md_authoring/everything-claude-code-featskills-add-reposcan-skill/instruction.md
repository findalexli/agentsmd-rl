# feat(skills): add repo-scan skill

Source: [affaan-m/everything-claude-code#911](https://github.com/affaan-m/everything-claude-code/pull/911)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/repo-scan/SKILL.md`

## What to add / change

## Summary

Adds **repo-scan**, a cross-stack source code asset audit skill for Claude Code.

- Scans C/C++, Java/Android, iOS, and Web projects in one unified pass
- Classifies every file as project code, third-party, or build artifact
- Auto-detects 50+ embedded libraries (FFmpeg, Boost, OpenSSL…) with version extraction
- Delivers four-level verdicts per module: Core Asset / Extract & Merge / Rebuild / Deprecate
- Generates interactive HTML reports with drill-down navigation
- Token-efficient: three-layer analysis (filename inference → key file → quality sampling)

**Tested on**: 50,000+ file C++ monorepo — identified legacy FFmpeg 2.x, 3x duplicated SDK wrappers, and 636 MB committed build artifacts.

**Repository**: https://github.com/haibindev/repo-scan

## Checklist

- [x] Skill includes a SKILL.md with proper frontmatter
- [x] Follows the existing skill format conventions
- [x] Repository is publicly accessible
- [x] MIT licensed

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Add `repo-scan`, a cross-stack source code audit skill for C/C++, Java/Android, iOS, and Web with interactive HTML reports; installation is now pinned and shallow-fetched for reproducible, safer installs.

- **New Features**
  - Classifies files as project code, third-party, or build artifacts
  - Detects 50+ embedded libraries and extracts versions
  - Outputs module verdicts: Core Asset / Extract & Merge / Rebuild / Deprecate
  - Supports configurable scan dep

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
