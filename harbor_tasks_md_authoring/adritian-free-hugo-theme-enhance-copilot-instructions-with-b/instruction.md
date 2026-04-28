# ✨ Enhance Copilot instructions with best practices

Source: [zetxek/adritian-free-hugo-theme#363](https://github.com/zetxek/adritian-free-hugo-theme/pull/363)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Overview

This PR enhances the `.github/copilot-instructions.md` file following [GitHub Copilot best practices for repository custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions). The file already existed with good foundation content, but was missing several recommended sections that help AI assistants provide better, more contextual suggestions.

## What Changed

Added **88 lines** of comprehensive guidance across 5 major new sections:

### 1. 🏗️ Project Overview with Technology Stack
- Explicit listing of all technologies used in the theme
- Version requirements (Hugo v0.136+ extended)
- Frontend frameworks (Bootstrap 5 v5.3.8)
- Build tools (PostCSS, Autoprefixer)
- Testing frameworks (Playwright)

This helps Copilot understand the full technical context when making suggestions.

### 2. 📋 Coding Standards and Conventions
Detailed language-specific guidelines for:
- **HTML/Hugo Templates**: Semantic HTML5, template naming conventions, use of Hugo built-in functions
- **SCSS/CSS**: Bootstrap 5 conventions, BEM methodology, CSS custom properties, file naming
- **JavaScript**: Vanilla JS preference, ES6+ syntax, progressive enhancement, minimal JavaScript approach
- **Content/Configuration**: YAML frontmatter patterns, TOML configuration standards
- **File Naming**: Consistent conventions across all file types

Ensures consistent code style across all AI-generated suggestions.

### 3. ♿ Web Accessibility Requirements
- WCAG 2.1 AA c

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
