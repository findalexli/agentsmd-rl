import os
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = "/workspace/hugo"
HUGO_BIN = "/tmp/hugo-task-bin"


def _build_hugo():
    """Compile hugo from the (possibly patched) source tree."""
    r = subprocess.run(
        ["go", "build", "-o", HUGO_BIN, "./"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CGO_ENABLED": "0"},
    )
    assert r.returncode == 0, f"go build failed:\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"


def _make_site(tmp_path: Path, hugo_min: str, hugo_max: str) -> Path:
    """Create a minimal Hugo site whose hugo.toml triggers a module version warning."""
    site = tmp_path / "site"
    (site / "layouts").mkdir(parents=True, exist_ok=True)
    (site / "hugo.toml").write_text(textwrap.dedent(f"""
        baseURL="https://example.org"

        [module]
        [module.hugoVersion]
        min = "{hugo_min}"
        max = "{hugo_max}"
    """).strip() + "\n")
    (site / "layouts" / "all.html").write_text("All.")
    return site


@pytest.fixture(scope="module", autouse=True)
def _hugo_built():
    _build_hugo()
    yield


def _run_hugo(cwd: Path, *args, timeout=60):
    return subprocess.run(
        [HUGO_BIN, *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "HOME": str(cwd), "HUGO_TESTRUN": "true"},
    )


# ---------- fail-to-pass ----------

def test_panic_on_warning_module_min_max_equal_exits_nonzero(tmp_path):
    """With --panicOnWarning, hugo must exit with a non-zero status when a module
    version warning is logged. With the bug, the flag is silently ignored and hugo
    exits 0."""
    site = _make_site(tmp_path, "0.148.0", "0.148.0")
    r = _run_hugo(site, "--panicOnWarning")
    assert r.returncode != 0, (
        f"Expected non-zero exit with --panicOnWarning, got {r.returncode}.\n"
        f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    )


def test_panic_on_warning_stderr_contains_compatibility_message(tmp_path):
    """The stderr must surface the module compatibility warning text when the
    panic fires (it is the message the hook panics with)."""
    site = _make_site(tmp_path, "0.148.0", "0.148.0")
    r = _run_hugo(site, "--panicOnWarning")
    assert "is not compatible with this Hugo" in r.stderr, (
        f"Expected compatibility message in stderr.\nSTDERR was: {r.stderr}"
    )


def test_panic_on_warning_min_only_exits_nonzero(tmp_path):
    """Different hugoVersion bound (min only, set far above current) must also
    trigger the panic — guards against tests that hardcode a single version."""
    site = _make_site(tmp_path, "9.99.0", "9.99.0")
    r = _run_hugo(site, "--panicOnWarning")
    assert r.returncode != 0, (
        f"Expected non-zero exit with --panicOnWarning (9.99.0).\n"
        f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    )
    assert "is not compatible with this Hugo" in r.stderr


def test_without_panic_on_warning_still_succeeds(tmp_path):
    """Sanity: a build that produces a warning but is run WITHOUT --panicOnWarning
    must still succeed. This guards against an over-eager fix that turns warnings
    into errors unconditionally."""
    site = _make_site(tmp_path, "0.148.0", "0.148.0")
    r = _run_hugo(site)
    assert r.returncode == 0, (
        f"Build without --panicOnWarning must succeed.\nSTDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    )
    assert "is not compatible with this Hugo" in r.stderr  # warning still shown


def test_panic_on_warning_clean_site_succeeds(tmp_path):
    """A clean site (no warnings) must still build successfully even with
    --panicOnWarning. This rules out a stub fix that always panics on the flag
    regardless of whether warnings exist."""
    site = tmp_path / "clean"
    (site / "layouts").mkdir(parents=True)
    (site / "hugo.toml").write_text('baseURL="https://example.org"\n')
    (site / "layouts" / "all.html").write_text("All.")
    r = _run_hugo(site, "--panicOnWarning")
    assert r.returncode == 0, (
        f"Clean site with --panicOnWarning should succeed.\n"
        f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    )


# ---------- pass-to-pass (repo CI signals) ----------

def test_repo_go_vet_commands():
    """`go vet ./commands/...` must remain clean."""
    r = subprocess.run(
        ["go", "vet", "./commands/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr}"


def test_repo_gofmt_commands_clean():
    """`gofmt -l commands/` must report no diffs."""
    r = subprocess.run(
        ["gofmt", "-l", "commands/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"gofmt errored:\n{r.stderr}"
    assert r.stdout.strip() == "", f"gofmt found unformatted files:\n{r.stdout}"


def test_repo_loggers_unit_tests():
    """Pre-existing loggers package tests must still pass."""
    r = subprocess.run(
        ["go", "test", "-count=1", "-timeout=120s", "./common/loggers/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"loggers tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_commands_package_compiles():
    """The commands package must still build."""
    r = subprocess.run(
        ["go", "build", "./commands/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"commands package failed to build:\n{r.stderr}"

# === Additional pass-to-pass (repo CI signals) ===

def test_repo_commands_unit_tests():
    """Existing tests in the commands package (the directly modified package)
    must still pass after the fix."""
    r = subprocess.run(
        ["go", "test", "-count=1", "-timeout=120s", "./commands/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"commands tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_full_build():
    """The full project must compile without errors."""
    r = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"full build failed:\n{r.stderr}"