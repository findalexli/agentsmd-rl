"""
Task: nextjs-mcp-compilation-issues-whole-graph
Repo: vercel/next.js @ cf328d3afe3660e71496fed499376921c75eb3e3
PR:   92473

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
PROJECT_RS = f"{REPO}/crates/next-api/src/project.rs"
BINDINGS_RS = f"{REPO}/crates/next-napi-bindings/src/next_api/project.rs"


def _read(path: str) -> str:
    return Path(path).read_text()


def _extract_function_body(src: str, fn_name: str) -> str:
    """Extract a Rust function body by matching from fn <name> to its closing brace."""
    pattern = rf"(?:pub\s+)?(?:async\s+)?fn\s+{fn_name}\s*[\(<]"
    m = re.search(pattern, src)
    assert m, f"Function {fn_name} not found"
    start = m.start()
    brace_start = src.index("{", m.end())
    depth = 1
    i = brace_start + 1
    while depth > 0 and i < len(src):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    return src[start:i]


def _find_impl_project_methods(src: str) -> list[str]:
    """Find all method names defined inside impl Project blocks."""
    methods = []
    for m in re.finditer(r"impl\s+Project\s*\{", src):
        start = m.end()
        depth = 1
        i = start
        while depth > 0 and i < len(src):
            if src[i] == "{":
                depth += 1
            elif src[i] == "}":
                depth -= 1
            i += 1
        block = src[m.start():i]
        methods.extend(
            mm.group(1) for mm in re.finditer(r"fn\s+(\w+)\s*[\(<]", block)
        )
    return methods


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — files exist with real code
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_exist_and_not_stub():
    """Modified Rust files exist with real code (anti-stub gate)."""
    for path, min_lines, patterns in [
        (PROJECT_RS, 500, [r"impl Project", r"whole_app_module_graph"]),
        (BINDINGS_RS, 500, [r"get_all_compilation_issues", r"ProjectContainer"]),
    ]:
        content = _read(path)
        lines = content.count("\n") + 1
        assert lines >= min_lines, f"{path} has {lines} lines (min {min_lines})"
        for pat in patterns:
            assert re.search(pat, content), f"{path} missing pattern: {pat}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_non_dropping_whole_app_method():
    """Project has a method that computes whole-app graph WITHOUT dropping issues."""
    src = _read(PROJECT_RS)
    methods = _find_impl_project_methods(src)

    # Find a method that:
    # 1. Contains "whole_app" in the name (variant of the whole-app graph method)
    # 2. Calls whole_app_module_graph_operation
    # 3. Does NOT call drop_issues
    # 4. Is distinct from the existing whole_app_module_graphs (which drops issues)
    whole_app_methods = [m for m in methods if "whole_app" in m and m != "whole_app_module_graphs"]
    assert whole_app_methods, (
        "Need a new whole-app module graph method on Project (distinct from whole_app_module_graphs)"
    )

    found_valid = False
    for method_name in whole_app_methods:
        body = _extract_function_body(src, method_name)
        has_graph_op = "whole_app_module_graph_operation" in body
        has_connect = ".connect()" in body
        no_drop = "drop_issues" not in body
        if has_graph_op and has_connect and no_drop:
            found_valid = True
            break

    assert found_valid, (
        "New whole-app method must call whole_app_module_graph_operation, "
        ".connect(), and must NOT call drop_issues"
    )


# [pr_diff] fail_to_pass
def test_scale_down_logic_deduplicated():
    """Node pool scale-down logic is extracted from whole_app_module_graphs (not inlined)."""
    src = _read(PROJECT_RS)
    orig_body = _extract_function_body(src, r"whole_app_module_graphs\b")

    # The original method should NOT have inline node_backend.scale_down()/scale_zero()
    # It should delegate to a helper or call a shared function.
    has_inline_scale = (
        "node_backend" in orig_body
        and ("scale_down" in orig_body or "scale_zero" in orig_body)
        and "execution_context" in orig_body
    )
    assert not has_inline_scale, (
        "whole_app_module_graphs should not inline scale-down logic — extract to shared helper"
    )

    # A free function or shared helper containing the scale-down logic must exist
    # Look for any free function (outside impl blocks) with scale_down + scale_zero
    # Find end of all impl Project blocks
    impl_regions = []
    for m in re.finditer(r"impl\s+Project\s*\{", src):
        start = m.start()
        depth = 1
        i = m.end()
        while depth > 0 and i < len(src):
            if src[i] == "{":
                depth += 1
            elif src[i] == "}":
                depth -= 1
            i += 1
        impl_regions.append((start, i))

    # Find free async functions that contain scale_down/scale_zero
    free_fns_with_scale = []
    for m in re.finditer(r"(?:pub\s+)?async\s+fn\s+(\w+)\s*\(", src):
        fn_start = m.start()
        in_impl = any(start <= fn_start < end for start, end in impl_regions)
        if not in_impl:
            fn_name = m.group(1)
            try:
                body = _extract_function_body(src, fn_name)
                if "scale_down" in body and "scale_zero" in body:
                    free_fns_with_scale.append(fn_name)
            except (AssertionError, ValueError):
                pass

    assert free_fns_with_scale, (
        "Must have a free helper function containing scale_down/scale_zero logic"
    )


# [pr_diff] fail_to_pass
def test_compilation_issues_uses_whole_app_graph():
    """get_all_compilation_issues_inner_operation calls a whole-app graph method (not comments)."""
    src = _read(BINDINGS_RS)
    body = _extract_function_body(src, "get_all_compilation_issues_inner_operation")

    # Strip Rust comments (// ...) to avoid matching mentions in old comments
    code_lines = [
        line for line in body.splitlines()
        if not line.strip().startswith("//")
    ]
    code_only = "\n".join(code_lines)

    # Must call a whole_app method on project (actual code, not comments)
    assert re.search(r"\.whole_app_module_graph", code_only), (
        "get_all_compilation_issues_inner_operation must call a whole_app_module_graph method "
        "(in code, not just comments)"
    )

    # Subprocess verification: the function body should contain the method call
    r = subprocess.run(
        ["grep", "-v", "^\\s*//", "crates/next-napi-bindings/src/next_api/project.rs"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    non_comment_lines = r.stdout
    assert "whole_app_module_graph" in non_comment_lines, (
        "whole_app_module_graph call must appear in non-comment code in bindings"
    )


# [pr_diff] fail_to_pass
def test_no_endpoint_group_iteration():
    """get_all_compilation_issues_inner_operation no longer iterates endpoint groups."""
    src = _read(BINDINGS_RS)
    body = _extract_function_body(src, "get_all_compilation_issues_inner_operation")

    assert "get_all_endpoint_groups" not in body, (
        "Should not call get_all_endpoint_groups — use whole-app graph instead"
    )
    # The old pattern used endpoint_group.module_graphs() in a map/join
    assert not re.search(r"endpoint_group.*module_graphs", body), (
        "Should not iterate endpoint groups calling module_graphs per route"
    )


# [pr_diff] fail_to_pass
def test_new_method_is_turbo_tasks_function():
    """The new whole-app graph method has #[turbo_tasks::function] attribute."""
    src = _read(PROJECT_RS)
    methods = _find_impl_project_methods(src)
    whole_app_new = [m for m in methods if "whole_app" in m and m != "whole_app_module_graphs"]
    assert whole_app_new, "Need a new whole-app method on Project"

    # Check the attribute is present before the function
    for method_name in whole_app_new:
        pattern = rf"#\[turbo_tasks::function\]\s*(?:pub\s+)?(?:async\s+)?fn\s+{method_name}"
        if re.search(pattern, src):
            return  # Found it

    assert False, (
        f"New whole-app method ({whole_app_new}) must have #[turbo_tasks::function] attribute"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_original_whole_app_module_graphs_preserved():
    """Original whole_app_module_graphs method still exists with drop_issues in dev path."""
    src = _read(PROJECT_RS)

    assert re.search(
        r"#\[turbo_tasks::function\]\s*(?:///[^\n]*\n\s*)*pub\s+async\s+fn\s+whole_app_module_graphs\b",
        src,
    ), "whole_app_module_graphs method must still exist as a turbo_tasks function"

    body = _extract_function_body(src, r"whole_app_module_graphs\b")
    assert "drop_issues" in body, (
        "whole_app_module_graphs must still call drop_issues() in dev mode"
    )
    assert "is_production" in body, (
        "whole_app_module_graphs must still check is_production()"
    )


# [pr_diff] pass_to_pass
def test_project_impl_structure_preserved():
    """impl Project block and key functions preserved."""
    src_project = _read(PROJECT_RS)
    src_bindings = _read(BINDINGS_RS)

    assert "impl Project" in src_project, "impl Project block must exist"
    assert "whole_app_module_graph_operation" in src_project, (
        "whole_app_module_graph_operation function must exist"
    )
    assert re.search(
        r"fn\s+get_all_compilation_issues_inner_operation", src_bindings
    ), "get_all_compilation_issues_inner_operation must exist"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks
# These tests verify the repo structure is intact for CI commands.
# Note: Full cargo check/clippy/test require Rust toolchain not in image.
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_cargo_toml_valid():
    """Cargo.toml exists and has valid workspace structure (pass_to_pass)."""
    cargo_toml = f"{REPO}/Cargo.toml"
    content = _read(cargo_toml)

    # Check workspace configuration exists
    assert "[workspace]" in content, "Cargo.toml must have [workspace] section"
    assert "members" in content, "Cargo.toml must have workspace members"
    assert "next-api" in content, "Cargo.toml must include next-api crate"
    assert "next-napi-bindings" in content, "Cargo.toml must include next-napi-bindings crate"


# [repo_tests] pass_to_pass
def test_repo_rust_files_valid_structure():
    """Modified Rust files have valid structure for compilation (pass_to_pass)."""
    # Check files are valid UTF-8 and non-empty
    for path in [PROJECT_RS, BINDINGS_RS]:
        content = _read(path)
        assert len(content) > 1000, f"{path} must have substantial content"
        # Check for common Rust file structure markers
        assert "use " in content or "mod " in content or "fn " in content, (
            f"{path} must contain Rust code (use/mod/fn)"
        )


# [repo_tests] pass_to_pass
def test_repo_crate_structure_preserved():
    """Crate structure is preserved for cargo build (pass_to_pass)."""
    # Check next-api crate structure
    next_api_cargo = f"{REPO}/crates/next-api/Cargo.toml"
    next_api_lib = f"{REPO}/crates/next-api/src/lib.rs"

    assert Path(next_api_cargo).exists(), "next-api/Cargo.toml must exist"
    assert Path(next_api_lib).exists(), "next-api/src/lib.rs must exist"

    next_api_cargo_content = _read(next_api_cargo)
    assert "[package]" in next_api_cargo_content, "next-api Cargo.toml must have [package]"

    # Check next-napi-bindings crate structure
    next_bindings_cargo = f"{REPO}/crates/next-napi-bindings/Cargo.toml"
    assert Path(next_bindings_cargo).exists(), "next-napi-bindings/Cargo.toml must exist"


# [repo_tests] pass_to_pass
def test_repo_rustfmt_config_preserved():
    """Rustfmt configuration exists for cargo fmt (pass_to_pass)."""
    rustfmt_toml = f"{REPO}/.rustfmt.toml"
    assert Path(rustfmt_toml).exists(), ".rustfmt.toml must exist"

    content = _read(rustfmt_toml)
    assert len(content) > 0, ".rustfmt.toml must not be empty"


# [repo_tests] pass_to_pass
def test_repo_git_commit_correct():
    """Repository is at expected base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Failed to get git HEAD: {r.stderr}"
    head_commit = r.stdout.strip()
    # The base commit from the task
    expected_commit = "cf328d3afe3660e71496fed499376921c75eb3e3"
    assert head_commit == expected_commit, (
        f"Git HEAD {head_commit[:8]} does not match expected {expected_commit[:8]}"
    )


# [repo_tests] pass_to_pass
def test_repo_cargo_toml_dependencies():
    """Cargo.toml has required dependencies for modified crates (pass_to_pass)."""
    cargo_toml = f"{REPO}/Cargo.toml"
    content = _read(cargo_toml)

    # Check workspace has the required crates as members
    assert "crates/next-api" in content, "Workspace must include next-api crate"
    assert "crates/next-napi-bindings" in content, "Workspace must include next-napi-bindings crate"
    assert "turbopack/crates/*" in content, "Workspace must include turbopack crates"


# [repo_tests] pass_to_pass
def test_repo_next_api_cargo_toml_valid():
    """next-api Cargo.toml has valid structure (pass_to_pass)."""
    next_api_cargo = f"{REPO}/crates/next-api/Cargo.toml"
    content = _read(next_api_cargo)

    # Check required fields
    assert "[package]" in content, "next-api/Cargo.toml must have [package]"
    assert "name = \"next-api\"" in content, "Package name must be next-api"

    # Check for key dependencies mentioned in the PR
    assert "[dependencies]" in content, "next-api/Cargo.toml must have [dependencies]"


# [repo_tests] pass_to_pass
def test_repo_next_napi_bindings_cargo_toml_valid():
    """next-napi-bindings Cargo.toml has valid structure (pass_to_pass)."""
    bindings_cargo = f"{REPO}/crates/next-napi-bindings/Cargo.toml"
    content = _read(bindings_cargo)

    # Check required fields
    assert "[package]" in content, "next-napi-bindings/Cargo.toml must have [package]"
    assert "name = \"next-napi-bindings\"" in content, "Package name must be next-napi-bindings"

    # Check for napi dependencies
    assert "[dependencies]" in content, "next-napi-bindings/Cargo.toml must have [dependencies]"
    assert "napi" in content, "Must have napi dependencies"


# [repo_tests] pass_to_pass
def test_repo_rust_code_has_turbo_tasks_attributes():
    """Modified Rust files have turbo_tasks::function attributes (pass_to_pass)."""
    # Check project.rs for turbo_tasks attributes
    project_src = _read(PROJECT_RS)
    assert r"#[turbo_tasks::function" in project_src, (
        "project.rs must contain turbo_tasks::function attributes"
    )

    # Check bindings for turbo_tasks attributes
    bindings_src = _read(BINDINGS_RS)
    assert r"#[turbo_tasks::function" in bindings_src, (
        "project.rs in bindings must contain turbo_tasks::function attributes"
    )


# [repo_tests] pass_to_pass
def test_repo_rust_code_has_required_traits():
    """Modified Rust files have required trait implementations (pass_to_pass)."""
    project_src = _read(PROJECT_RS)

    # Check for common traits used in the module graph code
    assert "impl Project" in project_src, "project.rs must have impl Project block"

    # Check for key types used in the PR
    assert "Vc<" in project_src, "project.rs must use Vc type (Turbopack primitive)"
    assert "ResolvedVc<" in project_src, "project.rs must use ResolvedVc type"


# [repo_tests] pass_to_pass
def test_repo_project_rs_has_module_graph_methods():
    """Project.rs has whole_app_module_graph related methods (pass_to_pass)."""
    project_src = _read(PROJECT_RS)

    # Check for the method that the PR modifies/uses
    assert "whole_app_module_graph" in project_src, (
        "project.rs must have whole_app_module_graph methods"
    )

    # Check for scale_down/scale_zero which are part of the fix
    assert "scale_down" in project_src, "project.rs must have scale_down logic"
    assert "scale_zero" in project_src, "project.rs must have scale_zero logic"


# [repo_tests] pass_to_pass
def test_repo_bindings_has_compilation_issues():
    """Bindings have get_all_compilation_issues methods (pass_to_pass)."""
    bindings_src = _read(BINDINGS_RS)

    # Check for the method that the PR modifies
    assert "get_all_compilation_issues" in bindings_src, (
        "bindings project.rs must have get_all_compilation_issues methods"
    )


# [repo_tests] pass_to_pass
def test_repo_rustfmt_config_valid():
    """Rustfmt configuration is valid TOML (pass_to_pass)."""
    rustfmt_toml = f"{REPO}/.rustfmt.toml"
    content = _read(rustfmt_toml)

    # Basic TOML validation - check for key-value pairs
    assert len(content) > 0, ".rustfmt.toml must not be empty"

    # Common rustfmt options
    assert "edition" in content or "imports_granularity" in content or "group_imports" in content, (
        ".rustfmt.toml must contain valid rustfmt options"
    )


# [repo_tests] pass_to_pass
def test_repo_lockfile_exists():
    """Cargo.lock exists and is valid (pass_to_pass)."""
    lockfile = f"{REPO}/Cargo.lock"

    r = subprocess.run(
        ["head", "-50", lockfile],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Cannot read Cargo.lock: {r.stderr}"

    content = r.stdout
    assert "version = 3" in content or "version = 4" in content, (
        "Cargo.lock must be a valid version 3 or 4 lockfile"
    )
    assert "[[package]]" in content, "Cargo.lock must contain package entries"


# [repo_tests] pass_to_pass
def test_repo_no_syntax_errors_in_modified_files():
    """Modified Rust files have no obvious syntax errors (pass_to_pass)."""
    # Check for common syntax issues
    for path in [PROJECT_RS, BINDINGS_RS]:
        content = _read(path)

        # Check braces are balanced (basic check)
        open_braces = content.count("{")
        close_braces = content.count("}")
        assert open_braces == close_braces, f"{path}: Unbalanced braces"

        # Check parentheses are balanced (rough check)
        open_parens = content.count("(")
        close_parens = content.count(")")
        assert open_parens == close_parens, f"{path}: Unbalanced parentheses"

        # Check for incomplete turbo_tasks attributes
        assert not re.search(r'#\[turbo_tasks::function\s*\Z', content, re.MULTILINE), (
            f"{path}: Incomplete turbo_tasks::function attribute"
        )


# [repo_tests] pass_to_pass
def test_repo_lib_rs_exports_present():
    """Crate lib.rs files export the expected modules (pass_to_pass)."""
    next_api_lib = f"{REPO}/crates/next-api/src/lib.rs"
    lib_content = _read(next_api_lib)

    # Check for common exports
    assert "mod project" in lib_content or "pub mod project" in lib_content, (
        "next-api lib.rs must export project module"
    )

    # Check bindings lib.rs
    bindings_lib = f"{REPO}/crates/next-napi-bindings/src/lib.rs"
    bindings_lib_content = _read(bindings_lib)
    assert "mod next_api" in bindings_lib_content or "pub mod next_api" in bindings_lib_content, (
        "next-napi-bindings lib.rs must export next_api module"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Real CI/CD commands via subprocess
# These tests run actual CI commands via subprocess.run() with origin: repo_tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass

# [repo_tests] pass_to_pass

# [repo_tests] pass_to_pass
def test_repo_cargo_toml_python_validation():
    """Root Cargo.toml is valid TOML via Python parser (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import tomllib; tomllib.load(open('/workspace/next.js/Cargo.toml', 'rb'))"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Cargo.toml TOML validation failed: {r.stderr[:500]}"


# [repo_tests] pass_to_pass
def test_repo_next_api_cargo_toml_python_validation():
    """next-api Cargo.toml is valid TOML via Python parser (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import tomllib; tomllib.load(open('/workspace/next.js/crates/next-api/Cargo.toml', 'rb'))"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"next-api Cargo.toml TOML validation failed: {r.stderr[:500]}"


# [repo_tests] pass_to_pass
def test_repo_next_napi_bindings_cargo_toml_python_validation():
    """next-napi-bindings Cargo.toml is valid TOML via Python parser (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import tomllib; tomllib.load(open('/workspace/next.js/crates/next-napi-bindings/Cargo.toml', 'rb'))"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"next-napi-bindings Cargo.toml TOML validation failed: {r.stderr[:500]}"


# [repo_tests] pass_to_pass
def test_repo_rust_toolchain_toml_python_validation():
    """rust-toolchain.toml is valid TOML via Python parser (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import tomllib; tomllib.load(open('/workspace/next.js/rust-toolchain.toml', 'rb'))"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"rust-toolchain.toml TOML validation failed: {r.stderr[:500]}"


# [repo_tests] pass_to_pass
def test_repo_rustfmt_toml_python_validation():
    """.rustfmt.toml is valid TOML via Python parser (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import tomllib; tomllib.load(open('/workspace/next.js/.rustfmt.toml', 'rb'))"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f".rustfmt.toml TOML validation failed: {r.stderr[:500]}"


# [repo_tests] pass_to_pass

# [repo_tests] pass_to_pass
def test_repo_package_json_valid():
    """package.json is valid JSON via Python parser (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import json; json.load(open('/workspace/next.js/package.json'))"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"package.json JSON validation failed: {r.stderr[:500]}"


# [repo_tests] pass_to_pass
# [repo_tests] pass_to_pass
def test_repo_git_log_check():
    """Git log shows expected base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "log", "-1", "--oneline"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Git log failed: {r.stderr[:500]}"
    expected_prefix = "cf328d3"
    assert r.stdout.strip().startswith(expected_prefix), (
        f"Git HEAD does not match expected base commit: {r.stdout[:50]}"
    )


# [repo_tests] pass_to_pass
def test_repo_shell_syntax_cargo_files():
    """Shell syntax check on Cargo.toml files via cat (pass_to_pass)."""
    r = subprocess.run(
        ["cat", "/workspace/next.js/Cargo.toml"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Cannot read Cargo.toml: {r.stderr[:500]}"
    assert len(r.stdout) > 100, "Cargo.toml appears too short"
    assert "[workspace]" in r.stdout, "Cargo.toml missing workspace section"


# [repo_tests] pass_to_pass
def test_repo_shell_syntax_next_api_cargo():
    """Shell syntax check on next-api Cargo.toml (pass_to_pass)."""
    r = subprocess.run(
        ["cat", "/workspace/next.js/crates/next-api/Cargo.toml"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Cannot read next-api Cargo.toml: {r.stderr[:500]}"
    assert "[package]" in r.stdout, "next-api Cargo.toml missing package section"
    assert 'name = "next-api"' in r.stdout, "next-api Cargo.toml missing package name"


# [repo_tests] pass_to_pass
def test_repo_shell_syntax_next_napi_bindings_cargo():
    """Shell syntax check on next-napi-bindings Cargo.toml (pass_to_pass)."""
    r = subprocess.run(
        ["cat", "/workspace/next.js/crates/next-napi-bindings/Cargo.toml"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Cannot read next-napi-bindings Cargo.toml: {r.stderr[:500]}"
    assert "[package]" in r.stdout, "next-napi-bindings Cargo.toml missing package section"
    assert "napi" in r.stdout, "next-napi-bindings Cargo.toml missing napi reference"


# [repo_tests] pass_to_pass
def test_repo_modified_files_readable():
    """Modified Rust files are readable via cat (pass_to_pass)."""
    for path in [PROJECT_RS, BINDINGS_RS]:
        r = subprocess.run(
            ["cat", path],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Cannot read {path}: {r.stderr[:500]}"
        assert len(r.stdout) > 5000, f"{path} appears too short"


# [repo_tests] pass_to_pass
def test_repo_ls_crates_dir():
    """ls command works on crates directory (pass_to_pass)."""
    r = subprocess.run(
        ["ls", "-la", "/workspace/next.js/crates/"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"ls on crates failed: {r.stderr[:500]}"
    assert "next-api" in r.stdout, "next-api crate not found"
    assert "next-napi-bindings" in r.stdout, "next-napi-bindings crate not found"


# [repo_tests] pass_to_pass
def test_repo_find_modified_files():
    """find command locates modified Rust files (pass_to_pass)."""
    r = subprocess.run(
        ["find", "/workspace/next.js/crates/next-api/src", "-name", "*.rs"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"find command failed: {r.stderr[:500]}"
    assert "project.rs" in r.stdout, "project.rs not found via find"


# [repo_tests] pass_to_pass
def test_repo_grep_turbo_tasks_in_project():
    """grep finds turbo_tasks in project.rs (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-c", "turbo_tasks", "/workspace/next.js/crates/next-api/src/project.rs"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"grep for turbo_tasks failed: {r.stderr[:500]}"
    count = int(r.stdout.strip())
    assert count > 10, f"Expected many turbo_tasks references, found {count}"


# [repo_tests] pass_to_pass
def test_repo_grep_whole_app_in_project():
    """grep finds whole_app_module_graph in project.rs (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-c", "whole_app_module_graph", "/workspace/next.js/crates/next-api/src/project.rs"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"grep for whole_app_module_graph failed: {r.stderr[:500]}"
    count = int(r.stdout.strip())
    assert count >= 2, f"Expected at least 2 whole_app_module_graph references, found {count}"


# [repo_tests] pass_to_pass
def test_repo_grep_compilation_issues_in_bindings():
    """grep finds get_all_compilation_issues in bindings (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-c", "get_all_compilation_issues", BINDINGS_RS],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"grep for get_all_compilation_issues failed: {r.stderr[:500]}"
    count = int(r.stdout.strip())
    assert count >= 2, f"Expected at least 2 get_all_compilation_issues references, found {count}"

# ---------------------------------------------------------------------------
# Pass-to-pass (repo_ci_validations) — CI/CD config file validations
# These tests validate that CI/CD configuration files are valid and complete.
# Note: Actual cargo check/clippy/test would require Rust toolchain.
# These tests only check things that already exist on the base commit.
# ---------------------------------------------------------------------------

# [repo_ci_validations] pass_to_pass
def test_repo_workspace_cargo_toml_syntax():
    """Root Cargo.toml has valid workspace syntax for cargo check (pass_to_pass)."""
    cargo_toml = f"{REPO}/Cargo.toml"
    content = _read(cargo_toml)

    # Basic TOML structure validation for workspace
    assert "[workspace]" in content, "Root Cargo.toml must declare [workspace]"
    assert "resolver = \"2\"" in content, "Workspace must use resolver = \"2\""

    # Extract members list and validate key crates are present
    members_match = re.search(r"members\s*=\s*\[([^\]]+)\]", content, re.DOTALL)
    assert members_match, "Workspace must have members list"
    members_section = members_match.group(1)

    # Critical crates for this PR must be in workspace members
    assert '"crates/next-api"' in members_section, "next-api must be in workspace members"
    assert '"crates/next-napi-bindings"' in members_section, (
        "next-napi-bindings must be in workspace members"
    )

    # Workspace lints must be configured
    assert "[workspace.lints.clippy]" in content, "Workspace must have clippy lints configured"
    assert "[workspace.lints.rust]" in content, "Workspace must have rust lints configured"


# [repo_ci_validations] pass_to_pass
def test_repo_next_api_cargo_toml_complete():
    """next-api Cargo.toml has complete configuration for cargo build (pass_to_pass)."""
    cargo_path = f"{REPO}/crates/next-api/Cargo.toml"
    content = _read(cargo_path)

    # Required sections for a valid crate
    assert "[package]" in content, "next-api/Cargo.toml must have [package] section"
    assert "name = \"next-api\"" in content, "Package name must be next-api"
    assert "version = " in content, "Package must have version"
    assert "edition = " in content, "Package must specify Rust edition"

    # Required for the crate to compile
    assert "[dependencies]" in content, "next-api must have [dependencies] section"
    assert "[lib]" in content, "next-api must have [lib] section"
    assert 'bench = false' in content, "next-api must set bench = false"

    # Check for critical dependencies used in the PR
    critical_deps = [
        "turbo-tasks",
        "turbopack",
        "turbopack-core",
        "turbopack-node",
        "next-core",
    ]
    for dep in critical_deps:
        assert dep in content, f"next-api must depend on {dep}"

    # Workspace lint inheritance
    assert "[lints]" in content and "workspace = true" in content, (
        "next-api must inherit workspace lints"
    )


# [repo_ci_validations] pass_to_pass
def test_repo_next_napi_bindings_cargo_toml_complete():
    """next-napi-bindings Cargo.toml has complete configuration for cargo build (pass_to_pass)."""
    cargo_path = f"{REPO}/crates/next-napi-bindings/Cargo.toml"
    content = _read(cargo_path)

    # Required sections
    assert "[package]" in content, "next-napi-bindings/Cargo.toml must have [package] section"
    assert "name = \"next-napi-bindings\"" in content, "Package name must be next-napi-bindings"
    assert "[dependencies]" in content, "next-napi-bindings must have [dependencies] section"

    # NAPI dependencies are required for bindings
    assert "napi" in content, "next-napi-bindings must have napi dependencies"
    assert "next-api" in content, "next-napi-bindings must depend on next-api"

    # Workspace lint inheritance
    assert "[lints]" in content and "workspace = true" in content, (
        "next-napi-bindings must inherit workspace lints"
    )


# [repo_ci_validations] pass_to_pass
def test_repo_rust_toolchain_config_valid():
    """rust-toolchain.toml has valid configuration for CI (pass_to_pass)."""
    toolchain_path = f"{REPO}/rust-toolchain.toml"
    content = _read(toolchain_path)

    # Must specify a channel
    assert "[toolchain]" in content, "rust-toolchain.toml must have [toolchain] section"
    assert "channel = " in content, "Toolchain must specify a channel"

    # Required components for CI
    assert "components = " in content, "Toolchain must specify components"
    assert "rustfmt" in content, "Toolchain must include rustfmt"
    assert "clippy" in content, "Toolchain must include clippy"


# [repo_ci_validations] pass_to_pass
def test_repo_rustfmt_config_complete():
    """.rustfmt.toml has complete formatting configuration for cargo fmt (pass_to_pass)."""
    rustfmt_path = f"{REPO}/.rustfmt.toml"
    content = _read(rustfmt_path)

    # Basic structure validation
    assert "edition = " in content, "rustfmt.toml must specify edition"
    assert "style_edition = " in content, "rustfmt.toml must specify style_edition"

    # Formatting rules that CI would enforce
    assert "max_width = " in content, "rustfmt.toml must specify max_width"
    assert "tab_spaces = " in content, "rustfmt.toml must specify tab_spaces"
    assert "hard_tabs = " in content, "rustfmt.toml must specify hard_tabs"

    # Import organization rules (used by CI)
    assert "imports_granularity = " in content, "rustfmt.toml must specify imports_granularity"
    assert "group_imports = " in content, "rustfmt.toml must specify group_imports"


# [repo_ci_validations] pass_to_pass
def test_repo_cargo_lock_exists():
    """Cargo.lock exists for reproducible builds (pass_to_pass)."""
    lockfile = f"{REPO}/Cargo.lock"

    r = subprocess.run(
        ["head", "-50", lockfile],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Cannot read Cargo.lock: {r.stderr}"
    content = r.stdout

    # Validate lockfile format
    assert "version = " in content, "Cargo.lock must specify version"
    assert "[[package]]" in content, "Cargo.lock must contain package entries"


# [repo_ci_validations] pass_to_pass
def test_repo_git_configured():
    """Git repository is properly configured for CI operations (pass_to_pass)."""
    # Check git config
    r = subprocess.run(
        ["git", "config", "user.name"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0 and r.stdout.strip(), "Git user.name must be configured"

    r = subprocess.run(
        ["git", "config", "user.email"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0 and r.stdout.strip(), "Git user.email must be configured"

    # Check that it's a valid git repo with expected commit
    r = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, "Must be a valid git repository"


# [repo_ci_validations] pass_to_pass
def test_repo_modified_files_have_valid_rust_structure():
    """Modified Rust files have structure valid for cargo check/clippy (pass_to_pass)."""
    for path in [PROJECT_RS, BINDINGS_RS]:
        content = _read(path)

        # Check for valid Rust file markers
        assert "use " in content or "mod " in content or "fn " in content or "impl " in content, (
            f"{path} must contain valid Rust code elements"
        )

        # Verify balanced braces (basic structural check)
        open_braces = content.count("{")
        close_braces = content.count("}")
        assert open_braces == close_braces, f"{path}: Unbalanced braces"

        # Check for turbo_tasks function attributes (required for compilation)
        assert "#[turbo_tasks::function" in content, (
            f"{path} must contain turbo_tasks::function attributes"
        )

        # Verify no obviously broken patterns
        assert content.count('"') % 2 == 0, f"{path}: Unbalanced quotes"


# [repo_ci_validations] pass_to_pass
def test_repo_ci_workflows_referenced():
    """CI workflow files exist and reference Rust checks (pass_to_pass)."""
    workflows_dir = f"{REPO}/.github/workflows"

    # Key workflow files must exist
    required_workflows = [
        "build_and_test.yml",
        "build_reusable.yml",
    ]
    for wf in required_workflows:
        wf_path = f"{workflows_dir}/{wf}"
        assert Path(wf_path).exists(), f"Required workflow {wf} must exist"

    # Check that test-turbopack-rust workflow exists for Rust testing
    rust_test_wf = f"{workflows_dir}/test-turbopack-rust-bench-test.yml"
    assert Path(rust_test_wf).exists(), "Rust test workflow must exist"

    # Verify workflows reference cargo commands
    build_test_wf = _read(f"{workflows_dir}/build_and_test.yml")
    assert "cargo" in build_test_wf, "build_and_test.yml must reference cargo commands"
    assert "test-cargo-unit" in build_test_wf or "cargo test" in build_test_wf, (
        "Workflow must reference cargo test commands"
    )


# [repo_ci_validations] pass_to_pass
def test_repo_whole_app_module_graphs_valid_signature():
    """Existing whole_app_module_graphs method has valid signature (pass_to_pass)."""
    src = _read(PROJECT_RS)

    # Check the method exists with valid turbo_tasks attribute on base commit
    pattern = r'#\[turbo_tasks::function\]\s*pub\s+async\s+fn\s+whole_app_module_graphs\b'
    assert re.search(pattern, src), (
        "whole_app_module_graphs must have valid method signature with turbo_tasks attribute"
    )

    # Verify it's inside impl Project block
    impl_blocks = list(re.finditer(r"impl\s+Project\s*\{", src))
    assert len(impl_blocks) > 0, "Project.rs must have impl Project blocks"


# [repo_ci_validations] pass_to_pass
def test_repo_get_all_compilation_issues_valid_signature():
    """get_all_compilation_issues_inner_operation has valid signature (pass_to_pass)."""
    src = _read(BINDINGS_RS)

    # Check the function exists with async and proper parameters (base commit version)
    # This test validates the function exists - the PR changes the implementation
    pattern = r"async\s+fn\s+get_all_compilation_issues_inner_operation\b"
    assert re.search(pattern, src), (
        "get_all_compilation_issues_inner_operation must have valid function signature"
    )

    # Verify return type is Result<Vc<()>> pattern
    fn_body = _extract_function_body(src, "get_all_compilation_issues_inner_operation")
    assert "Result" in fn_body, "Function must work with Result type"
    assert "Vc<()" in fn_body or "Vc::cell" in fn_body, "Function must return Vc type"
