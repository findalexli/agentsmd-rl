# fix(agents): resolve knowledge base tool hierarchy conflict (#10368)

Source: [neomjs/neo#10369](https://github.com/neomjs/neo/pull/10369)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Resolves #10368

Refactored `AGENTS.md` §15.1 and §15.3 to accurately reflect the tool hierarchy established in §2.1. This change removes legacy instructions that incorrectly promoted `query_documents` as the primary conceptual tool, replacing them with a strict mandate to use the `ask_knowledge_base` embedded RAG sub-agent for all "understanding the how" queries. `query_documents` is now explicitly demoted to a secondary path-discovery role.

Authored by Gemini 3.1 Pro (Antigravity). Session 27016011-8ae9-48bb-af87-9479dd5b0fd0.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
