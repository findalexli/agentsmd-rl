"""
Task: playwright-chore-playwrightcli-stub-for-local
Repo: microsoft/playwright @ 23b2c1599085bb6dad0f8fb916b631e3cb50ba4b
PR:   39432

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
from pathlib import Path

REPO = "/workspace/playwright"
STUB_DIR = Path(REPO) / "packages/playwright-cli-stub"
SKILL_MD = Path(REPO) / "packages/playwright/src/skill/SKILL.md"
ROOT_PKG = Path(REPO) / "package.json"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_root_package_json_valid():
    """Root package.json must remain valid JSON."""
    content = ROOT_PKG.read_text()
    data = json.loads(content)
    assert "scripts" in data, "package.json must have scripts section"
    assert "workspaces" in data, "package.json must have workspaces section"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_stub_package_has_bin_entry():
    """A stub package under packages/ must declare playwright-cli as a bin entry."""
    pkg_json = STUB_DIR / "package.json"
    assert pkg_json.exists(), \
        "packages/playwright-cli-stub/package.json must exist"
    data = json.loads(pkg_json.read_text())
    assert "bin" in data, "Stub package.json must have a bin field"
    assert "playwright-cli" in data["bin"], \
        "bin must include a 'playwright-cli' entry"
    # The bin entry must point to a .js file
    bin_target = data["bin"]["playwright-cli"]
    assert bin_target.endswith(".js"), \
        f"bin target must be a .js file, got: {bin_target}"


# [pr_diff] fail_to_pass
def test_stub_script_requires_program():
    """The stub JS file must import and invoke the CLI program from playwright."""
    # Find the JS file referenced by the bin entry
    pkg_json = STUB_DIR / "package.json"
    data = json.loads(pkg_json.read_text())
    js_file = STUB_DIR / data["bin"]["playwright-cli"]
    assert js_file.exists(), f"Stub script {js_file} must exist"

    content = js_file.read_text()
    # Must have a node shebang
    assert content.startswith("#!/usr/bin/env node") or \
           content.startswith("#!/usr/bin/node"), \
        "Stub script must have a node shebang"
    # Must require/import the playwright CLI program module
    assert "playwright" in content and ("program" in content or "cli" in content), \
        "Stub must import the playwright CLI program"
    # Must actually call the program (not just import)
    assert re.search(r'program\s*\(', content) or \
           re.search(r'cli\s*\(', content) or \
           re.search(r'main\s*\(', content), \
        "Stub must invoke the CLI program function"


# [pr_diff] fail_to_pass
def test_stub_script_has_error_handling():
    """The stub JS file must handle errors (catch + exit)."""
    pkg_json = STUB_DIR / "package.json"
    data = json.loads(pkg_json.read_text())
    js_file = STUB_DIR / data["bin"]["playwright-cli"]
    content = js_file.read_text()

    # Must have error handling (catch block with process.exit)
    assert ".catch" in content or "try" in content, \
        "Stub must have error handling (catch or try/catch)"
    assert "process.exit" in content, \
        "Stub must call process.exit on error"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — SKILL.md documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass

    # npx (local) must appear before npm install -g (global)
    npx_pos = install_section.find("npx playwright-cli")
    global_pos = install_section.find("npm install -g")
    assert npx_pos != -1, "Must mention npx playwright-cli"
    assert global_pos != -1, "Must still mention global install as fallback"
    assert npx_pos < global_pos, \
        "Local npx approach must be recommended before global npm install -g"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
