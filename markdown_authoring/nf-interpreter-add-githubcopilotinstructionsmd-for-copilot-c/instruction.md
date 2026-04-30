# Add .github/copilot-instructions.md for Copilot cloud agent onboarding

Source: [nanoframework/nf-interpreter#3292](https://github.com/nanoframework/nf-interpreter/pull/3292)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Comprehensive onboarding document for Copilot cloud agents working with this repository for the first time.

### Contents

- **Project overview** — what nf-interpreter produces (nanoBooter + nanoCLR), supported RTOS platforms and MCU architectures
- **Repository structure** — annotated directory tree covering `src/` layers (CLR/HAL/PAL), `targets/`, `CMake/`, Kconfig files
- **Build system** — CMake presets + Kconfig workflow, dev container images, out-of-source build requirement, no in-repo test runner
- **Coding conventions** — C++20/C17, `.clang-format` (Microsoft style, 120 cols, Allman braces), license headers, naming prefixes (`g_`, `CLR_`, `nanoHAL_`, `c_`)
- **Kconfig configuration** — `NF_FEATURE_HAS_*` vs `NF_FEATURE_USE_*` vs `API_*` naming patterns, defconfig fragment format
- **Target board structure** — directory layout, defconfig, preset, and CMake module conventions for adding/modifying boards
- **CI/CD** — Azure Pipelines primary builds, GitHub Actions dev container smoke tests
- **Common pitfalls** — cross-compiler requirements, no local test runner, UTF-8 BOM (except Kconfig), CRLF defaults, ESP-IDF version pinning

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
