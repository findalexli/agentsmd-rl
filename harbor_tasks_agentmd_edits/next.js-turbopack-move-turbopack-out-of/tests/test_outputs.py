"""
Task: next.js-turbopack-move-turbopack-out-of
Repo: vercel/next.js @ 46761a321042e8ac1863f4cfc8d73d527956e181
PR:   90543

Move Turbopack native build out of `pnpm build` into `pnpm build-all`.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
from pathlib import Path

REPO = "/workspace/next.js"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax / validity checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Root package.json and next-swc package.json are valid JSON."""
    root_pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    assert "scripts" in root_pkg, "package.json must have scripts"

    swc_pkg = json.loads(Path(f"{REPO}/packages/next-swc/package.json").read_text())
    assert "scripts" in swc_pkg, "next-swc package.json must have scripts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_all_script_exists():
    """Root package.json must have a 'build-all' script that runs both JS and native builds."""
    root_pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    scripts = root_pkg.get("scripts", {})
    assert "build-all" in scripts, "package.json must have a 'build-all' script"
    build_all_cmd = scripts["build-all"]
    build_cmd = scripts.get("build", "")
    # build-all must do MORE than build (it should include native compilation too)
    assert build_all_cmd != build_cmd, (
        "build-all must differ from build — it should include native auto-build"
    )
    # build-all must still include the JS build task
    assert "build" in build_all_cmd, (
        "build-all script must include the JS build task"
    )
    # build-all must reference something native-related beyond just "build"
    assert "native" in build_all_cmd.lower() or "swc" in build_all_cmd.lower() or "rust" in build_all_cmd.lower(), (
        "build-all script must reference a native/swc/rust build task"
    )


# [pr_diff] fail_to_pass
def test_next_swc_build_decoupled():
    """packages/next-swc 'build' script must not trigger native auto-build.

    The 'build' key in next-swc/package.json scripts should NOT trigger
    maybe-build-native.mjs. A differently-named script should handle it.
    """
    swc_pkg = json.loads(
        Path(f"{REPO}/packages/next-swc/package.json").read_text()
    )
    scripts = swc_pkg.get("scripts", {})

    # "build" must NOT point to maybe-build-native
    build_cmd = scripts.get("build", "")
    assert "maybe-build-native" not in build_cmd, (
        "next-swc 'build' script must not trigger maybe-build-native.mjs — "
        "native auto-build should use a different script name"
    )

    # Some other script must run maybe-build-native
    native_auto_scripts = [
        k for k, v in scripts.items()
        if "maybe-build-native" in v and k != "build"
    ]
    assert len(native_auto_scripts) > 0, (
        "next-swc must have a non-'build' script that runs maybe-build-native.mjs"
    )


# [pr_diff] fail_to_pass
def test_turbo_config_build_no_native():
    """Turbo config 'build' task in next-swc must NOT include native compilation inputs.

    On the base commit, the 'build' task has Cargo/crate inputs, meaning
    `pnpm build` triggers native Turbopack compilation. After the fix,
    either the 'build' task is removed/renamed or it no longer has native inputs.
    """
    turbo_dir = Path(f"{REPO}/packages/next-swc")
    turbo_path = turbo_dir / "turbo.jsonc"
    if not turbo_path.exists():
        turbo_path = turbo_dir / "turbo.json"
    assert turbo_path.exists(), "Turbo config must exist in packages/next-swc/"

    content = turbo_path.read_text()

    # Strip JS-style comments for JSON parsing
    stripped = re.sub(r'//[^\n]*', '', content)
    # Remove trailing commas before } or ]
    stripped = re.sub(r',\s*([}\]])', r'\1', stripped)

    config = json.loads(stripped)
    tasks = config.get("tasks", config.get("pipeline", {}))

    # The "build" task must NOT have native compilation inputs
    if "build" in tasks:
        build_cfg = tasks["build"]
        if isinstance(build_cfg, dict):
            inputs = build_cfg.get("inputs", [])
            has_native = any(
                "Cargo" in inp or "crates" in inp for inp in inputs
            )
            assert not has_native, (
                "Turbo config 'build' task must not include Cargo/crate inputs — "
                "native auto-build should use a differently-named task"
            )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — AGENTS.md update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    assert "build-all" in agents_md, (
        "AGENTS.md must document the 'build-all' command"
    )

    # Should appear in at least 2 distinct contexts (not just a single mention)
    lines_with_build_all = [
        line for line in agents_md.splitlines()
        if "build-all" in line
    ]
    assert len(lines_with_build_all) >= 2, (
        "AGENTS.md should reference 'build-all' in multiple relevant contexts "
        "(e.g., build commands section and rebuild-after-switch guidance)"
    )


# [config_edit] fail_to_pass

    After the change, 'pnpm build' no longer builds Turbopack native binaries.
    The description of 'pnpm build' should NOT say it builds 'everything'.
    """
    agents_md = Path(f"{REPO}/AGENTS.md").read_text()

    # Find the comment/heading right before "pnpm build" in the code block
    lines = agents_md.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "pnpm build" and i > 0:
            context = lines[max(0, i - 2):i]
            context_text = " ".join(context).lower()
            # Must NOT say "build everything" anymore
            if "build everything" in context_text:
                raise AssertionError(
                    "AGENTS.md still describes 'pnpm build' as building 'everything' — "
                    "it should clarify that 'pnpm build' only builds JS code"
                )
            # Should indicate JS-only scope
            if "js" in context_text or "javascript" in context_text:
                return  # Correct

    # Fallback: ensure "Build everything" + "pnpm build" combo is gone
    normalized = agents_md.replace("\r\n", "\n")
    assert "# Build everything\npnpm build" not in normalized, (
        "AGENTS.md must not describe 'pnpm build' as building everything"
    )
