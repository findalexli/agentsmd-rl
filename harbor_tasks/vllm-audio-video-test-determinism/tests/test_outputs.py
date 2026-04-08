"""
Task: vllm-audio-video-test-determinism
Repo: vllm-project/vllm @ c133f3374625652c88e122fff995e4126c4635c0
PR:   38492

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/vllm"
TARGET = f"{REPO}/tests/entrypoints/openai/chat_completion/test_audio_in_video.py"
FLAKY_FUNCS = [
    "test_online_audio_in_video",
    "test_online_audio_in_video_multi_videos",
]


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python validation code in a subprocess."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _find_functions(tree, names):
    """Return dict of {name: AST node} for async function defs matching names."""
    return {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and node.name in names
    }


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must be valid Python."""
    source = Path(TARGET).read_text()
    compile(source, TARGET, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_temperature_deterministic():
    """Both flaky test functions must set temperature=0.0 for deterministic output."""
    r = _run_py(
        f"""
import ast
from pathlib import Path

TARGET = {TARGET!r}
FLAKY_FUNCS = {FLAKY_FUNCS!r}

tree = ast.parse(Path(TARGET).read_text())
funcs = {{
    node.name: node
    for node in ast.walk(tree)
    if isinstance(node, ast.AsyncFunctionDef) and node.name in FLAKY_FUNCS
}}
assert len(funcs) == len(FLAKY_FUNCS), f"Missing: {{set(FLAKY_FUNCS) - set(funcs)}}"

for name, node in funcs.items():
    found = False
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            for kw in child.keywords:
                if kw.arg == "temperature":
                    if isinstance(kw.value, ast.Constant) and kw.value.value in (0, 0.0):
                        found = True
                if kw.arg is None and isinstance(kw.value, ast.Dict):
                    for k, v in zip(kw.value.keys, kw.value.values):
                        if isinstance(k, ast.Constant) and k.value == "temperature":
                            if isinstance(v, ast.Constant) and v.value in (0, 0.0):
                                found = True
    assert found, f"{{name}} must set temperature=0.0 for deterministic generation"
print("PASS")
"""
    )
    assert r.returncode == 0, f"temperature check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_max_tokens_reduced():
    """Both flaky test functions must use max_tokens <= 8 to force length cutoff."""
    r = _run_py(
        f"""
import ast
from pathlib import Path

TARGET = {TARGET!r}
FLAKY_FUNCS = {FLAKY_FUNCS!r}

tree = ast.parse(Path(TARGET).read_text())
funcs = {{
    node.name: node
    for node in ast.walk(tree)
    if isinstance(node, ast.AsyncFunctionDef) and node.name in FLAKY_FUNCS
}}
assert len(funcs) == len(FLAKY_FUNCS), f"Missing: {{set(FLAKY_FUNCS) - set(funcs)}}"

for name, node in funcs.items():
    found = False
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            for kw in child.keywords:
                if kw.arg in ("max_tokens", "max_completion_tokens"):
                    if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, (int, float)):
                        if kw.value.value <= 8:
                            found = True
    assert found, f"{{name}} must set max_tokens <= 8 (was 16) to ensure model hits token limit"
print("PASS")
"""
    )
    assert r.returncode == 0, f"max_tokens check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_debug_output_added():
    """Both flaky test functions must include debug output referencing finish_reason."""
    r = _run_py(
        f"""
import ast
from pathlib import Path

TARGET = {TARGET!r}
FLAKY_FUNCS = {FLAKY_FUNCS!r}

tree = ast.parse(Path(TARGET).read_text())
funcs = {{
    node.name: node
    for node in ast.walk(tree)
    if isinstance(node, ast.AsyncFunctionDef) and node.name in FLAKY_FUNCS
}}
assert len(funcs) == len(FLAKY_FUNCS), f"Missing: {{set(FLAKY_FUNCS) - set(funcs)}}"

for name, node in funcs.items():
    has_debug = False
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            call_src = ast.dump(child)
            func_name = ""
            if isinstance(child.func, ast.Name):
                func_name = child.func.id
            elif isinstance(child.func, ast.Attribute):
                func_name = child.func.attr
            if func_name in ("print", "debug", "info", "warning", "log"):
                if "finish_reason" in call_src:
                    has_debug = True
                    break
    assert has_debug, f"{{name}} must include debug output referencing finish_reason"
print("PASS")
"""
    )
    assert r.returncode == 0, f"debug output check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_interleaved_test_preserved():
    """Third test function (interleaved) must still exist with a real body."""
    tree = ast.parse(Path(TARGET).read_text())
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
    tree = ast.parse(Path(TARGET).read_text())
    funcs = _find_functions(tree, FLAKY_FUNCS)
    assert len(funcs) == len(FLAKY_FUNCS), f"Missing functions: {set(FLAKY_FUNCS) - set(funcs)}"

    for name, node in funcs.items():
        has_finish_assert = False
        has_choices_assert = False
        for child in ast.walk(node):
            if isinstance(child, ast.Assert) and isinstance(child.test, ast.Compare):
                left_dump = ast.dump(child.test.left)
                if "finish_reason" in left_dump:
                    for comp in child.test.comparators:
                        if isinstance(comp, ast.Constant) and comp.value == "length":
                            has_finish_assert = True
                if "choices" in left_dump:
                    has_choices_assert = True
        assert has_finish_assert, f"{name} must assert finish_reason == 'length'"
        assert has_choices_assert, f"{name} must assert len(choices) == 1"


# [static] pass_to_pass
def test_not_stubs():
    """Both flaky functions must have substantial bodies (loop, await, assert)."""
    tree = ast.parse(Path(TARGET).read_text())
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
    tree = ast.parse(Path(TARGET).read_text())
    funcs = _find_functions(tree, FLAKY_FUNCS)
    assert len(funcs) == len(FLAKY_FUNCS), f"Missing functions: {set(FLAKY_FUNCS) - set(funcs)}"

    for name, node in funcs.items():
        src = ast.dump(node)
        assert "mm_processor_kwargs" in src, f"{name} must pass mm_processor_kwargs"
        assert "use_audio_in_video" in src, f"{name} must set use_audio_in_video"
