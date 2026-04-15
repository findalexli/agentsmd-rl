# Fix Type Checker Visibility for Lazy Imports

## Problem

The `selenium.webdriver` package uses lazy imports in its `__init__.py` files to defer loading modules until they're accessed. This improves startup performance but breaks type checking—mypy and IDEs cannot see the available classes and submodules because they're not imported at package initialization time.

The lazy import mechanism also affects how `DesiredCapabilities` is accessed by some internal webdriver modules that import it through the top-level `selenium.webdriver` package.

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

### 2. Update `py/pyproject.toml`

Add `"*.pyi"` to the `[tool.setuptools.package-data]` section so stub files are included in the distribution.

### 3. Fix import issues caused by lazy imports

The lazy import mechanism in `selenium.webdriver` can break modules that depend on `DesiredCapabilities` being importable through the top-level package. Identify any modules affected by this and fix them so that:

- `DesiredCapabilities` can be imported directly from `selenium.webdriver.common.desired_capabilities`
- All existing unit tests continue to pass

## Verification

You can verify your changes by:

1. Confirming all 8 `.pyi` stub files exist in the correct locations
2. Running mypy on a test file that imports from `selenium.webdriver` (e.g., `Chrome`, `Firefox`, `ChromeOptions`, `Keys`) — there should be no "cannot find" errors related to webdriver
3. Verifying that `from selenium.webdriver.common.desired_capabilities import DesiredCapabilities` works
4. Checking that `"*.pyi"` is in pyproject.toml's package-data section
5. Running the repo's existing test suite to ensure nothing is broken

## Context

- The lazy imports were introduced for performance
- Type checkers cannot follow lazy import patterns, hence the need for parallel stub files
- See the repository's `py/AGENTS.md` for Python-specific conventions including type hint syntax (use `str | None` not `Optional[str]`)
