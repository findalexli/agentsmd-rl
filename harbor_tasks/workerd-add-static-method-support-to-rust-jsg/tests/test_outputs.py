"""
Task: workerd-add-static-method-support-to-rust-jsg
Repo: cloudflare/workerd @ d7dc27c438f7ea1fd5eb28a0258d5dbae265a99d
PR:   6279

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/workerd"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def _ensure_rustfmt():
    """Ensure rustfmt is installed (needed in Docker where each run is fresh)."""
    subprocess.run(
        ["rustup", "component", "add", "rustfmt"],
        capture_output=True, timeout=120,
    )


# [static] pass_to_pass
def test_rust_syntax_valid():
    """Modified .rs files must parse without rustfmt errors."""
    _ensure_rustfmt()
    rs_files = [
        Path(REPO) / "src/rust/jsg-macros/lib.rs",
        Path(REPO) / "src/rust/jsg/v8.rs",
    ]
    for f in rs_files:
        assert f.exists(), f"File not found: {f}"
        r = subprocess.run(
            ["rustfmt", "--check", "--edition", "2021", str(f)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        # rustfmt --check exits 1 if formatting differs; we only care about parse errors (exit 2+)
        assert r.returncode != 2, f"rustfmt parse error in {f.name}:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass gates (repo_tests) — CI checks that must pass before and after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - rustfmt config exists and is valid
def test_rustfmt_config_valid():
    """rustfmt.toml config file exists and is valid (pass_to_pass)."""
    config_path = Path(REPO) / "src/rust/rustfmt.toml"
    assert config_path.exists(), "rustfmt.toml not found"
    content = config_path.read_text()
    assert "group_imports" in content, "rustfmt.toml missing group_imports setting"
    assert "imports_granularity" in content, "rustfmt.toml missing imports_granularity setting"


# [repo_tests] pass_to_pass - jsg-macros lib.rs has valid syntax
def test_jsg_macros_syntax():
    """jsg-macros lib.rs can be parsed by rustfmt without parse errors (pass_to_pass)."""
    _ensure_rustfmt()
    lib_rs = Path(REPO) / "src/rust/jsg-macros/lib.rs"
    assert lib_rs.exists(), "lib.rs not found"
    r = subprocess.run(
        ["rustfmt", "--check", "--edition", "2021", str(lib_rs)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # Exit code 2 indicates syntax/parse errors
    assert r.returncode != 2, f"jsg-macros/lib.rs has syntax errors:\n{r.stderr}"


# [repo_tests] pass_to_pass - jsg v8.rs has valid syntax
def test_jsg_v8_syntax():
    """jsg v8.rs can be parsed by rustfmt without parse errors (pass_to_pass)."""
    _ensure_rustfmt()
    v8_rs = Path(REPO) / "src/rust/jsg/v8.rs"
    assert v8_rs.exists(), "v8.rs not found"
    r = subprocess.run(
        ["rustfmt", "--check", "--edition", "2021", str(v8_rs)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode != 2, f"jsg/v8.rs has syntax errors:\n{r.stderr}"


# [repo_tests] pass_to_pass - jsg ffi.c++ has valid syntax
def test_jsg_ffi_cpp_syntax():
    """jsg ffi.c++ exists and has valid C++ syntax (pass_to_pass)."""
    ffi_cpp = Path(REPO) / "src/rust/jsg/ffi.c++"
    assert ffi_cpp.exists(), "ffi.c++ not found"
    content = ffi_cpp.read_text()
    # Check for basic C++ syntax indicators
    assert "#include" in content, "ffi.c++ missing includes"
    assert "namespace" in content or "::workerd::" in content, "ffi.c++ missing namespace patterns"


# [repo_tests] pass_to_pass - jsg ffi.h has valid syntax
def test_jsg_ffi_h_syntax():
    """jsg ffi.h exists and has valid C++ header syntax (pass_to_pass)."""
    ffi_h = Path(REPO) / "src/rust/jsg/ffi.h"
    assert ffi_h.exists(), "ffi.h not found"
    content = ffi_h.read_text()
    assert "#pragma once" in content or "#ifndef" in content, "ffi.h missing header guard"
    assert "namespace" in content, "ffi.h missing namespace"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: proc macro static detection
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_jsg_method_static_detection():
    """jsg_method macro must detect receiver to distinguish static vs instance methods."""
    lib_rs = (Path(REPO) / "src/rust/jsg-macros/lib.rs").read_text()

    # Must track whether method has a self receiver (new variable introduced by the PR)
    assert "has_self" in lib_rs, \
        "lib.rs must track whether method has a self receiver"

    # Must branch on has_self to generate different invocation code
    assert "if has_self" in lib_rs, \
        "lib.rs must branch on has_self to generate conditional code"


# [pr_diff] fail_to_pass
def test_static_member_variant():
    """generate_resource_impl must emit Member::StaticMethod for receiver-less methods."""
    lib_rs = (Path(REPO) / "src/rust/jsg-macros/lib.rs").read_text()

    assert "Member::StaticMethod" in lib_rs, \
        "lib.rs must generate Member::StaticMethod for methods without a receiver"

    # Ensure both Method and StaticMethod are generated conditionally
    assert "Member::Method" in lib_rs, \
        "lib.rs must still generate Member::Method for instance methods"

    # The has_self check should appear in generate_resource_impl (not just jsg_method)
    # by checking that FnArg::Receiver appears at least twice (once per function)
    count = lib_rs.count("FnArg::Receiver")
    assert count >= 2, \
        f"FnArg::Receiver should appear in both jsg_method and generate_resource_impl, found {count} times"


# [pr_diff] fail_to_pass
def test_function_type_and_ffi():
    """v8.rs must define Function type and ffi.h must declare function_template_get_function."""
    v8_rs = (Path(REPO) / "src/rust/jsg/v8.rs").read_text()

    # Function type must be defined (distinct from FunctionTemplate)
    assert "pub struct Function;" in v8_rs, \
        "v8.rs must define a public Function struct (separate from FunctionTemplate)"

    # as_local_function method on Global<FunctionTemplate>
    assert "as_local_function" in v8_rs, \
        "v8.rs must implement as_local_function on Global<FunctionTemplate>"

    # FFI declaration for function_template_get_function
    assert "function_template_get_function" in v8_rs, \
        "v8.rs must declare function_template_get_function in the ffi module"

    # From<Local<Function>> impl for converting to Value (not FunctionTemplate)
    assert "From<Local<'a, Function>>" in v8_rs, \
        "v8.rs must implement From<Local<Function>> for Local<Value>"

    # C++ FFI header must also declare it
    ffi_h = (Path(REPO) / "src/rust/jsg/ffi.h").read_text()
    assert "function_template_get_function" in ffi_h, \
        "ffi.h must declare function_template_get_function"


# [pr_diff] fail_to_pass
def test_ffi_cpp_implements_get_function():
    """ffi.c++ must implement function_template_get_function to extract constructor Function."""
    ffi_cpp = (Path(REPO) / "src/rust/jsg/ffi.c++").read_text()

    assert "function_template_get_function" in ffi_cpp, \
        "ffi.c++ must implement function_template_get_function"
    assert "GetFunction" in ffi_cpp, \
        "ffi.c++ must call V8's GetFunction to extract the constructor"


# ---------------------------------------------------------------------------
# Config/documentation update tests (agentmd-edit, fail_to_pass)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:9 @ d7dc27c4
def test_agents_md_documents_static_methods():
    """src/rust/AGENTS.md must document that methods without &self become static methods."""
    agents_md = (Path(REPO) / "src/rust/AGENTS.md").read_text()

    # Must mention static methods in the JSG resources convention
    assert "static" in agents_md.lower(), \
        "AGENTS.md should mention static methods"
    assert "instance" in agents_md.lower() or "&self" in agents_md or "receiver" in agents_md.lower(), \
        "AGENTS.md should explain how instance vs static is determined (via receiver/&self)"


# [pr_diff] fail_to_pass
def test_readme_documents_static_instance():
    """jsg-macros README must document the static vs instance method distinction."""
    readme = (Path(REPO) / "src/rust/jsg-macros/README.md").read_text()

    # Must explain the automatic detection
    assert "static" in readme.lower() and "instance" in readme.lower(), \
        "README should explain both static and instance method concepts"
    assert "receiver" in readme.lower() or "&self" in readme, \
        "README should explain that receiver presence determines method type"
    assert "prototype" in readme.lower() or "constructor" in readme.lower(), \
        "README should mention where methods are placed (prototype vs constructor)"


# [pr_diff] fail_to_pass
def test_review_checklist_instance_static():
    """docs/reference/rust-review-checklist.md must document instance/static method behavior."""
    checklist = (Path(REPO) / "docs/reference/rust-review-checklist.md").read_text()

    # The jsg_method section must mention instance/static distinction
    assert "instance" in checklist.lower() or "prototype" in checklist.lower(), \
        "Review checklist should mention instance methods / prototype"
    assert "static" in checklist.lower() or "constructor" in checklist.lower(), \
        "Review checklist should mention static methods / constructor"
