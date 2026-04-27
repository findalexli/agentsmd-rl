# feat(skills): add santa-method - multi-agent adversarial verification

Source: [affaan-m/everything-claude-code#760](https://github.com/affaan-m/everything-claude-code/pull/760)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/santa-method/SKILL.md`

## What to add / change

## Summary

Adds the **Santa Method** - a multi-agent adversarial verification framework for post-generation quality assurance.

**Core idea:** A single agent reviewing its own output shares the same biases and blind spots that produced it. Two independent reviewers with no shared context break this failure mode.

## Why This Change

The existing `verification-loop` skill handles deterministic checks (build, lint, test). Santa Method fills the gap for **semantic verification** - catching hallucinations, factual errors, compliance violations, and inconsistencies that no linter can detect.

### The 4 Phases
1. **Make a List** - Generate the deliverable (no changes to normal workflow)
2. **Check It Twice** - Two independent review agents evaluate against a shared rubric (context-isolated, parallel)
3. **Naughty or Nice** - Both must pass. No partial credit.
4. **Fix Until Nice** - Convergence loop with max 3 iterations, then escalate

## What's Included
- Architecture diagram and full phase documentation
- Reviewer prompt template with structured JSON output
- Rubric design guide with domain-specific extensions (content, code, compliance)
- Three implementation patterns: subagent (recommended), sequential inline, batch sampling
- Failure modes table with mitigations
- Integration guidance with existing ECC skills (verification-loop, eval-harness, continuous-learning-v2)
- Metrics framework and cost analysis

## Type of Change
- [x] `feat:` New feature


## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
