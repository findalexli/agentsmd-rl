# docs: add test parallelism guidelines to CLAUDE.md

Source: [coder/httpjail#61](https://github.com/coder/httpjail/pull/61)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add documentation about test parallelism requirements
- Clarify when tests should be marked as serial vs parallel
- Explain that jails are designed to be independent and support concurrent testing

## Details
This PR adds a new "Test Parallelism" section to CLAUDE.md that documents:

1. Integration tests should run in parallel by default since jails operate independently
2. Tests should only be marked serial (`#[serial]`) when there's a specific global resource that would be contended
3. Examples of when serial might be needed:
   - Global system settings that affect all processes
   - Shared network ports or interfaces
   - System-wide firewall rules that can't be isolated
4. The rationale that each jail operates in isolation (network namespaces on Linux, separate proxy ports)

This guidance helps ensure the test suite runs efficiently by leveraging the independence of jail instances.

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
