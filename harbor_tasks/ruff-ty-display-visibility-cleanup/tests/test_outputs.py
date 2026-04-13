"""
Task: ruff-ty-display-visibility-cleanup
Repo: astral-sh/ruff @ 162852609ad01f171ba868900d18e57236573785
PR:   24486

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/ruff"
DISPLAY_RS = f"{REPO}/crates/ty_python_semantic/src/types/display.rs"


def _read_display_rs():
    return Path(DISPLAY_RS).read_text()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_truncate_long_unions_removed():
    """The truncate_long_unions method is dead code and must be removed entirely."""
    src = _read_display_rs()
    assert "fn truncate_long_unions" not in src, (
        "truncate_long_unions method should be removed entirely (dead code)"
    )


def test_specialization_display_removed():
    """The no-arg Specialization::display() method is unused and must be removed."""
    src = _read_display_rs()
    for line in src.splitlines():
        stripped = line.strip()
        # Match: fn display(self, db: ...) -> DisplaySpecialization
        # but NOT display_full, display_short, or display_with
        if (
            "fn display(" in stripped
            and "DisplaySpecialization" in stripped
            and "display_full" not in stripped
            and "display_short" not in stripped
            and "display_with" not in stripped
        ):
            assert False, (
                f"Specialization::display() should be removed, found: {stripped}"
            )


def test_no_unnecessary_pub_on_structs_enums():
    """Display helper structs and enums must not have unnecessary pub/pub(crate)."""
    src = _read_display_rs()
    items = [
        ("struct", "DisplayTuple"),
        ("struct", "DisplayFunctionType"),
        ("struct", "DisplayGenericContext"),
        ("struct", "DisplaySpecialization"),
        ("struct", "DisplayTypeArray"),
        ("enum", "QualificationLevel"),
        ("enum", "TupleSpecialization"),
    ]
    for kind, name in items:
        for line in src.splitlines():
            stripped = line.strip()
            if f"{kind} {name}" in stripped:
                assert not stripped.startswith("pub "), (
                    f"{name} {kind} should not be pub: {stripped}"
                )
                assert not stripped.startswith("pub(crate) "), (
                    f"{name} {kind} should not be pub(crate): {stripped}"
                )


def test_no_unnecessary_pub_on_methods():
    """Helper methods that are only used internally must not be pub/pub(crate)."""
    src = _read_display_rs()
    methods = [
        "fn singleline",
        "fn force_signature_name",
        "fn with_active_scopes",
    ]
    for method_sig in methods:
        found_pub = False
        for line in src.splitlines():
            stripped = line.strip()
            if method_sig in stripped:
                if stripped.startswith("pub ") or stripped.startswith("pub(crate) "):
                    found_pub = True
                    break
        assert not found_pub, (
            f"Method {method_sig} should not be pub or pub(crate)"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static / repo_tests) — regression + compilation gate
# ---------------------------------------------------------------------------


def test_cargo_check():
    """Crate must compile after visibility changes (incremental check)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    )


def test_cargo_clippy():
    """Crate must pass clippy lints (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo clippy failed:\n{r.stderr.decode()[-500:]}\n{r.stdout.decode()[-500:]}"
    )


def test_cargo_test_lib():
    """Crate library unit tests must pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--lib"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo test --lib failed:\n{r.stderr.decode()[-500:]}\n{r.stdout.decode()[-500:]}"
    )


def test_cargo_fmt():
    """Crate must be formatted according to rustfmt (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "-p", "ty_python_semantic", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"cargo fmt check failed:\n{r.stderr.decode()[-500:]}\n{r.stdout.decode()[-500:]}"
    )


def test_cargo_doc():
    """Crate documentation must build without warnings (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "doc", "--no-deps", "-p", "ty_python_semantic"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo doc failed:\n{r.stderr.decode()[-500:]}\n{r.stdout.decode()[-500:]}"
    )


def test_cargo_check_all_features():
    """Crate must compile with all features enabled (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic", "--all-features"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo check --all-features failed:\n{r.stderr.decode()[-500:]}\n{r.stdout.decode()[-500:]}"
    )


def test_cargo_clippy_all_features():
    """Crate must pass clippy lints with all features enabled (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic", "--all-features", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo clippy --all-features failed:\n{r.stderr.decode()[-500:]}\n{r.stdout.decode()[-500:]}"
    )


def test_cargo_test_doc():
    """Crate documentation tests must pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--doc"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo test --doc failed:\n{r.stderr.decode()[-500:]}\n{r.stdout.decode()[-500:]}"
    )


def test_cargo_check_all_targets():
    """Crate must compile with all targets (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic", "--all-targets"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo check --all-targets failed:\n{r.stderr.decode()[-500:]}\n{r.stdout.decode()[-500:]}"
    )


def test_cargo_clippy_all_targets():
    """Crate must pass clippy lints for all targets (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic", "--all-targets", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo clippy --all-targets failed:\n{r.stderr.decode()[-500:]}\n{r.stdout.decode()[-500:]}"
    )


def test_cargo_test_mdtest():
    """Crate mdtest tests must pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--test", "mdtest"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo test --test mdtest failed:\n{r.stderr.decode()[-500:]}\n{r.stdout.decode()[-500:]}"
    )


def test_qualified_fields_not_pub():
    """DisplaySettings.qualified and qualified_type_aliases fields must be private."""
    src = _read_display_rs()
    for line in src.splitlines():
        stripped = line.strip()
        if "qualified:" in stripped and "Rc<FxHashMap" in stripped:
            assert not stripped.startswith("pub "), (
                f"qualified field should not be pub: {stripped}"
            )
        if "qualified_type_aliases:" in stripped and "Rc<FxHashMap" in stripped:
            assert not stripped.startswith("pub "), (
                f"qualified_type_aliases field should not be pub: {stripped}"
            )
