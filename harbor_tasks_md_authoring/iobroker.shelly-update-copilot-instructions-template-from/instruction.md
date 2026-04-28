# Update Copilot instructions template from v0.4.0 to v0.4.2

Source: [iobroker-community-adapters/ioBroker.shelly#1258](https://github.com/iobroker-community-adapters/ioBroker.shelly/pull/1258)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Overview

This PR updates the GitHub Copilot instructions template from version 0.4.0 to 0.4.2, merging the latest ioBroker adapter development best practices while preserving all Shelly-specific customizations.

## What Changed

### Version Update
- Updated template version from **0.4.0** → **0.4.2**
- Maintained template source reference to DrozmotiX/ioBroker-Copilot-Instructions

### New Template Content Added (+650 lines)

The update adds comprehensive guidance across 8 major areas:

1. **Enhanced Integration Testing** - Added advanced testing patterns including:
   - Testing both success AND failure scenarios
   - Advanced state access patterns
   - Key integration testing rules and workflow dependencies
   - Clear "What NOT to Do" / "What TO Do" guidelines

2. **API Testing with Credentials** - New section covering:
   - Password encryption for integration tests
   - Demo credentials testing patterns
   - Enhanced test failure handling

3. **README Updates** - Documentation standards including:
   - Required sections for adapter READMEs
   - Mandatory README updates for PRs
   - Changelog management with AlCalzone release-script

4. **Dependency Updates** - Package management best practices and dependency guidelines

5. **JSON-Config Admin Instructions** - Configuration schema and admin interface guidelines

6. **Best Practices for Dependencies** - HTTP client library recommendations with practical examples

7. **Error Handling** - Adapter error patterns, example cod

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
