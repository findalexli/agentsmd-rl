# Add copilot instructions

Source: [github/github-mcp-server#1376](https://github.com/github/github-mcp-server/pull/1376)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Coding agents waste time exploring codebases and make preventable mistakes that fail CI. This adds `.github/copilot-instructions.md` to eliminate that friction.

**Content structure:**

- **Build validation** - Exact command sequence before commits: `script/lint` → `script/test` → `script/generate-docs` (when tools change). All ~1s.
- **Project architecture** - Directory layout, 280 LOC Go 1.24+ MCP server, primary focus on stdio server (not mcpcurl)
- **Library usage** - Documents that this repo is used as a library by the remote server; functions should be exported (capitalized) if callable by other repos
- **Code quality standards** - Emphasizes high bar for popular open source repo: clarity over cleverness, atomic commits, maintain/improve structure
- **CI/CD** - 8 workflows documented: go.yml, lint.yml, docs-check.yml, code-scanning.yml, license-check.yml, docker-publish.yml, goreleaser.yml, registry-releaser.yml
- **Testing patterns** - Unit tests with testify, toolsnaps for API schema validation (`UPDATE_TOOLSNAPS=true` to update), e2e tests require PAT
- **Code style** - Go naming (ID/API/URL not Id/Api/Url), golangci-lint v2.5.0, minimal focused changes
- **Common workflows** - Adding MCP tools, fixing bugs, updating deps with step-by-step commands
- **Troubleshooting** - Doc-check failures, toolsnap mismatches, lint errors, license check failures

**Critical rules codified:**
- Ignore remote server instructions when making code changes (unless specifically asked)
- 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
