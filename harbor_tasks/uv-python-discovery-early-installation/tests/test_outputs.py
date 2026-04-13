"""
Task: uv-python-discovery-early-installation
Repo: astral-sh/uv @ 6d628da78a2b1689640f5dbf2b04f56f179601b0
PR:   18564

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/repo"
DISCOVERY = f"{REPO}/crates/uv-python/src/discovery.rs"
INSTALL = f"{REPO}/crates/uv-python/src/installation.rs"


# ---------------------------------------------------------------------------
# Rust toolchain setup
# ---------------------------------------------------------------------------

def _ensure_rust_installed():
    """Ensure rustup and cargo are available for CI-style checks."""
    cargo_bin = Path.home() / ".cargo" / "bin"
    cargo_path = cargo_bin / "cargo"

    if cargo_path.exists():
        return str(cargo_bin)

    # Install rustup
    install_script = """
set -e
export RUSTUP_HOME="$HOME/.rustup"
export CARGO_HOME="$HOME/.cargo"
if ! command -v rustup &>/dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
fi
"""
    result = subprocess.run(
        ["bash", "-c", install_script],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Rust installation failed: {result.stderr}")

    return str(cargo_bin)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_rust_comments(src: str) -> str:
    """Remove Rust comments to prevent comment-injection gaming."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src


def _read_stripped(path: str) -> str:
    return _strip_rust_comments(Path(path).read_text())


def _extract_fn_body(src: str, fn_name: str) -> str | None:
    """Extract function body using brace counting."""
    pattern = rf"fn\s+{fn_name}\s*[<(]"
    match = re.search(pattern, src)
    if not match:
        return None
    start = match.start()
    brace_pos = src.index("{", start)
    depth = 1
    pos = brace_pos + 1
    while depth > 0 and pos < len(src):
        if src[pos] == "{":
            depth += 1
        elif src[pos] == "}":
            depth -= 1
        pos += 1
    return src[brace_pos:pos]


def _cargo_check_uv_python() -> subprocess.CompletedProcess:
    """Run cargo check on the uv-python crate to verify it compiles."""
    cargo_bin = _ensure_rust_installed()
    env = {**subprocess.os.environ, "PATH": f"{cargo_bin}:{subprocess.os.environ.get('PATH', '')}"}
    return subprocess.run(
        ["cargo", "check", "--package", "uv-python"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env=env,
    )


# ---------------------------------------------------------------------------
# Gates — both files must exist
# ---------------------------------------------------------------------------

def _gate():
    d = Path(DISCOVERY)
    i = Path(INSTALL)
    assert d.exists() and d.stat().st_size > 0, "discovery.rs missing or empty"
    assert i.exists() and i.stat().st_size > 0, "installation.rs missing or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core refactoring checks (BEHAVIORAL)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_refactored_code_compiles():
    """The refactored uv-python crate compiles successfully."""
    _gate()
    result = _cargo_check_uv_python()
    assert result.returncode == 0, f"uv-python crate failed to compile: {result.stderr}"


# [pr_diff] fail_to_pass
def test_from_tuple_removed():
    """from_tuple conversion method removed from installation.rs."""
    _gate()
    src = _read_stripped(INSTALL)
    assert "from_tuple" not in src, "from_tuple still in installation.rs"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + structural
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_find_python_installations_still_public():
    """The public API find_python_installations must remain public."""
    _gate()
    src = _read_stripped(DISCOVERY)
    assert re.search(r"pub\s+fn\s+find_python_installations", src), (
        "find_python_installations is no longer public"
    )


# [static] pass_to_pass
def test_helper_signatures_return_python_installation():
    """Internal helpers return PythonInstallation, not (PythonSource, Interpreter) tuples."""
    _gate()
    src = _read_stripped(DISCOVERY)

    # Check that renamed helpers exist with correct return type
    helpers = [
        "python_installations",
        "python_installations_from_executables",
        "python_installations_with_executable_name",
    ]
    for name in helpers:
        pat = rf"fn\s+{name}\s*<[^>]*>\s*\([^{{]*?\)\s*->\s*impl\s+Iterator\s*<\s*Item\s*=\s*Result\s*<\s*PythonInstallation"
        assert re.search(pat, src, re.DOTALL), (
            f"{name} does not return Result<PythonInstallation>"
        )

    # No tuple returns remaining anywhere in file
    tuple_ret = re.findall(
        r"Result\s*<\s*\(\s*PythonSource\s*,\s*Interpreter\s*\)", src
    )
    assert len(tuple_ret) == 0, f"{len(tuple_ret)} tuple return types still present"


# [static] pass_to_pass
def test_helper_bodies_not_stubs():
    """Discovery helper functions have real implementations (>= 8 non-blank lines)."""
    _gate()
    src = _read_stripped(DISCOVERY)
    # Check renamed helpers; fall back to old names so this passes on base too
    helper_pairs = [
        ("python_installations", "python_interpreters"),
        ("python_installations_from_executables", "python_interpreters_from_executables"),
        ("python_installations_with_executable_name", "python_interpreters_with_executable_name"),
    ]
    for new_name, old_name in helper_pairs:
        body = _extract_fn_body(src, new_name) or _extract_fn_body(src, old_name)
        assert body is not None, f"Neither {new_name} nor {old_name} found"
        non_blank = [l for l in body.splitlines() if l.strip()]
        assert len(non_blank) >= 8, (
            f"Helper body too short: {len(non_blank)} non-blank lines (need >= 8)"
        )


# [static] pass_to_pass
def test_find_python_installations_calls_renamed_helpers():
    """The public find_python_installations function calls the renamed helper functions."""
    _gate()
    src = _read_stripped(DISCOVERY)
    body = _extract_fn_body(src, "find_python_installations")
    assert body is not None, "find_python_installations not found"

    assert re.search(r"python_installations\s*\(", body), (
        "find_python_installations does not call python_installations()"
    )
    assert re.search(r"python_installations_with_executable_name\s*\(", body), (
        "find_python_installations does not call python_installations_with_executable_name()"
    )


# [static] pass_to_pass
def test_python_installation_constructed_in_from_executables():
    """PythonInstallation struct is constructed inside python_installations_from_executables."""
    _gate()
    src = _read_stripped(DISCOVERY)
    body = _extract_fn_body(src, "python_installations_from_executables")
    assert body is not None, "python_installations_from_executables not found"
    assert re.search(r"PythonInstallation\s*\{", body), (
        "No PythonInstallation struct construction in python_installations_from_executables"
    )


# [static] pass_to_pass
def test_closures_use_field_access_not_tuple_destructuring():
    """Closures in discovery.rs use .source/.interpreter field access, not tuple destructuring."""
    _gate()
    src = _read_stripped(DISCOVERY)

    field_src = len(re.findall(r"\w+\.source\b", src))
    field_int = len(re.findall(r"\w+\.interpreter\b", src))
    assert field_src >= 5, f"Only {field_src} .source field accesses (need >= 5)"
    assert field_int >= 5, f"Only {field_int} .interpreter field accesses (need >= 5)"

    tuple_destr = re.findall(
        r"\|\s*\(?\s*_?source\s*,\s*_?interpreter\s*\)?\s*\|", src
    )
    assert len(tuple_destr) == 0, (
        f"{len(tuple_destr)} tuple destructuring patterns remain"
    )


# ---------------------------------------------------------------------------
# Repo CI/CD pass-to-pass tests — verify repo standards aren't broken
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — cargo fmt
def test_repo_cargo_fmt():
    """Repo code passes cargo fmt check (pass_to_pass)."""
    cargo_bin = _ensure_rust_installed()
    env = {**subprocess.os.environ, "PATH": f"{cargo_bin}:{subprocess.os.environ.get('PATH', '')}"}
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass — cargo check on uv-python crate
def test_repo_cargo_check_uv_python():
    """uv-python crate compiles without errors (pass_to_pass)."""
    cargo_bin = _ensure_rust_installed()
    env = {**subprocess.os.environ, "PATH": f"{cargo_bin}:{subprocess.os.environ.get('PATH', '')}"}
    r = subprocess.run(
        ["cargo", "check", "--package", "uv-python"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — cargo clippy on uv-python crate
def test_repo_cargo_clippy_uv_python():
    """uv-python crate passes clippy linting (pass_to_pass)."""
    cargo_bin = _ensure_rust_installed()
    env = {**subprocess.os.environ, "PATH": f"{cargo_bin}:{subprocess.os.environ.get('PATH', '')}"}
    r = subprocess.run(
        ["cargo", "clippy", "--package", "uv-python", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — cargo test on uv-python crate
def test_repo_cargo_test_uv_python():
    """uv-python crate unit tests pass (pass_to_pass)."""
    cargo_bin = _ensure_rust_installed()
    env = {**subprocess.os.environ, "PATH": f"{cargo_bin}:{subprocess.os.environ.get('PATH', '')}"}
    r = subprocess.run(
        ["cargo", "test", "--package", "uv-python"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"cargo test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Python syntax check for uv-python Python files
def test_repo_python_syntax_uv_python():
    """Python files in uv-python crate have valid syntax (pass_to_pass)."""
    python_files = [
        "crates/uv-python/fetch-download-metadata.py",
        "crates/uv-python/python/get_interpreter_info.py",
    ]
    for f in python_files:
        r = subprocess.run(
            ["python", "-m", "py_compile", f"{REPO}/{f}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"Python syntax error in {f}: {repr(r.stderr)}"


# [repo_tests] pass_to_pass — ruff check on uv-python Python files
def test_repo_ruff_check_uv_python():
    """Python files in uv-python crate pass ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # pip install can return 0 even if already installed
    r = subprocess.run(
        ["ruff", "check", "crates/uv-python/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — ruff format check on uv-python Python files
def test_repo_ruff_format_uv_python():
    """Python files in uv-python crate pass ruff format check (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "crates/uv-python/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 6d628da
def test_no_unwrap_panic_unreachable():
    """AVOID using panic!, unreachable!, .unwrap(), unsafe, clippy ignores (CLAUDE.md:7)."""
    _gate()
    src = _read_stripped(DISCOVERY)
    helpers = [
        "python_installations",
        "python_installations_from_executables",
        "python_installations_with_executable_name",
    ]
    for name in helpers:
        body = _extract_fn_body(src, name)
        if body is None:
            continue
        for bad in [".unwrap()", "panic!", "unreachable!", "unsafe "]:
            assert bad not in body, f"{name} contains {bad}"
        assert not re.search(r"#\[allow\(clippy::", body), (
            f"{name} contains clippy rule ignore (#[allow(clippy::...)])"
        )


# [agent_config] pass_to_pass — CLAUDE.md:10 @ 6d628da
def test_no_allow_attribute():
    """PREFER #[expect()] over #[allow()] for clippy disables (CLAUDE.md:10)."""
    _gate()
    src = _read_stripped(DISCOVERY)
    helpers = [
        "python_installations",
        "python_installations_from_executables",
        "python_installations_with_executable_name",
    ]
    for name in helpers:
        body = _extract_fn_body(src, name)
        if body is None:
            continue
        allows = re.findall(r"#\[allow\(", body)
        assert not allows, f"{name} uses #[allow()] instead of #[expect()] ({len(allows)} occurrences)"


# [agent_config] pass_to_pass — CLAUDE.md:17 @ 6d628da
def test_no_abbreviated_variable_names():
    """AVOID shortening variable names in closures (CLAUDE.md:17)."""
    _gate()
    src = _read_stripped(DISCOVERY)
    bad = re.findall(
        r"(?:filter_ok|map_ok)\s*\(\s*(?:move\s+)?\|\s*(?:mut\s+)?(inst|pi|i|p)\s*\|",
        src,
    )
    assert not bad, f"Abbreviated closure parameter names found: {bad}"
