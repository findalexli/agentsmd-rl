# docs(skills): document markDirty in swamp-extension-datastore

Source: [systeminit/swamp#1226](https://github.com/systeminit/swamp/pull/1226)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/swamp-extension-datastore/references/api.md`
- `.claude/skills/swamp-extension-datastore/references/examples.md`

## What to add / change

## Summary

Pick up the \`markDirty()\` addition from #1225 in the skill that guides
authors building custom datastore providers.

- \`references/api.md\` — interface block includes \`markDirty(): Promise<void>\`,
  plus a section describing when it's load-bearing (fast-path implementations
  that cache a clean/dirty watermark) versus when a no-op is correct (sync
  services that unconditionally walk the cache).
- \`references/examples.md\` — the working sync service example returns a
  no-op \`markDirty\` with a comment pointing at the fast-path pattern in
  \`design/datastores.md\`.

No code changes, docs only — keeps guidance for extension authors in
lock-step with the core interface change that already shipped.

## Test Plan

- [x] \`deno fmt\` clean per the skill-files rule in CLAUDE.md.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
