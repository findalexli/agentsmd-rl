"""
Task: playwright-cli-stub-local-dev
Repo: microsoft/playwright @ 23b2c1599085bb6dad0f8fb916b631e3cb50ba4b
PR:   39432

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / validation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_root_package_json_valid():
    """Root package.json must be valid JSON after modifications."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('package.json','utf8'))"],
        cwd=REPO, capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"package.json is not valid JSON: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_stub_js_syntax():
    """playwright-cli-stub.js must be valid JavaScript (node --check)."""
    stub_path = Path(REPO) / "packages" / "playwright-cli-stub" / "playwright-cli-stub.js"
    assert stub_path.exists(), "packages/playwright-cli-stub/playwright-cli-stub.js does not exist"
    r = subprocess.run(
        ["node", "--check", str(stub_path)],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Syntax error in stub JS: {r.stderr}"


# [pr_diff] fail_to_pass
def test_stub_package_bin_field():
    """playwright-cli-stub package.json must declare bin.playwright-cli."""
    r = subprocess.run(
        ["node", "-e", """
const pkg = require('./packages/playwright-cli-stub/package.json');
if (!pkg.bin || pkg.bin['playwright-cli'] !== 'playwright-cli-stub.js') {
    console.error('bin field missing or incorrect:', JSON.stringify(pkg.bin));
    process.exit(1);
}
console.log('OK:', JSON.stringify(pkg.bin));
"""],
        cwd=REPO, capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Stub package.json bin field wrong: {r.stderr}"


# [pr_diff] fail_to_pass
def test_stub_requires_program_module():
    """Stub JS must import program from playwright/lib/cli/client/program."""
    stub_js = Path(REPO) / "packages" / "playwright-cli-stub" / "playwright-cli-stub.js"
    assert stub_js.exists(), "Stub JS file does not exist"
    content = stub_js.read_text()
    assert "playwright/lib/cli/client/program" in content, \
        "Stub must require 'playwright/lib/cli/client/program'"
    assert "program" in content, "Stub must reference the 'program' export"


# [pr_diff] fail_to_pass
def test_root_cli_script_removed():
    """Root package.json must NOT have the old 'playwright-cli' npm script."""
    r = subprocess.run(
        ["node", "-e", """
const pkg = require('./package.json');
if (pkg.scripts && pkg.scripts['playwright-cli']) {
    console.error('Found old script:', pkg.scripts['playwright-cli']);
    process.exit(1);
}
console.log('OK: no playwright-cli script in root package.json');
"""],
        cwd=REPO, capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Root package.json still has old playwright-cli script: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/doc update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_npx_before_global():
    """SKILL.md Installation section must recommend npx playwright-cli before global install."""
    skill_md = Path(REPO) / "packages" / "playwright" / "src" / "skill" / "SKILL.md"
    content = skill_md.read_text()
    # New text: try local npx version first
    assert "npx playwright-cli --version" in content, \
        "SKILL.md must contain 'npx playwright-cli --version' check"
    # npx approach must appear BEFORE global install instruction
    npx_pos = content.find("npx playwright-cli --version")
    global_pos = content.find("npm install -g @playwright/cli")
    assert global_pos != -1, "SKILL.md must still mention global install as fallback"
    assert npx_pos < global_pos, \
        "npx local approach must appear before global install in SKILL.md"


# [pr_diff] fail_to_pass
def test_skill_md_old_text_removed():
    """SKILL.md must not have old 'install globally first' wording."""
    skill_md = Path(REPO) / "packages" / "playwright" / "src" / "skill" / "SKILL.md"
    content = skill_md.read_text()
    assert "Once installed, `playwright-cli` will be available as a global command" not in content, \
        "Old text about global command availability should be removed"
    assert "adds a slight `npx` overhead" not in content, \
        "Old text about npx overhead should be removed"
