# chore: add AGENTS.md

Source: [hardyscc/nestjs-cqrs-starter#1041](https://github.com/hardyscc/nestjs-cqrs-starter/pull/1041)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Adds `AGENTS.md` to give AI coding agents (and new contributors) a fast ramp-up on how this repo is structured and how to work in it effectively.

## What's included

- **Project structure** — monorepo layout (`apps/gateway`, `apps/service-user`, `apps/service-account`, `libs/common`) and per-service DDD layer breakdown (commands, queries, events, sagas, resolvers)
- **Common commands** — install, build, lint, format, unit/e2e test, per-app dev start
- **Architecture conventions** — CQRS write/read separation, async event flow via EventStore, saga orchestration, Apollo Federation gateway, TypeORM entity naming, `@hardyscc/common` shared lib usage
- **Code style** — ESLint zero-warning policy, Prettier via lint-staged, Conventional Commits enforcement
- **Local dev dependencies** — ready-to-paste Docker commands for MySQL 8 and EventStore, with a note about required persistent subscription setup

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
