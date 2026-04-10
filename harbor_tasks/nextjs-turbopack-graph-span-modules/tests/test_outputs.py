"""
Task: nextjs-turbopack-graph-span-modules
Repo: vercel/next.js @ 25646b928f900c12504b8a30ce5939207533aa54
PR:   #91697

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Rust codebase — cargo and rustup are installed on-demand in tests.
f2p tests use subprocess to execute Python validation scripts that
parse Rust source files and verify the structural changes required by the PR.
"""

import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/next.js"
APP_FILE = f"{REPO}/crates/next-api/src/app.rs"
PROJECT_FILE = f"{REPO}/crates/next-api/src/project.rs"
MOD_FILE = f"{REPO}/turbopack/crates/turbopack-core/src/module_graph/mod.rs"


def _ensure_rustup():
    """Ensure rustup and the nightly toolchain are installed."""
    cargo_check = subprocess.run(
        ["which", "cargo"], capture_output=True, text=True, timeout=5
    )
    if cargo_check.returncode == 0:
        return  # cargo already available

    # Install rustup - the toolchain will be installed from rust-toolchain.toml
    install = subprocess.run(
        ["bash", "-c",
         "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain none"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if install.returncode != 0:
        pytest.skip(f"Failed to install rustup: {install.stderr}")


def _run_cargo(*args, cwd=REPO, timeout=300):
    """Run a cargo command with rustup available."""
    _ensure_rustup()
    # Use cargo from rustup installation
    cargo_path = Path.home() / ".cargo" / "bin" / "cargo"
    env_setup = "source $HOME/.cargo/env 2>/dev/null || true"
    cmd = f"{env_setup}; {cargo_path} {' '.join(args)}"
    return subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


def _run_validator(name: str, code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a Python validation script to /tmp and execute it via subprocess."""
    script = Path(f"/tmp/_validator_{name}.py")
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# pass_to_pass — anti-stub gate
# ---------------------------------------------------------------------------


def test_antistub_files_have_substantial_content():
    """All three modified files have substantial Rust code (not replaced with stubs)."""
    for path, name, min_lines in [
        (APP_FILE, "app.rs", 500),
        (PROJECT_FILE, "project.rs", 500),
        (MOD_FILE, "mod.rs", 200),
    ]:
        lines = Path(path).read_text().splitlines()
        assert len(lines) >= min_lines, f"{name} has {len(lines)} lines (need >= {min_lines})"
        fn_count = sum(1 for line in lines if "fn " in line)
        assert fn_count >= 5, f"{name} has {fn_count} fn defs (need >= 5)"


# ---------------------------------------------------------------------------
# pass_to_pass — repo CI/CD checks
# ---------------------------------------------------------------------------


def test_repo_rustfmt_check():
    """Repo Rust code passes rustfmt check (pass_to_pass). CI: cargo fmt --all -- --check"""
    r = _run_cargo("fmt", "--all", "--", "--check", timeout=120)
    assert r.returncode == 0, f"rustfmt check failed: {r.stderr[-500:]}"


def test_repo_cargo_check_turbopack_core():
    """Repo turbopack-core crate passes cargo check (pass_to_pass). CI: cargo check --package turbopack-core"""
    r = _run_cargo("check", "--package", "turbopack-core", timeout=300)
    assert r.returncode == 0, f"cargo check failed: {r.stderr[-500:]}"


def test_repo_cargo_check_next_api():
    """Repo next-api crate passes cargo check (pass_to_pass). CI: cargo check --package next-api"""
    r = _run_cargo("check", "--package", "next-api", timeout=300)
    assert r.returncode == 0, f"cargo check failed: {r.stderr[-500:]}"


def test_repo_cargo_check_next_core():
    """Repo next-core crate passes cargo check (pass_to_pass). CI: cargo check --package next-core"""
    r = _run_cargo("check", "--package", "next-core", timeout=300)
    assert r.returncode == 0, f"cargo check failed: {r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# fail_to_pass — subprocess-executed validation
# ---------------------------------------------------------------------------


def test_module_count_method_in_single_module_graph():
    """impl SingleModuleGraph exposes module count via turbo_tasks::function."""
    r = _run_validator("mod_count", _MOD_COUNT_VALIDATOR)
    assert r.returncode == 0, f"Validation failed: {r.stderr}"
    assert "PASS" in r.stdout


_MOD_COUNT_VALIDATOR = """import sys
from pathlib import Path

lines = Path("/workspace/next.js/turbopack/crates/turbopack-core/src/module_graph/mod.rs").read_text().splitlines()

count_fn_names = ["module_count", "get_module_count", "num_modules",
                  "modules_count", "count_modules", "module_len"]

found = False
for i, line in enumerate(lines):
    fn_name = None
    for name in count_fn_names:
        if "fn " + name in line:
            fn_name = name
            break
    if fn_name is None:
        continue

    depth = 0
    in_impl = False
    for j in range(i, -1, -1):
        depth += lines[j].count("}") - lines[j].count("{")
        if "impl SingleModuleGraph" in lines[j] and depth <= 0:
            in_impl = True
            break
    if not in_impl:
        continue

    preceding = lines[max(0, i - 5) : i + 1]
    if not any("turbo_tasks" in l and "function" in l for l in preceding):
        sys.exit(fn_name + " missing #[turbo_tasks::function] annotation")

    body = lines[i : i + 15]
    if not any("self" in l for l in body):
        sys.exit(fn_name + " body does not reference self")

    body_text = " ".join(body)
    if not any(t in body_text for t in ["u64", "usize", "i64", "u32"]):
        sys.exit(fn_name + " body does not involve numeric type (u64/usize/etc.)")

    meaningful = [l.strip() for l in lines[i + 1 : i + 15]
                  if l.strip() and l.strip() not in ("{", "}")]
    if len(meaningful) < 1:
        sys.exit(fn_name + " body is empty - likely a stub")

    found = True
    break

if not found:
    sys.exit("No module count method found in SingleModuleGraph impl")
print("PASS")
"""


def test_app_rs_records_module_count_in_span():
    """app.rs has a tracing span with modules field and records module count."""
    r = _run_validator("app_span", _APP_SPAN_VALIDATOR)
    assert r.returncode == 0, f"Validation failed: {r.stderr}"
    assert "PASS" in r.stdout


_APP_SPAN_VALIDATOR = """import sys
from pathlib import Path

lines = Path("/workspace/next.js/crates/next-api/src/app.rs").read_text().splitlines()

span_keywords = ["info_span!", "span!", "debug_span!", "trace_span!"]
has_span_with_modules = False
for i, line in enumerate(lines):
    has_span = any(kw in line for kw in span_keywords)
    has_modules_field = "modules" in line and ("=" in line or "Empty" in line)
    if has_span and has_modules_field:
        has_span_with_modules = True
        break

if not has_span_with_modules:
    sys.exit("No tracing span with modules field found in app.rs")

has_record = False
for line in lines:
    if ".record(" in line and "modules" in line:
        has_record = True
        break
if not has_record:
    sys.exit("No span.record(modules, ...) found in app.rs")

count_fn_names = ["module_count", "get_module_count", "num_modules",
                  "modules_count", "count_modules", "module_len"]
has_count_call = False
for line in lines:
    for name in count_fn_names:
        if name + "(" in line:
            has_count_call = True
            break
    if has_count_call:
        break
if not has_count_call:
    sys.exit("No module count call found in app.rs")

print("PASS")
"""


def test_project_rs_records_module_count_in_span():
    """project.rs has a tracing span with modules for whole-app graph path."""
    r = _run_validator("project_span", _PROJECT_SPAN_VALIDATOR)
    assert r.returncode == 0, f"Validation failed: {r.stderr}"
    assert "PASS" in r.stdout


_PROJECT_SPAN_VALIDATOR = """import sys
from pathlib import Path

lines = Path("/workspace/next.js/crates/next-api/src/project.rs").read_text().splitlines()

span_keywords = ["info_span!", "span!", "debug_span!", "trace_span!"]
has_span_with_modules = False
for i, line in enumerate(lines):
    has_span = any(kw in line for kw in span_keywords)
    has_modules_field = "modules" in line and ("=" in line or "Empty" in line)
    if has_span and has_modules_field:
        has_span_with_modules = True
        break

if not has_span_with_modules:
    sys.exit("No tracing span with modules field found in project.rs")

record_lines = []
for i, line in enumerate(lines):
    if ".record(" in line and "modules" in line:
        record_lines.append(i)
if not record_lines:
    sys.exit("No span.record(modules, ...) found in project.rs")

count_fn_names = ["module_count", "get_module_count", "num_modules",
                  "modules_count", "count_modules", "module_len"]
count_lines = []
for i, line in enumerate(lines):
    for name in count_fn_names:
        if name + "(" in line:
            count_lines.append(i)
            break
if not count_lines:
    sys.exit("No module count call found in project.rs")

whole_app_lines = [i for i, line in enumerate(lines)
                   if "whole_app" in line or "module_graph_operation" in line]

def near(a_lines, b_lines, distance):
    return any(abs(a - b) <= distance for a in a_lines for b in b_lines)

if not near(record_lines + count_lines, whole_app_lines, 80):
    sys.exit("modules span/record not scoped to whole-app graph code in project.rs")

print("PASS")
"""


def test_performance_guard_before_module_count():
    """Both app.rs and project.rs guard module count computation on span activity."""
    r = _run_validator("perf_guard", _PERF_GUARD_VALIDATOR)
    assert r.returncode == 0, f"Validation failed: {r.stderr}"
    assert "PASS" in r.stdout


_PERF_GUARD_VALIDATOR = """import sys
from pathlib import Path

count_fn_names = ["module_count", "get_module_count", "num_modules",
                  "modules_count", "count_modules", "module_len"]

for filepath, name in [
    ("/workspace/next.js/crates/next-api/src/app.rs", "app.rs"),
    ("/workspace/next.js/crates/next-api/src/project.rs", "project.rs"),
]:
    lines = Path(filepath).read_text().splitlines()

    guard_lines = []
    for i, line in enumerate(lines):
        if ("is_disabled" in line or "is_enabled" in line or
                "has_field" in line):
            guard_lines.append(i)
    if not guard_lines:
        sys.exit(name + " missing performance guard")

    relevant_lines = []
    for i, line in enumerate(lines):
        for fn_name in count_fn_names:
            if fn_name + "(" in line:
                relevant_lines.append(i)
                break
        if ".record(" in line and "modules" in line:
            relevant_lines.append(i)
    if not relevant_lines:
        sys.exit(name + " count call lines not found")

    near = any(abs(g - r) <= 40 for g in guard_lines for r in relevant_lines)
    if not near:
        sys.exit(name + " guard not near module count computation")

print("PASS")
"""


# ---------------------------------------------------------------------------
# pass_to_pass — existing functions/types preserved
# ---------------------------------------------------------------------------


def test_existing_functions_and_types_preserved():
    """Enhancement must not remove existing functions or types."""
    proj_raw = Path(PROJECT_FILE).read_text()
    for name in ["whole_app_module_graphs", "whole_app_module_graph_operation"]:
        assert ("fn " + name) in proj_raw, f"{name} function missing from project.rs"
    assert "BaseAndFullModuleGraph" in proj_raw, "BaseAndFullModuleGraph type missing"

    mod_raw = Path(MOD_FILE).read_text()
    assert "SingleModuleGraph" in mod_raw, "SingleModuleGraph missing from mod.rs"
    assert "number_of_modules" in mod_raw, "number_of_modules field missing from mod.rs"
