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


def _ensure_rustfmt():
    """Ensure rustfmt is installed (needed in Docker where each run is fresh)."""
    subprocess.run(
        ["rustup", "component", "add", "rustfmt"],
        capture_output=True, timeout=120,
    )


def test_rustfmt_jsg_macros_syntax():
    """jsg-macros lib.rs parses without syntax errors (pass_to_pass)."""
    _ensure_rustfmt()
    lib_rs = Path(REPO) / "src/rust/jsg-macros/lib.rs"
    r = subprocess.run(
        ["rustfmt", "--check", "--edition", "2021", str(lib_rs)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # Exit code 2 indicates syntax/parse errors (format differences = exit 1, which is ok)
    assert r.returncode != 2, "jsg-macros/lib.rs has syntax errors: " + r.stderr


def test_rustfmt_jsg_v8_syntax():
    """jsg v8.rs parses without syntax errors (pass_to_pass)."""
    _ensure_rustfmt()
    v8_rs = Path(REPO) / "src/rust/jsg/v8.rs"
    r = subprocess.run(
        ["rustfmt", "--check", "--edition", "2021", str(v8_rs)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode != 2, "jsg/v8.rs has syntax errors: " + r.stderr


def test_rustfmt_config_valid():
    """rustfmt.toml config file exists and is valid (pass_to_pass)."""
    config_path = Path(REPO) / "src/rust/rustfmt.toml"
    assert config_path.exists(), "rustfmt.toml not found"
    content = config_path.read_text()
    assert "group_imports" in content, "rustfmt.toml missing group_imports setting"
    assert "imports_granularity" in content, "rustfmt.toml missing imports_granularity setting"


def test_jsg_ffi_cpp_exists():
    """jsg ffi.c++ exists and has valid C++ structure (pass_to_pass)."""
    ffi_cpp = Path(REPO) / "src/rust/jsg/ffi.c++"
    assert ffi_cpp.exists(), "ffi.c++ not found"
    content = ffi_cpp.read_text()
    assert "#include" in content, "ffi.c++ missing includes"
    assert "namespace" in content or "::workerd::" in content, "ffi.c++ missing namespace patterns"


def test_jsg_ffi_h_exists():
    """jsg ffi.h exists and has valid C++ header structure (pass_to_pass)."""
    ffi_h = Path(REPO) / "src/rust/jsg/ffi.h"
    assert ffi_h.exists(), "ffi.h not found"
    content = ffi_h.read_text()
    assert "#pragma once" in content or "#ifndef" in content, "ffi.h missing header guard"
    assert "namespace" in content, "ffi.h missing namespace"


def test_jsg_method_static_detection():
    """jsg_method macro must detect receiver to distinguish static vs instance methods."""
    lib_rs = (Path(REPO) / "src/rust/jsg-macros/lib.rs").read_text()
    assert "has_self" in lib_rs, "lib.rs must track whether method has a self receiver"
    assert "if has_self" in lib_rs, "lib.rs must branch on has_self to generate conditional code"


def test_static_member_variant():
    """generate_resource_impl must emit Member::StaticMethod for receiver-less methods."""
    lib_rs = (Path(REPO) / "src/rust/jsg-macros/lib.rs").read_text()
    assert "Member::StaticMethod" in lib_rs, "lib.rs must generate Member::StaticMethod for methods without a receiver"
    assert "Member::Method" in lib_rs, "lib.rs must still generate Member::Method for instance methods"
    count = lib_rs.count("FnArg::Receiver")
    assert count >= 2, "FnArg::Receiver should appear in both jsg_method and generate_resource_impl, found " + str(count) + " times"


def test_function_type_and_ffi():
    """v8.rs must define Function type and ffi.h must declare function_template_get_function."""
    v8_rs = (Path(REPO) / "src/rust/jsg/v8.rs").read_text()
    assert "pub struct Function;" in v8_rs, "v8.rs must define a public Function struct"
    assert "as_local_function" in v8_rs, "v8.rs must implement as_local_function on Global<FunctionTemplate>"
    assert "function_template_get_function" in v8_rs, "v8.rs must declare function_template_get_function"
    assert "From<Local<'a, Function>>" in v8_rs, "v8.rs must implement From<Local<Function>> for Local<Value>"
    ffi_h = (Path(REPO) / "src/rust/jsg/ffi.h").read_text()
    assert "function_template_get_function" in ffi_h, "ffi.h must declare function_template_get_function"


def test_ffi_cpp_implements_get_function():
    """ffi.c++ must implement function_template_get_function to extract constructor Function."""
    ffi_cpp = (Path(REPO) / "src/rust/jsg/ffi.c++").read_text()
    assert "function_template_get_function" in ffi_cpp, "ffi.c++ must implement function_template_get_function"
    assert "GetFunction" in ffi_cpp, "ffi.c++ must call V8's GetFunction to extract the constructor"


def test_agents_md_documents_static_methods():
    """src/rust/AGENTS.md must document that methods without &self become static methods."""
    agents_md = (Path(REPO) / "src/rust/AGENTS.md").read_text()
    assert "static" in agents_md.lower(), "AGENTS.md should mention static methods"
    assert "instance" in agents_md.lower() or "&self" in agents_md or "receiver" in agents_md.lower(), "AGENTS.md should explain how instance vs static is determined"


def test_readme_documents_static_instance():
    """jsg-macros README must document the static vs instance method distinction."""
    readme = (Path(REPO) / "src/rust/jsg-macros/README.md").read_text()
    assert "static" in readme.lower() and "instance" in readme.lower(), "README should explain both concepts"
    assert "receiver" in readme.lower() or "&self" in readme, "README should explain receiver-based detection"
    assert "prototype" in readme.lower() or "constructor" in readme.lower(), "README should mention placement"


def test_review_checklist_instance_static():
    """docs/reference/rust-review-checklist.md must document instance/static method behavior."""
    checklist = (Path(REPO) / "docs/reference/rust-review-checklist.md").read_text()
    assert "instance" in checklist.lower() or "prototype" in checklist.lower(), "Checklist should mention instance methods"
    assert "static" in checklist.lower() or "constructor" in checklist.lower(), "Checklist should mention static methods"
