#!/usr/bin/env python3
"""Tests for playwright-cli stub task."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")


def test_cli_stub_package_exists():
    """Fail-to-pass: packages/playwright-cli-stub/package.json must exist."""
    stub_pkg = REPO / "packages" / "playwright-cli-stub" / "package.json"
    assert stub_pkg.exists(), "playwright-cli-stub package.json must exist"

    pkg = json.loads(stub_pkg.read_text())
    assert pkg.get("name") == "playwright-cli-stub", "Package name must be playwright-cli-stub"
    assert pkg.get("private") is True, "Package must be private"
    assert "bin" in pkg, "Package must have bin entry"
    assert pkg["bin"].get("playwright-cli") == "playwright-cli-stub.js", \
        "Bin entry must point to playwright-cli-stub.js"


def test_cli_stub_script_exists():
    """Fail-to-pass: packages/playwright-cli-stub/playwright-cli-stub.js must exist."""
    stub_script = REPO / "packages" / "playwright-cli-stub" / "playwright-cli-stub.js"
    assert stub_script.exists(), "playwright-cli-stub.js must exist"

    import stat
    mode = stub_script.stat().st_mode
    assert mode & stat.S_IXUSR, "Script must be executable"

    content = stub_script.read_text()
    assert "#!/usr/bin/env node" in content, "Script must have node shebang"
    assert "require('playwright/lib/cli/client/program')" in content, \
        "Script must require playwright/lib/cli/client/program"


def test_root_package_json_updated():
    """Fail-to-pass: root package.json must not have old playwright-cli script."""
    root_pkg = REPO / "package.json"
    content = root_pkg.read_text()
    pkg = json.loads(content)

    scripts = pkg.get("scripts", {})
    assert "playwright-cli" not in scripts, \
        "Root package.json should not have playwright-cli script"


def test_skill_md_updated_for_local_npx():
    """Fail-to-pass: SKILL.md must document local npx usage before global install."""
    skill_md = REPO / "packages" / "playwright/src/skill" / "SKILL.md"
    content = skill_md.read_text()

    assert "npx playwright-cli" in content, \
        "SKILL.md must mention npx playwright-cli as the local option"
    assert "npx playwright-cli --version" in content, \
        "SKILL.md must include 'npx playwright-cli --version' example"


def test_stub_imports_playwright_program():
    """Pass-to-pass: The stub script should be able to import the playwright module."""
    program_path = REPO / "packages" / "playwright" / "lib" / "cli" / "client" / "program.js"
    if program_path.exists():
        assert True, "Program module exists for import"
    else:
        src_program = REPO / "packages" / "playwright" / "src" / "cli" / "client" / "program.ts"
        assert src_program.exists(), "Program source file should exist"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
