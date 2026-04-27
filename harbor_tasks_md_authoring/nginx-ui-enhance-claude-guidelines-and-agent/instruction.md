# Enhance CLAUDE guidelines and agent linkage

Source: [0xJacky/nginx-ui#1464](https://github.com/0xJacky/nginx-ui/pull/1464)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Detail Go formatting and race-safe test expectations for backend work.

List frontend linting commands so CLAUDE matches current workflows.

Link AGENTS.md to CLAUDE.md so other agents reuse the strengthened guide.

GitHub Copilot summary:

> This pull request adds a new documentation file and updates the development guidelines and commands to emphasize code quality, formatting, and testing standards for both backend and frontend development.
> 
> Documentation updates:
> 
> * Added the `CLAUDE.md` file to the project documentation.
> 
> Backend development standards:
> 
> * Updated guidelines to require running `gofmt`/`goimports` for code formatting and validating changes with `go test ./... -race -cover` before pushing.
> * Enhanced backend commands to include `go generate ./...` and more detailed instructions for building and testing, including release artifact generation.
> 
> Frontend development standards:
> 
> * Added instructions to run `pnpm lint`, `pnpm lint:fix`, and `pnpm typecheck` to maintain style and type consistency.
> * Updated frontend commands to include linting and type checking as part of the development workflow.
> 
> Development environment:
> 
> * Added instructions for bootstrapping a demo stack using Docker Compose.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
