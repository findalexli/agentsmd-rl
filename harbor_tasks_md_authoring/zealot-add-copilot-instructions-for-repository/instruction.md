# Add Copilot instructions for repository

Source: [tryzealot/zealot#2094](https://github.com/tryzealot/zealot/pull/2094)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds `.github/copilot-instructions.md` to provide context-aware guidance for GitHub Copilot when working with this codebase.

## Key Sections

- **Technology Stack**: Rails 8.0+, Ruby 3.4+, PostgreSQL, GoodJob, Stimulus, Turbo, pnpm
- **Coding Standards**: RuboCop configuration, 2-space indentation, 120 char line length, frozen string literals
- **Testing**: RSpec patterns, Factory Bot usage, coverage expectations
- **Architecture**: Service objects, GraphQL mutations, API serializers, background job patterns
- **i18n**: English/Chinese locales managed via Crowdin
- **Security**: Input validation, parameterized queries, Pundit authorization

The file follows GitHub's recommended structure for Copilot instructions, enabling more accurate code suggestions aligned with project conventions.

## Updates

- Updated package manager references from Yarn to pnpm to reflect recent codebase migration
- All JavaScript/Frontend commands now use `pnpm` instead of `yarn`
- Updated Ruby version from 3.2+ to 3.4+ to reflect recent Ruby upgrade

> [!WARNING]
>
><issue_title>✨ Set up Copilot instructions</issue_title>
><issue_description>Configure instructions for this repository as documented in <a href="https://gh.io/copilot-coding-agent-tips">Best practices for Copilot coding agent in your repository</a>.
> 
> </issue_description>
> 
> ## Comments on the Issue (you are @copilot in this section)
> 
><comments>
></comments>
>

- Fixes tryzealot/zealot#2093

<issue_title>✨ Set up Copilot instru

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
