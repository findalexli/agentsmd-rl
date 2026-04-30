# Fix kerbrute spray loop and improve skill methodology

Source: [blacklanternsecurity/red-run#52](https://github.com/blacklanternsecurity/red-run/pull/52)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/credential/password-spraying/SKILL.md`
- `skills/network/network-recon/SKILL.md`
- `skills/orchestrator/SKILL.md`
- `skills/web/file-upload-bypass/SKILL.md`
- `skills/web/web-discovery/SKILL.md`

## What to add / change

## Summary
- **Fix kerbrute spray**: kerbrute `passwordspray` takes a single password string, not a wordlist file. Added a loop-based spray script variant that iterates through the wordlist, plus a complete kerbrute spray script template for NTLM-disabled environments.
- **Improve discovery→technique retry policy**: Discovery agents now always record blocked techniques with `retry: "with_context"` instead of `retry: "no"`, since technique skills have deeper bypass methodology that discovery never tests.
- **Context passing guidance**: Orchestrator passes discovery findings as informational context, not directives to skip techniques — prevents the orchestrator from overriding technique skill methodology.
- **Network recon `-Pn` retry**: Auto-retry with `-Pn` when host appears down (common in HTB/CTF/cloud), with strict rules against escalating scan type.
- **File upload bypass enhancements**: Added ZIP null byte filename truncation, ZIP local/central header mismatch techniques, and fixed PHP `<script language="php">` note (removed in PHP 7.0).
- **Web discovery routing fix**: Upload endpoints where execution is blocked now route to file-upload-bypass instead of being treated as dead ends.

## Test plan
- [x] Verify kerbrute spray loop correctly iterates passwords against user list
- [x] Verify nxc `--kerberos` flag works in NTLM-disabled environments
- [x] Verify `-Pn` retry triggers on 0-hosts-up scan results
- [x] Verify discovery agents record blocked techniques with `retry

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
