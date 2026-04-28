# Add comprehensive GitHub Copilot instructions for AMBA repository

Source: [Azure/azure-monitor-baseline-alerts#714](https://github.com/Azure/azure-monitor-baseline-alerts/pull/714)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR adds a comprehensive `.github/copilot-instructions.md` file that provides GitHub Copilot coding agents with detailed instructions on how to work effectively in the Azure Monitor Baseline Alerts (AMBA) repository.

## What's Included

The instructions cover all essential aspects for developers working with this codebase:

- **Complete build process**: Hugo site building (13s), Python alert processing (5s), and Bicep compilation (3s)
- **Exact timing requirements**: All commands tested with explicit timeout recommendations and "NEVER CANCEL" warnings
- **Validation workflows**: YAML schema validation, Hugo build checks, and Bicep compilation verification
- **Manual testing scenarios**: Documentation site navigation, alert processing validation, and template compilation
- **Repository structure guide**: Key directories, configuration files, and their purposes
- **Common development tasks**: Adding alerts, modifying documentation, working with ALZ policies

## Key Features

- **Exhaustively validated**: Every command has been tested and timed in the actual repository
- **Safety margins**: All timeout recommendations include significant buffers based on measured execution times
- **Imperative tone**: Clear, actionable instructions ("Run this command", "Do not do this")
- **CI compliance**: Includes exact commands needed to ensure GitHub Actions workflows pass

## Validation Results

All build processes and validation commands have been tested:

```bash
# Hugo site build: 1

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
