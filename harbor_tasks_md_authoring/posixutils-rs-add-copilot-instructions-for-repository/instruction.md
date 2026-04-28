# Add Copilot instructions for repository

Source: [rustcoreutils/posixutils-rs#473](https://github.com/rustcoreutils/posixutils-rs/pull/473)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Configures GitHub Copilot instructions per best practices to provide context on project conventions and requirements.

## Changes

Created `.github/copilot-instructions.md` with:

- **Core principles**: POSIX.2024 baseline, minimalism over GNU bloat, race-free design
- **Code style**: `cargo fmt` required, no warnings, small functions, readability priority
- **Dependencies**: Prefer std-only, avoid mega-crates, standard deps (clap, libc, regex, chrono)
- **Testing**: TestPlan framework pattern, feature flags for slow/root tests
- **Project structure**: Utility categories, plib shared code, ftw for race-free file operations
- **Build commands**: `cargo build --release`, `cargo test --release -p posixutils-CRATE`
- **Utility lifecycle stages**: Rough draft → Feature complete → Test coverage → Code coverage → Translated → Audited

Sourced from README.md, CONTRIBUTING.md, and CI workflows to ensure consistency with existing practices.

<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

> 
> ----
> 
> *This section details on the original issue you should resolve*
> 
> <issue_title>✨ Set up Copilot instructions</issue_title>
> <issue_description>Configure instructions for this repository as documented in [Best practices for Copilot coding agent in your repository](https://gh.io/copilot-coding-agent-tips).
> 
> <Onboard this repo></issue_description>
> 
> ## Comments on the Issue (you are @copilot in this section)
> 
> <comments>
> </comments>


## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
