# Simplify AgentOS infrastructure starter template naming

## Problem

The `InfraStarterTemplate` enum in `libs/agno_infra/agno/infra/enums.py` uses redundant `-template` suffixes in both member names and values (e.g., `agentos_docker_template = "agentos-docker-template"`). This naming leaks into user-facing prompts, default directory names, and the `TEMPLATE_TO_NAME_MAP` in `libs/agno_infra/agno/infra/operator.py`, making the CLI output unnecessarily verbose.

## Expected Behavior

- Enum member names and values should drop the `-template` suffix (e.g., `agentos_docker = "agentos-docker"`)
- All references in `operator.py` (maps, defaults, user prompts) should use the shorter names
- The actual GitHub repository URLs in `TEMPLATE_TO_REPO_MAP` must remain unchanged
- The `agno-infra` package version in `libs/agno_infra/pyproject.toml` should be bumped to reflect this change

Additionally, the project's `CLAUDE.md` should be updated to document a known issue with GitHub operations: the `gh pr edit` command can fail with GraphQL errors related to classic projects. Add guidance on using the GitHub API directly as a workaround, including the correct API path and method for updating PR descriptions.

## Files to Look At

- `libs/agno_infra/agno/infra/enums.py` -- enum definition
- `libs/agno_infra/agno/infra/operator.py` -- maps, defaults, and user-facing prompt strings
- `libs/agno_infra/pyproject.toml` -- package version
- `CLAUDE.md` -- project instructions for Claude Code
