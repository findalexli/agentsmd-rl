# fix: Stop hook fails on Windows — multiline YAML command not parsed by Git Bash

Source: [OthmanAdi/planning-with-files#86](https://github.com/OthmanAdi/planning-with-files/pull/86)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.codebuddy/skills/planning-with-files/SKILL.md`
- `.codex/skills/planning-with-files/SKILL.md`
- `.cursor/skills/planning-with-files/SKILL.md`
- `.kilocode/skills/planning-with-files/SKILL.md`
- `.mastracode/skills/planning-with-files/SKILL.md`
- `.opencode/skills/planning-with-files/SKILL.md`
- `skills/planning-with-files/SKILL.md`

## What to add / change

## Summary

- The Stop hook in SKILL.md uses a YAML multiline block (`command: |`) with a ~25-line bash script for OS detection. On Windows, Claude Code passes hook commands through Git Bash, which fails to parse the multiline content — `SCRIPT_DIR=...` is interpreted as a command name instead of a variable assignment
- Replaced the multiline block with a single-line command: set `SD` variable inline, try `powershell.exe` first (Windows), fall back to `sh` (Linux/macOS). The OS-detection logic is eliminated entirely since the fallback chain handles it implicitly
- Applied to all 7 tool variants (claude, cursor, codex, codebuddy, kilocode, mastracode, opencode)

## Error on Windows (before fix)

```
Stop hook error: Failed with non-blocking status code: bash:
SCRIPT_DIR=/c/Users/rayku/.claude/skills/planning-with-files/scripts: No such file or directory
sh: /check-complete.sh: No such file or directory
```

## Root Cause

YAML `command: |` multiline blocks are not reliably parsed by Git Bash on Windows. The shell receives the first line (`SCRIPT_DIR=...`) as a command to execute rather than a variable assignment, causing the entire hook to fail.

## Fix

Before (25 lines per variant):
```yaml
command: |
  SCRIPT_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/planning-with-files}/scripts"
  IS_WINDOWS=0
  if [ "${OS-}" = "Windows_NT" ]; then
    ...20 more lines of OS detection...
  fi
```

After (1 line per variant):
```yaml
command: "SD=\"${CLAUDE_PLUGIN_ROOT:-$HOME/.claude

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
