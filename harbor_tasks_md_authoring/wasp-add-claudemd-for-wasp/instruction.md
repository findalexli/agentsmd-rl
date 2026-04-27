# Add CLAUDE.md for Wasp

Source: [wasp-lang/wasp#3878](https://github.com/wasp-lang/wasp/pull/3878)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Description

Added a comprehensive `CLAUDE.md` file to document the Wasp monorepo structure, development workflow, and collaboration guidelines. This serves as a reference for AI agents and developers working on the project.

Covers:
- Repository structure (waspc compiler, examples, docs, etc.)
- Build & development commands via `./run` script
- Toolchain versions (GHC 9.6.7, Node v22.12.0, Prettier, Ormolu, etc.)
- Code conventions for Haskell and TypeScript
- CI pipeline overview
- Critical notes about E2E snapshots, documentation versioning, and PR templates

## Type of change

- [x] **🔧 Just code/docs improvement** <!-- no functional change -->
- [ ] **🐞 Bug fix** <!-- non-breaking change which fixes an issue -->
- [ ] **🚀 New/improved feature** <!-- non-breaking change which adds functionality -->
- [ ] **💥 Breaking change** <!-- fix or feature that would cause existing functionality to not work as expected -->

## Checklist

- [ ] I tested my change in a Wasp app to verify that it works as intended.

- 🧪 Tests and apps:

  - [ ] I added **unit tests** for my change. <!-- If not, explain why. -->
  - [ ] _(if you fixed a bug)_ I added a **regression test** for the bug I fixed. <!-- If not, explain why. -->
  - [ ] _(if you added/updated a feature)_ I added/updated **e2e tests** in \`examples/kitchen-sink/e2e-tests\`.
  - [ ] _(if you added/updated a feature)_ I updated the **starter templates** in \`waspc/data/Cli/templates\`, as needed.
  - [ ] _(if you added/updated

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
