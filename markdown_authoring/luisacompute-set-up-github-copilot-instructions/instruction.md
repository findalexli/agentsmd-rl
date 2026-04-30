# ✨ Set up GitHub Copilot instructions

Source: [LuisaGroup/LuisaCompute#218](https://github.com/LuisaGroup/LuisaCompute/pull/218)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR adds comprehensive GitHub Copilot instructions to help AI assistants better understand and contribute to the LuisaCompute project.

## What's Changed

Added `.github/copilot-instructions.md` containing detailed guidance on:

- **Project Overview**: Description of LuisaCompute as a high-performance cross-platform computing framework with its embedded DSL, unified runtime, and multiple backend support (CUDA, DirectX, Metal, CPU)

- **Build System**: Instructions for both CMake and XMake build systems, including requirements (C++20, LLVM toolchain), quick start commands, and backend-specific dependencies

- **Code Style**: References to `.clang-format` and `.clang-tidy` configurations, C++20 best practices, and special DSL macros like `$if`, `$for`, `$while` that behave like C++ keywords

- **Project Structure**: Overview of the codebase organization including core modules (AST/IR, backends, DSL, runtime, Python bindings)

- **DSL and Runtime Concepts**: Key types (vectors, matrices, Var<T>), constructs (Callable, Kernel), runtime resources (Context, Device, Stream, Buffer, Image), and typical workflow patterns

- **Testing**: Using doctest framework with backend-specific command-line arguments

- **Python Frontend**: Installation instructions and key differences from C++ DSL

- **Best Practices**: Guidelines for adding features, modifying DSL, working with backends, and managing dependencies

- **Common Commands**: Building, code generation, and development workflows

#

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
