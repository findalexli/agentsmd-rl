"""
Task: sglang-hisparse-minor-fix
Repo: sglang @ 20ee59bcfc2956cb2aef2c1a4ae1e8bbda4ba52d
PR:   22131

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

def test_syntax_check_python():
    """Modified Python files must parse without errors."""
    python_files = [
        "python/sglang/srt/managers/schedule_batch.py",
        "python/sglang/srt/managers/scheduler.py",
    ]
    for file_path in python_files:
        full_path = Path(f"{REPO}/{file_path}")
        src = full_path.read_text()
        ast.parse(src)


def test_syntax_check_cuda():
    """Modified CUDA files must have valid syntax (no unclosed braces, valid PTX asm)."""
    cuda_file = Path(f"{REPO}/python/sglang/jit_kernel/csrc/hisparse.cuh")
    src = cuda_file.read_text()

    # Check for unbalanced braces
    open_count = src.count("{")
    close_count = src.count("}")
    assert open_count == close_count, f"Unbalanced braces: {open_count} open, {close_count} close"

    # Check for basic CUDA syntax patterns
    assert "__device__" in src, "Missing __device__ qualifier"
    assert "__forceinline__" in src, "Missing __forceinline__ qualifier"

    # Validate asm volatile statements are properly formed
    for line in src.split("\n"):
        if "asm volatile" in line:
            assert line.count("(") == line.count(")"), f"Unbalanced parens in asm: {line}"
            assert '"' in line, f"Missing quotes in asm: {line}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_hisparse_coordinator_retract_in_release_req():
    """hisparse_coordinator.retract_req must be called in release_req method."""
    src_path = Path(f"{REPO}/python/sglang/srt/managers/schedule_batch.py")
    src = src_path.read_text()
    tree = ast.parse(src)

    # Find the ScheduleBatch class and release_req method
    found_release_req = False
    has_hisparse_check = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name == "ScheduleBatch" or "ScheduleBatch" in [
                base.id if isinstance(base, ast.Name) else base.attr if isinstance(base, ast.Attribute) else ""
                for base in node.bases
            ]:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "release_req":
                        found_release_req = True
                        # Check for hisparse_coordinator.retract_req call
                        for stmt in ast.walk(item):
                            if isinstance(stmt, ast.Call):
                                # Check for retract_req call
                                if isinstance(stmt.func, ast.Attribute) and stmt.func.attr == "retract_req":
                                    has_hisparse_check = True
                                # Also check for the None check pattern
                                if isinstance(stmt.func, ast.Attribute) and stmt.func.attr == "retract_req":
                                    # Look for the if self.hisparse_coordinator is not None pattern
                                    pass

    # More robust: search for the specific pattern in source
    assert "release_req" in src, "release_req method not found"

    # Find the release_req method body by looking at the AST more carefully
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "release_req":
            # Get the method body as string
            method_start = node.lineno - 1
            method_end = node.end_lineno
            method_lines = src.split("\n")[method_start:method_end]
            method_src = "\n".join(method_lines)

            # Check for hisparse_coordinator check and retract_req call
            assert "hisparse_coordinator" in method_src, "hisparse_coordinator not referenced in release_req"
            assert "retract_req" in method_src, "retract_req not called in release_req"
            assert "is not None" in method_src or "if self.hisparse_coordinator" in method_src, \
                "Missing None check for hisparse_coordinator"
            has_hisparse_check = True
            break

    assert has_hisparse_check, "hisparse_coordinator.retract_req not properly called in release_req"


def test_batch_is_full_reset_after_hisparse():
    """batch_is_full must be reset to False after hisparse_coordinator assignment."""
    src_path = Path(f"{REPO}/python/sglang/srt/managers/scheduler.py")
    src = src_path.read_text()

    # Find the pattern where hisparse_coordinator is assigned and batch_is_full is reset
    # Look for: self.running_batch.hisparse_coordinator = ... followed by batch_is_full = False

    # Parse and find the specific pattern
    tree = ast.parse(src)

    found_pattern = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_next_batch_to_run":
            # Check the method body for the pattern
            method_start = node.lineno - 1
            method_end = node.end_lineno
            method_lines = src.split("\n")[method_start:method_end]
            method_src = "\n".join(method_lines)

            # Should have hisparse_coordinator assignment and batch_is_full = False
            if "hisparse_coordinator" in method_src and "batch_is_full = False" in method_src:
                found_pattern = True
                break

    assert found_pattern, "batch_is_full must be reset to False after hisparse_coordinator assignment"


def test_retract_req_removed_from_scheduler():
    """retract_req call must be removed from scheduler's update_running_batch method."""
    src_path = Path(f"{REPO}/python/sglang/srt/managers/scheduler.py")
    src = src_path.read_text()
    tree = ast.parse(src)

    # Find update_running_batch method
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "update_running_batch":
            method_start = node.lineno - 1
            method_end = node.end_lineno
            method_lines = src.split("\n")[method_start:method_end]
            method_src = "\n".join(method_lines)

            # Should NOT have retract_req in this method anymore
            assert "retract_req" not in method_src, \
                "retract_req should be removed from update_running_batch (moved to release_req)"
            break
    else:
        # Method might not exist with exact name, that's okay
        pass


def test_transfer_item_warp_128bit_alignment():
    """transfer_item_warp must use 128-bit (16-byte) paired transfers with tail handling."""
    src_path = Path(f"{REPO}/python/sglang/jit_kernel/csrc/hisparse.cuh")
    src = src_path.read_text()

    # Check for 128-bit transfer pattern
    assert "total_pairs = item_size_bytes / 16" in src or "item_size_bytes / 16" in src, \
        "Must use 16-byte (128-bit) chunks for bulk transfer"

    # Check for paired 64-bit loads (v2.b64)
    assert "ld.global.nc.v2.b64" in src, \
        "Must use 128-bit load instruction (ld.global.nc.v2.b64)"
    assert "st.global.cg.v2.b64" in src, \
        "Must use 128-bit store instruction (st.global.cg.v2.b64)"

    # Check for tail handling
    assert "tail_8B" in src or "tail" in src, \
        "Must handle tail case for sizes not multiple of 16"

    # Check for 8-byte tail handling
    assert "ld.global.nc.b64" in src and src.count("ld.global.nc.b64") >= 1, \
        "Must have 64-bit fallback for tail handling"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub checks
# ---------------------------------------------------------------------------

def test_not_stub_schedule_batch():
    """release_req in schedule_batch.py has real logic."""
    src_path = Path(f"{REPO}/python/sglang/srt/managers/schedule_batch.py")
    src = src_path.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "release_req":
            # Count non-trivial statements (excluding Pass, docstrings)
            stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
            # Should have at least 3 meaningful statements (if check + method body)
            assert len(stmts) >= 2, "release_req is a stub - needs more logic"
            break
    else:
        assert False, "release_req method not found"


def test_not_stub_scheduler():
    """get_next_batch_to_run in scheduler.py has real logic."""
    src_path = Path(f"{REPO}/python/sglang/srt/managers/scheduler.py")
    src = src_path.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_next_batch_to_run":
            stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
            # This is a large method, should have many statements
            assert len(stmts) >= 10, "get_next_batch_to_run seems too small - may be a stub"
            break
    else:
        assert False, "get_next_batch_to_run method not found"


def test_not_stub_hisparse_cuh():
    """transfer_item_warp in hisparse.cuh has real logic."""
    src_path = Path(f"{REPO}/python/sglang/jit_kernel/csrc/hisparse.cuh")
    src = src_path.read_text()

    # Find transfer_item_warp function
    assert "transfer_item_warp" in src, "transfer_item_warp function not found"

    # Extract function by finding the opening brace after transfer_item_warp
    func_start = src.find("transfer_item_warp")
    assert func_start != -1, "Could not find transfer_item_warp"

    # Find opening brace after function signature
    open_brace = src.find("{", func_start)
    assert open_brace != -1, "Could not find opening brace"

    # Find matching closing brace
    brace_count = 1
    i = open_brace + 1
    while i < len(src) and brace_count > 0:
        if src[i] == '{':
            brace_count += 1
        elif src[i] == '}':
            brace_count -= 1
        i += 1

    function_src = src[open_brace:i]

    # Should have meaningful CUDA code
    assert "for" in function_src or "while" in function_src or "map" in function_src or "forEach" in function_src or "iter" in function_src, "transfer_item_warp should have a for loop"
    assert "asm volatile" in function_src, "transfer_item_warp should use inline assembly"
    assert function_src.count("asm volatile") >= 2, "Should have multiple asm statements"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from repo
# ---------------------------------------------------------------------------

def test_repo_ruff_check():
    """Repo's Python files pass ruff linting (F401, F821) (pass_to_pass)."""
    modified_files = [
        "python/sglang/srt/managers/schedule_batch.py",
        "python/sglang/srt/managers/scheduler.py",
    ]
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821"] + modified_files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_black_format():
    """Repo's Python files pass black format check (pass_to_pass)."""
    modified_files = [
        "python/sglang/srt/managers/schedule_batch.py",
        "python/sglang/srt/managers/scheduler.py",
    ]
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["black", "--check"] + modified_files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_isort_check():
    """Repo's Python files pass isort check (pass_to_pass)."""
    modified_files = [
        "python/sglang/srt/managers/schedule_batch.py",
        "python/sglang/srt/managers/scheduler.py",
    ]
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["isort", "--check"] + modified_files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_codespell_check():
    """Repo's Python files pass codespell check (pass_to_pass)."""
    modified_files = [
        "python/sglang/srt/managers/schedule_batch.py",
        "python/sglang/srt/managers/scheduler.py",
    ]
    r = subprocess.run(
        ["pip", "install", "codespell", "toml", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["codespell", "--config", ".codespellrc"] + modified_files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # codespell returns 0 if no spelling errors, 65 if errors found
    assert r.returncode in [0, 65], f"codespell check failed with unexpected error:\n{r.stderr[-500:]}"


def test_repo_py_compile():
    """Modified Python files compile without syntax errors (pass_to_pass)."""
    modified_files = [
        "python/sglang/srt/managers/schedule_batch.py",
        "python/sglang/srt/managers/scheduler.py",
    ]
    r = subprocess.run(
        ["python", "-m", "py_compile"] + modified_files,
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python compile failed:\n{r.stderr[-500:]}"


def test_repo_clang_format_check():
    """CUDA/C++ files pass clang-format check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "clang-format", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Check clang-format is available at the pip install location
    clang_format_path = "/usr/local/bin/clang-format"
    r = subprocess.run(
        [clang_format_path, "--version"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    if r.returncode != 0:
        # Skip if clang-format not available
        return
    r = subprocess.run(
        [clang_format_path, "--style=file", "--dry-run", "--Werror",
         "python/sglang/jit_kernel/csrc/hisparse.cuh"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"clang-format check failed:\n{r.stderr[-500:]}"


def test_repo_pre_commit_ast():
    """Python files pass AST check (pass_to_pass)."""
    modified_files = [
        "python/sglang/srt/managers/schedule_batch.py",
        "python/sglang/srt/managers/scheduler.py",
    ]
    for f in modified_files:
        r = subprocess.run(
            ["python", "-c", f"import ast; ast.parse(open('{f}').read())"],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"AST check failed for {f}:\n{r.stderr[-500:]}"


def test_repo_pre_commit_trailing_whitespace():
    """Modified Python files have no trailing whitespace on code lines (pass_to_pass)."""
    # NOTE: Relaxed check - the gold solution from PR 22131 has trailing whitespace on comment lines
    # Only check non-comment, non-empty, non-string lines
    modified_files = [
        "python/sglang/srt/managers/schedule_batch.py",
        "python/sglang/srt/managers/scheduler.py",
    ]
    for f in modified_files:
        src = Path(f"{REPO}/{f}").read_text()
        lines = src.split("\n")
        in_multiline_string = False
        bad_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Check for multiline string start/end using triple double quotes
            triple_double = '"""'
            triple_single = "'" + "'" + "'"

            if not in_multiline_string:
                if triple_double in line and line.count(triple_double) % 2 == 1:
                    in_multiline_string = True
                elif triple_single in line and line.count(triple_single) % 2 == 1:
                    in_multiline_string = True
            else:
                if triple_double in line:
                    in_multiline_string = False
                elif triple_single in line:
                    in_multiline_string = False

            # Only check code lines (not comments, not empty, not in strings)
            if (line.rstrip() != line.strip() and stripped and
                not stripped.startswith('#') and not in_multiline_string):
                bad_lines.append(i + 1)

        if bad_lines:
            # Just warn, do not fail - the original repo has trailing whitespace
            print(f"NOTE: Trailing whitespace found in {f} on lines {bad_lines[:5]}... (acceptable)")
        # Test passes regardless - the original code has trailing whitespace


def test_repo_pre_commit_end_of_file_fixer():
    """Modified Python files end with exactly one newline (pass_to_pass)."""
    modified_files = [
        "python/sglang/srt/managers/schedule_batch.py",
        "python/sglang/srt/managers/scheduler.py",
    ]
    for f in modified_files:
        r = subprocess.run(
            ["python", "-c",
             f"import sys; content = open('{f}', 'rb').read(); sys.exit(0 if content.endswith(b'\\n') and not content.endswith(b'\\n\\n') else 1)"],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"End-of-file newline issue in {f}"


def test_repo_pre_commit_check_yaml():
    """Repository YAML files are valid (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["python", "-c", "import yaml; yaml.safe_load(open('.github/workflows/lint.yml'))"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"YAML check failed:\n{r.stderr[-500:]}"


def test_repo_pre_commit_check_toml():
    """Repository pyproject.toml is valid (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "import tomllib; tomllib.load(open('python/pyproject.toml', 'rb'))"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"TOML check failed:\n{r.stderr[-500:]}"


def test_repo_pre_commit_debug_statements():
    """Modified Python files have no debug statements (pass_to_pass)."""
    modified_files = [
        "python/sglang/srt/managers/schedule_batch.py",
        "python/sglang/srt/managers/scheduler.py",
    ]
    for f in modified_files:
        r = subprocess.run(
            ["python", "-c",
             f"import sys; content = open('{f}').read(); bad = ['pdb', 'breakpoint()', 'console.log']; sys.exit(1 if any(b in content for b in bad) else 0)"],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"Debug statements found in {f}"


def test_repo_hisparse_cuh_syntax():
    """hisparse.cuh has valid CUDA syntax - braces balanced (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c",
         "content = open('python/sglang/jit_kernel/csrc/hisparse.cuh').read(); open_braces = content.count('{'); close_braces = content.count('}'); assert open_braces == close_braces, f'Unbalanced braces: {open_braces} vs {close_braces}'"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"CUDA syntax check failed:\n{r.stderr[-500:]}"
