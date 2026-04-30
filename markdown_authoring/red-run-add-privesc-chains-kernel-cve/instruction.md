# Add privesc chains, kernel CVE, and CTF flag capture

Source: [blacklanternsecurity/red-run#82](https://github.com/blacklanternsecurity/red-run/pull/82)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/orchestrator/SKILL.md`
- `skills/privesc/linux-discovery/SKILL.md`
- `skills/privesc/linux-kernel-exploits/SKILL.md`
- `skills/privesc/linux-sudo-suid-capabilities/SKILL.md`

## What to add / change

## Summary

- **linux-discovery**: Add PAM `user_readenv` check, logind session property enumeration, and polkit `allow_active` policy scan with routing to linux-sudo-suid-capabilities
- **linux-sudo-suid-capabilities**: Add Step 4b — PAM environment injection → Active session hijack → polkit `allow_active` bypass → UDisks2/libblockdev nosuid mount race for SUID execution
- **linux-kernel-exploits**: Add CVE-2024-1086 (nf_tables UAF, kernel 5.14–6.6) with exploitation steps, alternative PoC repos, and troubleshooting
- **orchestrator**: Add Flag Capture directive — orchestrator injects flag-check instructions into agent prompts for shell-access skills. Agents check common flag paths immediately, write findings via state-interim `add_vuln`, and continue enumeration. Event watcher treats flag events as top-priority with immediate operator notification.

## Test plan

- [ ] Re-index skills (`uv run --directory tools/skill-router python indexer.py`)
- [ ] Verify `search_skills("PAM polkit privesc")` returns linux-sudo-suid-capabilities
- [ ] Verify `search_skills("kernel exploit nf_tables")` returns linux-kernel-exploits
- [ ] Run a CTF engagement and confirm flag capture directive appears in agent prompts for shell-access skills
- [ ] Confirm flag events surface via event watcher with prominent callout

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
