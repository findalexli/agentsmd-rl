# Create copilot-instructions.md with plugin development guidelines

Source: [Fu-Jie/openwebui-extensions#7](https://github.com/Fu-Jie/openwebui-extensions/pull/7)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Establishes standardized development guidelines for Copilot to follow when generating code or documentation for this repository.

## Key Guidelines

- **Bilingual requirements**: Every plugin must have English (`plugin_name.py`) and Chinese (`插件名.py`) versions with corresponding `README.md` and `README_CN.md`

- **Standardized docstring format**:
```python
"""
title: 插件名称
author: Fu-Jie
author_url: https://github.com/Fu-Jie
funding_url: https://github.com/Fu-Jie/awesome-openwebui
version: 0.1.0
icon_url: data:image/svg+xml;base64,<base64-encoded-svg>
requirements: python-docx==1.1.2
description: Brief description of plugin functionality.
"""
```

- **Unified author/license info**: All docs must include Fu-Jie attribution and MIT License
- **Icon source**: Lucide Icons with Base64 encoding
- **Valves naming**: UPPER_SNAKE_CASE for all configuration fields
- **Logging**: Use `logging` module, not `print()`
- **HTML injection**: Unified wrapper template with `<!-- OPENWEBUI_PLUGIN_OUTPUT -->` marker
- **i18n**: Extract user language from `__user__.get("language")` with appropriate defaults per version

Includes development checklist and references to existing templates in the repository.

<!-- START COPILOT CODING AGENT SUFFIX -->



<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

> 创建 copilot-instructions.md，参考下面的内容创建
> 
> 1. 要求每一个插件都有中文版2个版本，都需要2个版本的readme，统一信息
> ## Author
> 
> Fu-Jie  
> GitHub: [Fu-Jie/awesome-openwebui](https://githu

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
