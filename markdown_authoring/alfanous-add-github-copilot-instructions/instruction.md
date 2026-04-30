# Add GitHub Copilot instructions

Source: [Alfanous-team/alfanous#557](https://github.com/Alfanous-team/alfanous/pull/557)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds `.github/copilot-instructions.md` to provide Copilot with repository context for better code suggestions.

## Documentation Coverage

- **Project structure**: Python 3.8+ Quranic search API using Whoosh and PyParsing
- **Development workflow**: Makefile-based build system, pytest testing, dependency management
- **Code conventions**: PEP 8 standards, Arabic text handling requirements, API design patterns
- **Domain-specific guidance**: Quranic data processing considerations, UTF-8/transliteration support

The instructions cover common development tasks (adding search features, modifying indexes) and reference key files (api.py, engines.py, indexing.py) to help Copilot understand the codebase architecture.

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
> - Configure [Actions setup steps](https://gh.io/copilot/actions-setup-steps) to set up my environment, which run before the firewall is enabled
> - Add the appropriate URLs or hosts to the custom

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
