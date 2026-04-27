# Fix Type Checker Visibility for Lazy Imports

## Problem

The `selenium.webdriver` package uses lazy imports in its `__init__.py` files to defer loading modules until they're accessed. This improves startup performance but breaks type checking—mypy and IDEs cannot see the available classes and submodules because they're not imported at package initialization time.

The lazy import mechanism also affects how some internal webdriver modules resolve names that are only available through the lazy loading pattern.

## What You Need to Do

### 1. Create type stub (`.pyi`) files

Create `.pyi` stub files in `py/selenium/webdriver/` for these packages:

- `__init__.pyi` — main webdriver exports
- `chrome/__init__.pyi` — chrome submodule exports (must include `options` and `webdriver` submodules)
- `edge/__init__.pyi` — edge submodule exports
- `firefox/__init__.pyi` — firefox submodule exports (must include `firefox_profile`)
- `safari/__init__.pyi` — safari submodule exports
- `ie/__init__.pyi` — ie submodule exports
- `webkitgtk/__init__.pyi` — webkitgtk submodule exports
- `wpewebkit/__init__.pyi` — wpewebkit submodule exports

Each stub file should:
- Mirror the exports from the corresponding `__init__.py`
- Use explicit import statements (not lazy) since stubs are only read by type checkers
- Include the standard Apache 2.0 license header
- Have a docstring explaining the stub's purpose

#### Required exports for the main `webdriver/__init__.pyi`

The main stub must make these names available for type checking:

- Browser classes: `Chrome`, `Firefox`, `Edge`, `Safari`, `Remote`
- Option classes: `ChromeOptions`, `FirefoxOptions`, `EdgeOptions`, `SafariOptions`
- Service classes: `ChromeService`, `FirefoxService`, `EdgeService`
- Utility classes: `ActionChains`, `Keys`

### 2. Update build configuration

Ensure that `.pyi` stub files are included in the distributed package by updating the package data configuration in `py/pyproject.toml`.

### 3. Fix import issues caused by lazy imports

Some internal webdriver modules import `DesiredCapabilities` through the top-level `selenium.webdriver` package, which relies on the lazy import mechanism. This can cause issues when the lazy loading hasn't resolved the name yet. Find any such modules and fix them to use direct imports from the appropriate submodule instead of relying on the lazy import mechanism.

All existing unit tests should continue to pass after your fix.

## Verification

You can verify your changes by:

1. Confirming all 8 `.pyi` stub files exist in the correct locations
2. Running mypy on a test file that imports from `selenium.webdriver` (e.g., `Chrome`, `Firefox`, `ChromeOptions`, `Keys`) — there should be no "cannot find" errors related to webdriver
3. Checking that `"*.pyi"` is in pyproject.toml's package-data section
4. Running the repo's existing test suite to ensure nothing is broken

## Code Style Requirements

This repository uses **ruff** for Python linting. All new `.pyi` files and any modified `.py` files must pass `ruff check` without errors.

## Context

- The lazy imports were introduced for performance
- Type checkers cannot follow lazy import patterns, hence the need for parallel stub files
- See the repository's `py/AGENTS.md` for Python-specific conventions including type hint syntax (use `str | None` not `Optional[str]`)
