"""Behavioral tests for the prql Taskfile/CLAUDE.md token-reduction PR.

Each test maps 1:1 to a check id in eval_manifest.yaml.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path("/workspace/prql")
TASKFILE = REPO / "Taskfile.yaml"
CLAUDE_MD = REPO / "CLAUDE.md"


def _load_taskfile() -> dict:
    with TASKFILE.open() as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# pass_to_pass — sanity gates that hold on the base commit
# ---------------------------------------------------------------------------


def test_taskfile_is_valid_yaml():
    """Taskfile.yaml parses as YAML and has a `tasks` mapping."""
    data = _load_taskfile()
    assert isinstance(data, dict), "Taskfile root is not a mapping"
    assert "tasks" in data, "Taskfile has no `tasks` key"
    assert isinstance(data["tasks"], dict)


def test_task_binary_lists_tasks():
    """`task --list-all` runs against the Taskfile and lists key tasks."""
    r = subprocess.run(
        ["task", "--list-all", "--taskfile", str(TASKFILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"`task --list-all` failed (exit={r.returncode})\n"
        f"stdout: {r.stdout[-400:]}\nstderr: {r.stderr[-400:]}"
    )
    out = r.stdout
    assert "build-all" in out, "`build-all` task not listed"
    assert "test-rust" in out, "`test-rust` task not listed"


# ---------------------------------------------------------------------------
# fail_to_pass — encode the PR's behavioral changes
# ---------------------------------------------------------------------------


def test_buildall_cargo_build_uses_quiet():
    """Every `cargo build` command in the build-all task includes --quiet."""
    data = _load_taskfile()
    cmds = data["tasks"]["build-all"]["cmds"]
    cargo_builds = [
        c for c in cmds
        if isinstance(c, str) and c.lstrip().startswith("cargo build")
    ]
    assert len(cargo_builds) >= 4, (
        f"expected at least 4 cargo-build commands in build-all, "
        f"got {len(cargo_builds)}: {cargo_builds!r}"
    )
    missing = [c for c in cargo_builds if "--quiet" not in c]
    assert not missing, (
        f"these cargo-build commands in build-all are missing --quiet: {missing!r}"
    )


def test_buildall_cargo_doc_uses_quiet():
    """The `cargo doc` command in the build-all task includes --quiet."""
    data = _load_taskfile()
    cmds = data["tasks"]["build-all"]["cmds"]
    cargo_docs = [
        c for c in cmds
        if isinstance(c, str) and c.lstrip().startswith("cargo doc")
    ]
    assert cargo_docs, "no cargo-doc command found in build-all"
    missing = [c for c in cargo_docs if "--quiet" not in c]
    assert not missing, (
        f"these cargo-doc commands in build-all are missing --quiet: {missing!r}"
    )


def test_buildeachcrate_template_uses_quiet():
    """The cargo build template in build-each-crate includes --quiet."""
    data = _load_taskfile()
    cmds = data["tasks"]["build-each-crate"]["cmds"]
    string_cmds = [c for c in cmds if isinstance(c, str)]
    joined = "\n".join(string_cmds)
    # Every line that builds a package via -p must use --quiet.
    template_lines = [
        line for line in joined.splitlines()
        if "cargo build" in line and "-p" in line
    ]
    assert template_lines, (
        f"no `cargo build … -p …` template line found in build-each-crate; cmds={cmds!r}"
    )
    missing = [line for line in template_lines if "--quiet" not in line]
    assert not missing, (
        f"build-each-crate cargo-build template missing --quiet: {missing!r}"
    )


def test_testrust_has_nextest_status_level_env():
    """test-rust task sets NEXTEST_STATUS_LEVEL=fail to suppress passing-test output."""
    data = _load_taskfile()
    test_rust = data["tasks"]["test-rust"]
    env = test_rust.get("env")
    assert env is not None, (
        f"test-rust task has no `env` block; keys={list(test_rust.keys())}"
    )
    assert "NEXTEST_STATUS_LEVEL" in env, (
        f"NEXTEST_STATUS_LEVEL missing from test-rust env: {env!r}"
    )
    # Accept str or normalised value
    assert str(env["NEXTEST_STATUS_LEVEL"]).strip().lower() == "fail", (
        f"NEXTEST_STATUS_LEVEL should be 'fail', got {env['NEXTEST_STATUS_LEVEL']!r}"
    )


def test_testrust_has_nextest_final_status_level_env():
    """test-rust task sets NEXTEST_FINAL_STATUS_LEVEL=slow to surface slow tests in summary."""
    data = _load_taskfile()
    env = data["tasks"]["test-rust"].get("env") or {}
    assert "NEXTEST_FINAL_STATUS_LEVEL" in env, (
        f"NEXTEST_FINAL_STATUS_LEVEL missing from test-rust env: {env!r}"
    )
    assert str(env["NEXTEST_FINAL_STATUS_LEVEL"]).strip().lower() == "slow", (
        f"NEXTEST_FINAL_STATUS_LEVEL should be 'slow', "
        f"got {env['NEXTEST_FINAL_STATUS_LEVEL']!r}"
    )


def test_claude_md_documents_inner_outer_loop():
    """CLAUDE.md introduces the inner/outer loop testing workflow."""
    content = CLAUDE_MD.read_text()
    # Distinctive phrases the gold diff added — workflow concept.
    assert "Inner loop" in content, (
        "CLAUDE.md does not mention the 'Inner loop' workflow"
    )
    assert "Outer loop" in content, (
        "CLAUDE.md does not mention the 'Outer loop' workflow"
    )


def test_claude_md_documents_token_reduction_config():
    """CLAUDE.md explains the test-suite token-usage configuration."""
    content = CLAUDE_MD.read_text()
    lower = content.lower()
    # The PR's documentation explains both halves of the optimisation.
    assert "nextest" in lower, (
        "CLAUDE.md does not mention nextest's role in reducing test output"
    )
    assert "--quiet" in content, (
        "CLAUDE.md does not mention the --quiet cargo-build flag"
    )


# ---------------------------------------------------------------------------
# Anti-tautology gate — verify the file actually changed at the right scope.
# This guards against an agent that satisfies signal lines by appending random
# text rather than restructuring the file.
# ---------------------------------------------------------------------------


def test_claude_md_workflow_section_above_tests_section():
    """The Development Workflow / inner-outer-loop content appears before
    the (kept) Tests section, mirroring the gold reorganisation."""
    content = CLAUDE_MD.read_text()
    inner_idx = content.find("Inner loop")
    tests_idx = content.find("\n## Tests")
    if tests_idx == -1:
        tests_idx = content.find("## Tests")
    assert inner_idx != -1, "Inner loop content missing"
    assert tests_idx != -1, "## Tests heading missing"
    assert inner_idx < tests_idx, (
        f"Inner-loop content should precede the ## Tests section "
        f"(inner_loop@{inner_idx}, tests@{tests_idx})"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "--tb=short"]))

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_grammars_build_grammar():
    """pass_to_pass | CI job 'test-grammars' → step 'Build grammar'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun install && bun run build'], cwd=os.path.join(REPO, 'grammars/prql-lezer/'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build grammar' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_grammars_test_grammar():
    """pass_to_pass | CI job 'test-grammars' → step 'Test grammar'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun install && bun run test'], cwd=os.path.join(REPO, 'grammars/prql-lezer/'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test grammar' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")