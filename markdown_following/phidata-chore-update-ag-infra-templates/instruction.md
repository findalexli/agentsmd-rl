# Simplify AgentOS infrastructure starter template naming

## Problem

The `InfraStarterTemplate` enum uses redundant `-template` suffixes in both member names and values. This naming leaks into user-facing prompts, default directory name mappings, and operator.py strings, making the CLI output unnecessarily verbose. The enum members and their values still contain the `-template` suffix when they should not.

## Expected Behavior

- Enum member names and values should not contain the `-template` suffix
- All references in user prompts and default directory name mappings should use the shorter names
- The actual GitHub repository URLs (which naturally include `-template` in the repo name on GitHub) must remain unchanged
- The `agno-infra` package version in `libs/agno_infra/pyproject.toml` should be updated to reflect this change

Additionally, the project's `CLAUDE.md` should be updated to document a known issue with GitHub operations: the `gh pr edit` command can fail with GraphQL errors related to classic projects. Add guidance on using the GitHub API directly as a workaround, including:
- Mention that GraphQL errors can occur with `gh pr edit`
- Show the `gh api` command with a PATCH method
- Use an API path format for updating PR descriptions (repos/\<owner\>/\<repo\>/pulls/\<number\>)

## Files to Look At

- `libs/agno_infra/agno/infra/enums.py` -- InfraStarterTemplate enum definition
- `libs/agno_infra/agno/infra/operator.py` -- TEMPLATE_TO_NAME_MAP, TEMPLATE_TO_REPO_MAP, and user-facing prompt strings
- `libs/agno_infra/pyproject.toml` -- package version
- `CLAUDE.md` -- must include a GitHub Operations section

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
- `mypy (Python type checker)`
