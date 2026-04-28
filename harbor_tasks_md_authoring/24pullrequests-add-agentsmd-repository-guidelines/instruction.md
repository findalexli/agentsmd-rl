# Add AGENTS.md repository guidelines

Source: [24pullrequests/24pullrequests#4853](https://github.com/24pullrequests/24pullrequests/pull/4853)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Document setup and test workflow for contributors and coding agents.

Include local/Docker quick start, CI-parity test commands, test harness gotchas, and seasonal behavior notes.

References:
- https://agents.md
- https://github.com/agentsmd/agents.md
- https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/

GitHub Copilot PR summary:

> This pull request adds a comprehensive `AGENTS.md` documentation file to the repository. The new file provides essential guidelines for contributors and coding agents, including setup instructions, project structure, testing practices, coding conventions, and security tips.
> 
> Documentation improvements:
> 
> * Added a new `AGENTS.md` file outlining repository-specific commands, setup steps (including prerequisites for Ruby, PostgreSQL, Node, and Chrome), and instructions for both local and Docker-based development.
> * Documented the project structure, common Rails and Rake commands, and detailed testing instructions (including CI parity, Docker usage, and test harness gotchas such as time travel and network stubbing).
> * Included sections on seasonal behavior, useful rake tasks, coding style and conventions (with references to `.editorconfig` and `.rubocop.yml`), as well as security and configuration tips.
> * Provided guidelines for commits and pull requests, including best practices for writing commit messages and PR descriptions.
> * Added "Agent Guardrails"

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
