# docs: add GitHub Copilot instructions file

Source: [linuxdeepin/dde-control-center#2914](https://github.com/linuxdeepin/dde-control-center/pull/2914)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Added comprehensive GitHub Copilot instructions file (.github/copilot-
instructions.md) to provide AI coding agents with detailed project
context and development guidelines. This file includes:
1. Project overview of DDE Control Center v6.0+ as a Qt6/QML-based
desktop control panel
2. Critical architecture concepts including the V25 plugin system with
two-phase loading
3. Core framework classes like DccObject, DccApp, and DccFactory
4. QML-C++ integration patterns and build workflows
5. Plugin development patterns with CMake templates and registration
examples
6. Project conventions for file naming, configuration management, and Qt
version usage
7. Testing information and common pitfalls to avoid

This file was created to help AI assistants understand the complex
plugin-based architecture and provide accurate code suggestions,
reducing development errors and improving productivity.

Influence:
1. Review the instructions file for accuracy and completeness
2. Test if AI coding assistants can generate appropriate code based on
these guidelines
3. Verify that the build instructions work correctly
4. Check that plugin development patterns are correctly documented
5. Ensure common pitfalls are adequately addressed

docs: 添加 GitHub Copilot 指令文件

新增了全面的 GitHub Copilot 指令文件 (.github/copilot-instructions.md)，
为 AI 编码助手提供详细的项目上下文和开发指南。该文件包含：
1. DDE 控制中心 v6.0+ 的项目概述，作为基于 Qt6/QML 的桌面控制面板
2. 关键架构概念，包括具有两阶段加载的 V25 插件系统
3. 核心框架类如 DccObject、DccApp 和 DccFactory
4. QML-C++ 集成模式和构建工作流程
5. 插件开发模式

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
