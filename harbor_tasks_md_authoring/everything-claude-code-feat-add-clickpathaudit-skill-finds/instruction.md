# feat: add click-path-audit skill — finds state interaction bugs

Source: [affaan-m/everything-claude-code#729](https://github.com/affaan-m/everything-claude-code/pull/729)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/click-path-audit/SKILL.md`

## What to add / change

## Summary

New debugging skill that fills a gap no existing skill covers: **tracing button handlers through shared state to find bugs where functions individually work but cancel each other out.**

### The problem

Systematic debugging checks: does the function exist? Does it crash? Does it return the right type? But it does NOT check: **does the final UI state match what the button label promises?**

### Real-world results

We ran systematic debugging on a production React + Zustand app and found 54 bugs. Then a user reported a button that "does nothing." Systematic debugging had missed it because:
- The button had an onClick handler (not dead)
- Both functions in the handler existed (no missing wiring)
- Neither function crashed (no runtime error)
- The data types were correct (no type mismatch)

The root cause: `selectThread(null)` had a **side effect** resetting `composeMode: false`, undoing what `setComposeMode(true)` had just set. Two functions that work perfectly individually, but cancel each other out.

We created this skill and ran it across the entire app — **found 48 additional bugs** that systematic debugging completely missed.

### What the skill does

1. **Maps all state store actions** with their side effects (what they set AND what they silently reset)
2. **Traces every button handler** through its call sequence against that map
3. **Checks 6 bug patterns:** Sequential Undo, Async Race (double-click), Stale Closure, Missing State Transition, Conditional Dead 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
