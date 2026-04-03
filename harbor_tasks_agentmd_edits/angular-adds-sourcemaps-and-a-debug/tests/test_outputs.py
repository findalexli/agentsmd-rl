"""
Task: angular-adds-sourcemaps-and-a-debug
Repo: angular/angular @ f30ed6bbf6706790437a6e4dbfffed3fa8708f57
PR:   67189

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
from pathlib import Path

REPO = "/workspace/angular"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified .bzl and BUILD.bazel files must have balanced parentheses."""
    bzl_files = [
        Path(REPO) / "devtools" / "tools" / "defaults.bzl",
        Path(REPO) / "devtools" / "BUILD.bazel",
        Path(REPO) / "devtools" / "projects" / "shell-browser" / "src" / "BUILD.bazel",
        Path(REPO) / "devtools" / "projects" / "shell-browser" / "src" / "app" / "BUILD.bazel",
    ]
    for f in bzl_files:
        content = f.read_text()
        assert content.count("(") == content.count(")"), \
            f"Unbalanced parentheses in {f.name}"
        assert content.count("[") == content.count("]"), \
            f"Unbalanced brackets in {f.name}"


# [static] pass_to_pass
def test_package_json_valid():
    """package.json must be valid JSON with a scripts object."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    assert "scripts" in pkg, "package.json must have scripts"
    assert isinstance(pkg["scripts"], dict)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core build config tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_defaults_bzl_esbuild_wrapper():
    """defaults.bzl must define a custom esbuild() wrapper with minify/sourcemap."""
    content = (Path(REPO) / "devtools" / "tools" / "defaults.bzl").read_text()
    assert re.search(r"^def\s+esbuild\s*\(", content, re.MULTILINE), \
        "defaults.bzl must define 'def esbuild(' wrapper function"
    assert "minify" in content, \
        "esbuild wrapper must handle the minify parameter"
    assert "sourcemap" in content, \
        "esbuild wrapper must handle the sourcemap parameter"


# [pr_diff] fail_to_pass
def test_debug_flag_defined():
    """devtools/BUILD.bazel must define a debug bool_flag and config_setting."""
    content = (Path(REPO) / "devtools" / "BUILD.bazel").read_text()
    assert "bool_flag(" in content, \
        "devtools/BUILD.bazel must define a bool_flag"
    assert re.search(r'name\s*=\s*"debug"', content), \
        "bool_flag must be named 'debug'"
    assert "config_setting(" in content, \
        "devtools/BUILD.bazel must define a config_setting"
    assert re.search(r'name\s*=\s*"debug_build"', content), \
        "config_setting must be named 'debug_build'"


# [pr_diff] fail_to_pass
def test_package_json_debug_scripts():
    """package.json must have debug build scripts for chrome and firefox."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "devtools:build:chrome:debug" in scripts, \
        "package.json must have devtools:build:chrome:debug script"
    assert "devtools:build:firefox:debug" in scripts, \
        "package.json must have devtools:build:firefox:debug script"
    chrome_debug = scripts["devtools:build:chrome:debug"]
    assert "debug" in chrome_debug.lower(), \
        "Chrome debug script must reference debug mode"


# [pr_diff] fail_to_pass
def test_sourcemap_inline_for_injected_scripts():
    """Injected script esbuild targets must use sourcemap = 'inline'."""
    content = (Path(REPO) / "devtools" / "projects" / "shell-browser" / "src" / "app" / "BUILD.bazel").read_text()
    blocks = re.split(r'\besbuild\s*\(', content)[1:]
    injected_scripts = ["detect-angular.ts", "backend.ts", "ng-validate.ts", "content-script.ts"]
    for script in injected_scripts:
        found = False
        for block in blocks:
            if script in block:
                found = True
                assert 'sourcemap = "inline"' in block or "sourcemap = 'inline'" in block, \
                    f"esbuild target for {script} must have sourcemap = 'inline'"
                break
        assert found, f"Could not find esbuild target for {script}"


# [pr_diff] fail_to_pass
def test_no_hardcoded_minify_in_shell_browser_src():
    """devtools/projects/shell-browser/src/BUILD.bazel must not hardcode minify = True."""
    content = (Path(REPO) / "devtools" / "projects" / "shell-browser" / "src" / "BUILD.bazel").read_text()
    assert "minify = True" not in content, \
        "shell-browser/src/BUILD.bazel must not hardcode minify = True"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_release_scripts_intact():
    """Existing release build scripts must still be present in package.json."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "devtools:build:chrome:release" in scripts, \
        "devtools:build:chrome:release script must still exist"
    assert "devtools:build:firefox:release" in scripts, \
        "devtools:build:firefox:release script must still exist"
    assert "devtools:build:chrome" in scripts, \
        "devtools:build:chrome base script must still exist"
