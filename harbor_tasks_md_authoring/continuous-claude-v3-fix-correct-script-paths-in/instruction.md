# fix: Correct script paths in skills (mcp/ and core/ subdirectories)

Source: [parcadei/Continuous-Claude-v3#79](https://github.com/parcadei/Continuous-Claude-v3/pull/79)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/firecrawl-scrape/SKILL.md`
- `.claude/skills/github-search/SKILL.md`
- `.claude/skills/help/SKILL.md`
- `.claude/skills/implement_task/SKILL.md`
- `.claude/skills/morph-apply/SKILL.md`
- `.claude/skills/morph-search/SKILL.md`
- `.claude/skills/nia-docs/SKILL.md`
- `.claude/skills/perplexity-search/SKILL.md`
- `.claude/skills/recall-reasoning/SKILL.md`
- `.claude/skills/recall/SKILL.md`
- `.claude/skills/remember/SKILL.md`
- `.claude/skills/research-agent/SKILL.md`
- `.claude/skills/research-external/SKILL.md`
- `.claude/skills/system_overview/SKILL.md`

## What to add / change

Multiple skills referenced scripts at wrong paths. The scripts were moved to subdirectories but skill documentation wasn't updated.

Fixed paths:
- scripts/perplexity_search.py → scripts/mcp/perplexity_search.py
- scripts/nia_docs.py → scripts/mcp/nia_docs.py
- scripts/morph_search.py → scripts/mcp/morph_search.py
- scripts/firecrawl_scrape.py → scripts/mcp/firecrawl_scrape.py
- scripts/github_search.py → scripts/mcp/github_search.py
- scripts/morph_apply.py → scripts/mcp/morph_apply.py
- scripts/artifact_query.py → scripts/core/artifact_query.py
- scripts/artifact_index.py → scripts/core/artifact_index.py
- scripts/recall_learnings.py → scripts/core/recall_learnings.py
- scripts/store_learning.py → scripts/core/store_learning.py

Files modified (13):
- perplexity-search/SKILL.md
- research-external/SKILL.md
- nia-docs/SKILL.md
- morph-search/SKILL.md
- firecrawl-scrape/SKILL.md
- github-search/SKILL.md
- morph-apply/SKILL.md
- implement_task/SKILL.md
- recall-reasoning/SKILL.md
- recall/SKILL.md
- remember/SKILL.md
- help/SKILL.md
- system_overview/SKILL.md

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Updated command examples and script path references across skill documentation files to reflect helper script reorganization. Scripts have been relocated to new module directories including mcp/ and core/ subdirectories. All usage examples and command invocations updated

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
