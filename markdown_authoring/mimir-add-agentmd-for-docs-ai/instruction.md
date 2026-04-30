# Add AGENT.md for docs ai

Source: [grafana/mimir#12926](https://github.com/grafana/mimir/pull/12926)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

#### What this PR does
This pull request adds a new documentation file, `AGENTS.md`, which provides comprehensive authoring guidelines for [Docs AI toolkit](https://github.com/grafana/docs-ai/tree/main) documentation. The document outlines standards for writing style, structure, terminology, formatting, and technical content, ensuring consistency and clarity across documentation.

Documentation standards and structure:

* Introduces detailed instructions for writing documentation in Markdown, including section organization, use of headings, front matter, and introductory content.
* Specifies language and style guidelines, such as using active voice, present simple tense, second-person perspective, and preferred terminology (e.g., "allowlist" instead of "whitelist").

Formatting and technical guidance:

* Provides rules for formatting code, UI elements, lists, images, and links, including examples for code blocks, placeholders, and API documentation.
* Defines conventions for product names, observability signal order, and references to Grafana solutions and integrations.
* Includes best practices for presenting CLI commands, code samples, configuration sections, and admonitions using Hugo shortcodes.

#### Which issue(s) this PR fixes or relates to

Fixes  https://github.com/grafana/mimir-squad/issues/3289

#### Checklist

- [ ] Tests updated.
- [ ] Documentation added.
- [ ] `CHANGELOG.md` updated - the order of entries should be `[CHANGE]`, `[FEATURE]`,

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
