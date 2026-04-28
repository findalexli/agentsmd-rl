"""Tests for mlflow#22328: dev/check_action_pins.py + action-pins pre-commit hook.

Tests are deliberately behavioural — they invoke the script via subprocess on
synthetic workflow files and assert exit codes / stderr content. Network calls
to `git ls-remote` are avoided either by feeding inputs that short-circuit
before verification (non-SHA refs / missing version comments) or by
pre-populating the cache file `.cache/action-pins.json` so that
`_verify_sha_tag` returns from the cache.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path("/workspace/mlflow")
SCRIPT = REPO / "dev" / "check_action_pins.py"

# A real, well-known 40-char SHA for actions/checkout — used only as a
# syntactically-valid stand-in. Tests never rely on it actually matching a tag
# upstream; they always seed the cache when they need verification to succeed.
SAMPLE_SHA = "692973e3d937129bcbf40652eb9f2f61becf3332"
OTHER_SHA = "11bd71901bbe5b1630ceea73d27597364c9af683"


def _run(args, *, cwd, timeout=30):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )


def _make_workspace(tmp: Path, files: dict[str, str], cache: dict | None = None) -> None:
    for rel, content in files.items():
        f = tmp / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
    if cache is not None:
        (tmp / ".cache").mkdir(exist_ok=True)
        (tmp / ".cache" / "action-pins.json").write_text(json.dumps(cache))


# --------------------------------------------------------------------------- #
# Sanity / structural
# --------------------------------------------------------------------------- #

def test_script_present_and_executable_with_python():
    """The validator script lives at dev/check_action_pins.py and is runnable."""
    assert SCRIPT.is_file(), f"Expected {SCRIPT} to exist"
    # Must be syntactically valid Python.
    r = subprocess.run(
        [sys.executable, "-c", f"import ast; ast.parse(open({str(SCRIPT)!r}).read())"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Script is not valid Python:\n{r.stderr}"


def test_script_uses_only_stdlib():
    """The script must be stdlib-only (no third-party imports).

    The PR description states this explicitly so the hook can run inside the
    `lint` uv group without dragging extra dependencies into the cache.
    """
    import ast
    tree = ast.parse(SCRIPT.read_text())
    stdlib = {
        "argparse", "ast", "collections", "contextlib", "dataclasses",
        "functools", "glob", "hashlib", "io", "itertools", "json", "os",
        "pathlib", "re", "subprocess", "sys", "typing", "urllib", "shutil",
        "tempfile", "logging", "textwrap",
    }
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in stdlib:
                    bad.append(top)
        elif isinstance(node, ast.ImportFrom) and node.module:
            top = node.module.split(".")[0]
            if top not in stdlib:
                bad.append(top)
    assert not bad, f"Non-stdlib imports detected: {sorted(set(bad))}"


# --------------------------------------------------------------------------- #
# Behavioural — exit codes
# --------------------------------------------------------------------------- #

def test_clean_workflow_with_no_uses_lines_passes():
    """A workflow file with no `uses:` lines should not produce any violation."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        wf = tmp / "wf.yml"
        wf.write_text("name: test\non: push\njobs: {}\n")
        r = _run([str(wf)], cwd=tmp)
        assert r.returncode == 0, f"stderr:\n{r.stderr}"


def test_local_action_uses_is_skipped():
    """`uses: ./local-action` references local actions and must NOT be checked."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        wf = tmp / "wf.yml"
        wf.write_text(
            "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
            "      - uses: ./.github/actions/some-local-action\n"
        )
        r = _run([str(wf)], cwd=tmp)
        assert r.returncode == 0, f"Local action triggered an error:\n{r.stderr}"


def test_tag_ref_without_sha_is_rejected():
    """A `uses: actions/checkout@v4` ref (a tag, not a SHA) must fail."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        wf = tmp / "wf.yml"
        wf.write_text(
            "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
            "      - uses: actions/checkout@v4\n"
        )
        r = _run([str(wf)], cwd=tmp)
        assert r.returncode == 1, f"Expected exit 1 for tag ref, got {r.returncode}"
        assert r.stderr.strip(), "Expected non-empty stderr describing the violation"


def test_short_sha_ref_is_rejected():
    """A 7-char SHA prefix is not a valid pin — only full 40-char SHAs are accepted."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        wf = tmp / "wf.yml"
        wf.write_text(
            "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
            "      - uses: actions/checkout@692973e # v5.0.0\n"
        )
        r = _run([str(wf)], cwd=tmp)
        assert r.returncode == 1
        assert r.stderr.strip()


def test_full_sha_without_version_comment_is_rejected():
    """A SHA-pinned ref without any `# vX.Y.Z` comment is not allowed."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        wf = tmp / "wf.yml"
        wf.write_text(
            "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
            f"      - uses: actions/checkout@{SAMPLE_SHA}\n"
        )
        r = _run([str(wf)], cwd=tmp)
        assert r.returncode == 1
        assert r.stderr.strip()


def test_full_sha_with_short_version_comment_is_rejected():
    """A version comment like `# v4` (not vX.Y.Z) is rejected as ambiguous."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        wf = tmp / "wf.yml"
        wf.write_text(
            "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
            f"      - uses: actions/checkout@{SAMPLE_SHA} # v4\n"
        )
        r = _run([str(wf)], cwd=tmp)
        assert r.returncode == 1, f"stderr:\n{r.stderr}"
        assert r.stderr.strip()


def test_full_sha_with_partial_version_comment_is_rejected():
    """`# v4.2` (missing patch component) is rejected."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        wf = tmp / "wf.yml"
        wf.write_text(
            "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
            f"      - uses: actions/checkout@{SAMPLE_SHA} # v4.2\n"
        )
        r = _run([str(wf)], cwd=tmp)
        assert r.returncode == 1
        assert r.stderr.strip(), f"Expected non-empty stderr, got: {r.stderr!r}"


def test_full_pin_with_cached_match_passes():
    """SHA + `# vX.Y.Z` + cache says the SHA matches the tag → exit 0."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        cache = {f"actions/checkout@{SAMPLE_SHA}#v5.0.0": True}
        _make_workspace(
            tmp,
            {
                "wf.yml": (
                    "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
                    f"      - uses: actions/checkout@{SAMPLE_SHA} # v5.0.0\n"
                ),
            },
            cache=cache,
        )
        r = _run([str(tmp / "wf.yml")], cwd=tmp)
        assert r.returncode == 0, f"Expected exit 0 with cached match.\nstderr:\n{r.stderr}"


def test_full_pin_with_cached_mismatch_fails():
    """If the cache says the SHA does NOT match the tag, exit 1."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        cache = {f"actions/checkout@{OTHER_SHA}#v5.0.0": False}
        _make_workspace(
            tmp,
            {
                "wf.yml": (
                    "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
                    f"      - uses: actions/checkout@{OTHER_SHA} # v5.0.0\n"
                ),
            },
            cache=cache,
        )
        r = _run([str(tmp / "wf.yml")], cwd=tmp)
        assert r.returncode == 1
        assert r.stderr.strip()


def test_multiple_files_first_clean_second_bad():
    """When given multiple files, ALL violations across files are reported (exit 1)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        clean = tmp / "clean.yml"
        clean.write_text("name: ok\non: push\njobs: {}\n")
        bad = tmp / "bad.yml"
        bad.write_text(
            "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
            "      - uses: actions/checkout@v5\n"
        )
        r = _run([str(clean), str(bad)], cwd=tmp)
        assert r.returncode == 1, f"stderr:\n{r.stderr}"


def test_subpath_action_pinning_enforced():
    """`uses: owner/repo/sub/path@<ref>` is a remote action and must be pinned."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        wf = tmp / "wf.yml"
        wf.write_text(
            "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
            "      - uses: actions/cache/restore@v4\n"
        )
        r = _run([str(wf)], cwd=tmp)
        assert r.returncode == 1
        assert r.stderr.strip(), f"Expected non-empty stderr for subpath violation, got: {r.stderr!r}"


def test_default_glob_discovers_workflows_under_dot_github():
    """Without explicit args, the script must scan .github/workflows/ + .github/actions/ recursively."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # Place a bad workflow under .github/workflows/ to trigger discovery.
        _make_workspace(
            tmp,
            {
                ".github/workflows/lint.yml": (
                    "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
                    "      - uses: actions/checkout@main\n"
                ),
            },
        )
        r = _run([], cwd=tmp)
        assert r.returncode == 1, (
            f"Default-glob discovery should have found .github/workflows/lint.yml.\n"
            f"stderr:\n{r.stderr}"
        )


# --------------------------------------------------------------------------- #
# Static contract: pre-commit hook + lint workflow cache step
# --------------------------------------------------------------------------- #

def test_precommit_config_registers_action_pins_hook():
    """`.pre-commit-config.yaml` must register an `action-pins` hook that runs the script."""
    cfg = (REPO / ".pre-commit-config.yaml").read_text()
    assert "id: action-pins" in cfg, "Hook id `action-pins` not found in .pre-commit-config.yaml"
    assert "dev/check_action_pins.py" in cfg, (
        "Hook entry should call dev/check_action_pins.py"
    )


def test_precommit_hook_targets_workflow_and_action_yamls():
    """The action-pins hook must restrict its `files:` glob to GitHub Action YAML files."""
    cfg = (REPO / ".pre-commit-config.yaml").read_text()
    # The hook's `files:` regex should reference both workflows and actions paths.
    block_start = cfg.find("id: action-pins")
    assert block_start >= 0
    # Look at ~400 chars following the hook id for a `files:` directive.
    block = cfg[block_start : block_start + 400]
    assert "files:" in block, "action-pins hook missing a `files:` filter"
    assert "workflows" in block, (
        "action-pins hook `files:` pattern should mention `workflows`"
    )
    assert "actions" in block, (
        "action-pins hook `files:` pattern should mention `actions`"
    )


def test_lint_workflow_caches_action_pins_json():
    """The lint workflow must cache `.cache/action-pins.json` between runs."""
    lint_yml = (REPO / ".github" / "workflows" / "lint.yml").read_text()
    assert ".cache/action-pins.json" in lint_yml, (
        "lint.yml should cache the action-pins JSON file so the GitHub API is hit at most once per pin"
    )


# --------------------------------------------------------------------------- #
# pass_to_pass: existing dev/ tooling is intact (compiles)
# --------------------------------------------------------------------------- #

def test_existing_dev_normalize_chars_compiles():
    """Sanity: pre-existing dev/normalize_chars.py is unaffected and compiles."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(REPO / "dev" / "normalize_chars.py")],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"


def test_repo_python_version_constraint_unchanged():
    """Sanity: pyproject.toml still declares >=3.10 — the new script uses match/case + slots."""
    pyproject = (REPO / "pyproject.toml").read_text()
    assert 'requires-python = ">=3.10"' in pyproject
