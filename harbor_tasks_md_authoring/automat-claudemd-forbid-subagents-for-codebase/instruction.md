# CLAUDE.md: forbid sub-agents for codebase exploration

Source: [mafik/automat#5](https://github.com/mafik/automat/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Adds a short note at the top of CLAUDE.md telling future Claude sessions not to dispatch sub-agents (Agent / Task / Explore) for exploring this codebase, and pointing at the authoritative global-state manifests (`src/automat.hh`, `src/root_widget.hh`) and owning scope (`automat::Main()`).

Rationale: sub-agent summaries of this codebase have introduced factual errors (inventing globals, misreading init order, misattributing ownership). Reading the source directly avoids those.

https://claude.ai/code/session_01UYcLHu2uG4Q9GpGi8U1StB

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
