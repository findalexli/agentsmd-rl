"""
Task: nextjs-mcp-compilation-issues-whole-graph
Repo: vercel/next.js @ cf328d3afe3660e71496fed499376921c75eb3e3
PR:   92473

All checks must pass for reward = 1. Any failure = reward 0.
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
        methods.extend(mm.group(1) for mm in re.finditer(r"fn\s+(\w+)\s*[\(<]", block))
    return methods


# Fail-to-pass (pr_diff) tests

# [pr_diff] fail_to_pass
def test_non_dropping_whole_app_method():
    """Project has a method that computes whole-app graph WITHOUT dropping issues."""
    src = _read(PROJECT_RS)
    methods = _find_impl_project_methods(src)
    whole_app_methods = [m for m in methods if "whole_app" in m and m != "whole_app_module_graphs"]
    assert whole_app_methods, "Need a new whole-app module graph method on Project"
    found_valid = False
    for method_name in whole_app_methods:
        body = _extract_function_body(src, method_name)
        has_graph_op = "whole_app_module_graph_operation" in body
        has_connect = ".connect()" in body
        no_drop = "drop_issues" not in body
        if has_graph_op and has_connect and no_drop:
            found_valid = True
            break
    assert found_valid, "New whole-app method must call whole_app_module_graph_operation, .connect(), and must NOT call drop_issues"


# [pr_diff] fail_to_pass
def test_scale_down_logic_deduplicated():
    """Node pool scale-down logic is extracted from whole_app_module_graphs."""
    src = _read(PROJECT_RS)
    orig_body = _extract_function_body(src, r"whole_app_module_graphs\b")
    has_inline_scale = ("node_backend" in orig_body and ("scale_down" in orig_body or "scale_zero" in orig_body) and "execution_context" in orig_body)
    assert not has_inline_scale, "whole_app_module_graphs should not inline scale-down logic"
    impl_regions = []
    for m in re.finditer(r"impl\s+Project\s*\{", src):
        start = m.start()
        depth = 1
        i = m.end()
        while depth > 0 and i < len(src):
            if src[i] == "{": depth += 1
            elif src[i] == "}": depth -= 1
            i += 1
        impl_regions.append((start, i))
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
    assert free_fns_with_scale, "Must have a free helper function with scale_down/scale_zero"


# [pr_diff] fail_to_pass
def test_compilation_issues_uses_whole_app_graph():
    """get_all_compilation_issues_inner_operation calls a whole-app graph method."""
    src = _read(BINDINGS_RS)
    body = _extract_function_body(src, "get_all_compilation_issues_inner_operation")
    code_lines = [line for line in body.splitlines() if not line.strip().startswith("//")]
    code_only = "\n".join(code_lines)
    assert re.search(r"\.whole_app_module_graph", code_only), "Must call a whole_app_module_graph method in code"
    r = subprocess.run(["grep", "-v", "^\\s*//", "crates/next-napi-bindings/src/next_api/project.rs"], cwd=REPO, capture_output=True, text=True, timeout=10)
    assert "whole_app_module_graph" in r.stdout


# [pr_diff] fail_to_pass
def test_no_endpoint_group_iteration():
    """get_all_compilation_issues_inner_operation no longer iterates endpoint groups."""
    src = _read(BINDINGS_RS)
    body = _extract_function_body(src, "get_all_compilation_issues_inner_operation")
    assert "get_all_endpoint_groups" not in body
    assert not re.search(r"endpoint_group.*module_graphs", body)


# [pr_diff] fail_to_pass
def test_new_method_is_turbo_tasks_function():
    """The new whole-app graph method has #[turbo_tasks::function] attribute."""
    src = _read(PROJECT_RS)
    methods = _find_impl_project_methods(src)
    whole_app_new = [m for m in methods if "whole_app" in m and m != "whole_app_module_graphs"]
    assert whole_app_new, "Need a new whole-app method on Project"
    for method_name in whole_app_new:
        pattern = rf"#\[turbo_tasks::function\]\s*(?:pub\s+)?(?:async\s+)?fn\s+{method_name}"
        if re.search(pattern, src):
            return
    assert False, "New whole-app method must have #[turbo_tasks::function] attribute"


# Pass-to-pass (pr_diff) regression checks

# [pr_diff] pass_to_pass
def test_original_whole_app_module_graphs_preserved():
    """Original whole_app_module_graphs method still exists with drop_issues."""
    src = _read(PROJECT_RS)
    assert re.search(r"#\[turbo_tasks::function\]\s*pub\s+async\s+fn\s+whole_app_module_graphs\b", src)
    body = _extract_function_body(src, r"whole_app_module_graphs\b")
    assert "drop_issues" in body
    assert "is_production" in body


# [pr_diff] pass_to_pass
def test_project_impl_structure_preserved():
    """impl Project block and key functions preserved."""
    src_project = _read(PROJECT_RS)
    src_bindings = _read(BINDINGS_RS)
    assert "impl Project" in src_project
    assert "whole_app_module_graph_operation" in src_project
    assert re.search(r"fn\s+get_all_compilation_issues_inner_operation", src_bindings)


# Gates (pass_to_pass, static)

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


# Pass-to-pass (repo_tests) - CI/Derived validation tests


# [repo_tests] pass_to_pass
def test_repo_git_log_follow_modified():
    """Git log --follow works on modified Rust files (pass_to_pass)."""
    for rel_path in [
        "crates/next-api/src/project.rs",
        "crates/next-napi-bindings/src/next_api/project.rs"
    ]:
        r = subprocess.run(["git", "log", "--oneline", "--follow", "-3", "--", rel_path], cwd=REPO, capture_output=True, text=True, timeout=30)
        assert r.returncode == 0
        assert len(r.stdout.strip()) > 0




# [repo_tests] pass_to_pass
def test_repo_head_command_on_cargo_lock():
    """head command reads Cargo.lock successfully (pass_to_pass)."""
    r = subprocess.run(["head", "-100", f"{REPO}/Cargo.lock"], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0
    assert "version = " in r.stdout
    assert "[[package]]" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_grep_pattern_in_project_rs():
    """grep finds key patterns in project.rs (pass_to_pass)."""
    for pattern in ["impl Project", "whole_app_module_graph", "turbo_tasks::function"]:
        r = subprocess.run(["grep", "-q", pattern, PROJECT_RS], capture_output=True, text=True)
        assert r.returncode == 0


# [repo_tests] pass_to_pass
def test_repo_grep_pattern_in_bindings_rs():
    """grep finds key patterns in bindings project.rs (pass_to_pass)."""
    for pattern in ["get_all_compilation_issues", "ProjectContainer", "turbo_tasks::function"]:
        r = subprocess.run(["grep", "-q", pattern, BINDINGS_RS], capture_output=True, text=True)
        assert r.returncode == 0


# [repo_tests] pass_to_pass
def test_repo_wc_lines_in_modified_files():
    """Modified Rust files have substantial line counts via wc (pass_to_pass)."""
    for path in [PROJECT_RS, BINDINGS_RS]:
        r = subprocess.run(["wc", "-l", path], capture_output=True, text=True, timeout=10)
        assert r.returncode == 0
        line_count = int(r.stdout.strip().split()[0])
        assert line_count > 1000


# [repo_tests] pass_to_pass
def test_repo_find_rs_files_in_crates():
    """find locates Rust files in crates directory (pass_to_pass)."""
    r = subprocess.run(["find", f"{REPO}/crates", "-name", "*.rs", "-type", "f"], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    files = r.stdout.strip().split("\n")
    assert len(files) > 10
    assert any("next-api/src/project.rs" in f for f in files)


# [repo_tests] pass_to_pass
def test_repo_ls_next_api_structure():
    """ls shows next-api crate has expected structure (pass_to_pass)."""
    r = subprocess.run(["ls", "-la", f"{REPO}/crates/next-api/"], capture_output=True, text=True)
    assert r.returncode == 0
    assert "Cargo.toml" in r.stdout
    assert "src" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_ls_bindings_structure():
    """ls shows next-napi-bindings crate has expected structure (pass_to_pass)."""
    r = subprocess.run(["ls", "-la", f"{REPO}/crates/next-napi-bindings/"], capture_output=True, text=True)
    assert r.returncode == 0
    assert "Cargo.toml" in r.stdout
    assert "src" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_git_ls_files_crate_sources():
    """Git ls-files shows source files in modified crates (pass_to_pass)."""
    r = subprocess.run(["git", "ls-files", "crates/next-api/src/*.rs", "crates/next-napi-bindings/src/next_api/*.rs"], cwd=REPO, capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    assert "project.rs" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_cat_project_rs_has_functions():
    """cat project.rs contains expected function definitions (pass_to_pass)."""
    r = subprocess.run(["cat", PROJECT_RS], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    assert "fn whole_app_module_graphs" in r.stdout
    assert "impl Project" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_cat_bindings_rs_has_functions():
    """cat bindings project.rs contains expected function definitions (pass_to_pass)."""
    r = subprocess.run(["cat", BINDINGS_RS], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    assert "get_all_compilation_issues" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_git_commit_correct():
    """Repository is at expected base commit (pass_to_pass)."""
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0
    assert r.stdout.strip() == "cf328d3afe3660e71496fed499376921c75eb3e3"


# [repo_tests] pass_to_pass
def test_repo_git_status_clean():
    """Git repository has clean working tree at base commit (pass_to_pass)."""
    r = subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0
    project_rs = Path(REPO) / "crates/next-api/src/project.rs"
    if "whole_app_module_graphs_without_dropping_issues" not in project_rs.read_text():
        assert r.stdout.strip() == ""


# Pass-to-pass (static) - Static file structure checks

# [static] pass_to_pass
def test_repo_workspace_cargo_toml_syntax():
    """Root Cargo.toml has valid workspace syntax (pass_to_pass)."""
    content = _read(f"{REPO}/Cargo.toml")
    assert "[workspace]" in content
    assert "resolver" in content
    assert "next-api" in content
    assert "next-napi-bindings" in content


# [static] pass_to_pass
def test_repo_next_api_cargo_toml_complete():
    """next-api Cargo.toml has complete configuration (pass_to_pass)."""
    content = _read(f"{REPO}/crates/next-api/Cargo.toml")
    assert "[package]" in content
    assert "name = \"next-api\"" in content
    assert "[dependencies]" in content
    assert "turbo-tasks" in content


# [static] pass_to_pass
def test_repo_next_napi_bindings_cargo_toml_complete():
    """next-napi-bindings Cargo.toml has complete configuration (pass_to_pass)."""
    content = _read(f"{REPO}/crates/next-napi-bindings/Cargo.toml")
    assert "[package]" in content
    assert "napi" in content
    assert "next-api" in content


# [static] pass_to_pass
def test_repo_rust_toolchain_config_valid():
    """rust-toolchain.toml has valid configuration (pass_to_pass)."""
    content = _read(f"{REPO}/rust-toolchain.toml")
    assert "[toolchain]" in content
    assert "channel" in content
    assert "rustfmt" in content
    assert "clippy" in content


# [static] pass_to_pass
def test_repo_rustfmt_config_complete():
    """.rustfmt.toml has complete formatting configuration (pass_to_pass)."""
    content = _read(f"{REPO}/.rustfmt.toml")
    assert "edition" in content
    assert "style_edition" in content
    assert "max_width" in content
    assert "imports_granularity" in content


# [static] pass_to_pass
def test_repo_ci_workflows_referenced():
    """CI workflow files exist and reference Rust checks (pass_to_pass)."""
    workflows_dir = f"{REPO}/.github/workflows"
    for wf in ["build_and_test.yml", "build_reusable.yml"]:
        assert Path(f"{workflows_dir}/{wf}").exists()
    assert Path(f"{workflows_dir}/test-turbopack-rust-bench-test.yml").exists()
    build_test_wf = _read(f"{workflows_dir}/build_and_test.yml")
    assert "cargo" in build_test_wf


# [static] pass_to_pass
def test_repo_whole_app_module_graphs_valid_signature():
    """Existing whole_app_module_graphs method has valid signature (pass_to_pass)."""
    src = _read(PROJECT_RS)
    assert re.search(r"#\[turbo_tasks::function\]\s*pub\s+async\s+fn\s+whole_app_module_graphs\b", src)


# [static] pass_to_pass
def test_repo_get_all_compilation_issues_valid_signature():
    """get_all_compilation_issues_inner_operation has valid signature (pass_to_pass)."""
    src = _read(BINDINGS_RS)
    assert re.search(r"async\s+fn\s+get_all_compilation_issues_inner_operation\b", src)
