# Type Checking Support for Lazy-Loaded Modules

## Problem

After a recent change to implement lazy loading of classes and modules in the Python bindings, IDEs and type checkers (like mypy, Pylance, pyright) can no longer detect type hints on imported items from `selenium.webdriver`.

For example, this code works at runtime but type checkers show errors:

```python
from selenium.webdriver import Chrome, ChromeOptions, Keys

driver = Chrome()  # Type checker: Cannot find "Chrome" in "selenium.webdriver"
```

The lazy loading optimization defers imports until they're actually used at runtime, which is great for startup performance. However, static analysis tools examine the code without executing it, so they can't see what the lazy loader would eventually provide.

## Affected Areas

- `py/selenium/webdriver/` - Main webdriver package
- Browser-specific submodules: `chrome/`, `edge/`, `firefox/`, `ie/`, `safari/`, `webkitgtk/`, `wpewebkit/`

## Requirements

### 1. Type stub files for webdriver package

Create a `__init__.pyi` stub file at `py/selenium/webdriver/__init__.pyi` that exports the following classes so type checkers can see them:

- `Chrome` (maps to `selenium.webdriver.chrome.webdriver.WebDriver`)
- `Firefox` (maps to `selenium.webdriver.firefox.webdriver.WebDriver`)
- `Edge` (maps to `selenium.webdriver.edge.webdriver.WebDriver`)
- `ActionChains` (maps to `selenium.webdriver.common.action_chains.ActionChains`)
- `DesiredCapabilities` (maps to `selenium.webdriver.common.desired_capabilities.DesiredCapabilities`)
- `Keys` (maps to `selenium.webdriver.common.keys.Keys`)

### 2. Type stub files for browser submodules

Each browser submodule needs a `__init__.pyi` stub file at `py/selenium/webdriver/<browser>/__init__.pyi`:

- **chrome**: must export `options`, `service`, `webdriver` modules and define `__all__`
- **edge**: must export `options`, `service`, `webdriver` modules and define `__all__`
- **firefox**: must export `firefox_profile`, `options`, `service`, `webdriver` modules and define `__all__`
- **ie**: must export `options`, `service`, `webdriver` modules and define `__all__`
- **safari**: must export `permissions`, `options`, `service`, `webdriver` modules and define `__all__`
- **webkitgtk**: must export `options`, `service`, `webdriver` modules and define `__all__`
- **wpewebkit**: must export `options`, `service`, `webdriver` modules and define `__all__`

### 3. Build configuration update

Modify `py/pyproject.toml` to include `*.pyi` files in the package data so they are distributed with the package.

### 4. Import path corrections

Some remote connection files may currently import `DesiredCapabilities` through the lazy-loading `selenium.webdriver` namespace. These must be changed to use a direct import path from `selenium.webdriver.common.desired_capabilities` to avoid circular dependency issues when type stubs are loaded.

The correct import path is:
```
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
```

## Hints

- Python provides a mechanism for supplying type information separately from runtime code using stub files (`.pyi` extension)
- The build configuration file controls what files are included in package distributions
- Some files may have imports that go through the lazy-loading namespace when they should use a direct path
- Each browser stub file should define an `__all__` list to explicitly declare what it exports
