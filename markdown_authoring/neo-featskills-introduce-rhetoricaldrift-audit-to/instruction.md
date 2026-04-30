# feat(skills): introduce rhetorical-drift audit to pr-review Depth Floor (#10301)

Source: [neomjs/neo#10398](https://github.com/neomjs/neo/pull/10398)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agent/skills/pr-review/assets/pr-review-template.md`
- `.agent/skills/pr-review/references/pr-review-guide.md`

## What to add / change

Authored by Claude Opus 4.7 (Claude Code). Session a0abd010-e4fc-4e79-92e7-11ec5a074b2f.

Resolves #10301

Adds the fourth Depth Floor checkpoint (§7.4 Rhetorical-Drift Audit) to the pr-review skill. Closes the gap where structurally-compliant reviews can still let through PR prose that drifts away from mechanical reality — poisoning the \`ask_knowledge_base\` ingestion pipeline one PR at a time.

## What ships

### `pr-review-guide.md` — new §7.4 + renumber §7.4 → §7.5

**§7.4 Rhetorical-Drift Audit** defines the failure mode (divergence of stated framing from substrate truth) and structures the audit across four review surfaces:

1. **PR description** — does the architectural narrative match what the diff substantiates?
2. **Anchor & Echo summaries** (JSDoc) — precise codebase terminology vs. overshooting metaphor
3. **`[RETROSPECTIVE]` tags** — accurate characterization vs. inflated architectural significance
4. **Linked-anchor accuracy** — \"implements pattern X from #N\" or \"similar to PR #M\" must actually establish the cited pattern, not borrow authority

Includes Required Action template + three explicit author response options (tighten prose / expand implementation / defend the metaphor) so the audit doesn't degenerate into style-policing.

**\"What this audit is NOT\"** subsection prevents scope creep against §7.3 (Provenance, audits *origin* not *description*) and §3.2 (Score Justification, targets reviewer prose not author prose).

**Two empirical anchors:**
- **

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
