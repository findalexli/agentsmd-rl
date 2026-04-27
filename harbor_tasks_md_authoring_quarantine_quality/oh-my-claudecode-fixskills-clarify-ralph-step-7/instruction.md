# fix(skills): clarify ralph step 7 chaining and ai-slop-cleaner skill invocation

Source: [Yeachan-Heo/oh-my-claudecode#2245](https://github.com/Yeachan-Heo/oh-my-claudecode/pull/2245)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/ralph/SKILL.md`

## What to add / change

## Summary

Two adjacent bugs in `skills/ralph/SKILL.md` that combined to break a real autonomous Ralph session. **Documentation-only fix** — no code, no tests.

**Source-only diff: 1 file, +6/-2.**

## Bug 1 — polite-stop after Step 7 approval

Step 7 (reviewer verification) ended with no explicit "what next" directive on approval. Step 7.5 opened with the conditional frame *"Unless `--no-deslop`, run..."* which reads as optional/decision-dependent. The Escalation section enumerated every blocker scenario but never said *"on approval, proceed without pausing to report"*.

The `"the boulder never stops"` invariant lives in the Escalation section ~90 lines away from the Step 7 → 7.5 boundary, semantically inverted (it tells the AI when stopping IS OK, not that chaining is mandatory).

**Symptom from a real session:** architect verification returned APPROVED, the AI wrote a summary ending on *"Ready to proceed with Step 7.5 (deslop) and Step 7.6 (regression)"*, then **stopped and waited for user acknowledgment**. The user had to type *"why have you stopped?"* to restart the chain. The AI later admitted it was a *"polite-stop reflex"* and a *"false consultation moment"*.

## Bug 2 — `ai-slop-cleaner` invoked as agent instead of skill

Step 7.5 said `run oh-my-claudecode:ai-slop-cleaner` without specifying the invocation mechanism. **Sixteen lines later** in the same file, the Tool_Usage section uses `Task(subagent_type="oh-my-claudecode:architect")` for actual agents. The neares

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
