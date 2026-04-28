# docs: add AGENTS.md with guidance for AI coding agents

Source: [The-Art-of-Hacking/websploit#84](https://github.com/The-Art-of-Hacking/websploit/pull/84)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Closes #83

## Summary

- Adds `AGENTS.md` at the repo root to give AI coding agents project-specific operating guidance.
- Calls out the most important rule: the apps under `additional-labs/` are **intentionally vulnerable** and must not be "fixed". Distinguishes in-scope hardening targets (infra, install scripts, docs, Dockerfile hygiene) from out-of-scope lab application source.
- Documents repo layout, the directory → container → IP → host-port mapping, container conventions (static IPs in `10.6.6.0/24`, `platform: linux/amd64` for prebuilt amd64 images, `restart: unless-stopped`), and a checklist for adding a new lab.
- Captures run commands (`docker compose up -d --build`, etc.), notes that `install.sh` is Kali/Parrot-only, and records small style/doc conventions.

No code, compose, or lab behavior changes.

## Test plan

- [x] Render `AGENTS.md` on GitHub and confirm formatting (tables, code blocks, tree).
- [x] Confirm directory → container-name → IP → host-port mapping matches `docker-compose.yml` and `additional-labs/README.md`.
- [x] Confirm no other files were modified (`git diff master...docs/add-agents-md` shows only `AGENTS.md`).


Made with [Cursor](https://cursor.com)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
