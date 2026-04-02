"""
Task: uv-python-preference-consolidation
Repo: astral-sh/uv @ bd2e0c9b09551c6570b14c4da80364fe90805b78
PR:   18567

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/repo")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check_uv_python():
    """The uv-python crate must compile after refactoring."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-python"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check -p uv-python failed:\n{r.stderr.decode()[-2000:]}"
    )


# [static] pass_to_pass
def test_cargo_check_uv():
    """All call sites in the uv crate must compile with the updated API."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check -p uv failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core refactoring checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_free_function_removed():
    """satisfies_python_preference free function must be removed and no longer called.

    The function existed as a standalone in discovery.rs and was exported from lib.rs.
    A correct fix consolidates it into a method on PythonPreference or PythonInstallation.
    """
    discovery = (REPO / "crates/uv-python/src/discovery.rs").read_text()
    lib = (REPO / "crates/uv-python/src/lib.rs").read_text()

    # Must not be defined as a free function
    assert not re.search(
        r"^pub\s+fn\s+satisfies_python_preference\b", discovery, re.MULTILINE
    ), "satisfies_python_preference free function still defined in discovery.rs"

    # Must not be exported from lib.rs
    assert "satisfies_python_preference" not in lib, (
        "satisfies_python_preference still exported from lib.rs"
    )

    # Must not be called from any .rs file under crates/uv/src
    for rs_file in (REPO / "crates/uv/src").rglob("*.rs"):
        content = rs_file.read_text()
        lines = [l for l in content.splitlines() if not l.strip().startswith("//")]
        cleaned = "\n".join(lines)
        assert "satisfies_python_preference(" not in cleaned, (
            f"{rs_file.relative_to(REPO)} still calls satisfies_python_preference"
        )


# [pr_diff] fail_to_pass
def test_is_system_interpreter_removed():
    """is_system_interpreter free function must be removed from discovery.rs.

    This helper duplicated logic that should live on PythonInstallation.
    """
    discovery = (REPO / "crates/uv-python/src/discovery.rs").read_text()
    # Match any visibility: pub, pub(crate), or private
    assert not re.search(
        r"^\s*(pub(\s*\(crate\))?\s+)?fn\s+is_system_interpreter\b", discovery, re.MULTILINE
    ), "is_system_interpreter free function still exists in discovery.rs"


# [pr_diff] fail_to_pass
def test_list_inline_preference_removed():
    """list.rs must not reimplement preference logic with inline match on variants.

    The base code has a filter closure matching on OnlyManaged/OnlySystem with
    .is_managed() — this doesn't account for explicit sources. A correct fix
    delegates to a consolidated method instead.
    """
    list_rs = (REPO / "crates/uv/src/commands/python/list.rs").read_text()
    lines = [l for l in list_rs.splitlines() if not l.strip().startswith("//")]
    cleaned = "\n".join(lines)

    has_only_managed = "PythonPreference::OnlyManaged" in cleaned
    has_only_system = "PythonPreference::OnlySystem" in cleaned
    has_is_managed = ".is_managed()" in cleaned

    assert not (has_only_managed and has_only_system and has_is_managed), (
        "list.rs still has inline preference variant match with is_managed()"
    )


# [pr_diff] fail_to_pass
def test_preference_method_on_type():
    """PythonPreference must have an allows_installation method that takes
    &PythonInstallation, consolidating the preference check onto the type
    rather than keeping it as a free function with loose parameters.
    """
    discovery = (REPO / "crates/uv-python/src/discovery.rs").read_text()

    # Must have a method that takes &PythonInstallation (not loose source + interpreter params)
    # Accepts allows_installation, satisfies_installation, check_installation, etc.
    has_consolidated = re.search(
        r"fn\s+\w+installation\w*\s*\(\s*self\s*,\s*\w+\s*:\s*&PythonInstallation\b",
        discovery,
    )
    assert has_consolidated, (
        "PythonPreference missing method that takes &PythonInstallation"
    )


# [pr_diff] fail_to_pass
def test_installation_has_is_managed():
    """PythonInstallation must have an is_managed(&self) method.

    The PR moves the system/managed check from a free function in discovery.rs
    to a method on the installation type itself, using source as fast path
    and falling back to interpreter.is_managed().
    """
    installation = (REPO / "crates/uv-python/src/installation.rs").read_text()

    has_method = re.search(
        r"pub\s+fn\s+is_managed\s*\(\s*&self\s*\)", installation
    )
    assert has_method, (
        "PythonInstallation missing pub fn is_managed(&self) method"
    )


# [pr_diff] fail_to_pass
def test_allows_interpreter_method():
    """PythonPreference must have an allows_interpreter method that checks
    whether an interpreter (not a full installation) satisfies the preference.

    This is a building block used by allows_installation and separates
    the interpreter-level check from the source-level check.
    """
    discovery = (REPO / "crates/uv-python/src/discovery.rs").read_text()

    # Accepts allows_interpreter, satisfies_interpreter, check_interpreter, etc.
    has_method = re.search(
        r"pub\s+fn\s+\w+interpreter\w*\s*\(\s*self\s*,\s*\w+\s*:\s*&Interpreter\b",
        discovery,
    )
    assert has_method, (
        "PythonPreference missing pub method that takes &Interpreter for preference checking"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_cargo_test_uv_python():
    """uv-python crate's own unit tests must still pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-python", "--lib"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo test -p uv-python --lib failed:\n{r.stderr.decode()[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_lib_exports_core_types():
    """lib.rs must still export core types used by downstream crates."""
    lib = (REPO / "crates/uv-python/src/lib.rs").read_text()
    required = ["PythonPreference", "PythonSource", "find_python_installations", "PythonRequest"]
    missing = [name for name in required if name not in lib]
    assert not missing, f"lib.rs missing exports: {missing}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:10 @ bd2e0c9b09551c6570b14c4da80364fe90805b78
def test_no_allow_attr_in_modified_files():
    """No #[allow(...)] attributes in PythonPreference/PythonInstallation impl blocks.

    CLAUDE.md line 10: 'PREFER #[expect()] over [allow()] if clippy must be disabled'
    Checks the files modified by this PR for new #[allow()] usage.
    """
    files_to_check = [
        REPO / "crates/uv-python/src/discovery.rs",
        REPO / "crates/uv-python/src/installation.rs",
    ]
    for fpath in files_to_check:
        content = fpath.read_text()
        # Extract impl blocks for PythonPreference and PythonInstallation
        in_impl = False
        brace_depth = 0
        impl_lines = []
        for line in content.splitlines():
            if re.search(r"impl\s+(PythonPreference|PythonInstallation)\b", line) and "{" in line:
                in_impl = True
                brace_depth = 0
            if in_impl:
                brace_depth += line.count("{") - line.count("}")
                impl_lines.append(line)
                if brace_depth <= 0 and len(impl_lines) > 1:
                    in_impl = False
        impl_text = "\n".join(impl_lines)
        allows = re.findall(r"#\[allow\(", impl_text)
        assert not allows, (
            f"{fpath.name} has #[allow()] in impl block — use #[expect()] instead per CLAUDE.md:10"
        )


# [agent_config] pass_to_pass — CLAUDE.md:7 @ bd2e0c9b09551c6570b14c4da80364fe90805b78
def test_no_unwrap_panic_in_preference_impl():
    """No unwrap/panic/unreachable in PythonPreference impl block.

    CLAUDE.md line 7: 'AVOID using panic!, unreachable!, .unwrap(), unsafe code'
    """
    discovery = (REPO / "crates/uv-python/src/discovery.rs").read_text()

    # Extract impl PythonPreference block(s)
    in_impl = False
    brace_depth = 0
    impl_lines = []
    for line in discovery.splitlines():
        if "impl PythonPreference" in line and "{" in line:
            in_impl = True
            brace_depth = 0
        if in_impl:
            brace_depth += line.count("{") - line.count("}")
            stripped = line.strip()
            if not stripped.startswith("//"):
                impl_lines.append(line)
            if brace_depth <= 0 and len(impl_lines) > 1:
                break

    impl_text = "\n".join(impl_lines)
    found = [p for p in [".unwrap()", "panic!", "unreachable!"] if p in impl_text]
    assert not found, f"Found {found} in PythonPreference impl block"
