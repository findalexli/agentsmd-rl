"""
Task: react-devtools-disable-activity-slices
Repo: facebook/react @ 3ce1316b05968d2a8cffe42a110f2726f2c44c3e
PR:   35685

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/react"
CONFIG_DIR = f"{REPO}/packages/react-devtools-shared/src/config"
SUSPENSE_TAB = f"{REPO}/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.js"

FB_CONFIGS = [
    f"{CONFIG_DIR}/DevToolsFeatureFlags.core-fb.js",
    f"{CONFIG_DIR}/DevToolsFeatureFlags.extension-fb.js",
]

OSS_CONFIGS = [
    f"{CONFIG_DIR}/DevToolsFeatureFlags.core-oss.js",
    f"{CONFIG_DIR}/DevToolsFeatureFlags.extension-oss.js",
    f"{CONFIG_DIR}/DevToolsFeatureFlags.default.js",
]

ALL_CONFIGS = FB_CONFIGS + OSS_CONFIGS


def _run_node(script: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Execute a Node.js script in the repo directory."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _eval_config(config_path: str, dev_value: bool = True) -> dict:
    """Evaluate a DevTools feature flag config via Node, returning exported values."""
    r = _run_node(f"""
const fs = require('fs');
let src = fs.readFileSync({json.dumps(config_path)}, 'utf8');
src = src.replace(/:\\s*boolean/g, '');
src = src.replace(/export\\s+const\\s+(\\w+)\\s*=/g, 'result.$1 =');
const __DEV__ = {json.dumps(dev_value)};
const result = {{}};
eval(src);
console.log(JSON.stringify(result));
""")
    assert r.returncode == 0, f"Node eval failed for {config_path}: {r.stderr}"
    return json.loads(r.stdout.strip())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_flag_false_in_fb_configs():
    """Facebook build configs (core-fb, extension-fb) export enableActivitySlices as false."""
    for path in FB_CONFIGS:
        exports = _eval_config(path)
        assert "enableActivitySlices" in exports, (
            f"enableActivitySlices not exported from {path}"
        )
        assert exports["enableActivitySlices"] is False, (
            f"Expected false in {path}, got {exports['enableActivitySlices']}"
        )


# [pr_diff] fail_to_pass
def test_flag_dev_in_oss_configs():
    """OSS configs export enableActivitySlices gated on __DEV__ (true in dev, false in prod)."""
    for path in OSS_CONFIGS:
        dev_exports = _eval_config(path, dev_value=True)
        assert "enableActivitySlices" in dev_exports, (
            f"enableActivitySlices not exported from {path}"
        )
        assert dev_exports["enableActivitySlices"] is True, (
            f"enableActivitySlices should be true when __DEV__=true in {path}"
        )
        prod_exports = _eval_config(path, dev_value=False)
        assert prod_exports["enableActivitySlices"] is False, (
            f"enableActivitySlices should be false when __DEV__=false in {path}"
        )


# [pr_diff] fail_to_pass
def test_suspense_tab_imports_flag():
    """SuspenseTab.js imports enableActivitySlices from react-devtools-feature-flags."""
    r = _run_node(f"""
const fs = require('fs');
const src = fs.readFileSync({json.dumps(SUSPENSE_TAB)}, 'utf8');
const re = /import\\s*\\{{[^}}]*enableActivitySlices[^}}]*\\}}\\s*from\\s*['"]react-devtools-feature-flags['"]/;
if (!re.test(src)) {{
    console.error('No import of enableActivitySlices from react-devtools-feature-flags');
    process.exit(1);
}}
console.log('PASS');
""")
    assert r.returncode == 0, f"Import check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_suspense_tab_uses_flag():
    """activityListDisabled expression correctly gates on enableActivitySlices."""
    r = _run_node(f"""
const fs = require('fs');
const src = fs.readFileSync({json.dumps(SUSPENSE_TAB)}, 'utf8');

// Extract the activityListDisabled assignment expression
const match = src.match(/const\\s+activityListDisabled\\s*=\\s*(.+?)\\s*;/);
if (!match) {{
    console.error('activityListDisabled assignment not found');
    process.exit(1);
}}
const expr = match[1];

// Evaluate with different flag/activity combinations
// [enableActivitySlices, activities.length, expected]
const cases = [
    [false, 0, true],   // flag off, no activities -> disabled
    [false, 5, true],   // flag off, has activities -> still disabled (flag gates)
    [true, 0, true],    // flag on, no activities -> disabled
    [true, 5, false],   // flag on, has activities -> enabled
];

for (const [flagVal, actLen, expected] of cases) {{
    const enableActivitySlices = flagVal;
    const activities = {{ length: actLen }};
    const result = eval(expr);
    if (result !== expected) {{
        console.error(
            `FAIL: enableActivitySlices=${{flagVal}}, activities.length=${{actLen}} ` +
            `-> ${{result}} (expected ${{expected}})`
        );
        process.exit(1);
    }}
}}
console.log('PASS');
""")
    assert r.returncode == 0, f"Flag gating check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — new flags must be in ALL fork files
# Source: .claude/skills/feature-flags/SKILL.md:45 @ 3ce1316b
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass
def test_flag_present_in_all_fork_files():
    """enableActivitySlices must be declared in every one of the 5 fork config files."""
    for path in ALL_CONFIGS:
        exports = _eval_config(path)
        assert "enableActivitySlices" in exports, (
            f"enableActivitySlices flag missing from {path} — "
            "all fork files must declare every new flag"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression guard
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_flag_files_maintain_structure():
    """All 5 feature flag config files still export enableLogger (existing flag, not removed)."""
    for path in ALL_CONFIGS:
        content = Path(path).read_text()
        assert "enableLogger" in content, (
            f"enableLogger flag missing from {path} — config file structure was corrupted"
        )
