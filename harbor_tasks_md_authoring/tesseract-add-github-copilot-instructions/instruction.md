# Add GitHub Copilot instructions

Source: [tesseract-ocr/tesseract#4508](https://github.com/tesseract-ocr/tesseract/pull/4508)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds repository custom instructions to reduce AI coding agent exploration time and build/test failures.

## Changes

Created `.github/copilot-instructions.md` with:

- **Build systems**: Autotools and CMake workflows, including out-of-source build requirements and common options
- **Dependencies**: Leptonica (required), training tools dependencies (pango, cairo, icu), traineddata setup
- **Testing**: Unit test commands for both build systems, CLI validation examples
- **Project structure**: Source directory layout (api, ccmain, lstm, training), key entry points
- **CI/CD**: Workflow descriptions (cmake.yml, autotools.yml, unittest.yml, codeql), timing expectations
- **Common issues**: 7 documented build failures with solutions (Leptonica missing, CMake in-source, tessdata path, submodules)
- **Validation steps**: Complete check sequence including sanitizer builds
- **Quick reference**: Shell-portable commands for build/test/format/debug

Designed per GitHub's guidance on repository custom instructions for coding agents.

> [!WARNING]
>
> <details>
> <summary>Firewall rules blocked me from connecting to one or more addresses (expand for details)</summary>
>
> #### I tried to connect to the following addresses, but was blocked by firewall rules:
>
> - `gh.io`
>   - Triggering command: `/home/REDACTED/work/_temp/ghcca-node/node/bin/node /home/REDACTED/work/_temp/ghcca-node/node/bin/node --enable-source-maps /home/REDACTED/work/_temp/copilot-developer-action-main/dist/index.js` (

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
