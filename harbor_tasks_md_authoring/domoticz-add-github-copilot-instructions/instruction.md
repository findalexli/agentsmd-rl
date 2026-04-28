# Add GitHub Copilot instructions

Source: [domoticz/domoticz#6551](https://github.com/domoticz/domoticz/pull/6551)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Configures repository-specific guidance for GitHub Copilot via `.github/copilot-instructions.md`.

## Instructions Coverage

- **Code Style**: C++ formatting rules (tabs, brace style, 200 char limit) from existing `clang-format.txt`
- **Architecture**: Project structure (`main/`, `hardware/`, `webserver/`, `dzVents/`, etc.)
- **Build & Test**: CMake workflow, pytest-3/Gherkin BDD, busted/mocha test frameworks
- **Development Flow**: Branch from `development`, forum discussion for features
- **Security**: Credential defaults, reporting process (security@domoticz.com)
- **Dependencies**: Boost ≥1.69.0, prefer bundled libs (JsonCPP, Minizip, JWT-CPP)

Enables context-aware code suggestions aligned with project conventions and multi-platform requirements (Linux/Windows/embedded).

> [!WARNING]
>
> <details>
> <summary>Firewall rules blocked me from connecting to one or more addresses (expand for details)</summary>
>
> #### I tried to connect to the following addresses, but was blocked by firewall rules:
>
> - `gh.io`
>   - Triggering command: `/home/REDACTED/work/_temp/ghcca-node/node/bin/node /home/REDACTED/work/_temp/ghcca-node/node/bin/node --enable-source-maps /home/REDACTED/work/_temp/copilot-developer-action-main/dist/index.js` (dns block)
>
> If you need me to access, download, or install something from one of these locations, you can either:
>
> - Configure [Actions setup steps](https://gh.io/copilot/actions-setup-steps) to set up my environment, which run before the fire

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
