"""
Task: openclaw-plugin-scan-block-install
Repo: openclaw/openclaw @ 8db20c196598b12043886ddc1c3ec0fd7695b9b4
PR:   57729

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

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


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without errors."""
    # AST-only because: TypeScript modules with complex ESM project deps
    # cannot be imported from Python.
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
# AST-only because: TypeScript modules with complex project-level ESM deps
# cannot be imported/called from Python.
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_scan_failure_blocks_install():
    """install.ts must block (not warn-and-continue) when scan fails."""
    code = _read("src/plugins/install.ts")
    # Base has 3 occurrences of "Installation continues" in logger.warn calls.
    # The fix removes all of them — scan failures now block instead of continuing.
    assert "Installation continues" not in code, (
        "install.ts still contains 'Installation continues' — "
        "scan failures must block the install, not warn and continue"
    )


# [pr_diff] fail_to_pass
def test_error_codes_defined():
    """PLUGIN_INSTALL_ERROR_CODE must include security scan block/fail codes."""
    code = _read("src/plugins/install.ts")
    m = re.search(
        r"PLUGIN_INSTALL_ERROR_CODE\s*=\s*\{([^}]+)\}", code, re.DOTALL,
    )
    assert m, "PLUGIN_INSTALL_ERROR_CODE object not found in install.ts"
    obj_body = m.group(1)
    assert re.search(r'SECURITY_SCAN_BLOCKED\s*:\s*"security_scan_blocked"', obj_body), (
        "Missing SECURITY_SCAN_BLOCKED: 'security_scan_blocked' in error codes"
    )
    assert re.search(r'SECURITY_SCAN_FAILED\s*:\s*"security_scan_failed"', obj_body), (
        "Missing SECURITY_SCAN_FAILED: 'security_scan_failed' in error codes"
    )


# [pr_diff] fail_to_pass
def test_error_codes_used_in_handling():
    """Security scan error codes are used in error-handling logic, not just defined."""
    code = _read("src/plugins/install.ts")
    # The codes must appear beyond their definition — in buildBlockedInstallResult,
    # catch blocks, or equivalent error-handling paths.
    # Definition accounts for 1 reference each; usage adds more.
    blocked_refs = len(re.findall(r"SECURITY_SCAN_BLOCKED", code))
    assert blocked_refs >= 2, (
        f"SECURITY_SCAN_BLOCKED found {blocked_refs} time(s) — expected >= 2 "
        "(definition + usage in blocked-result building)"
    )
    failed_refs = len(re.findall(r"SECURITY_SCAN_FAILED", code))
    assert failed_refs >= 2, (
        f"SECURITY_SCAN_FAILED found {failed_refs} time(s) — expected >= 2 "
        "(definition + usage in error handling)"
    )


# [pr_diff] fail_to_pass
def test_runtime_blocks_critical_findings():
    """Runtime sets code 'security_scan_blocked' for critical scan findings."""
    code = _read("src/plugins/install-security-scan.runtime.ts")
    # Base: no "security_scan_blocked" string. Fix adds it when critical > 0.
    assert re.search(r'code:\s*"security_scan_blocked"', code), (
        "Runtime must set code: 'security_scan_blocked' in blocked result "
        "for critical scan findings"
    )


# [pr_diff] fail_to_pass
def test_runtime_blocks_scan_errors():
    """Runtime sets code 'security_scan_failed' for scan exceptions."""
    code = _read("src/plugins/install-security-scan.runtime.ts")
    # Base: no "security_scan_failed" string. Fix adds it on scan error.
    assert re.search(r'code:\s*"security_scan_failed"', code), (
        "Runtime must set code: 'security_scan_failed' in blocked result "
        "for scan errors"
    )


# [pr_diff] fail_to_pass
def test_hook_precedence_over_builtin_block():
    """Hook block takes precedence over builtin block; builtin is fallback."""
    code = _read("src/plugins/install-security-scan.runtime.ts")
    # Base: all 3 scan functions do `return await runBeforeInstallHook(...)`.
    # Fix: captures hookResult, returns hook block if present, else builtinBlocked.
    direct_returns = len(re.findall(
        r"return\s+await\s+runBeforeInstallHook\s*\(", code,
    ))
    assert direct_returns == 0, (
        f"Found {direct_returns} direct 'return await runBeforeInstallHook(...)' — "
        "scan functions must capture hook result and apply builtin block fallback"
    )
    # Verify the runtime checks hook .blocked state for precedence logic.
    assert re.search(r"\?\.blocked", code), (
        "Runtime must check hookResult.blocked for hook-takes-precedence logic"
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
    # AST-only because: TypeScript type definitions are compile-time constructs.
    types_code = _read("src/plugins/install-security-scan.ts")
    # Base: blocked?: { reason: string } — no code field.
    # Fix: code?: "security_scan_blocked" | "security_scan_failed"
    assert re.search(
        r'code\??\s*:\s*"security_scan_blocked"\s*\|\s*"security_scan_failed"',
        types_code,
    ), (
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
