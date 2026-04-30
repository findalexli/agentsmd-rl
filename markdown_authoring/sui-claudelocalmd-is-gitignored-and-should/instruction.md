# Claude.local.md is gitignored and should not be checked in

Source: [MystenLabs/sui#23758](https://github.com/MystenLabs/sui/pull/23758)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.local.md`

## What to add / change

## Description 

No functional changes

## Test plan 

No functional changes

---

## Release notes

Check each box that your changes affect. If none of the boxes relate to your changes, release notes aren't required.

For each box you select, include information after the relevant heading that describes the impact of your changes that a user might notice and any actions they must take to implement updates. 

- [ ] Protocol: 
- [ ] Nodes (Validators and Full nodes): 
- [ ] gRPC:
- [ ] JSON-RPC: 
- [ ] GraphQL: 
- [ ] CLI: 
- [ ] Rust SDK:

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
