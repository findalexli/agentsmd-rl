# chore: update copilot instructions to reflect latest repository state

Source: [vacp2p/nim-libp2p#2297](https://github.com/vacp2p/nim-libp2p/pull/2297)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Syncs `.github/copilot-instructions.md` with the actual current state of the codebase. Several entries were stale or missing.

## Summary

- **chronos** version floor corrected: `>= 4.0.4` → `>= 4.2.2` (matches `libp2p.nimble`)
- **CI workflows**: added missing `daily_ci_report.yml` entry (opens/updates GitHub issues on daily CI failures)
- **Discovery section**: removed references to `kad_disco.nim` / `kademlia_discovery/` (don't exist); replaced with `service_discovery.nim` + `service_discovery/` (do exist)
- **Protocols**: documented `identify.nim` (Identify / Identify Push) which was absent from the Source Module Guide

## Affected Areas

- [ ] Gossipsub  

- [ ] Transports  

- [ ] Peer Management / Discovery

- [ ] Protocol Logic

- [ ] Build / Tooling

- [x] Other  
  Documentation only — `.github/copilot-instructions.md`


## Compatibility & Downstream Validation

N/A — documentation change only.

- **Nimbus:** N/A
- **Waku:** N/A
- **Codex:** N/A


## Impact on Library Users

None. Internal documentation update for the Copilot coding agent.


## Risk Assessment

No risk. Documentation-only change.


## References

- Automated weekly update workflow: `.github/workflows/update_copilot_instructions.yml`


## Additional Notes

None.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
