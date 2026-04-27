# exploring-codebases v2.2.1: good/bad batching examples (salvaged from #559)

Source: [oaustegard/claude-skills#565](https://github.com/oaustegard/claude-skills/pull/565)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `exploring-codebases/SKILL.md`

## What to add / change

v2.2.1 — salvages the batching rule + good/bad examples from #559.

## Context

#559 was opened earlier today by a parallel Muninn session reacting to the same MoDA review failure. It proposed two fixes: (a) a `git clone` Phase 0, and (b) promoting the batching note to a bolded rule with good/bad examples.

#559 is being closed as superseded, because:
- (a) `git clone` is blocked in claude.ai containers by the egress proxy (see `accessing-github-repos`) — #560's tarball-via-API approach is the working equivalent and already landed.
- The PR structurally targets the old Phase-1-through-4 prose, not the numbered-steps layout from #560/#561, so it's `mergeable: false`.

But (b) is a genuine improvement that didn't fully land in v2.2.0 — the current step 2 has a single sentence on batching and one example. Making the anti-pattern visible next to the good pattern is materially stronger, especially for a failure mode that repeats (the MoDA review ran 4–5 sequential treesit calls on the same path, each paying the full ~700ms scan cost).

## v2.2.1 changes

One edit inside step 2:

```diff
-When you do drill, BATCH queries in one call — each extra query adds
-~0ms, separate invocations re-scan from scratch:
-
-```bash
-$PYTHON $TREESIT /tmp/$REPO --path=SUBDIR --detail=full \
-  'find:*Handler*:function' 'source:main' 'refs:Config'
-```
+**When you do drill, batch queries in one invocation.** Every treesit
+call pays the full scan cost. Multiple queries added to the same command
+sha

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
