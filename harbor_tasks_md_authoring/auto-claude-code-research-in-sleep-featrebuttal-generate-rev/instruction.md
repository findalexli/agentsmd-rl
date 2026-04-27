# feat(rebuttal): generate REVISION_PLAN.md with overall checklist

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#144](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/144)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/rebuttal/SKILL.md`

## What to add / change

## Summary
- Add a new `rebuttal/REVISION_PLAN.md` output to Workflow 4 that collects every paper revision promised in the rebuttal into a single overall GitHub-style checklist, keyed by `issue_id` back to `ISSUE_BOARD.md`.
- Include grouped-by-section/severity views, a commitment summary (`already_done` / `approved_for_rebuttal` / `future_work_only`), and an out-of-scope log so deferred concerns don't silently disappear.
- Wire the new artifact into the existing safety model: Phase 4 generates it, Phase 5's Commitment lint now requires draft ↔ checklist parity, Phase 7 refreshes it on finalize, and Phase 8 keeps it live across follow-up rounds.

## Motivation
Today the rebuttal skill produces `STRATEGY_PLAN.md` and `ISSUE_BOARD.md`, but there is no single artifact the author can hand to their future self (or co-authors) to track which paper edits were actually promised in the rebuttal. `REVISION_PLAN.md` closes that gap and gives the commitment gate a concrete document to validate against.

## Test plan
- [ ] Run `/rebuttal` on a sample paper + reviews and confirm `rebuttal/REVISION_PLAN.md` is generated alongside `REBUTTAL_DRAFT_v1.md` and `PASTE_READY.txt`
- [ ] Verify every checklist item references a valid `issue_id` from `ISSUE_BOARD.md`
- [ ] Verify Phase 5 Commitment lint flags any draft promise not present in the checklist (and any orphan checklist items)
- [ ] Run a follow-up round and confirm `REVISION_PLAN.md` is updated in place rather than regenerated

🤖 Generat

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
