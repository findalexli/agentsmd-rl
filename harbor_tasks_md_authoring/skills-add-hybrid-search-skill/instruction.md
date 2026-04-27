# add hybrid search skill

Source: [qdrant/skills#45](https://github.com/qdrant/skills/pull/45)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `skills/qdrant-search-quality/diagnosis/SKILL.md`
- `skills/qdrant-search-quality/search-strategies/SKILL.md`
- `skills/qdrant-search-quality/search-strategies/hybrid-search/SKILL.md`
- `skills/qdrant-search-quality/search-strategies/hybrid-search/combining-searches/SKILL.md`
- `skills/qdrant-search-quality/search-strategies/hybrid-search/search-types/SKILL.md`

## What to add / change

## What this PR does

Hybrid Search Skill, summarizing Qdrant-specific knowledge for configuring hybrid search. Needed to reduce the number of repeating requests from the community/clients.

## Type

<!-- check one -->
- [+] new skill
- [ ] skill improvement
- [ ] bug fix
- [ ] repo hygiene

## Checklist

<!-- for new/improved skills, check all that apply -->
- [+] `python3 scripts/validate_skills.py` passes
- [+] skill answers "when?" or "why?", not "how?"
- [+] skill navigates to docs, does not duplicate or replace them
- [+] description has `Use when` with 5+ trigger phrases
- [+] leaf skills omit `allowed-tools`, hub skills declare them
- [+] ends with `## What NOT to Do` section
- [+] no code blocks except minimal snippets when absolutely required (reference the docs instead)
- [+] all doc links go to `search.qdrant.tech/md/documentation/`
- [ ] tested with a realistic prompt (paste below or link to eval)

## Test prompt

<!-- paste a realistic user question you tested this skill against, and summarize what the agent responded. skip for non-skill PRs. -->

```
<prompt here>
```

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
