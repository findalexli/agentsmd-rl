# fix(ce-compound, ce-compound-refresh): use injected memory block

Source: [EveryInc/compound-engineering-plugin#569](https://github.com/EveryInc/compound-engineering-plugin/pull/569)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md`
- `plugins/compound-engineering/skills/ce-compound/SKILL.md`

## What to add / change

## Summary

`ce-compound` and `ce-compound-refresh` now read auto-memory entries from the "user's auto-memory" block Claude Code injects into the system prompt, instead of reading `MEMORY.md` from disk.

The previous phrasing sent Claude to a filesystem path — first vaguely ("read MEMORY.md from the auto memory directory"), later explicitly (`${CLAUDE_PROJECT_DIR}/memory/MEMORY.md`). Neither resolved correctly: `${CLAUDE_PROJECT_DIR}` is not substituted inside SKILL.md content, and auto-memory lives under `~/.claude/projects/<encoded-cwd>/memory/`, not the project tree. When the Read failed, Claude would fall back to Glob/Grep and scan the user's filesystem for `MEMORY.md` — the spurious-search behavior users reported.

Keying off the in-context block removes both failure modes: there is no path to resolve, and absence of the block is the natural skip signal, with no failed Read to trigger fallback searches. Non-Claude-Code platforms never see the block and skip automatically.

Fixes #318.

---

[![Compound Engineering](https://img.shields.io/badge/Built_with-Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
![Claude Code](https://img.shields.io/badge/Opus_4.6_(1M)-D97757?logo=claude&logoColor=white)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
