"""
Task: transformers-jitscript-copied-comment-py313
Repo: huggingface/transformers @ 0e1978c9eb69ec64b55245212dbf63deab19d25b
PR:   44986

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

AST-only because: torch is not installed in the test image (functions use
@torch.jit.script and tensor ops — cannot be imported or called without GPU libs).
"""

import ast
import re
import subprocess
from pathlib import Path

REPO = "/workspace/huggingface__transformers"

DEBERTA = f"{REPO}/src/transformers/models/deberta_v2/modeling_deberta_v2.py"
SEW_D = f"{REPO}/src/transformers/models/sew_d/modeling_sew_d.py"

AFFECTED_FILES = [DEBERTA, SEW_D]

EXPECTED_FUNCS = {
    "c2p_dynamic_expand": ["c2p_pos", "query_layer", "relative_pos"],
    "p2c_dynamic_expand": ["c2p_pos", "query_layer", "key_layer"],
    "pos_dynamic_expand": ["pos_index", "p2c_att", "key_layer"],
}


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both affected files must be valid Python."""
    for filepath in AFFECTED_FILES:
        src = Path(filepath).read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_content_between_decorator_and_def():
    """No non-blank, non-def content between @torch.jit.script and def statement.
    This directly checks the root cause: comments between decorator and def
    break Python 3.13's stricter parser via inspect.getsource + ast.parse."""
    for filepath in AFFECTED_FILES:
        lines = Path(filepath).read_text().splitlines()
        violations = []
        for i, line in enumerate(lines):
            if line.strip() == "@torch.jit.script":
                j = i + 1
                # Skip blank lines (those are harmless)
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                if j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line.startswith("def "):
                        violations.append(
                            f"{filepath} line {j + 1}: {next_line!r}"
                        )
        assert not violations, (
            f"Content between @torch.jit.script and def will break "
            f"Python 3.13 import:\n" + "\n".join(violations)
        )


# [pr_diff] fail_to_pass
def test_no_copied_from_breaks_jit_pattern():
    """The '# Copied from' comments must not appear immediately after
    @torch.jit.script decorators. This specific pattern (decorator followed by
    copy-tracking comment then def) is what triggers the Python 3.13
    IndentationError via torch.jit.script's inspect.getsource call."""
    pattern = re.compile(
        r"@torch\.jit\.script\s*\n\s*#\s*Copied\s+from\s+",
        re.MULTILINE,
    )
    for filepath in AFFECTED_FILES:
        src = Path(filepath).read_text()
        matches = list(pattern.finditer(src))
        assert not matches, (
            f"{filepath}: found {len(matches)} '# Copied from' comment(s) "
            f"after @torch.jit.script — this breaks Python 3.13 import"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_functions_preserved_with_signatures():
    """All three jit-scripted functions exist in both files with correct
    parameter names and @torch.jit.script decorator."""
    for filepath in AFFECTED_FILES:
        src = Path(filepath).read_text()
        tree = ast.parse(src)
        found = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in EXPECTED_FUNCS:
                args = [a.arg for a in node.args.args]
                # Verify @torch.jit.script decorator
                has_jit = any(
                    "torch" in ast.dump(d)
                    and "jit" in ast.dump(d)
                    and "script" in ast.dump(d)
                    for d in node.decorator_list
                )
                assert has_jit, (
                    f"{filepath}: {node.name} missing @torch.jit.script decorator"
                )
                found[node.name] = args

        for name, expected_args in EXPECTED_FUNCS.items():
            assert name in found, f"{filepath}: function {name} not found"
            assert found[name] == expected_args, (
                f"{filepath}: {name} args {found[name]} != expected {expected_args}"
            )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_function_bodies_nontrivial():
    """Each function body must contain real tensor operations: at least 3
    combined Call + Subscript AST nodes (the real .expand([...size()...])
    patterns have 4-5 each). Rejects stubs like return None or return x."""

    class NodeCounter(ast.NodeVisitor):
        def __init__(self):
            self.count = 0

        def visit_Call(self, node):
            self.count += 1
            self.generic_visit(node)

        def visit_Subscript(self, node):
            self.count += 1
            self.generic_visit(node)

    for filepath in AFFECTED_FILES:
        tree = ast.parse(Path(filepath).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in EXPECTED_FUNCS:
                # Must have a return with a value
                returns = [
                    n
                    for n in ast.walk(node)
                    if isinstance(n, ast.Return) and n.value is not None
                ]
                assert returns, (
                    f"{filepath}: {node.name} has no return with value (stub)"
                )
                counter = NodeCounter()
                for stmt in node.body:
                    counter.visit(stmt)
                assert counter.count >= 3, (
                    f"{filepath}: {node.name} body too trivial "
                    f"({counter.count} Call+Subscript nodes, need >=3)"
                )


# ---------------------------------------------------------------------------
# Repo CI tests (repo_tests) — actual CI commands from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — CI: make style (ruff check)
def test_ruff_lint():
    """Ruff lint passes on both affected files (CI: make style)."""
    # Use the repo's own pyproject.toml ruff config (which ignores E501 etc.)
    r = subprocess.run(
        ["ruff", "check", "--quiet"] + AFFECTED_FILES,
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Ruff lint failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [repo_tests] pass_to_pass
def test_ruff_format_check():
    """Ruff format check passes on affected files (CI: make style)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "--quiet"] + AFFECTED_FILES,
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Ruff format check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [repo_tests] pass_to_pass
def test_py_compile_deberta_v2():
    """Deberta V2 model file compiles without syntax errors (CI: py_compile)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", DEBERTA],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Python syntax check failed for deberta_v2:\n{r.stderr.decode()}"
    )


# [repo_tests] pass_to_pass
def test_py_compile_sew_d():
    """SEW-D model file compiles without syntax errors (CI: py_compile)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", SEW_D],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Python syntax check failed for sew_d:\n{r.stderr.decode()}"
    )


# [repo_tests] pass_to_pass
def test_repo_check_inits():
    """Repository init structure check passes (CI: make check-repo)."""
    r = subprocess.run(
        ["python", "utils/check_inits.py"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"Repository init check failed:\n{r.stderr.decode()[-500:]}"
    )
