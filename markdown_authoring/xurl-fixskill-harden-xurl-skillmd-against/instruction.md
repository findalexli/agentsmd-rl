# fix(skill) harden xurl SKILL.md against secret leakage

Source: [xdevplatform/xurl#34](https://github.com/xdevplatform/xurl/pull/34)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary
This PR hardens the xurl skill documentation to reduce the risk of credential leakage in agent/LLM workflows.

## What changed
- Updated `/Users/xmm/workspace/opensource/xurl/SKILL.md` with a mandatory **Secret Safety** section.
- Added explicit rules to:
  - never read, print, parse, or send `~/.xurl` to LLM context
  - never ask users to paste credentials/tokens into chat
  - require users to manage secrets manually on their own machine
  - avoid running auth commands with inline secrets in agent sessions
  - forbid `--verbose` / `-v` in agent sessions (can expose auth headers/tokens)
- Removed examples that included secret-bearing CLI options (`--client-id`, `--client-secret`, `--consumer-key`, `--consumer-secret`, `--access-token`, `--token-secret`, `--bearer-token`).
- Kept `xurl auth status` as the safe way to check whether an app with credentials is already registered.
- Added a prerequisite note that this skill requires the `xurl` CLI utility: [https://github.com/xdevplatform/xurl](https://github.com/xdevplatform/xurl).

## Why
Agent prompts, command output, and logs can unintentionally expose credentials. These changes make secret-handling boundaries explicit and safer by default.

## Impact
Documentation-only change. No code or runtime behavior changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
