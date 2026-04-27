# Fix outdated tool names and parameters in CLI skill

Source: [getsentry/XcodeBuildMCP#217](https://github.com/getsentry/XcodeBuildMCP/pull/217)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/xcodebuildmcp-cli/SKILL.md`

## What to add / change

I noticed that many of the tool names in the CLI agent skill were wrong(/outdated), making the skill less than helpful. 
I had codex update it using this prompt (using the installed 2.0.7 CLI tool): 
"Use the installed xcodebuildmcp CLI tool to explore its available tools and options and fix any mistakes in SKILL.md that don't line up with what is available in the actual CLI tool."

-----

The xcodebuildmcp skill guide contained outdated command and tool names that no longer match the installed CLI interface. This patch updates the examples to the currently supported workflow/tool names and argument shapes so agents can execute documented commands without translation or failures.

Validated against live CLI output via:
- xcodebuildmcp --help
- xcodebuildmcp tools --json
- per-workflow and per-tool --help checks for all commands referenced in SKILL.md

Key updates:
- Replaced deprecated names such as discover-projs/list-sims/build-run-sim/build-sim/test-sim with discover-projects/list/build-and-run/build/test
- Updated device examples from list-devices/build-device/get-device-app-path/install-app-device/launch-app-device to list/build/get-app-path/install/launch
- Updated logging and debugging examples to start/stop-simulator-log-capture and debugging attach
- Updated macOS and scaffolding commands to build/build-and-run and scaffold-ios/scaffold-macos
- Removed invalid arguments from examples (e.g. --app-path on device launch, --package-path on swift-package

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
