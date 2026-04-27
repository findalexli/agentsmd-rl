# feat(ce-compound): add discoverability check for docs/solutions/ in instruction files

Source: [EveryInc/compound-engineering-plugin#456](https://github.com/EveryInc/compound-engineering-plugin/pull/456)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md`
- `plugins/compound-engineering/skills/ce-compound/SKILL.md`

## What to add / change

## Summary

The `docs/solutions/` knowledge store only compounds value when agents can find it. Today, only plugin-mediated workflows (ce:plan via learnings-researcher) know to search there. Agents in fresh sessions, other tools (Cursor, Copilot), or collaborators without the plugin have no reason to discover it.

Both ce:compound and ce:compound-refresh now run a discoverability check after their main work completes. If the project's instruction file (AGENTS.md or CLAUDE.md) doesn't surface the knowledge store to agents, the skill suggests a minimal addition — with consent before editing.

## What gets added

The addition adapts to the AGENTS.md\/CLAUDE.md\'s existing structure. Two examples from testing:

**When AGENTS.md\/CLAUDE.md has a directory listing or architecture section** — a single line is added:

```
app/
  models/        # ActiveRecord models
  controllers/   # Request handling
  views/         # ERB templates
docs/
  solutions/     # Documented solutions to past problems (bugs, best practices, workflow patterns), organized by category with YAML frontmatter (module, tags, problem_type)
```

**When AGENTS.md\/CLAUDE.md has a documentation section with bullet entries** — a bullet is added:

```markdown
## Documentation

- `docs/adr/` — Architecture Decision Records
- `docs/api/` — OpenAPI specs (auto-generated from code annotations)
- `docs/runbooks/` — Incident response procedures
- `docs/solutions/` — Searchable knowledge store of previously solved problems, or

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
