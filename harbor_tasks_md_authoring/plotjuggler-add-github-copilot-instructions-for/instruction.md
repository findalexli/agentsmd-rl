# Add GitHub Copilot instructions for repository context

Source: [PlotJuggler/PlotJuggler#1242](https://github.com/PlotJuggler/PlotJuggler/pull/1242)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Configures `.github/copilot-instructions.md` to provide Copilot with repository-specific context per [gh.io/copilot-coding-agent-tips](https://gh.io/copilot-coding-agent-tips).

## Contents

- **Project architecture**: Core library (plotjuggler_base), GUI app, plugin system with 5 plugin types
- **Build instructions**: Platform-specific commands for Linux/macOS/Windows, plus ROS1/ROS2 variants
- **Code conventions**: Google C++ style with customizations, clang-format config, naming patterns, MPL-2.0 headers
- **Plugin development**: Base classes, structure requirements, Qt plugin system usage
- **CI/CD workflows**: 8 workflows covering platform builds, ROS integration, security scanning
- **Dependencies**: Qt5, CMake 3.16+, C++17, fmt, protobuf, ZeroMQ, lz4, zstd

This enables Copilot to understand PlotJuggler's cross-platform Qt/C++ architecture, plugin extensibility model, and ROS integration when assisting with development tasks.

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
> </comments

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
