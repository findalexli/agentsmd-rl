# Add GitHub Copilot instructions for repository

Source: [btraceio/btrace#783](https://github.com/btraceio/btrace/pull/783)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Configures Copilot instructions per [gh.io/copilot-coding-agent-tips](https://gh.io/copilot-coding-agent-tips) to provide AI assistants with repository-specific context and conventions.

## Changes

- **Created `.github/copilot-instructions.md`** with:
  - Project structure (Gradle multi-module, `btrace-*` modules)
  - Architecture overview (agent, compiler, instr, runtime, client, services)
  - Build commands (`./gradlew build`, `./gradlew -Pintegration test`)
  - Code style (Java 8, Google Java Format via Spotless, JUnit 5)
  - Commit conventions (Conventional Commits)
  - Example BTrace script pattern
  - Key dependencies (ASM, JCTools, hppcrt)
  - References to `AGENTS.md` for detailed guidelines

The instructions emphasize simplicity and performance, matching the repository's development philosophy.

> [!WARNING]
>
> <details>
> <summary>Firewall rules blocked me from connecting to one or more addresses (expand for details)</summary>
>
> #### I tried to connect to the following addresses, but was blocked by firewall rules:
>
> - `gh.io`
>   - Triggering command: `/usr/bin/curl curl -L REDACTED` (dns block)
>
> If you need me to access, download, or install something from one of these locations, you can either:
>
> - Configure [Actions setup steps](https://gh.io/copilot/actions-setup-steps) to set up my environment, which run before the firewall is enabled
> - Add the appropriate URLs or hosts to the custom allowlist in this repository's [Copilot coding agent settings](ht

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
