# Add async-signal-safety-review skill

Source: [kstenerud/KSCrash#820](https://github.com/kstenerud/KSCrash/pull/820)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/async-signal-safety-review/SKILL.md`
- `.claude/skills/async-signal-safety-review/apple-oss-reference.md`

## What to add / change

## Summary
- Adds a project-level Claude Code skill at `.claude/skills/async-signal-safety-review/SKILL.md` for reviewing diffs/branches/PRs strictly for async-signal-safety violations on KSCrash's signal-handler path.
- Grounds verdicts in Apple's real implementation: the skill instructs Claude to fetch source from `github.com/apple-oss-distributions` (Libc, libplatform, libpthread, libdispatch, libmalloc, dyld, xnu, objc4, CF) via `gh api` / WebFetch and cite `<repo>/<path>:LINE` evidence for every lock/alloc claim.
- Parallelizes per-symbol lookups by delegating each to a `general-purpose` subagent in a single message; the main context only synthesizes the verdict.
- Output format is strict and binary (`signal-safe` / `NOT signal-safe`). Explicit negative list forbids style, doc-wording, DX, "worth a second look", test-coverage, and PR-landing opinions so the skill stays scoped to signal safety only.

## Test plan
- [ ] Invoke `/async-signal-safety-review` on a PR that touches `Sources/KSCrashRecording*` and confirm the output contains only Scope, reachable files, and the binary verdict (plus Violations/Stale-comment sections if applicable).
- [ ] Invoke on a PR that only touches Swift / Filters / Sinks / docs and confirm it reports those as skipped with `Verdict: signal-safe`.
- [ ] Confirm subagents are spawned in parallel for multiple suspect symbols (single message, multiple Agent calls).
- [ ] Confirm at least one violation report cites an `apple-oss-distributions/<re

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
