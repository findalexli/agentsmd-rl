"""
Task: opencode-effect-timeout-option-rename
Repo: anomalyco/opencode @ f736116967f5b57d89978e51961f2e78eedb443b

Upgrade effect + @effect/platform-node to 4.0.0-beta.42 and rename
onTimeout → orElse in Effect.timeoutOrElse calls.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/opencode"

MODIFIED_FILES = [
    "packages/app/src/app.tsx",
    "packages/opencode/src/effect/cross-spawn-spawner.ts",
]


def _strip_comments(src: str) -> str:
    """Remove JS/TS single-line and multi-line comments."""
    out = re.sub(r"//.*$", "", src, flags=re.MULTILINE)
    return re.sub(r"/\*[\s\S]*?\*/", "", out)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_effect_or_else_runtime():
    """Effect.timeoutOrElse with orElse callback fires correctly on timeout."""
    # Test with multiple durations to prevent hardcoding
    for timeout_ms, label in [("200 millis", "fast"), ("500 millis", "medium")]:
        script = textwrap.dedent(f"""\
            import {{ Effect }} from "effect"

            const slow = Effect.sleep("5 seconds").pipe(Effect.as(42))

            const result = await Effect.runPromise(
                Effect.timeoutOrElse(slow, {{
                    duration: "{timeout_ms}",
                    orElse: () => Effect.succeed("timeout_{label}"),
                }})
            )

            if (result === "timeout_{label}") {{
                process.exit(0)
            }} else {{
                console.error("Expected timeout_{label}, got " + result)
                process.exit(1)
            }}
        """)
        test_file = Path(REPO) / f"__test_effect_api_{label}__.ts"
        test_file.write_text(script)
        try:
            r = subprocess.run(
                ["bun", "run", str(test_file)],
                cwd=REPO, capture_output=True, timeout=30,
            )
            assert r.returncode == 0, (
                f"orElse runtime test ({label}) failed:\n"
                f"{r.stdout.decode()}\n{r.stderr.decode()}"
            )
        finally:
            test_file.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_effect_version_upgraded():
    """effect package upgraded to 4.0.0-beta.42 in workspace catalog."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    catalog = pkg.get("workspaces", {}).get("catalog", {}) or pkg.get("catalog", {})
    ver = catalog.get("effect", "")
    assert ver == "4.0.0-beta.42", f"effect version is {ver!r}, expected 4.0.0-beta.42"


# [pr_diff] fail_to_pass
def test_platform_node_version_upgraded():
    """@effect/platform-node upgraded to 4.0.0-beta.42 in workspace catalog."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    catalog = pkg.get("workspaces", {}).get("catalog", {}) or pkg.get("catalog", {})
    ver = catalog.get("@effect/platform-node", "")
    assert ver == "4.0.0-beta.42", (
        f"@effect/platform-node version is {ver!r}, expected 4.0.0-beta.42"
    )


# [pr_diff] fail_to_pass
def test_source_uses_or_else_not_on_timeout():
    """timeoutOrElse calls in both files use orElse, not onTimeout."""
    for f in MODIFIED_FILES:
        stripped = _strip_comments((Path(REPO) / f).read_text())

        parts = stripped.split("timeoutOrElse")
        assert len(parts) >= 2, f"{f}: no timeoutOrElse call found"

        for i in range(1, len(parts)):
            ctx = parts[i][:400]
            assert "onTimeout" not in ctx, (
                f"{f}: onTimeout still present in timeoutOrElse call"
            )
            assert "orElse" in ctx, (
                f"{f}: orElse missing from timeoutOrElse call"
            )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_timeout_or_else_calls_preserved():
    """timeoutOrElse calls still present in both files (not deleted)."""
    for f in MODIFIED_FILES:
        src = (Path(REPO) / f).read_text()
        assert "timeoutOrElse" in src, f"{f}: timeoutOrElse call removed"


# [pr_diff] pass_to_pass
def test_sigkill_escalation_preserved():
    """SIGKILL escalation logic preserved in cross-spawn-spawner.ts."""
    src = (Path(REPO) / "packages/opencode/src/effect/cross-spawn-spawner.ts").read_text()
    stripped = _strip_comments(src)
    assert "SIGKILL" in stripped, "SIGKILL not found in non-comment code"


# [static] pass_to_pass
def test_files_not_stubbed():
    """Modified files maintain reasonable size (not gutted)."""
    app = (Path(REPO) / "packages/app/src/app.tsx").read_text()
    spawner = (Path(REPO) / "packages/opencode/src/effect/cross-spawn-spawner.ts").read_text()
    # Originals: app.tsx ~260 lines, spawner ~360 lines
    assert len(app.splitlines()) >= 100, (
        f"app.tsx too short: {len(app.splitlines())} lines"
    )
    assert len(spawner.splitlines()) >= 200, (
        f"cross-spawn-spawner.ts too short: {len(spawner.splitlines())} lines"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ f736116967f5b57d89978e51961f2e78eedb443b
def test_no_any_type_at_call_sites():
    """No `as any` type assertions near timeoutOrElse calls."""
    # An agent might suppress type errors with `as any` instead of fixing the API.
    for f in MODIFIED_FILES:
        src = (Path(REPO) / f).read_text()
        lines = src.splitlines()
        for i, line in enumerate(lines):
            if "timeoutOrElse" in line:
                # Check a window of ±5 lines around the call
                window = lines[max(0, i - 5):i + 6]
                for wline in window:
                    stripped = _strip_comments(wline)
                    assert "as any" not in stripped, (
                        f"{f}:{i+1}: 'as any' near timeoutOrElse — "
                        "fix the API call instead of suppressing types"
                    )


# [agent_config] pass_to_pass — AGENTS.md:12 @ f736116967f5b57d89978e51961f2e78eedb443b
def test_no_try_catch_around_timeout():
    """No try/catch wrapping around timeoutOrElse calls."""
    # An agent might wrap the call in try/catch instead of fixing the API.
    # AGENTS.md:12 says "Avoid try/catch where possible".
    for f in MODIFIED_FILES:
        src = (Path(REPO) / f).read_text()
        lines = src.splitlines()
        for i, line in enumerate(lines):
            if "timeoutOrElse" in line:
                # Check 10 lines before the call for a wrapping try block
                window_before = "\n".join(lines[max(0, i - 10):i])
                stripped = _strip_comments(window_before)
                assert stripped.count("try {") - stripped.count("catch") <= 0, (
                    f"{f}:{i+1}: try/catch wrapping timeoutOrElse — "
                    "AGENTS.md:12 says avoid try/catch"
                )


# [pr_diff] pass_to_pass
def test_effect_succeed_false_preserved():
    """Health check fallback uses Effect.succeed(false), not a raw value."""
    # The ConnectionGate health check must return Effect.succeed(false) on timeout,
    # consistent with Effect patterns (packages/opencode/AGENTS.md:20).
    src = (Path(REPO) / "packages/app/src/app.tsx").read_text()
    stripped = _strip_comments(src)
    parts = stripped.split("timeoutOrElse")
    assert len(parts) >= 2, "app.tsx: timeoutOrElse not found"
    ctx = parts[1][:300]
    assert "Effect.succeed" in ctx, (
        "app.tsx: orElse callback should use Effect.succeed, not a raw value"
    )
