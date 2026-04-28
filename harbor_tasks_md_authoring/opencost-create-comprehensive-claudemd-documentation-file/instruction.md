# Create comprehensive CLAUDE.md documentation file

Source: [opencost/opencost#3493](https://github.com/opencost/opencost/pull/3493)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Add comprehensive documentation for AI assistants working with the OpenCost codebase. This includes:

- Project overview and key features
- Repository structure explanation
- Development setup and build commands
- Key environment variables
- API endpoints reference
- Code conventions and style guidelines
- Common development tasks
- Architecture notes

## Description
<!-- Provide a clear and concise description of what this PR changes. -->

## Related Issues
<!-- Link related issues using keywords: Fixes #123, Closes #456, Relates to #789 -->

## User Impact
<!-- Describe any user-facing changes. Is this a breaking change? Is there backwards compatibility? -->

## Testing
<!-- Describe how you tested your changes: unit tests, manual tests, integration tests, etc. -->
<!-- Integration tests: https://github.com/opencost/opencost-integration-tests -->

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Adds a comprehensive AI assistant guide (`CLAUDE.md`) covering project overview, setup, configuration, APIs, architecture, and development conventions.
> 
> - **Documentation**:
>   - Add `CLAUDE.md` with:
>     - Project overview and key features
>     - Repository structure
>     - Development setup, build, and test commands
>     - Key environment variables and feature flags
>     - API endpoints reference
>     - Code conventions, module structure, testing, and logging
>     - PR guidelines
>     - Architecture notes (data flow, key types, cloud detection)
>     -

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
