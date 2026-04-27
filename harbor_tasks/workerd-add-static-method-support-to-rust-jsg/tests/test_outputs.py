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


# ── pass_to_pass ──────────────────────────────────────────────────────────


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


# ── fail_to_pass ──────────────────────────────────────────────────────────


def test_jsg_method_static_detection():
    """jsg_method macro must detect receiver to distinguish static vs instance methods."""
    r = subprocess.run(
        ["python3", "-c", """
import re

lib_rs = open('/workspace/workerd/src/rust/jsg-macros/lib.rs').read()

# The syn crate's FnArg::Receiver variant is the standard API for detecting
# &self/&mut self.  It must appear at least twice: once in jsg_method (to
# branch code generation for instance vs static invocation) and once in
# generate_resource_impl (to emit different Member:: variants).
count = lib_rs.count('FnArg::Receiver')
assert count >= 2, (
    f"FnArg::Receiver must appear at least twice "
    f"(in jsg_method and generate_resource_impl), found {count}"
)

# Verify it appears specifically inside the jsg_method function body.
jsg_method_start = lib_rs.find('fn jsg_method(')
assert jsg_method_start != -1, "jsg_method function not found"
jsg_resource_start = lib_rs.find('fn jsg_resource(', jsg_method_start + 1)
jsg_method_body = lib_rs[jsg_method_start:jsg_resource_start]

# jsg_method must use FnArg::Receiver beyond just filtering params - it must
# actively detect the receiver to decide how to generate the callback body.
receiver_uses = jsg_method_body.count('FnArg::Receiver')
assert receiver_uses >= 2, (
    f"jsg_method must use FnArg::Receiver for both param filtering and "
    f"receiver detection, found {receiver_uses} use(s)"
)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_static_member_variant():
    """generate_resource_impl must emit different Member:: variants for instance vs static."""
    r = subprocess.run(
        ["python3", "-c", """
import re

lib_rs = open('/workspace/workerd/src/rust/jsg-macros/lib.rs').read()

# Extract the generate_resource_impl function body.
gen_start = lib_rs.find('fn generate_resource_impl(')
assert gen_start != -1, "generate_resource_impl function not found"
next_fn = lib_rs.find('\\nfn ', gen_start + 1)
gen_body = lib_rs[gen_start:next_fn] if next_fn != -1 else lib_rs[gen_start:]

# Must have at least 2 different Member:: variants - one for instance methods
# and one for static methods.
member_variants = set(re.findall(r'Member::\\w+', gen_body))
assert len(member_variants) >= 2, (
    f"generate_resource_impl needs at least 2 distinct Member:: variants "
    f"(instance and static), found: {member_variants}"
)

# Must use FnArg::Receiver to decide which variant to emit.
assert 'FnArg::Receiver' in gen_body, (
    "generate_resource_impl must use FnArg::Receiver to detect receiver per method"
)

# Must have conditional logic (if/match) to branch between variants.
assert re.search(r'if\\s+\\w+', gen_body), (
    "generate_resource_impl must branch to select the correct Member variant"
)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_function_type_and_ffi():
    """v8.rs must define Function type and FFI bridge for FunctionTemplate->Function conversion."""
    r = subprocess.run(
        ["python3", "-c", """
import re

v8_rs = open('/workspace/workerd/src/rust/jsg/v8.rs').read()

# v8.rs must define a public struct for V8's Function type (mirrors v8::Function).
assert re.search(r'pub\\s+struct\\s+Function\\b', v8_rs), (
    "v8.rs must define a public Function struct (mirrors V8's v8::Function)"
)

# Must have an impl block on Global<FunctionTemplate> to provide a method
# for retrieving the constructor Function.
assert re.search(r'impl\\s+Global<FunctionTemplate>', v8_rs), (
    "v8.rs must have impl Global<FunctionTemplate> for Function access"
)

# Must implement From<Local<Function>> to allow converting to Local<Value>.
assert re.search(r"From<Local<'\\w+,\\s*Function>>", v8_rs), (
    "v8.rs must implement From<Local<Function>> for Local<Value>"
)

# ffi.h must declare a new FFI function that takes a Global reference and
# returns a Local (for converting FunctionTemplate -> Function).
# Baseline already has global_to_local and wrap_resource matching this pattern.
ffi_h = open('/workspace/workerd/src/rust/jsg/ffi.h').read()
fn_decls = re.findall(r'Local\\s+(\\w+)\\s*\\([^)]*Global[^)]*\\)', ffi_h)
new_fns = [f for f in fn_decls if f not in ('global_to_local', 'wrap_resource')]
assert len(new_fns) >= 1, (
    f"ffi.h must declare a new function (Local return, Global param) "
    f"for FunctionTemplate->Function conversion (found only: {fn_decls})"
)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_ffi_cpp_implements_get_function():
    """ffi.c++ must implement FunctionTemplate->Function conversion using V8's GetFunction API."""
    r = subprocess.run(
        ["python3", "-c", """
ffi_cpp = open('/workspace/workerd/src/rust/jsg/ffi.c++').read()

# The C++ implementation must call V8's GetFunction API.
# GetFunction is V8's actual API on v8::FunctionTemplate to extract the
# constructor v8::Function - any correct implementation must call it.
assert 'GetFunction' in ffi_cpp, (
    "ffi.c++ must call V8's GetFunction API to extract constructor Function "
    "from FunctionTemplate"
)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_agents_md_documents_static_methods():
    """src/rust/AGENTS.md must document that methods without &self become static methods."""
    agents_md = (Path(REPO) / "src/rust/AGENTS.md").read_text()
    assert "static" in agents_md.lower(), "AGENTS.md should mention static methods"
    assert (
        "instance" in agents_md.lower()
        or "&self" in agents_md
        or "receiver" in agents_md.lower()
    ), "AGENTS.md should explain how instance vs static is determined"


def test_readme_documents_static_instance():
    """jsg-macros README must document the static vs instance method distinction."""
    readme = (Path(REPO) / "src/rust/jsg-macros/README.md").read_text()
    assert "static" in readme.lower() and "instance" in readme.lower(), (
        "README should explain both static and instance concepts"
    )
    assert "receiver" in readme.lower() or "&self" in readme, (
        "README should explain receiver-based detection"
    )
    assert "prototype" in readme.lower() or "constructor" in readme.lower(), (
        "README should mention where methods are placed (prototype/constructor)"
    )


def test_review_checklist_instance_static():
    """docs/reference/rust-review-checklist.md must document instance/static method behavior."""
    checklist = (Path(REPO) / "docs/reference/rust-review-checklist.md").read_text()
    assert "instance" in checklist.lower() or "prototype" in checklist.lower(), (
        "Checklist should mention instance methods or prototype"
    )
    assert "static" in checklist.lower() or "constructor" in checklist.lower(), (
        "Checklist should mention static methods or constructor"
    )
