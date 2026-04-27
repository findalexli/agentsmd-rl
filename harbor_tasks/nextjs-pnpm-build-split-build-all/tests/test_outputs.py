"""Tests for the pnpm build / pnpm build-all split (vercel/next.js#90543).

Strategy: run `turbo run <tasks> --dry-run=json` and inspect the resulting
task graph for `@next/swc`. Turbo's planner reads the workspace's
package.json files and per-package turbo.json/turbo.jsonc and resolves
which command would run for each task. This is real behavior, not text
inspection.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/nextjs")


def _turbo_dry_run(*tasks: str) -> dict:
    env = {**os.environ, "TURBO_TELEMETRY_DISABLED": "1", "DO_NOT_TRACK": "1"}
    cmd = ["turbo", "run", *tasks, "--dry-run=json"]
    r = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    assert r.returncode == 0, (
        f"turbo dry-run failed for {tasks!r}:\n"
        f"stdout tail: {r.stdout[-800:]}\n"
        f"stderr tail: {r.stderr[-800:]}"
    )
    out = r.stdout
    brace = out.find("{")
    assert brace >= 0, f"no JSON in turbo output: {out[:200]}"
    return json.loads(out[brace:])


def _swc_tasks(plan: dict) -> dict[str, dict]:
    return {t["taskId"]: t for t in plan["tasks"] if t.get("package") == "@next/swc"}


# ---------------------------------------------------------------------------
# Fail-to-pass: behavioral tests of the build / build-all split.
# ---------------------------------------------------------------------------


def test_pnpm_build_does_not_invoke_native_build():
    """`pnpm build` (i.e. `turbo run build`) must not trigger the
    @next/swc native (Rust) build path."""
    plan = _turbo_dry_run("build")
    swc = _swc_tasks(plan)
    build_task = swc.get("@next/swc#build")
    if build_task is not None:
        cmd = build_task.get("command", "")
        assert cmd in ("<NONEXISTENT>", "", None), (
            f"@next/swc#build has a real command in `pnpm build`: {cmd!r}. "
            f"It must not invoke the native build helper."
        )
    cmds = [t.get("command", "") for t in swc.values()]
    assert "node maybe-build-native.mjs" not in cmds, (
        f"`pnpm build` still invokes maybe-build-native.mjs via @next/swc tasks: {cmds}"
    )


def test_pnpm_build_all_invokes_native_build_helper():
    """`pnpm build-all` (resolves to `turbo run build build-native-auto`)
    must include a @next/swc task whose command runs the native build helper."""
    plan = _turbo_dry_run("build", "build-native-auto")
    swc = _swc_tasks(plan)
    cmds = {tid: t.get("command", "") for tid, t in swc.items()}
    assert any(c == "node maybe-build-native.mjs" for c in cmds.values()), (
        f"build-all does not invoke `node maybe-build-native.mjs` via any "
        f"@next/swc task. Got: {cmds}"
    )


def test_swc_native_auto_task_is_named_build_native_auto():
    """The @next/swc task that runs the native build helper must be named
    `build-native-auto` (so it can be selected separately from the JS
    `build` graph)."""
    plan = _turbo_dry_run("build", "build-native-auto")
    swc = _swc_tasks(plan)
    auto = swc.get("@next/swc#build-native-auto")
    assert auto is not None, (
        f"No `@next/swc#build-native-auto` task found. SWC tasks: {list(swc)}"
    )
    assert auto.get("command") == "node maybe-build-native.mjs", (
        f"@next/swc#build-native-auto command is {auto.get('command')!r}, "
        f"expected 'node maybe-build-native.mjs'."
    )


def test_root_build_all_script_runs_both_tasks():
    """The root `build-all` pnpm script must drive turbo to run both
    `build` and `build-native-auto`."""
    pkg = json.loads((REPO / "package.json").read_text())
    scripts = pkg.get("scripts", {})
    build_all = scripts.get("build-all")
    assert build_all is not None, (
        f"Root package.json has no `build-all` script. Scripts: {sorted(scripts)}"
    )
    # Run the underlying command and inspect the task graph it produces.
    # We don't grep the script string itself - we verify what it does.
    parts = build_all.split()
    assert parts[0] == "turbo" and parts[1] == "run", (
        f"`build-all` should invoke `turbo run ...`, got: {build_all!r}"
    )
    # Extract the positional task names (everything before the first flag)
    tasks = []
    for tok in parts[2:]:
        if tok.startswith("-"):
            break
        tasks.append(tok)
    assert "build" in tasks and "build-native-auto" in tasks, (
        f"`build-all` should run turbo tasks `build` AND `build-native-auto`. "
        f"Got tasks: {tasks}"
    )

    plan = _turbo_dry_run(*tasks)
    swc = _swc_tasks(plan)
    cmds = [t.get("command", "") for t in swc.values()]
    assert "node maybe-build-native.mjs" in cmds, (
        f"build-all's turbo invocation does not produce a native build "
        f"step. SWC commands: {cmds}"
    )


def test_swc_package_json_no_longer_has_build_script():
    """`packages/next-swc/package.json` must not have a `build` script
    (it has been renamed). Otherwise `pnpm --filter=@next/swc build`
    would still trigger the Rust build."""
    pkg = json.loads((REPO / "packages/next-swc/package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "build" not in scripts, (
        f"@next/swc still has a `build` script: {scripts.get('build')!r}. "
        f"It should be renamed so it isn't picked up by `pnpm build`."
    )
    assert "build-native-auto" in scripts, (
        f"@next/swc must define a `build-native-auto` script. "
        f"Got scripts: {sorted(scripts)}"
    )
    assert scripts["build-native-auto"] == "node maybe-build-native.mjs", (
        f"@next/swc#build-native-auto should run `node maybe-build-native.mjs`, "
        f"got {scripts['build-native-auto']!r}"
    )


def test_agents_md_documents_build_all():
    """AGENTS.md must teach agents about the new `pnpm build-all` command,
    since that is now the way to build JS+Rust together."""
    text = (REPO / "AGENTS.md").read_text()
    assert "pnpm build-all" in text, (
        "AGENTS.md does not mention `pnpm build-all`. "
        "When introducing a new top-level pnpm script that agents must "
        "use during bootstrap / branch switches, AGENTS.md must be updated."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: sanity checks that should hold both at base and after fix.
# These guard against the test environment being broken.
# ---------------------------------------------------------------------------


def test_turbo_planner_works():
    """Sanity: the turbo planner runs at all and produces a non-empty plan."""
    plan = _turbo_dry_run("build")
    assert isinstance(plan.get("tasks"), list) and len(plan["tasks"]) > 0, (
        f"turbo dry-run produced empty/invalid plan: {str(plan)[:300]}"
    )
    assert "@next/swc" in plan.get("packages", []), (
        "Workspace topology is missing @next/swc; the test environment is broken."
    )


def test_repo_at_expected_base_or_descendant():
    """Sanity: we are operating on the next.js repo at the right place."""
    pkg = json.loads((REPO / "package.json").read_text())
    assert pkg.get("name") == "nextjs-project", (
        f"Unexpected root package: {pkg.get('name')!r}"
    )
