#!/usr/bin/env python3
"""
Test outputs for playwright-cli-stub task.

Tests both:
1. Code changes: playwright-cli-stub package created, package.json updated
2. Config changes: SKILL.md updated with new installation instructions
"""

import json
import subprocess
from pathlib import Path

REPO = Path("/workspace/playwright")

# =============================================================================
# Code Behavior Tests (f2p)
# =============================================================================

def test_stub_package_exists():
    """FAIL-TO-PASS: playwright-cli-stub package must exist with correct structure."""
    stub_dir = REPO / "packages" / "playwright-cli-stub"
    assert stub_dir.exists(), f"Directory {stub_dir} does not exist"
    
    # Check package.json exists
    pkg_json = stub_dir / "package.json"
    assert pkg_json.exists(), "package.json does not exist"
    
    # Check stub JS file exists and is executable
    stub_js = stub_dir / "playwright-cli-stub.js"
    assert stub_js.exists(), "playwright-cli-stub.js does not exist"
    
    # Check it's executable
    import stat
    mode = stub_js.stat().st_mode
    assert mode & stat.S_IXUSR, "playwright-cli-stub.js is not executable"


def test_stub_package_json_content():
    """FAIL-TO-PASS: package.json must have correct name, version, and bin entry."""
    pkg_json = REPO / "packages" / "playwright-cli-stub" / "package.json"
    
    if not pkg_json.exists():
        # Skip if file doesn't exist - this is caught by test_stub_package_exists
        return
    
    content = json.loads(pkg_json.read_text())
    
    assert content.get("name") == "playwright-cli-stub", f"Wrong name: {content.get('name')}"
    assert content.get("version") == "0.0.0", f"Wrong version: {content.get('version')}"
    assert content.get("private") == True, "Should be private"
    
    bin_entry = content.get("bin", {})
    assert "playwright-cli" in bin_entry, "Missing bin entry for playwright-cli"
    assert bin_entry["playwright-cli"] == "playwright-cli-stub.js", \
        f"Wrong bin path: {bin_entry.get('playwright-cli')}"


def test_stub_js_content():
    """FAIL-TO-PASS: playwright-cli-stub.js must import program and handle errors."""
    stub_js = REPO / "packages" / "playwright-cli-stub" / "playwright-cli-stub.js"
    
    if not stub_js.exists():
        return
    
    content = stub_js.read_text()
    
    # Check shebang
    assert content.startswith("#!/usr/bin/env node"), "Missing shebang"
    
    # Check it imports program from playwright
    assert "require('playwright/lib/cli/client/program')" in content, \
        "Must import program from playwright/lib/cli/client/program"
    
    # Check it handles errors
    assert "program().catch" in content or "catch" in content, \
        "Must handle promise rejection"
    assert "process.exit(1)" in content, "Must exit with code 1 on error"


def test_package_json_script_removed():
    """FAIL-TO-PASS: package.json should no longer have playwright-cli script."""
    pkg_json = REPO / "package.json"
    content = json.loads(pkg_json.read_text())
    
    scripts = content.get("scripts", {})
    assert "playwright-cli" not in scripts, \
        "playwright-cli script should be removed from package.json scripts"


def test_package_lock_updated():
    """FAIL-TO-PASS: package-lock.json should reference playwright-cli-stub."""
    lock_file = REPO / "package-lock.json"
    
    if not lock_file.exists():
        # Some setups might not use package-lock
        return
    
    content = lock_file.read_text()
    
    # Should mention playwright-cli-stub
    assert "playwright-cli-stub" in content, \
        "package-lock.json should reference playwright-cli-stub"


# =============================================================================
# Config/Documentation Update Tests (f2p - REQUIRED for agentmd-edit tasks)
# =============================================================================

def test_skill_md_installation_section():
    """
    FAIL-TO-PASS: SKILL.md must be updated with new installation instructions.
    
    The documentation should now recommend trying npx playwright-cli first
    before installing globally.
    """
    skill_md = REPO / "packages" / "playwright" / "src" / "skill" / "SKILL.md"
    assert skill_md.exists(), "SKILL.md does not exist"
    
    content = skill_md.read_text()
    
    # Check for the key change: recommending npx playwright-cli first
    # This is the main behavioral change in the documentation
    assert "npx playwright-cli" in content, \
        "SKILL.md must mention 'npx playwright-cli' in installation section"
    
    # Check that it documents the local-first approach
    assert "local version" in content.lower() or "npx" in content.lower(), \
        "SKILL.md should document the local version approach"


def test_skill_md_recommends_npx_first():
    """
    FAIL-TO-PASS: SKILL.md should recommend trying npx before global install.
    
    The new flow is:
    1. Try npx playwright-cli --version
    2. If that works, use npx playwright-cli for commands
    3. Only if that fails, install globally
    """
    skill_md = REPO / "packages" / "playwright" / "src" / "skill" / "SKILL.md"
    
    if not skill_md.exists():
        return
    
    content = skill_md.read_text()
    
    # Find the Installation section
    lines = content.split('\n')
    in_installation = False
    installation_section = []
    
    for line in lines:
        if line.strip() == '## Installation':
            in_installation = True
            continue
        if in_installation:
            if line.startswith('## ') and line != '## Installation':
                break
            installation_section.append(line)
    
    installation_text = '\n'.join(installation_section)
    
    # Should mention trying npx first
    assert "npx playwright-cli --version" in installation_text or \
           "npx playwright-cli" in installation_text, \
        "Installation section should mention using npx to check version"
    
    # Should still document global install as fallback
    assert "npm install -g @playwright/cli" in installation_text, \
        "Installation section should still document global install as fallback"


# =============================================================================
# Pass-to-Pass Tests (safety checks)
# =============================================================================

def test_package_json_valid():
    """PASS-TO-PASS: package.json should be valid JSON."""
    pkg_json = REPO / "package.json"
    content = json.loads(pkg_json.read_text())
    assert "name" in content, "package.json should have name field"


def test_skill_md_has_required_sections():
    """PASS-TO-PASS: SKILL.md should have basic structure intact."""
    skill_md = REPO / "packages" / "playwright" / "src" / "skill" / "SKILL.md"
    
    if not skill_md.exists():
        return
    
    content = skill_md.read_text()
    
    # Should have frontmatter
    assert content.startswith("---"), "Should have YAML frontmatter"
    
    # Should have name field in frontmatter
    assert "name: playwright-cli" in content, "Should have correct name in frontmatter"
    
    # Should have key sections
    assert "## Quick start" in content, "Should have Quick start section"
    assert "## Commands" in content, "Should have Commands section"
    assert "## Installation" in content, "Should have Installation section"


if __name__ == "__main__":
    # Run pytest programmatically
    subprocess.run(["python3", "-m", "pytest", __file__, "-v"], check=False)
