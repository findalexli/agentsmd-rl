# docs: add FSM troubleshooting workflow to CLAUDE.md

Source: [united-manufacturing-hub/united-manufacturing-hub#2270](https://github.com/united-manufacturing-hub/united-manufacturing-hub/pull/2270)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

This PR adds a systematic FSM troubleshooting workflow to CLAUDE.md and improves the overall structure based on Anthropic's best practices for Claude.

## Main Changes

### Added Troubleshooting Workflow
- **Issue Investigation Workflow**: Systematic approach for debugging FSM issues
  - Gather context (action logs, Linear issues)  
  - Analyze logs systematically
  - Trace code paths through FSM files
  - Analyze service state with S6 analyzer
  - Build timelines with evidence

### Documentation Improvements  
- **Terminology section**: Maps UI naming to YAML keys (Bridge = protocolConverter, etc.)
- **Non-Intuitive Patterns**: Documents gotchas like variable flattening, S6 log suffixes, FSM precedence
- **Consolidated Architecture**: Merged FSM and Critical Patterns into concise section

### Cleanup (Following Anthropic Best Practices)
- Streamlined commands to declarative bullets
- Removed verbose Linear issue template (belongs in team docs)
- Reduced file by ~40% while adding crucial patterns
- Focus on non-obvious patterns not intuitive from code

## Context

This originated from investigating ENG-3468 ("stopping: not existing" FSM stuck state) and documenting the investigation methodology that proved effective. The workflow helps Claude assist with debugging similar issues more systematically.

## Test Plan

- [x] CLAUDE.md loads correctly in Claude Code
- [x] Terminology mappings are accurate  
- [x] Commands still work as documented
- [x] File is more conc

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
