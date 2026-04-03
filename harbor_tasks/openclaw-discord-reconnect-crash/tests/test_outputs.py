"""
Task: openclaw-discord-reconnect-crash
Repo: openclaw/openclaw @ 496a1a35bd7ac7a1719d39a3723a731e2d131e8b
PR:   55991

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
from pathlib import Path

REPO = "/workspace/openclaw"
TARGET = f"{REPO}/extensions/discord/src/monitor/provider.lifecycle.ts"


def _read_target():
    """Read the target file, fail fast if missing."""
    p = Path(TARGET)
    assert p.exists(), f"Target file not found: {TARGET}"
    return p.read_text()


def _extract_drain_body(src):
    """Extract the drainPendingGatewayErrors callback body.

    The bug lives in drainPendingGatewayErrors, NOT handleGatewayEvent.
    handleGatewayEvent legitimately uses lifecycleStopping && reconnect-exhausted
    for the logging path. The drain callback is where buffered events are
    processed and where the gate must be removed.
    """
    # Find drainPendingGatewayErrors definition
    drain_idx = src.find("drainPendingGatewayErrors")
    assert drain_idx != -1, "drainPendingGatewayErrors not found"

    # Find the opening brace of the drainPending callback
    # Pattern: drainPending((event) => {
    cb_start = src.find("drainPending(", drain_idx)
    assert cb_start != -1, "drainPending( call not found"
    brace_start = src.find("{", cb_start)
    assert brace_start != -1, "Opening brace of drain callback not found"

    # Match braces to find the end
    depth = 0
    for i in range(brace_start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[brace_start:i + 1]

    return src[brace_start:]  # fallback


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_drain_reconnect_exhausted_not_gated():
    """In drainPendingGatewayErrors, reconnect-exhausted must not be
    AND-gated by lifecycleStopping.

    The bug: (lifecycleStopping && event.type === "reconnect-exhausted")
    in the drain callback missed buffered events queued before teardown
    flipped lifecycleStopping, causing a crash via throw event.err.
    """
    src = _read_target()
    drain = _extract_drain_body(src)

    # The buggy pattern in the drain callback
    buggy = re.search(
        r'lifecycleStopping\s*&&[^;{]*reconnect-exhausted', drain
    )
    assert buggy is None, (
        "drainPendingGatewayErrors still gates reconnect-exhausted "
        "behind lifecycleStopping && — buffered events before teardown will crash"
    )

    buggy_rev = re.search(
        r'reconnect-exhausted[^;{]*&&\s*lifecycleStopping', drain
    )
    assert buggy_rev is None, (
        "drainPendingGatewayErrors still gates reconnect-exhausted "
        "behind && lifecycleStopping"
    )


# [pr_diff] fail_to_pass
def test_drain_reconnect_exhausted_returns_stop():
    """In drainPendingGatewayErrors, reconnect-exhausted must lead to
    return 'stop' unconditionally (not fall through to throw event.err).
    """
    src = _read_target()
    drain = _extract_drain_body(src)

    # Strip single-line comments so we only analyze code
    drain_code = re.sub(r'//[^\n]*', '', drain)

    # reconnect-exhausted must be checked in the drain callback CODE
    match = re.search(r'event\.type\s*===?\s*["\']reconnect-exhausted["\']', drain_code)
    assert match is not None, (
        "reconnect-exhausted type check not found in drainPendingGatewayErrors code — "
        "buffered events will fall through to throw"
    )

    # It must lead to return "stop", not throw
    after = drain_code[match.start():match.start() + 300]
    assert re.search(r'return\s+["\']stop["\']', after), (
        "reconnect-exhausted in drain does not return 'stop'"
    )

    # And must NOT be inside a lifecycleStopping guard
    before = drain_code[max(0, match.start() - 200):match.start()]
    assert not re.search(
        r'\(\s*lifecycleStopping\s*&&[^)]*$', before
    ), "reconnect-exhausted wrapped in (lifecycleStopping && ...) guard"


# [pr_diff] fail_to_pass
def test_drain_no_parenthesized_lifecycle_guard():
    """The drain callback must not have a parenthesized
    (lifecycleStopping && ...reconnect-exhausted) sub-expression.

    This is the exact pattern that caused the race condition.
    """
    src = _read_target()
    drain = _extract_drain_body(src)

    buggy = re.search(
        r'\(\s*lifecycleStopping\s*&&[^)]*reconnect-exhausted[^)]*\)', drain
    )
    assert buggy is None, (
        "Found (lifecycleStopping && ...reconnect-exhausted) in drain — "
        "this is the exact buggy pattern"
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
    """Extension code must not import from core src/ via relative paths.

    Rule: extension production code should treat openclaw/plugin-sdk/* as
    the public surface, not import core src/** directly.
    """
    ext_dir = os.path.join(REPO, "extensions/discord/src")
    violations = []

    for root, _dirs, files in os.walk(ext_dir):
        for fname in files:
            if not fname.endswith(".ts") or fname.endswith((".test.ts", ".d.ts")):
                continue
            filepath = os.path.join(root, fname)
            with open(filepath) as f:
                for i, line in enumerate(f, 1):
                    if re.search(r'^import .* from [\'"]\.\.\/\.\.\/\.\.\/src\/', line):
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
    # The base file has zero eslint-disable comments; the fix should not add any
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
    # Find all static imports
    static_modules = set(re.findall(r'from\s+["\']([^"\']+)["\']', src))
    # Find all dynamic imports
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
    # extensions/discord/src/monitor/ — going up 4+ levels escapes the extension
    # ../../../../ would leave extensions/discord/
    escaping = re.findall(r'from\s+["\'](\.\./\.\./\.\./\.\.[^"\']*)["\']', src)
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
