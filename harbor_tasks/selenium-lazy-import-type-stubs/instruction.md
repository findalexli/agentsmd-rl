# Fix Type Checker Visibility for Lazy Imports

## Problem

The `selenium.webdriver` package uses lazy imports in its `__init__.py` files to defer loading modules until they're accessed. This improves startup performance but breaks type checking—mypy and IDEs cannot see the available classes and submodules because they're not imported at package initialization time.

## What You Need to Do

Create `.pyi` (type stub) files for the webdriver packages so type checkers get full visibility while runtime keeps the lazy import behavior.

### Files to Modify

1. **Create type stubs** in `py/selenium/webdriver/`:
   - `__init__.pyi` - main webdriver exports (Chrome, Firefox, Edge, Safari, Ie, WebKitGTK, WPEWebKit, etc.)
   - `chrome/__init__.pyi` - chrome submodule exports
   - `edge/__init__.pyi` - edge submodule exports
   - `firefox/__init__.pyi` - firefox submodule exports (includes firefox_profile)
   - `safari/__init__.pyi` - safari submodule exports
   - `ie/__init__.pyi` - ie submodule exports
   - `webkitgtk/__init__.pyi` - webkitgtk submodule exports
   - `wpewebkit/__init__.pyi` - wpewebkit submodule exports

2. **Update `py/pyproject.toml`**:
   - Add `"*.pyi"` to the `[tool.setuptools.package-data]` section so stub files are included in the distribution

3. **Fix imports** in `py/selenium/webdriver/chrome/remote_connection.py` and `py/selenium/webdriver/edge/remote_connection.py`:
   - Change `from selenium.webdriver import DesiredCapabilities` to `from selenium.webdriver.common.desired_capabilities import DesiredCapabilities`

### Requirements for Stub Files

Each stub file should:
- Mirror the exports from the corresponding `__init__.py`
- Use explicit import statements (not lazy) since stubs are only read by type checkers
- Include the standard Apache 2.0 license header
- Have a docstring explaining the stub's purpose

Example structure for `chrome/__init__.pyi`:
```python
"""Type stub with lazy import mapping from __init__.py.

This stub file is necessary for type checkers and IDEs to automatically have
visibility into lazy modules since they are not imported immediately at runtime.
"""

from . import options, remote_connection, service, webdriver

__all__ = ["options", "remote_connection", "service", "webdriver"]
```

The main `webdriver/__init__.pyi` should export all the webdriver classes like Chrome, Firefox, Edge, Safari, Ie, WebKitGTK, WPEWebKit, plus common utilities like ActionChains, Keys, etc.

### Testing Your Fix

Run these checks to verify your solution:

1. **Stub files exist**: Check that all 8 `.pyi` files are created in the correct locations

2. **mypy can resolve types**: Create a test file that imports from selenium.webdriver and run mypy on it:
   ```python
   from selenium.webdriver import Chrome, Firefox, ChromeOptions
   ```

3. **Imports work**: Verify direct import of DesiredCapabilities works:
   ```python
   from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
   ```

4. **pyproject.toml updated**: Check that `*.pyi` is in the package-data section

## Context

- The lazy imports were introduced in PR #16993 for performance
- Type checkers cannot follow lazy import patterns, hence the need for parallel stub files
- This is a packaging/distribution fix that affects developer experience

See the repository's `py/AGENTS.md` for Python-specific conventions including type hint syntax (use `str | None` not `Optional[str]`).
