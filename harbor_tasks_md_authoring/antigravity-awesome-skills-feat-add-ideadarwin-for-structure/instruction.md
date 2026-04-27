# feat: add idea-darwin for structured idea iteration and evolution

Source: [sickn33/antigravity-awesome-skills#469](https://github.com/sickn33/antigravity-awesome-skills/pull/469)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/idea-darwin/SKILL.md`

## What to add / change

## What This Adds

Adds **idea-darwin** — a Darwinian idea evolution engine to the skills collection.

**GitHub**: https://github.com/warmskull/idea-darwin
**ClawHub**: `clawhub install idea-darwin`

## What It Does

Toss rough ideas into `ideas.md`, and the system treats them as competing organisms on an evolution island:

- **6-dimensional scoring** (Novelty, Feasibility, Value, Logic, Cross Potential, Verifiability)
- **Automated rounds** of deepening, crossbreeding, mutation, critique, and validation
- **External stimulus disruption** to prevent local optima
- **Full lineage tracking** across idea generations
- **Species cards** as structured output for each idea

## Metadata

- **Risk**: safe (pure Markdown skill, no shell commands or network access)
- **Source**: community
- **Languages**: English, Chinese, Japanese
- **License**: MIT

## Commands

```
/idea-darwin init
/idea-darwin round
/idea-darwin round 3
/idea-darwin status
/idea-darwin dormant IDEA-0005
/idea-darwin wake IDEA-0005
```

## Quality Bar Checklist ✅

- [x] SKILL.md follows canonical template format
- [x] YAML/frontmatter metadata reviewed
- [x] "When to Use" section included
- [x] Real-world examples included where applicable
- [x] Source-only (no generated CATALOG/data artifacts)
- [x] Risk metadata reviewed

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
