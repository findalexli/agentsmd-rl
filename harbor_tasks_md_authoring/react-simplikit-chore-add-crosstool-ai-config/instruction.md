# chore: add cross-tool AI config files (AGENTS.md, .cursorrules, copilot-instructions.md)

Source: [toss/react-simplikit#322](https://github.com/toss/react-simplikit/pull/322)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursorrules`
- `.github/copilot-instructions.md`
- `AGENTS.md`

## What to add / change

## Summary
- Add `AGENTS.md` — tool-neutral **single source of truth** for project conventions (~160 lines, full examples)
- Add `.cursorrules` — Cursor AI compact rules (~27 lines, bullets only)
- Add `.github/copilot-instructions.md` — GitHub Copilot compact rules (~24 lines, bullets only)

Detailed code examples and pattern explanations live only in `AGENTS.md`. Tool-specific files contain compact rule bullets with a reference to AGENTS.md for the full standards.

**[3/3] AI tool settings exposure series** (based on #320)

## Why three files?

Different AI tools read different config files:
| Tool | Config file |
|---|---|
| Claude Code | `CLAUDE.md` |
| OpenAI Codex | `AGENTS.md` |
| Cursor | `.cursorrules` |
| GitHub Copilot | `.github/copilot-instructions.md` |

By providing all formats, any contributor using any AI tool gets project conventions automatically loaded.

## Content hierarchy

```
CLAUDE.md (most detailed, Claude Code-specific)
  └── AGENTS.md ← Single Source of Truth (full examples + patterns)
        ├── .cursorrules (compact bullets + SoF reference)
        └── .github/copilot-instructions.md (compact bullets + SoF reference)
```

- **AGENTS.md**: SSR-safe patterns, nullish check examples, hook return conventions, testing patterns, file structure, JSDoc, commands, commit convention
- **.cursorrules / copilot-instructions.md**: Code style bullet list only — no duplicated code blocks

## Test plan
- [x] No sensitive information in any file
- [x] Content co

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
