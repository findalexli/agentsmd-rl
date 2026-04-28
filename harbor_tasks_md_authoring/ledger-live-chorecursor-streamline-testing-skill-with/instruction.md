# chore(cursor): streamline testing skill with golden rules

Source: [LedgerHQ/ledger-live#15231](https://github.com/LedgerHQ/ledger-live/pull/15231)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/skills/testing/SKILL.md`

## What to add / change

### ✅ Checklist

- [ ] `npx changeset` was attached. _Not applicable — only `.cursor/skills/` config files changed, no npm packages impacted._
- [ ] **Covered by automatic tests.** _Not applicable — documentation/tooling change only._
- [x] **Impact of the changes:**
  - No runtime impact — only affects Cursor AI agent behavior when writing tests

### 📝 Description

**Problem**: The testing skill file was too dense (416 lines) with redundant sections, causing the AI agent to lose track of key rules buried in verbose examples.

**Solution**: Rewrote the skill from scratch:
- **Added "Golden Rules" section** at the top with the 7 most important testing principles, ensuring they're the first thing the agent reads
- **Added `toBeVisible()` preference** — agents should assert visibility, not just DOM presence
- **Added "Search before you create" rule** — agents must `rg` for existing mocks/fixtures before creating new ones (mutualization)
- **Removed redundant sections** — Don'ts list (duplicated Golden Rules), verbose code examples, Workflow section (obvious)
- **Result**: 416 → 172 lines (~60% reduction) with zero information loss

### ❓ Context

- Internal tooling improvement — no JIRA ticket
- Addresses recurring issues where the agent creates duplicate mocks and uses `toBeInTheDocument()` instead of `toBeVisible()`

---

### 🧐 Checklist for the PR Reviewers

- **The code aligns with the requirements** described in the linked JIRA or GitHub issue.
- **The PR description clearl

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
