# chore: add dev-toolbar-review skill for growth eng PR reviews

Source: [supabase/supabase#44819](https://github.com/supabase/supabase/pull/44819)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/dev-toolbar-review/SKILL.md`

## What to add / change

Came up in a conversation with @pamelachia  about what growth eng should actually look for when reviewing dev toolbar PRs. We realized the review criteria were all in my head and not documented anywhere, so this adds a Claude skill that surfaces a checklist when PRs touch the relevant files.

### What it covers

- Environment guards (tree-shaking ternaries, `IS_LOCAL_DEV` runtime checks) — especially relevant since we're expanding visibility to staging/preview
- Flag override cookies (`x-ph-flag-overrides`, `x-cc-flag-overrides`) and the read/write sync across dev-tools, posthog-client, and feature-flags
- Telemetry event subscription (`subscribeToEvents` / `emitToDevListeners`) side-effect safety
- SSE server telemetry stream and cross-repo implications
- App-level mounting across studio, www, docs
- Also calls out a CODEOWNERS gap: `posthog-client.ts` and `feature-flags.tsx` aren't assigned to growth-eng, so PRs touching only those files won't auto-request review

### Testing

Verified the skill is discovered by Claude Code from the repo root. Content reviewed against the actual code in `packages/dev-tools/` and `packages/common/`.

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added internal review guidelines for development-toolbar changes, covering build-time hiding outside local dev, local feature-flag override handling, client telemetry listener expectations, server-sent-event s

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
