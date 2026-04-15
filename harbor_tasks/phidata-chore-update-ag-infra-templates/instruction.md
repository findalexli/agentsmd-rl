# Simplify AgentOS infrastructure starter template naming

## Problem

The `InfraStarterTemplate` enum uses redundant `-template` suffixes in both member names and values (e.g., `agentos_docker_template = "agentos-docker-template"`). This naming leaks into user-facing prompts, default directory names, and mapping structures, making the CLI output unnecessarily verbose.

## Expected Behavior

- Enum member names and values should drop the `-template` suffix (e.g., `agentos_docker = "agentos-docker"`)
- All references in user prompts and default directory name mappings should use the shorter names without the `-template` suffix
- The actual GitHub repository URLs (which contain `-template` in the repo name) must remain unchanged
- The `agno-infra` package version in `libs/agno_infra/pyproject.toml` should be bumped to version `1.0.7` to reflect this change

Additionally, the project's `CLAUDE.md` should be updated to document a known issue with GitHub operations: the `gh pr edit` command can fail with GraphQL errors related to classic projects. Add guidance on using the GitHub API directly as a workaround, including:
- Mention that GraphQL errors can occur with `gh pr edit`
- Show the `gh api` command with the `-X PATCH` method
- Use the API path format `repos/<owner>/<repo>/pulls/<number>` for updating PR descriptions

## Files to Look At

- `libs/agno_infra/agno/infra/enums.py` -- enum definition with redundant `-template` suffixes
- `libs/agno_infra/agno/infra/operator.py` -- maps, defaults, and user-facing prompt strings containing `-template` suffixes
- `libs/agno_infra/pyproject.toml` -- package version must be set to `1.0.7`
- `CLAUDE.md` -- must include a "GitHub Operations" section with guidance on using `gh api`, mentioning GraphQL errors with `gh pr edit`, showing the `-X PATCH` method, and the API path format `repos/<owner>/<repo>/pulls/<number>`
