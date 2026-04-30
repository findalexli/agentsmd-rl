# feat: add skill-check for agentskills.io spec validation

Source: [sickn33/antigravity-awesome-skills#263](https://github.com/sickn33/antigravity-awesome-skills/pull/263)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/skill-check/SKILL.md`

## What to add / change

## Summary

- Adds `skill-check`, a read-only skill that validates SKILL.md files against the [agentskills specification](https://agentskills.io) and Anthropic best practices
- Catches structural errors, semantic contradictions, naming anti-patterns, and quality gaps in a single pass
- Works with Claude Code, Cursor, Windsurf, and Codex CLI

## Quality Bar Checklist

- [x] `## When to Use This Skill` section present
- [x] Code block / interaction examples (2 examples)
- [x] `## Limitations` section with 6 explicit limitations
- [x] `## Common Pitfalls` section
- [x] `npm run validate` passes
- [x] `npm run validate:references` passes
- [x] Frontmatter: `risk: safe`, `source:` URL, `date_added`, `author`, `tags`

## Details

- **Risk**: safe (read-only, uses only `Read` and `Glob` tools)
- **License**: MIT
- **Source**: https://github.com/olgasafonova/SkillCheck-Free
- **Website**: https://getskillcheck.com
- **Free tier**: 31 checks across structure, naming, semantic, and quality categories
- **Pro tier** (separate): anti-slop, security, WCAG, token, enterprise, workflow checks
<!-- devin-review-badge-begin -->

---

<a href="https://app.devin.ai/review/sickn33/antigravity-awesome-skills/pull/263" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://static.devin.ai/assets/gh-open-in-devin-review-dark.svg?v=1">
    <img src="https://static.devin.ai/assets/gh-open-in-devin-review-light.svg?v=1" alt="Open with Devin">
  </picture>
</a>
<!

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
