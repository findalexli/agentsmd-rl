# docs(skills): add setup-dev skill for dev environment setup

Source: [getsentry/sentry#108744](https://github.com/getsentry/sentry/pull/108744)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/setup-dev/SKILL.md`
- `.agents/skills/setup-dev/references/orbstack-fix.md`

## What to add / change

## Summary

Add a comprehensive agent skill (`.claude/skills/setup-dev/`) that guides engineers through setting up the Sentry dev environment from scratch — from a bare machine to a running dev server.

## Motivation

Setting up Sentry locally is a complex, multi-step process that takes 30-45 minutes and involves many tools (devenv, devservices, direnv, Docker runtimes, etc.). The existing documentation is spread across multiple sources, and several common pitfalls aren't well-documented:

- **direnv hangs silently** when the Docker runtime isn't running
- **Chicken-and-egg problem**: direnv checks for node/sentry before `devenv sync` can install them
- **OrbStack users get Colima errors** because scripts hardcode the Colima socket path
- **`devservices up` takes 5-10 minutes** on first run (Docker image pulls) with no warning
- **Database needs `sentry upgrade`**, not just `migrate` — without seeding, every page 500s
- **Kafka topic warnings** on first boot look alarming but are normal
- **Blank white screen** without the Cookie Sync extension, with no hint about what's wrong

This skill encodes all of that hard-won knowledge so AI agents can walk engineers through setup smoothly.

## What's included

```
.claude/skills/setup-dev/
├── SKILL.md                    # Full 7-step walkthrough with troubleshooting
└── references/
    └── orbstack-fix.md         # How to patch devservices.py for OrbStack support
```

The skill covers:
1. **State detection** — checks what's already 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
