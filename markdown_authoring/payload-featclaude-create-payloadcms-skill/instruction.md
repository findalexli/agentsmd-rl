# feat(claude): create payload-cms skill

Source: [payloadcms/payload#14368](https://github.com/payloadcms/payload/pull/14368)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/payload-cms/SKILL.md`
- `.claude/skills/payload-cms/reference/ACCESS-CONTROL-ADVANCED.md`
- `.claude/skills/payload-cms/reference/ACCESS-CONTROL.md`
- `.claude/skills/payload-cms/reference/ADAPTERS.md`
- `.claude/skills/payload-cms/reference/ADVANCED.md`
- `.claude/skills/payload-cms/reference/COLLECTIONS.md`
- `.claude/skills/payload-cms/reference/FIELDS.md`
- `.claude/skills/payload-cms/reference/HOOKS.md`
- `.claude/skills/payload-cms/reference/QUERIES.md`

## What to add / change

Creates a `payload-cms` skill for use with Claude. Follows all best practices in Claude Code Docs.

- [Claude Code Skills](https://www.anthropic.com/news/skills)
- [Skills Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)

Eventually this should be published somewhere as a Claude Code plugin or similar.

## Summary

- `SKILL.md` is ~200 lines, only containing quick ref table, essential patterns, project structure
- `reference/` contains deep-dive into specific topics, which are referenced on-demand via cross-links. This follows the "progressive disclosure" best practice for skills. 

```
.claude/skills/payload-cms/
├── SKILL.md
└── reference/
    ├── ACCESS-CONTROL-ADVANCED.md
    ├── ACCESS-CONTROL.md
    ├── ADAPTERS.md
    ├── ADVANCED.md
    ├── COLLECTIONS.md
    ├── FIELDS.md
    ├── HOOKS.md
    └── QUERIES.md
```

### Resources Analyzed:

- Official Docs: docs/access-control/, field type documentation, API references
- Test Configs: test/access-control/, test/fields/, test/auth/ - real implementation patterns
- Templates: templates/ directory - production-ready configurations
- Source Code: Collection/hook/adapter implementations from core packages
- Official Sites: payloadcms.com/llms-full.txt, payloadcms.com/docs, GitHub examples

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
