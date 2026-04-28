# chore(wallet-cli): update skill — session view first, labels, trim verbosity

Source: [LedgerHQ/ledger-live#16833](https://github.com/LedgerHQ/ledger-live/pull/16833)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/ledger-wallet-cli/SKILL.md`

## What to add / change

### ✅ Checklist

- [ ] `npx changeset` was attached.
- [x] **Covered by automatic tests.** N/A — documentation only
- [x] **Impact of the changes:**
  - `ledger-wallet-cli` skill updated: agent now runs `session view` immediately on invocation (no prompting), documents session labels, trimmed ~65% verbosity

### 📝 Description

Updates the `ledger-wallet-cli` agent skill following PR #16598 (session layer):

- Agent runs `session view` immediately when invoked without a task — no asking first
- Documents session labels (`ethereum-1`, `bitcoin-native-1`, …) and `session view`/`session reset` commands
- Removed implementation details (V1 descriptor format, `session.yaml` path, JSON output shapes)
- Removed redundant full-descriptor fallback examples per step (heuristic is sufficient)

<img width="482" height="235" alt="Screenshot 2026-04-27 at 11 22 20" src="https://github.com/user-attachments/assets/48b5a5b6-a0e4-4f60-9aaf-fe60ff924713" />


### ❓ Context

- **Related PR**: #16598 — feat(wallet-cli): session layer

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
