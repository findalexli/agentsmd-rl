"""
Task: react-component-performance-track-static
Repo: facebook/react @ 3e319a943cff862b8fbb8e96868f9f153a9e199d
PR:   35629

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
FORKS = Path(f"{REPO}/packages/shared/forks")


def _run_shell(cmd: list, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a shell command in the repo directory."""
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — files must exist
# ---------------------------------------------------------------------------

def test_files_exist():
    """All four feature flag fork files must be present."""
    for name in [
        "ReactFeatureFlags.native-fb-dynamic.js",
        "ReactFeatureFlags.native-fb.js",
        "ReactFeatureFlags.www-dynamic.js",
        "ReactFeatureFlags.www.js",
    ]:
        assert (FORKS / name).exists(), f"Missing required fork file: {name}"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass tests — verify repo checks still pass
# ---------------------------------------------------------------------------


def test_repo_license():
    """Repo license check passes (pass_to_pass)."""
    r = _run_shell(["./scripts/ci/check_license.sh"], timeout=30)
    assert r.returncode == 0, f"License check failed:\n{r.stderr[-500:]}"


def test_repo_version_check():
    """Repo version check passes (pass_to_pass)."""
    r = _run_shell(["node", "./scripts/tasks/version-check.js"], timeout=30)
    assert r.returncode == 0, f"Version check failed:\n{r.stderr[-500:]}"


def test_repo_eslint():
    """Repo ESLint check passes (pass_to_pass)."""
    r = _run_shell(["node", "./scripts/tasks/eslint.js"], timeout=120)
    assert r.returncode == 0, f"ESLint check failed:\n{r.stderr[-500:]}"


def test_repo_print_warnings():
    """Repo print warnings check passes (pass_to_pass)."""
    r = _run_shell(["./scripts/ci/test_print_warnings.sh"], timeout=30)
    assert r.returncode == 0, f"Print warnings check failed:\n{r.stderr[-500:]}"


def test_repo_tests_shared():
    """Repo shared package tests pass (pass_to_pass)."""
    r = _run_shell(
        ["node", "./scripts/jest/jest-cli.js", "--testPathPattern=shared", "--ci"],
        timeout=180
    )
    assert r.returncode == 0, f"Shared tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via Node execution
# ---------------------------------------------------------------------------

NATIVE_FB_DYNAMIC_CHECK = '''
const fs = require("fs");
const content = fs.readFileSync(
    "packages/shared/forks/ReactFeatureFlags.native-fb-dynamic.js", "utf8"
);
const lines = content.split(/\\r?\\n/).filter(
    l => /export\\s+const\\s+enableComponentPerformanceTrack/.test(l)
);
if (lines.length > 0) {
    console.error("FAIL: enableComponentPerformanceTrack still exported in native-fb-dynamic.js");
    console.error(lines.join("\\n"));
    process.exit(1);
}
console.log("PASS");
'''

WWW_DYNAMIC_CHECK = '''
const fs = require("fs");
const content = fs.readFileSync(
    "packages/shared/forks/ReactFeatureFlags.www-dynamic.js", "utf8"
);
const lines = content.split(/\\r?\\n/).filter(
    l => /export\\s+const\\s+enableComponentPerformanceTrack/.test(l)
);
if (lines.length > 0) {
    console.error("FAIL: enableComponentPerformanceTrack still exported in www-dynamic.js");
    console.error(lines.join("\\n"));
    process.exit(1);
}
console.log("PASS");
'''

NATIVE_FB_STATIC_CHECK = '''
const fs = require("fs");
const content = fs.readFileSync(
    "packages/shared/forks/ReactFeatureFlags.native-fb.js", "utf8"
);

// Find the declaration and extract the full expression (may span multiple lines).
const lines = content.split(/\\r?\\n/);
let startIdx = -1;
for (let i = 0; i < lines.length; i++) {
    if (/export\\s+const\\s+enableComponentPerformanceTrack/.test(lines[i])) {
        startIdx = i;
        break;
    }
}
if (startIdx === -1) {
    console.error("FAIL: enableComponentPerformanceTrack declaration not found");
    process.exit(1);
}

// Collect lines until we hit a semicolon
let chunk = "";
for (let i = startIdx; i < lines.length; i++) {
    chunk += lines[i] + "\\n";
    if (lines[i].includes(";")) break;
}

// Extract expression between first "=" and first ";"
const eqIdx = chunk.indexOf("=");
const semiIdx = chunk.indexOf(";", eqIdx);
const expr = chunk.slice(eqIdx + 1, semiIdx).trim();

if (!expr) {
    console.error("FAIL: could not extract expression");
    process.exit(1);
}

// Evaluate with __PROFILE__=false to detect runtime gating.
// Base commit: "__PROFILE__ && dynamicFlags.enableComponentPerformanceTrack" -> false
// Fixed commit: "true" -> true
const __PROFILE__ = false;
const dynamicFlags = { enableComponentPerformanceTrack: false };
let value;
try {
    value = eval(expr);
} catch(e) {
    console.error("EVAL_ERROR: " + e.message + " (expr: " + expr + ")");
    process.exit(1);
}

if (value !== true) {
    console.error("FAIL: enableComponentPerformanceTrack = " + JSON.stringify(value) +
                  " (expected true, expr: " + expr + ")");
    process.exit(1);
}
console.log("PASS");
'''

WWW_STATIC_CHECK = '''
const fs = require("fs");
const content = fs.readFileSync(
    "packages/shared/forks/ReactFeatureFlags.www.js", "utf8"
);

// Look for a standalone "export const enableComponentPerformanceTrack ... = true"
// On base commit, it only exists inside a destructuring block (no standalone export).
// After the fix, there is a standalone static export.
const lines = content.split(/\\r?\\n/);
let found = false;
for (const line of lines) {
    if (/export\\s+const\\s+enableComponentPerformanceTrack/.test(line) &&
        line.includes("= true")) {
        found = true;
        break;
    }
}

if (!found) {
    console.error("FAIL: No standalone static true export for enableComponentPerformanceTrack in www.js");
    process.exit(1);
}
console.log("PASS");
'''

WWW_NOT_DESTRUCTURED_CHECK = '''
const fs = require("fs");
const content = fs.readFileSync(
    "packages/shared/forks/ReactFeatureFlags.www.js", "utf8"
);

// Find the destructuring block: export const { ... } = ...
const match = content.match(/export\\s+const\\s+\\{([^}]+)\\}/s);
if (match) {
    const destructured = match[1];
    if (destructured.includes("enableComponentPerformanceTrack")) {
        console.error("FAIL: enableComponentPerformanceTrack still destructured from dynamic flags in www.js");
        process.exit(1);
    }
}
console.log("PASS");
'''


def test_native_fb_dynamic_flag_removed():
    """enableComponentPerformanceTrack must not be exported in native-fb-dynamic.js."""
    r = _run_node(NATIVE_FB_DYNAMIC_CHECK)
    assert r.returncode == 0, f"Flag still exported in native-fb-dynamic.js: {r.stderr}"
    assert "PASS" in r.stdout


def test_www_dynamic_flag_removed():
    """enableComponentPerformanceTrack must not be exported in www-dynamic.js."""
    r = _run_node(WWW_DYNAMIC_CHECK)
    assert r.returncode == 0, f"Flag still exported in www-dynamic.js: {r.stderr}"
    assert "PASS" in r.stdout


def test_native_fb_static_true():
    """enableComponentPerformanceTrack evaluates to true in native-fb.js regardless of __PROFILE__."""
    r = _run_node(NATIVE_FB_STATIC_CHECK)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_www_static_true():
    """enableComponentPerformanceTrack is statically set to true in www.js."""
    r = _run_node(WWW_STATIC_CHECK)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_www_not_destructured_from_dynamic():
    """enableComponentPerformanceTrack must not be destructured from the dynamic flags import in www.js."""
    r = _run_node(WWW_NOT_DESTRUCTURED_CHECK)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression check
# ---------------------------------------------------------------------------

def test_performance_issue_reporting_intact():
    """enablePerformanceIssueReporting must still reference enableComponentPerformanceTrack in native-fb.js."""
    content = (FORKS / "ReactFeatureFlags.native-fb.js").read_text()
    assert "enablePerformanceIssueReporting" in content, (
        "enablePerformanceIssueReporting is missing from native-fb.js"
    )
    lines = content.splitlines()
    perf_issue_indices = [
        i for i, line in enumerate(lines)
        if "enablePerformanceIssueReporting" in line
    ]
    assert perf_issue_indices, "enablePerformanceIssueReporting not found"
    found = False
    for idx in perf_issue_indices:
        nearby = "\n".join(lines[max(0, idx - 1):idx + 3])
        if "enableComponentPerformanceTrack" in nearby:
            found = True
            break
    assert found, (
        "enablePerformanceIssueReporting no longer references enableComponentPerformanceTrack in native-fb.js"
    )
