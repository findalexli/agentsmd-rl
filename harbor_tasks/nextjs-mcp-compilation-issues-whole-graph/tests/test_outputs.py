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
