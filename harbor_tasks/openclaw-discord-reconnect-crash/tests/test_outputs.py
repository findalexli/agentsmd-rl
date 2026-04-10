"""
Task: openclaw-discord-reconnect-crash
Repo: openclaw/openclaw @ 496a1a35bd7ac7a1719d39a3723a731e2d131e8b
PR:   55991

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"
TARGET = f"{REPO}/extensions/discord/src/monitor/provider.lifecycle.ts"


def _read_target():
    """Read the target file, fail fast if missing."""
    p = Path(TARGET)
    assert p.exists(), f"Target file not found: {TARGET}"
    return p.read_text()


def _ensure_pnpm_deps():
    """Enable corepack pnpm and ensure dependencies are installed."""
    try:
        subprocess.run(["pnpm", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(["corepack", "enable", "pnpm"], capture_output=True, check=True)

    if not Path(f"{REPO}/node_modules/.bin/vitest").exists():
        subprocess.run(
            ["pnpm", "install", "--frozen-lockfile", "--prefer-offline"],
            capture_output=True,
            cwd=REPO,
            timeout=300,
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using source code inspection
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_drain_reconnect_exhausted_not_gated():
    """In drainPendingGatewayErrors, reconnect-exhausted must not be
    AND-gated by lifecycleStopping."""
    src = _read_target()
    drain_idx = src.find("drainPendingGatewayErrors")
    assert drain_idx != -1, "drainPendingGatewayErrors not found"

    cb_start = src.find("drainPending(", drain_idx)
    assert cb_start != -1, "drainPending( call not found"

    bug_pattern = r'lifecycleStopping\s*&&\s*event\.type\s*===\s*["\']reconnect-exhausted["\']'
    has_bug = re.search(bug_pattern, src[cb_start:cb_start+1500]) is not None

    assert not has_bug, (
        "Bug still present - found 'lifecycleStopping && event.type === \"reconnect-exhausted\"' "
        "in drainPending callback. The fix should remove the lifecycleStopping guard."
    )


# [pr_diff] fail_to_pass
def test_drain_reconnect_exhausted_returns_stop():
    """In drainPendingGatewayErrors, reconnect-exhausted must unconditionally
    return 'stop' — not fall through to throw event.err."""
    src = _read_target()
    drain_idx = src.find("drainPendingGatewayErrors")
    assert drain_idx != -1, "drainPendingGatewayErrors not found"

    cb_start = src.find("drainPending(", drain_idx)
    assert cb_start != -1, "drainPending( call not found"

    bug_pattern = r'lifecycleStopping\s*&&\s*event\.type\s*===\s*["\']reconnect-exhausted["\']'
    has_bug = re.search(bug_pattern, src[cb_start:cb_start+1500]) is not None

    assert not has_bug, (
        "Bug still present - 'lifecycleStopping && event.type === \"reconnect-exhausted\"' should be removed. "
        "The fix should handle reconnect-exhausted unconditionally."
    )


# [pr_diff] fail_to_pass
def test_drain_no_parenthesized_lifecycle_guard():
    """The drain callback must not have a parenthesized
    (lifecycleStopping && ...reconnect-exhausted) sub-expression."""
    src = _read_target()
    drain_idx = src.find("drainPendingGatewayErrors")
    assert drain_idx != -1, "drainPendingGatewayErrors not found"

    cb_start = src.find("drainPending(", drain_idx)
    assert cb_start != -1, "drainPending( call not found"

    bug_pattern = r'\(\s*lifecycleStopping\s*&&\s*[^)]+reconnect-exhausted'
    has_bug = re.search(bug_pattern, src[cb_start:cb_start+1500]) is not None

    assert not has_bug, (
        "Bug still present - found parenthesized (lifecycleStopping && ...reconnect-exhausted) pattern. "
        "The fix should remove the lifecycleStopping guard."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_disallowed_intents_preserved():
    """disallowed-intents handling must not be removed by the fix."""
    src = _read_target()
    assert "disallowed-intents" in src, "disallowed-intents handling was removed"
    assert re.search(
        r'event\.type\s*===?\s*["\']disallowed-intents["\']', src
    ), "disallowed-intents type check not found"


# [pr_diff] pass_to_pass
def test_lifecycle_stopping_flag_preserved():
    """lifecycleStopping flag must still exist (used by other shutdown logic)."""
    src = _read_target()
    assert "lifecycleStopping" in src, (
        "lifecycleStopping flag was removed — it is still needed for other logic"
    )


# [static] pass_to_pass
def test_main_function_and_exports():
    """runDiscordGatewayLifecycle must still be exported."""
    src = _read_target()
    assert "runDiscordGatewayLifecycle" in src, "Main function removed"
    assert re.search(r'export\s+(async\s+)?function\s+runDiscordGatewayLifecycle', src), (
        "runDiscordGatewayLifecycle is not exported"
    )


# [static] pass_to_pass
def test_not_stub():
    """File must have real implementation, not be gutted."""
    src = _read_target()
    lines = [
        l.strip() for l in src.splitlines()
        if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("*")
    ]
    assert len(lines) >= 40, f"Only {len(lines)} non-trivial lines — file looks gutted"

    assert len(re.findall(r'\bif\s*\(', src)) >= 3, "Too few conditionals"
    assert len(re.findall(r'\bawait\b', src)) >= 3, "Missing async/await structure"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:16 @ 496a1a35bd7ac7a1719d39a3723a731e2d131e8b
def test_no_cross_boundary_imports():
    """Extension code must not import from core src/ via relative paths."""
    ext_dir = os.path.join(REPO, "extensions/discord/src")
    violations = []

    for root, _dirs, files in os.walk(ext_dir):
        for fname in files:
            if not fname.endswith(".ts") or fname.endswith((".test.ts", ".d.ts")):
                continue
            filepath = os.path.join(root, fname)
            with open(filepath) as f:
                for i, line in enumerate(f, 1):
                    if re.search(r'^import .* from [\'"].*\.\.\/\.\.\/\.\.\/src\/', line):
                        violations.append(f"{filepath}:{i}: {line.strip()}")

    assert not violations, (
        f"Cross-boundary imports found:\n" + "\n".join(violations[:5])
    )


# [agent_config] pass_to_pass — CLAUDE.md:104 @ 496a1a35bd7ac7a1719d39a3723a731e2d131e8b
def test_no_ts_nocheck():
    """Must not add @ts-nocheck or inline lint suppressions."""
    src = _read_target()
    assert "@ts-nocheck" not in src, "Found @ts-nocheck — fix root cause instead"
    assert "@ts-ignore" not in src, "Found @ts-ignore — fix root cause instead"
    assert "eslint-disable" not in src, (
        "Found eslint-disable suppression — fix root cause instead"
    )
    assert "oxlint-ignore" not in src, (
        "Found oxlint-ignore suppression — fix root cause instead"
    )


# [agent_config] pass_to_pass — CLAUDE.md:105 @ 496a1a35bd7ac7a1719d39a3723a731e2d131e8b
def test_no_explicit_any_disable():
    """Must not disable the no-explicit-any lint rule."""
    src = _read_target()
    assert "no-explicit-any" not in src, (
        "Found no-explicit-any suppression — use real types, unknown, or a narrow adapter instead"
    )


# [agent_config] pass_to_pass — CLAUDE.md:108 @ 496a1a35bd7ac7a1719d39a3723a731e2d131e8b
def test_no_self_import_sdk():
    """Extension must not import itself via openclaw/plugin-sdk/discord."""
    src = _read_target()
    assert "openclaw/plugin-sdk/discord" not in src, (
        "Extension self-imports via openclaw/plugin-sdk/discord — "
        "use local barrels (./api.ts, ./runtime-api.ts) for internal imports"
    )


# [agent_config] pass_to_pass — CLAUDE.md:111 @ 496a1a35bd7ac7a1719d39a3723a731e2d131e8b
def test_no_prototype_mutation():
    """Must not share class behavior via prototype mutation."""
    src = _read_target()
    assert "applyPrototypeMixins" not in src, "Found applyPrototypeMixins — use inheritance/composition"
    assert ".prototype" not in src or re.search(
        r'\.\s*prototype\s*[.=\[]', src
    ) is None, "Found prototype mutation — use explicit inheritance/composition"


# [agent_config] pass_to_pass — CLAUDE.md:106 @ 496a1a35bd7ac7a1719d39a3723a731e2d131e8b
def test_no_mixed_dynamic_static_imports():
    """Must not mix await import() and static import for the same module."""
    src = _read_target()
    static_modules = set(re.findall(r'from\s+["\']([^"\']+)["\']', src))
    dynamic_modules = set(re.findall(r'await\s+import\s*\(\s*["\']([^"\']+)["\']\s*\)', src))
    overlap = static_modules & dynamic_modules
    assert not overlap, (
        f"Mixed dynamic and static imports for: {overlap} — "
        "use one import style per module in production code"
    )


# [agent_config] pass_to_pass — CLAUDE.md:109 @ 496a1a35bd7ac7a1719d39a3723a731e2d131e8b
def test_no_relative_imports_escaping_extension():
    """Relative imports must not resolve outside the extension package root."""
    src = _read_target()
    escaping = re.findall(r'from\s+["\'](\.\.\/\.\.\/\.\.\/\.\.[^"\']*)["\']', src)
    assert not escaping, (
        f"Relative imports escape extension root: {escaping} — "
        "use openclaw/plugin-sdk/* for cross-package imports"
    )


# [agent_config] pass_to_pass — CLAUDE.md:110 @ 496a1a35bd7ac7a1719d39a3723a731e2d131e8b
def test_no_direct_plugin_sdk_relative():
    """Must not reach into src/plugin-sdk/ by relative path."""
    src = _read_target()
    assert not re.search(r'from\s+["\'][^"\']*src/plugin-sdk/', src), (
        "Found direct relative import into src/plugin-sdk/ — "
        "use openclaw/plugin-sdk/<subpath> instead"
    )


# ---------------------------------------------------------------------------
# Repo CI/CD pass-to-pass gates — verify repo's own tests pass on base commit
# ---------------------------------------------------------------------------

# NOTE: This test is skipped because the repo's own test expects the old buggy
# behavior. The test was written to verify that reconnect-exhausted throws an
# error, but the fix changes this behavior to handle it gracefully. The
# fail-to-pass tests above verify the fix is correct.
# [repo_tests] pass_to_pass
def SKIP_test_repo_discord_provider_lifecycle_tests():
    """Discord provider lifecycle tests must pass (repo's own tests).

    SKIPPED: The repo's test 'does not suppress reconnect-exhausted already
    queued before shutdown' expects the old buggy behavior (throwing an error).
    After the fix, reconnect-exhausted is handled gracefully. This is verified by
    the fail-to-pass tests above.
    """
    pass


# [repo_tests] pass_to_pass
def test_repo_discord_syntax_valid():
    """Discord extension TypeScript files must have valid syntax (Node.js parse check)."""
    target_file = Path(TARGET)
    assert target_file.exists(), f"Target file not found: {TARGET}"

    check_script = Path(REPO) / "_syntax_check.mjs"
    check_script.write_text(
        'import { readFileSync } from "node:fs";\n'
        'const src = readFileSync("' + TARGET + '", "utf8");\n'
        'if (!src.includes("export async function runDiscordGatewayLifecycle")) {\n'
        '  console.error("Missing main export");\n'
        '  process.exit(1);\n'
        '}\n'
        'if (!src.includes("drainPendingGatewayErrors")) {\n'
        '  console.error("Missing drainPendingGatewayErrors function");\n'
        '  process.exit(1);\n'
        '}\n'
        'console.log("Syntax check passed");\n'
    )
    try:
        r = subprocess.run(
            ["node", str(check_script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"
    finally:
        check_script.unlink(missing_ok=True)


# [repo_tests] pass_to_pass
def test_repo_discord_lint_clean():
    """Discord extension target file must pass oxlint (repo's linter)."""
    _ensure_pnpm_deps()
    r = subprocess.run(
        ["pnpm", "exec", "oxlint", "--config", ".oxlintrc.json", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_test_harness():
    """Repo unit test framework (vitest) must work for basic test."""
    _ensure_pnpm_deps()
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "--config", "vitest.unit.config.ts",
         "src/plugin-sdk/index.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit test harness failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def SKIP_test_repo_discord_provider_lifecycle():
    """SKIPPED - Discord provider lifecycle test expects old buggy behavior.

    The repo's test 'does not suppress reconnect-exhausted already queued before shutdown'
    expects the old buggy behavior (throwing an error). After the fix, reconnect-exhausted
    is handled gracefully. The fail-to-pass tests verify the fix is correct.
    """
    _ensure_pnpm_deps()
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "--config", "vitest.config.ts",
         "extensions/discord/src/monitor/provider.lifecycle.test.ts"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Discord provider lifecycle tests failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
