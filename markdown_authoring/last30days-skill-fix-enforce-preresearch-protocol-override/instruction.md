# fix: enforce pre-research protocol + override WebSearch Sources mandate

Source: [mvanhorn/last30days-skill#266](https://github.com/mvanhorn/last30days-skill/pull/266)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary

Restores the rich synthesis output. Closes three prompt-level loopholes that let the model silently take a degraded path:

1. **Research Execution precondition gate.** Steps 0.55 (entity resolution) and 0.75 (query planner) are non-skippable on WebSearch platforms. \`--emit md\` banned as a primary user-facing flow; \`--emit=compact --plan\` is mandatory. OpenClaw \`--auto-resolve\` fallback preserved.
2. **WebSearch Sources mandate override.** The WebSearch tool description contains a CRITICAL/MUST mandate to append a Sources section. Explicitly superseded inside \`/last30days\` with matched-register CRITICAL/MANDATORY language plus BAD/GOOD example.
3. **Pre-present self-check.** Before displaying, the model verifies bold per-paragraph headlines, per-source emoji stats, quoted highlights, Polymarket block, coverage footer, and (critically) no trailing Sources block. One regeneration permitted if checks fail.

Also adds explicit MANDATORY language to the "What I learned" template requiring bold headline phrases on every narrative paragraph.

## Root cause

Same-session A/B on 2026-04-15 between \`/last30days kanye west\` and \`/last30days hermes ai\` showed:

| Aspect | Kanye (rich) | Hermes (bland) |
|---|---|---|
| Step 0.55 entity resolution | ran | skipped |
| Step 0.75 query planner | ran | skipped |
| \`--emit\` flag | \`compact\` | \`md\` |
| \`--plan\` JSON | present | absent |
| \`--x-handle\`/\`--subreddits\`/\`--tiktok-hashtags\` | resolved + passed | 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
