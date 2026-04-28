# Add AGENTS.md with containerization guidelines

Source: [jauderho/dockerfiles#6835](https://github.com/jauderho/dockerfiles/pull/6835)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This change adds an `AGENTS.md` file to the root of the repository. This file serves as a comprehensive guide for both human contributors and AI agents on how to correctly containerize and integrate new programs into the codebase, ensuring consistency in security, optimization, and documentation across the project.

---
*PR created automatically by Jules for task [13400934124857324504](https://jules.google.com/task/13400934124857324504) started by @jauderho*
<!-- ELLIPSIS_HIDDEN -->

----

> [!IMPORTANT]
> Adds `AGENTS.md` with guidelines for containerizing new programs, covering structure, workflows, Dockerfile standards, README, and repository updates.
> 
>   - **New File**:
>     - Adds `AGENTS.md` to the root of the repository.
>   - **Guidelines**:
>     - Directory structure: Create `<program>` directory with `Dockerfile` and `README.md`.
>     - GitHub Action workflow: Use `harden-runner`, pin actions to commit hashes, push images to registries, and set triggers.
>     - Dockerfile standards: Use image digests, specific base images, multi-stage builds, and non-root users.
>     - Program README: Include standard badges and usage information.
>     - Root updates: Update `README.md` and `BUILD_STATUS.md` alphabetically.
>     - Language examples: Use `adguardhome`, `onetun`, `ruff`, `ansible` as templates.
> 
> <sup>This description was created by </sup>[<img alt="Ellipsis" src="https://img.shields.io/badge/Ellipsis-blue?color=175173">](https://www.ellipsis.dev?ref=jaud

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
