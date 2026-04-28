# chore(copilot): add more instructions

Source: [vacp2p/nim-libp2p#2307](https://github.com/vacp2p/nim-libp2p/pull/2307)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Summary
<!--
Provide a clear and concise description of the purpose of this PR.

Explain:
- What this PR does
- Why it is needed
- The problem it solves or the improvement it introduces
-->

- Add new guidance around `asyncSpawn` usage and documenting `AsyncLock` usage.
- Add a new “Leverage the Type System” section (prefer `chronos.Duration`, avoid tuples in public interfaces).

## Affected Areas
<!--
Indicate which parts of the codebase are impacted.
Check all that apply and briefly describe the scope of the changes.
-->
- [X] Build / Tooling
  <!-- Describe below -->


## Compatibility & Downstream Validation
<!--
For PRs affecting behavior on existing features, provide evidence that
dependent projects build and function correctly with these changes.
-->

Reference PRs / branches / commits demonstrating successful integration:

- **Nimbus:**  
  <!-- Link PR or branch -->

- **Waku:**  
  <!-- Link PR or branch -->

- **Codex:**  
  <!-- Link PR or branch -->

this pr has no code changes.

## Impact on Library Users
<!--
Describe how this affects downstream users of nim-libp2p.

Examples:
- API changes
- Behavior changes
- Performance implications
- Migration requirements
- No impact (internal refactor)
-->

no. this pr has no code changes.

## Risk Assessment
<!--
Identify potential risks introduced by this change.

Consider:
- Backward compatibility
- Network behavior changes
- Performance regressions
- Se

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
