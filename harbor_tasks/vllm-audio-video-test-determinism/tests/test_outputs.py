"""
Task: vllm-audio-video-test-determinism
Repo: vllm-project/vllm @ c133f3374625652c88e122fff995e4126c4635c0
PR:   38492

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/vllm"
TARGET = f"{REPO}/tests/entrypoints/openai/chat_completion/test_audio_in_video.py"
FLAKY_FUNCS = [
    "test_online_audio_in_video",
    "test_online_audio_in_video_multi_videos",
]


def _load_target_ast() -> ast.AST:
    """Parse and return the AST of the target test file."""
    source = Path(TARGET).read_text()
    return ast.parse(source)


def _find_functions(tree: ast.AST, names: list) -> dict:
    """Return dict of {name: AST node} for async function defs matching names."""
    return {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and node.name in names
    }


def _get_keyword_value(node: ast.Call, keyword: str):
    """Extract the value of a keyword argument from a Call node."""
    for kw in node.keywords:
        if kw.arg == keyword:
            if isinstance(kw.value, ast.Constant):
                return kw.value.value
            if isinstance(kw.value, (ast.Num, ast.Str)):  # Python < 3.8 compat
                return kw.value.n if isinstance(kw.value, ast.Num) else kw.value.s
    return None


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must be valid Python."""
    source = Path(TARGET).read_text()
    compile(source, TARGET, "exec")


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via AST inspection
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_temperature_deterministic():
    """Both flaky test functions must set temperature=0.0 for deterministic output."""
    tree = _load_target_ast()
    funcs = _find_functions(tree, FLAKY_FUNCS)
    assert len(funcs) == len(FLAKY_FUNCS), f"Missing: {set(FLAKY_FUNCS) - set(funcs)}"

    for name, node in funcs.items():
        found = False
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                temp = _get_keyword_value(child, "temperature")
                if temp in (0, 0.0):
                    found = True
                    break
        assert found, f"{name} must set temperature=0.0 for deterministic generation"


# [pr_diff] fail_to_pass
def test_max_tokens_reduced():
    """Both flaky test functions must use max_tokens <= 8 to force length cutoff."""
    tree = _load_target_ast()
    funcs = _find_functions(tree, FLAKY_FUNCS)
    assert len(funcs) == len(FLAKY_FUNCS), f"Missing: {set(FLAKY_FUNCS) - set(funcs)}"

    for name, node in funcs.items():
        found = False
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                for kw in ("max_tokens", "max_completion_tokens"):
                    val = _get_keyword_value(child, kw)
                    if val is not None and isinstance(val, (int, float)) and val <= 8:
                        found = True
                        break
            if found:
                break
        assert found, f"{name} must set max_tokens <= 8 (was 16) to ensure model hits token limit"


# [pr_diff] fail_to_pass
def test_debug_output_added():
    """Both flaky test functions must include debug output referencing finish_reason."""
    tree = _load_target_ast()
    funcs = _find_functions(tree, FLAKY_FUNCS)
    assert len(funcs) == len(FLAKY_FUNCS), f"Missing: {set(FLAKY_FUNCS) - set(funcs)}"

    for name, node in funcs.items():
        has_debug = False
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func_name = ""
                if isinstance(child.func, ast.Name):
                    func_name = child.func.id
                elif isinstance(child.func, ast.Attribute):
                    func_name = child.func.attr

                if func_name == "print":
                    # Check if any argument contains "finish_reason"
                    for arg in child.args:
                        if isinstance(arg, ast.JoinedStr):
                            # f-string - check format specifiers
                            for val in arg.values:
                                if isinstance(val, ast.FormattedValue):
                                    if isinstance(val.value, ast.Attribute):
                                        if val.value.attr == "finish_reason":
                                            has_debug = True
                                            break
                        elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            if "finish_reason" in arg.value:
                                has_debug = True
                                break
                if has_debug:
                    break
        assert has_debug, f"{name} must include debug output referencing finish_reason"


# [pr_diff] fail_to_pass
def test_turn_variable_used():
    """Both flaky test functions must use 'turn' variable in the loop (changed from '_')."""
    tree = _load_target_ast()
    funcs = _find_functions(tree, FLAKY_FUNCS)
    assert len(funcs) == len(FLAKY_FUNCS), f"Missing: {set(FLAKY_FUNCS) - set(funcs)}"

    for name, node in funcs.items():
        found_turn_loop = False
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.AsyncFor)):
                # Check if the target is 'turn' (not '_')
                if isinstance(child.target, ast.Name) and child.target.id == "turn":
                    found_turn_loop = True
                    break
        assert found_turn_loop, f"{name} must use 'turn' as loop variable (changed from '_')"


# -----------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# -----------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_interleaved_test_preserved():
    """Third test function (interleaved) must still exist with a real body."""
    tree = _load_target_ast()
    funcs = _find_functions(tree, ["test_online_audio_in_video_interleaved"])
    assert "test_online_audio_in_video_interleaved" in funcs, (
        "test_online_audio_in_video_interleaved must not be deleted"
    )
    node = funcs["test_online_audio_in_video_interleaved"]
    body_stmts = [
        s for s in node.body
        if not isinstance(s, ast.Pass)
        and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
    ]
    assert len(body_stmts) >= 3, "test_online_audio_in_video_interleaved body looks like a stub"


# [pr_diff] pass_to_pass
def test_assertions_preserved():
    """Both flaky functions must still assert finish_reason=='length' and len(choices)==1."""
    tree = _load_target_ast()
    funcs = _find_functions(tree, FLAKY_FUNCS)
    assert len(funcs) == len(FLAKY_FUNCS), f"Missing functions: {set(FLAKY_FUNCS) - set(funcs)}"

    for name, node in funcs.items():
        has_finish_assert = False
        has_choices_assert = False
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                # Check for finish_reason == "length"
                if isinstance(child.test, ast.Compare):
                    left_dump = ast.dump(child.test.left)
                    if "finish_reason" in left_dump:
                        for comp in child.test.comparators:
                            if isinstance(comp, ast.Constant) and comp.value == "length":
                                has_finish_assert = True
                    # Check for len(choices) == 1
                    if "choices" in left_dump:
                        has_choices_assert = True
        assert has_finish_assert, f"{name} must assert finish_reason == 'length'"
        assert has_choices_assert, f"{name} must assert len(choices) == 1"


# [static] pass_to_pass
def test_not_stubs():
    """Both flaky functions must have substantial bodies (loop, await, assert)."""
    tree = _load_target_ast()
    funcs = _find_functions(tree, FLAKY_FUNCS)
    assert len(funcs) == len(FLAKY_FUNCS), f"Missing functions: {set(FLAKY_FUNCS) - set(funcs)}"

    for name, node in funcs.items():
        meaningful = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                                  ast.Assert, ast.Return, ast.For, ast.AsyncFor,
                                  ast.AsyncWith, ast.With)):
                meaningful += 1
            elif isinstance(child, ast.Expr) and isinstance(child.value, (ast.Call, ast.Await)):
                meaningful += 1
        has_loop = any(isinstance(c, (ast.For, ast.AsyncFor)) for c in ast.walk(node))
        has_await = any(isinstance(c, ast.Await) for c in ast.walk(node))
        has_assert = any(isinstance(c, ast.Assert) for c in ast.walk(node))
        assert meaningful >= 8, f"{name} has only {meaningful} statements — looks like a stub"
        assert has_loop, f"{name} must contain a loop (multi-turn testing)"
        assert has_await, f"{name} must contain await calls (async API calls)"
        assert has_assert, f"{name} must contain assertions"


# [pr_diff] pass_to_pass
def test_mm_processor_kwargs_preserved():
    """Both flaky functions must pass mm_processor_kwargs with use_audio_in_video."""
    tree = _load_target_ast()
    funcs = _find_functions(tree, FLAKY_FUNCS)
    assert len(funcs) == len(FLAKY_FUNCS), f"Missing functions: {set(FLAKY_FUNCS) - set(funcs)}"

    for name, node in funcs.items():
        src = ast.dump(node)
        assert "mm_processor_kwargs" in src, f"{name} must pass mm_processor_kwargs"
        assert "use_audio_in_video" in src, f"{name} must set use_audio_in_video"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's ruff linting passes on target test file (pass_to_pass)."""
    import subprocess
    import sys

    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "--quiet"],
        capture_output=True,
        timeout=60,
    )
    # Ignore pip install output; if ruff install fails, the next command will fail

    r = subprocess.run(
        ["ruff", "check", TARGET],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff formatting passes on target test file (pass_to_pass)."""
    import subprocess
    import sys

    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "--quiet"],
        capture_output=True,
        timeout=60,
    )

    r = subprocess.run(
        ["ruff", "format", "--check", TARGET],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_spdx_header():
    """Repo's SPDX header check passes on target test file (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/check_spdx_header.py", TARGET],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"SPDX header check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_boolean_context_manager():
    """Repo's boolean context manager check passes on target test file (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/check_boolean_context_manager.py", TARGET],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Boolean context manager check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_forbidden_imports():
    """Repo's forbidden imports check passes on target test file (pass_to_pass)."""
    import subprocess
    import sys

    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "regex", "--quiet"],
        capture_output=True,
        timeout=60,
    )

    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/check_forbidden_imports.py", TARGET],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Forbidden imports check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_torch_cuda():
    """Repo's torch.cuda API check passes on target test file (pass_to_pass)."""
    import subprocess
    import sys

    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "regex", "--quiet"],
        capture_output=True,
        timeout=60,
    )

    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/check_torch_cuda.py", TARGET],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Torch CUDA check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_init_lazy_imports():
    """Repo's root __init__ lazy imports check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/check_init_lazy_imports.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Init lazy imports check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_check_filenames():
    """Repo's filename check passes - no spaces in filenames (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", 'git ls-files | grep " " && echo "Filenames should not contain spaces!" && exit 1 || exit 0'],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Filename check failed (spaces in filenames):\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_no_symlink_utils():
    """Repo's symlink utils check passes on target test file (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c",
         "import sys; "
         "from pathlib import Path; "
         "content = Path(sys.argv[1]).read_text(); "
         "sys.exit(1 if 'from vllm.utils import' in content and 'symlink' in content else 0)",
         TARGET],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Symlink utils check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_validate_config():
    """Repo's config validation passes on target test file (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "regex", "--quiet"],
        capture_output=True,
        timeout=60,
    )
    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/validate_config.py", TARGET],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Config validation failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_shellcheck():
    """Repo's shellcheck passes on shell scripts (pass_to_pass)."""
    # Install shellcheck
    r = subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True,
        timeout=60,
    )
    r = subprocess.run(
        ["apt-get", "install", "-y", "shellcheck", "-qq"],
        capture_output=True,
        timeout=120,
    )
    # Run shellcheck via the repo's script
    r = subprocess.run(
        ["bash", f"{REPO}/tools/pre_commit/shellcheck.sh"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Shellcheck failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_actionlint():
    """Repo's actionlint passes on GitHub workflow files (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "actionlint-py", "--quiet"],
        capture_output=True,
        timeout=60,
    )
    r = subprocess.run(
        ["actionlint", f"{REPO}/.github/workflows/pre-commit.yml"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Actionlint failed:\n{r.stdout}\n{r.stderr}"
