# add run-rust-benchmarks claude skills

Source: [RediSearch/RediSearch#8241](https://github.com/RediSearch/RediSearch/pull/8241)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.skills/run-rust-benchmarks/SKILL.md`
- `.skills/run-rust-tests/SKILL.md`

## What to add / change

Helper to run Rust micro benchmarks and easily compare results.

Also fix a typo in `run-rust-tests`.

- [ ] This PR introduces API changes
- [ ] This PR introduces serialization changes

#### Release Notes

- [ ] This PR requires release notes
- [x] This PR does not require release notes

If a release note is required (bug fix / new feature / enhancement), describe the **user impact** of this PR in the title.  

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Low risk: adds documentation-only skill instructions and corrects a typo; no runtime code, APIs, or data handling are affected.
> 
> **Overview**
> Adds a new Claude skill, `run-rust-benchmarks`, documenting how to run Rust benchmark crates (or a specific bench) via `cargo bench` and summarize Rust vs C average timings.
> 
> Fixes argument examples/typos in `run-rust-tests` to use the correct `/run-rust-tests` command name.
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit ef1f135281cdaf85c6778e394e55d746efad2e13. This will update automatically on new commits. Configure [here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
