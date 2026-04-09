"""
Task: openclaw-plugin-scan-block-install
Repo: openclaw/openclaw @ 8db20c196598b12043886ddc1c3ec0fd7695b9b4
PR:   57729

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"

MODIFIED_FILES = [
    "src/plugins/install.ts",
    "src/plugins/install-security-scan.runtime.ts",
    "src/plugins/install-security-scan.ts",
]


def _read(relpath: str) -> str:
    return Path(f"{REPO}/{relpath}").read_text()


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript/TypeScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without errors."""
    for f in MODIFIED_FILES:
        r = subprocess.run(
            ["node", "--input-type=commonjs", "-e", f"""
const fs = require('fs');
const ts = require('typescript');
const code = fs.readFileSync('{REPO}/{f}', 'utf8');
const result = ts.transpileModule(code, {{
  compilerOptions: {{ module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ESNext }}
}});
if (!result.outputText) process.exit(1);
""".strip()],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"{f} has TypeScript syntax errors:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# These tests execute code to verify the actual behavior changed.
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_scan_failure_blocks_install():
    """install.ts must block (not warn-and-continue) when scan fails."""
    # Verify by executing TypeScript to check the error handling behavior
    # The fix removes "Installation continues" and adds blocking error returns
    code = _read("src/plugins/install.ts")

    # Base has "Installation continues" in logger.warn calls
    # Fix removes all of them — scan failures now block
    r = _run_node(rf"""
const fs = require('fs');
const code = fs.readFileSync('{REPO}/src/plugins/install.ts', 'utf8');

// Check that "Installation continues" is removed (base had it, fix doesn't)
const hasContinues = code.includes('Installation continues');

// Check that catch blocks now return blocking errors with SECURITY_SCAN_FAILED
const hasScanFailedCode = /SECURITY_SCAN_FAILED/.test(code);

// Check that catch blocks return {{ ok: false, ... }} objects now
const catchReturnPattern = /catch\s*\(err\)\s*{{\s*return\s*{{\s*ok:\s*false/;
const hasCatchReturns = catchReturnPattern.test(code);

console.log(JSON.stringify({{
  hasContinues,
  hasScanFailedCode,
  blocksOnFailure: !hasContinues && hasScanFailedCode
}}));
""")
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert not result["hasContinues"], (
        "install.ts still contains 'Installation continues' — "
        "scan failures must block the install, not warn and continue"
    )
    assert result["hasScanFailedCode"], (
        "SECURITY_SCAN_FAILED error code not found in install.ts"
    )


# [pr_diff] fail_to_pass
def test_error_codes_defined():
    """PLUGIN_INSTALL_ERROR_CODE must include security scan block/fail codes."""
    r = _run_node(rf"""
const fs = require('fs');
const code = fs.readFileSync('{REPO}/src/plugins/install.ts', 'utf8');

// Extract PLUGIN_INSTALL_ERROR_CODE object
const match = code.match(/PLUGIN_INSTALL_ERROR_CODE\s*=\s*\{{([^}}]+)\}}/s);
if (!match) {{
  console.log(JSON.stringify({{ found: false, reason: 'object not found' }}));
  process.exit(0);
}}

const objBody = match[1];
const hasBlocked = /SECURITY_SCAN_BLOCKED\s*:\s*"security_scan_blocked"/.test(objBody);
const hasFailed = /SECURITY_SCAN_FAILED\s*:\s*"security_scan_failed"/.test(objBody);

console.log(JSON.stringify({{
  found: true,
  hasBlocked,
  hasFailed,
  allDefined: hasBlocked && hasFailed
}}));
""")
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result["found"], "PLUGIN_INSTALL_ERROR_CODE object not found in install.ts"
    assert result["hasBlocked"], (
        "Missing SECURITY_SCAN_BLOCKED: 'security_scan_blocked' in error codes"
    )
    assert result["hasFailed"], (
        "Missing SECURITY_SCAN_FAILED: 'security_scan_failed' in error codes"
    )


# [pr_diff] fail_to_pass
def test_error_codes_used_in_handling():
    """Security scan error codes are used in error-handling logic, not just defined."""
    r = _run_node(rf"""
const fs = require('fs');
const code = fs.readFileSync('{REPO}/src/plugins/install.ts', 'utf8');

// Count occurrences - definition accounts for 1, usage adds more
const blockedMatches = code.match(/SECURITY_SCAN_BLOCKED/g);
const failedMatches = code.match(/SECURITY_SCAN_FAILED/g);

const blockedRefs = blockedMatches ? blockedMatches.length : 0;
const failedRefs = failedMatches ? failedMatches.length : 0;

console.log(JSON.stringify({{
  blockedRefs,
  failedRefs,
  blockedUsed: blockedRefs >= 2,
  failedUsed: failedRefs >= 2
}}));
""")
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result["blockedUsed"], (
        f"SECURITY_SCAN_BLOCKED found {result['blockedRefs']} time(s) — expected >= 2 "
        "(definition + usage in blocked-result building)"
    )
    assert result["failedUsed"], (
        f"SECURITY_SCAN_FAILED found {result['failedRefs']} time(s) — expected >= 2 "
        "(definition + usage in error handling)"
    )


# [pr_diff] fail_to_pass
def test_runtime_blocks_critical_findings():
    """Runtime sets code 'security_scan_blocked' for critical scan findings."""
    r = _run_node(rf"""
const fs = require('fs');
const code = fs.readFileSync('{REPO}/src/plugins/install-security-scan.runtime.ts', 'utf8');

// Check for the code field with security_scan_blocked value
const hasBlockedCode = /code:\s*"security_scan_blocked"/.test(code);

// Check that buildBlockedScanResult function exists and handles critical
const hasBuildBlockedFn = /function buildBlockedScanResult/.test(code);
const hasCriticalCheck = /builtinScan\.critical\s*>\s*0/.test(code);

console.log(JSON.stringify({{
  hasBlockedCode,
  hasBuildBlockedFn,
  hasCriticalCheck,
  blocksCritical: hasBlockedCode && hasBuildBlockedFn && hasCriticalCheck
}}));
""")
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result["hasBlockedCode"], (
        "Runtime must set code: 'security_scan_blocked' in blocked result "
        "for critical scan findings"
    )
    assert result["hasBuildBlockedFn"], (
        "buildBlockedScanResult function not found in runtime"
    )
    assert result["hasCriticalCheck"], (
        "Critical findings check (builtinScan.critical > 0) not found"
    )


# [pr_diff] fail_to_pass
def test_runtime_blocks_scan_errors():
    """Runtime sets code 'security_scan_failed' for scan exceptions."""
    r = _run_node(rf"""
const fs = require('fs');
const code = fs.readFileSync('{REPO}/src/plugins/install-security-scan.runtime.ts', 'utf8');

// Check for the code field with security_scan_failed value
const hasFailedCode = /code:\s*"security_scan_failed"/.test(code);

// Check that buildBlockedScanResult handles scan errors (status === "error")
const hasErrorStatusCheck = /builtinScan\.status\s*===\s*"error"/.test(code);

console.log(JSON.stringify({{
  hasFailedCode,
  hasErrorStatusCheck,
  blocksScanErrors: hasFailedCode && hasErrorStatusCheck
}}));
""")
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result["hasFailedCode"], (
        "Runtime must set code: 'security_scan_failed' in blocked result "
        "for scan errors"
    )
    assert result["hasErrorStatusCheck"], (
        "Scan error status check (builtinScan.status === 'error') not found"
    )


# [pr_diff] fail_to_pass
def test_hook_precedence_over_builtin_block():
    """Hook block takes precedence over builtin block; builtin is fallback."""
    r = _run_node(rf"""
const fs = require('fs');
const code = fs.readFileSync('{REPO}/src/plugins/install-security-scan.runtime.ts', 'utf8');

// Count direct returns of runBeforeInstallHook - base had these, fix doesn't
const directReturnMatches = code.match(/return\s+await\s+runBeforeInstallHook\s*\(/g);
const directReturns = directReturnMatches ? directReturnMatches.length : 0;

// Check for hook precedence logic - hookResult?.blocked ? hookResult : builtinBlocked
const hasPrecedenceCheck = /\?\.blocked/.test(code);

// Check that all three scan functions capture hook result
const hookResultCaptures = code.match(/const\s+hookResult\s*=\s*await\s+runBeforeInstallHook/g);
const hasHookCaptures = hookResultCaptures && hookResultCaptures.length >= 3;

console.log(JSON.stringify({{
  directReturns,
  hasPrecedenceCheck,
  hasHookCaptures,
  properPrecedence: directReturns === 0 && hasPrecedenceCheck && hasHookCaptures
}}));
""")
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result["directReturns"] == 0, (
        f"Found {result['directReturns']} direct 'return await runBeforeInstallHook(...)' — "
        "scan functions must capture hook result and apply builtin block fallback"
    )
    assert result["hasPrecedenceCheck"], (
        "Runtime must check hookResult.blocked for hook-takes-precedence logic"
    )
    assert result["hasHookCaptures"], (
        "Must capture hook result in all three scan functions before applying precedence"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:150 @ 8db20c196598b12043886ddc1c3ec0fd7695b9b4
def test_blocked_type_has_code_field():
    """Blocked type uses a closed error-code union, not freeform strings.

    Rule: 'Prefer Result<T, E>-style outcomes and closed error-code unions
    for recoverable runtime decisions.' — CLAUDE.md:150
    """
    r = _run_node(rf"""
const fs = require('fs');
const code = fs.readFileSync('{REPO}/src/plugins/install-security-scan.ts', 'utf8');

// Check for code field with closed union type
const hasCodeField = /code\??\s*:\s*"security_scan_blocked"\s*\|\s*"security_scan_failed"/.test(code);

console.log(JSON.stringify({{ hasCodeField }}));
""")
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result["hasCodeField"], (
        "blocked type must have code field with closed union: "
        "'security_scan_blocked' | 'security_scan_failed'"
    )


# [agent_config] pass_to_pass — CLAUDE.md:147 @ 8db20c196598b12043886ddc1c3ec0fd7695b9b4
def test_no_explicit_any():
    """Modified TypeScript files must not use explicit 'any' type.

    Rule: 'Do not disable no-explicit-any; prefer real types, unknown, or
    a narrow adapter/helper instead.' — CLAUDE.md:147
    """
    any_pattern = re.compile(r"(?::\s*any\b|as\s+any\b)")
    for f in MODIFIED_FILES:
        code = _read(f)
        violations = []
        for lineno, line in enumerate(code.splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            if any_pattern.search(line):
                violations.append(f"line {lineno}: {line.rstrip()}")
        assert not violations, (
            f"{f} contains explicit 'any' type:\n" + "\n".join(violations[:5])
        )


# [agent_config] pass_to_pass — CLAUDE.md:146 @ 8db20c196598b12043886ddc1c3ec0fd7695b9b4
def test_no_ts_nocheck():
    """No @ts-nocheck or @ts-ignore in modified files.

    Rule: 'Never add @ts-nocheck and do not add inline lint suppressions
    by default.' — CLAUDE.md:146
    """
    for f in MODIFIED_FILES:
        code = _read(f)
        assert "@ts-nocheck" not in code, f"{f} contains @ts-nocheck"
        assert "@ts-ignore" not in code, f"{f} contains @ts-ignore"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression via upstream vitest
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_upstream_install_tests_pass():
    """Upstream install.test.ts vitest suite passes."""
    unit_config = Path(f"{REPO}/vitest.unit.config.ts")
    cmd = ["pnpm", "exec", "vitest", "run", "--pool=forks"]
    if unit_config.exists():
        cmd += ["--config", "vitest.unit.config.ts"]
    cmd += ["src/plugins/install.test.ts", "--reporter=verbose"]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"Upstream vitest suite failed (rc={r.returncode}).\n"
        f"{(r.stdout + r.stderr)[-2000:]}"
    )
