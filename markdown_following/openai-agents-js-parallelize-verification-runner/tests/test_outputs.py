"""Behavioral tests for openai-agents-js#1120 — code-change-verification parallel runner.

The base commit ships only POSIX/PowerShell wrappers that run six pnpm commands
sequentially. The fix introduces .agents/skills/code-change-verification/scripts/run.mjs,
which keeps `pnpm i` and `pnpm build` as sequential barriers and runs the four
validation commands (build-check, dist:check, lint, test) in parallel with
fail-fast cancellation and `[label] line` output prefixes. The shell/PowerShell
wrappers delegate to the Node runner.

These tests exercise the runner via mock subprocess steps so the openai-agents-js
monorepo does not need to be installed.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path("/workspace/openai-agents-js")
SKILL_DIR = REPO / ".agents/skills/code-change-verification"
RUN_MJS = SKILL_DIR / "scripts" / "run.mjs"
RUN_SH = SKILL_DIR / "scripts" / "run.sh"


def _node_module(script: str, timeout: int = 45):
    return subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO),
    )


def _mjs_specifier() -> str:
    return json.dumps(str(RUN_MJS))


def test_run_mjs_help_exits_zero():
    """`node run.mjs --help` must exit 0 and print usage."""
    r = subprocess.run(
        ["node", str(RUN_MJS), "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"--help exited {r.returncode}: stdout={r.stdout!r} stderr={r.stderr!r}"
    assert "code-change-verification" in r.stdout, f"usage missing: {r.stdout!r}"


def test_create_default_plan_structure():
    """Default plan: install+build sequentially, then build-check+dist-check+lint+test in parallel."""
    script = f"""
    const m = await import({_mjs_specifier()});
    const plan = m.createDefaultPlan();
    process.stdout.write(JSON.stringify({{
      seq: plan.sequentialSteps.map(s => ({{ label: s.label, commandText: s.commandText }})),
      par: plan.parallelSteps.map(s => ({{ label: s.label, commandText: s.commandText }})),
    }}));
    """
    r = _node_module(script)
    assert r.returncode == 0, f"node failed: {r.stderr}"
    data = json.loads(r.stdout)

    seq_labels = [s["label"] for s in data["seq"]]
    assert seq_labels == ["install", "build"], (
        f"sequential phase must be exactly install then build, got {seq_labels}"
    )

    par_labels = sorted(s["label"] for s in data["par"])
    assert par_labels == ["build-check", "dist-check", "lint", "test"], (
        f"parallel phase must contain build-check, dist-check, lint, test; got {par_labels}"
    )

    seq_cmds = [s["commandText"] for s in data["seq"]]
    par_cmds = [s["commandText"] for s in data["par"]]
    assert "pnpm i" in seq_cmds, seq_cmds
    assert "pnpm build" in seq_cmds, seq_cmds
    assert "pnpm -r build-check" in par_cmds, par_cmds
    assert any("dist:check" in c and "@openai/*" in c for c in par_cmds), par_cmds
    assert "pnpm lint" in par_cmds, par_cmds
    assert "pnpm test" in par_cmds, par_cmds


def test_sequential_failure_blocks_parallel():
    """A failing sequential step must skip parallel steps and propagate the exit code."""
    script = f"""
    const m = await import({_mjs_specifier()});
    const code = await m.runVerification({{
      sequentialSteps: [
        {{ label: 's1', command: process.execPath, args: ['-e', 'process.exit(0)'], commandText: 's1' }},
        {{ label: 's2', command: process.execPath, args: ['-e', 'process.exit(7)'], commandText: 's2' }},
      ],
      parallelSteps: [
        {{ label: 'p1', command: process.execPath, args: ['-e', 'console.log("PARALLEL_RAN_AFTER_SEQ_FAIL"); process.exit(0)'], commandText: 'p1' }},
      ],
      repoRoot: process.cwd(),
    }});
    process.stdout.write('\\n__FINAL_EXIT__=' + code + '\\n');
    """
    r = _node_module(script)
    assert "__FINAL_EXIT__=7" in r.stdout, (
        f"exit code must propagate from failing sequential step; stdout={r.stdout!r} stderr={r.stderr!r}"
    )
    assert "PARALLEL_RAN_AFTER_SEQ_FAIL" not in r.stdout, (
        "parallel steps must NOT execute when a sequential step fails"
    )


def test_parallel_fail_fast_terminates_others():
    """When one parallel step fails, the runner must terminate the still-running steps quickly."""
    script = f"""
    const m = await import({_mjs_specifier()});
    const start = Date.now();
    const code = await m.runVerification({{
      sequentialSteps: [],
      parallelSteps: [
        {{ label: 'fail', command: process.execPath, args: ['-e', 'process.exit(3)'], commandText: 'fail' }},
        {{ label: 'sleep', command: process.execPath, args: ['-e', 'setTimeout(() => process.exit(0), 60000)'], commandText: 'sleep' }},
      ],
      repoRoot: process.cwd(),
    }});
    const elapsed = Date.now() - start;
    process.stdout.write('\\n__RESULT__=' + JSON.stringify({{ code, elapsed }}) + '\\n');
    """
    r = _node_module(script, timeout=45)
    line = next((l for l in r.stdout.splitlines() if l.startswith("__RESULT__=")), None)
    assert line, f"missing __RESULT__ line: stdout={r.stdout!r} stderr={r.stderr!r}"
    data = json.loads(line.split("=", 1)[1])
    assert data["code"] == 3, f"failed step's exit code must propagate; got {data['code']}"
    assert data["elapsed"] < 30000, (
        f"fail-fast: surviving long-running step should be terminated quickly; took {data['elapsed']}ms"
    )


def test_parallel_steps_run_concurrently():
    """Independent parallel steps must run concurrently — total time ~max(step), not sum."""
    script = f"""
    const m = await import({_mjs_specifier()});
    const sleepStep = (label, ms) => ({{
      label,
      command: process.execPath,
      args: ['-e', `setTimeout(() => process.exit(0), ${{ms}})`],
      commandText: label,
    }});
    const start = Date.now();
    const code = await m.runVerification({{
      sequentialSteps: [],
      parallelSteps: [
        sleepStep('a', 2000),
        sleepStep('b', 2000),
        sleepStep('c', 2000),
        sleepStep('d', 2000),
      ],
      repoRoot: process.cwd(),
    }});
    const elapsed = Date.now() - start;
    process.stdout.write('\\n__RESULT__=' + JSON.stringify({{ code, elapsed }}) + '\\n');
    """
    r = _node_module(script, timeout=30)
    line = next((l for l in r.stdout.splitlines() if l.startswith("__RESULT__=")), None)
    assert line, f"missing __RESULT__: stdout={r.stdout!r} stderr={r.stderr!r}"
    data = json.loads(line.split("=", 1)[1])
    assert data["code"] == 0, f"all steps should succeed; got code {data['code']}"
    assert data["elapsed"] < 6000, (
        f"4 parallel 2s steps must complete in <6s when truly concurrent; took {data['elapsed']}ms"
    )


def test_output_prefixed_with_label():
    """Each line of step output must be prefixed with `[label]` so concurrent streams are disambiguated."""
    script = f"""
    const m = await import({_mjs_specifier()});
    await m.runVerification({{
      sequentialSteps: [
        {{ label: 'mystep', command: process.execPath, args: ['-e', 'console.log("hello-from-step")'], commandText: 'mystep' }},
      ],
      parallelSteps: [],
      repoRoot: process.cwd(),
    }});
    """
    r = _node_module(script)
    assert "[mystep] hello-from-step" in r.stdout, (
        f"output lines must be prefixed with [label]; got: stdout={r.stdout!r} stderr={r.stderr!r}"
    )


def test_run_sh_delegates_to_node_runner():
    """The POSIX wrapper must forward args to the Node runner.

    We invoke `bash run.sh --help` and expect exit 0 with the runner's usage banner.
    At the base commit run.sh ignores args and immediately calls `pnpm i`; pnpm is
    not installed in this test environment, so the base script exits non-zero.
    """
    r = subprocess.run(
        ["bash", str(RUN_SH), "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"bash run.sh --help should delegate to the Node runner and exit 0; "
        f"got {r.returncode}, stderr={r.stderr!r}"
    )
    assert "code-change-verification" in r.stdout, (
        f"usage banner from run.mjs missing in output: {r.stdout!r}"
    )


def test_node_check_run_mjs():
    """`node --check run.mjs` must exit 0 (valid ESM syntax)."""
    r = subprocess.run(
        ["node", "--check", str(RUN_MJS)],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"node --check run.mjs must exit 0; got {r.returncode}, "
        f"stderr={r.stderr!r}"
    )


# === pass-to-pass ===

def test_run_sh_bash_syntax_valid():
    """bash -n on run.sh passes (true at base and after fix)."""
    r = subprocess.run(
        ["bash", "-n", str(RUN_SH)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, f"bash -n failed: {r.stderr}"


def test_repo_layout_intact():
    """Repo layout sanity checks (true at base and after fix)."""
    assert (REPO / "package.json").is_file(), "package.json must exist at repo root"
    assert (REPO / "AGENTS.md").is_file(), "AGENTS.md must exist at repo root"
    assert (SKILL_DIR / "SKILL.md").is_file(), "code-change-verification SKILL.md must exist"
    assert RUN_SH.is_file(), "run.sh must exist"
