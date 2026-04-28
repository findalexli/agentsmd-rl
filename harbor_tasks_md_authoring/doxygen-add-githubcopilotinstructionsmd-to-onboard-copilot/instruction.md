# Add .github/copilot-instructions.md to onboard Copilot cloud agent

Source: [doxygen/doxygen#12091](https://github.com/doxygen/doxygen/pull/12091)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds agent onboarding instructions so Copilot cloud agent can work effectively in this repo from the first session.

## What's documented

- **Build system** – out-of-source CMake workflow, all key `-D` options (wizard, libclang, search, doc, coverage, tracing), how to run/filter regression tests
- **Architecture pipeline** – config → preprocessing → parsing → symbol resolution → output generation; key classes (`Definition`, `MemberDef`, `ParserManager`, parser interfaces) and the Flex scanner landscape
- **Code style** – clang-format rules (Allman braces, 2-space indent, `Type *ptr` alignment, no column limit)
- **Common workflows** – adding config options (edit `config.xml`, rebuild to regenerate C++ files), adding doxygen commands, adding regression tests, modifying Flex scanners
- **Generated files** – which files must not be edited manually (`configvalues.h/cpp`, scanner `.cpp` files, etc.)
- **Debug flags** – full list of `-d <option>` values and `-t` tracing
- **Known issues** – in-place builds with coverage, Windows libiconv, Ubuntu snap conflicts in CI, Flex buffer sizing

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
