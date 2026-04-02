"""
Task: transformers-phi3-batchencoding-sdpa-skip
Repo: huggingface/transformers @ 44686173b26bb174f3c7eb6e59f08a338d1adf54
PR:   #45004

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: AST-based checks are used because the actual Phi-3 tests require
multi-GB model weights and GPU hardware (SDPA flash attention).
AST checks detect the BUG PATTERN, not a specific fix pattern,
so any valid fix passes.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/transformers"
PHI3_TEST = f"{REPO}/tests/models/phi3/test_modeling_phi3.py"
COMMON_TEST = f"{REPO}/tests/test_modeling_common.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile

    for path in [PHI3_TEST, COMMON_TEST]:
        py_compile.compile(path, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_phi3_generate_no_bare_inputs():
    """No model.generate() call passes bare 'inputs' as a positional arg.

    Buggy pattern: model.generate(inputs, max_new_tokens=32)
    Valid fixes: model.generate(**inputs, ...) or model.generate(inputs["input_ids"], ...)
    """
    source = Path(PHI3_TEST).read_text()
    tree = ast.parse(source)

    buggy_calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (isinstance(node.func, ast.Attribute) and node.func.attr == "generate"):
            continue
        for arg in node.args:
            if isinstance(arg, ast.Name) and arg.id == "inputs":
                buggy_calls.append(f"line {node.lineno}")

    assert not buggy_calls, (
        f"generate() calls still pass bare 'inputs' as positional arg: {buggy_calls}"
    )

    # Sanity: generate() calls should still exist (not deleted)
    gen_calls = sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "generate"
    )
    assert gen_calls >= 4, (
        f"Expected at least 4 generate() calls in phi3 test, found {gen_calls}"
    )


# [pr_diff] fail_to_pass
def test_sdpa_skip_new_models():
    """test_sdpa_can_dispatch_on_flash skip list includes EvollaModel, parakeet_encoder, parakeet_ctc, pi0."""
    source = Path(COMMON_TEST).read_text()
    tree = ast.parse(source)

    func_node = _find_function(tree, "test_sdpa_can_dispatch_on_flash")
    assert func_node is not None, "test_sdpa_can_dispatch_on_flash not found"

    string_literals = {
        child.value
        for child in ast.walk(func_node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    }

    required = ["evolla", "parakeet_encoder", "parakeet_ctc", "pi0"]
    missing = [
        key
        for key in required
        if not any(key in s.lower() for s in string_literals)
    ]
    assert not missing, f"Missing from SDPA skip list (as code literals): {missing}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_sdpa_skip_existing_models_preserved():
    """Existing SDPA skip entries and PaliGemma logic must not be removed."""
    source = Path(COMMON_TEST).read_text()
    tree = ast.parse(source)

    func_node = _find_function(tree, "test_sdpa_can_dispatch_on_flash")
    assert func_node is not None, "test_sdpa_can_dispatch_on_flash not found"

    string_literals = {
        child.value
        for child in ast.walk(func_node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    }

    existing_required = ["modernbert", "gemma3", "pixtral", "sam", "kosmos-2", "mllama"]
    missing = [r for r in existing_required if r not in string_literals]
    assert not missing, f"Existing skip entries removed: {missing}"

    # PaliGemma skip logic must also exist (can be string, Name, or Attribute)
    func_lines = source.splitlines()[func_node.lineno - 1 : func_node.end_lineno]
    func_text = "\n".join(func_lines)
    assert "paligemma" in func_text.lower(), "PaliGemma skip logic removed"


# [pr_diff] pass_to_pass
def test_phi3_test_methods_intact():
    """All four Phi3 integration test methods still defined with non-trivial bodies."""
    source = Path(PHI3_TEST).read_text()
    tree = ast.parse(source)

    required_methods = [
        "test_phi3_mini_4k_instruct_generation",
        "test_phi3_mini_4k_instruct_with_static_cache",
        "test_phi3_mini_128k_instruct_generation",
        "test_phi3_mini_128k_instruct_with_static_cache",
    ]

    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in required_methods:
            body = [
                n
                for n in node.body
                if not isinstance(n, ast.Expr)
                or not isinstance(getattr(n, "value", None), ast.Constant)
            ]
            if len(body) >= 2:
                found.add(node.name)

    missing = set(required_methods) - found
    assert not missing, f"Test methods missing or stubbed out: {missing}"


# ---------------------------------------------------------------------------
# Anti-stub (static) — meaningful changes detected
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_meaningful_changes():
    """Both target files have meaningful (non-comment, non-whitespace) diffs."""
    phi3_changes = _count_code_changes("tests/models/phi3/test_modeling_phi3.py")
    common_changes = _count_code_changes("tests/test_modeling_common.py")

    assert phi3_changes >= 2, (
        f"Only {phi3_changes} meaningful change(s) in phi3 test (need >=2)"
    )
    assert common_changes >= 1, (
        f"Only {common_changes} meaningful change(s) in test_modeling_common.py (need >=1)"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — ruff style check
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:2 @ 44686173b26bb174f3c7eb6e59f08a338d1adf54
def test_ruff_style():
    """Modified files pass ruff lint (CLAUDE.md: 'make style: runs formatters and linters (ruff)')."""
    for path in [PHI3_TEST, COMMON_TEST]:
        r = subprocess.run(
            ["ruff", "check", path, "--select", "E,W", "--ignore", "E501", "--quiet"],
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, f"ruff check failed on {path}:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [agent_config] pass_to_pass — CLAUDE.md:66 @ 44686173b26bb174f3c7eb6e59f08a338d1adf54
def test_copied_from_not_edited():
    """'# Copied from' blocks must not be edited (CLAUDE.md: will be reverted by make fix-repo).

    AST-only because: checking comment presence requires source text scanning, not execution.
    """
    for path in [PHI3_TEST, COMMON_TEST]:
        source = Path(path).read_text()
        # Collect all '# Copied from' lines with their line numbers
        copied_lines = [
            (i + 1, line)
            for i, line in enumerate(source.splitlines())
            if line.strip().startswith("# Copied from")
        ]
        # Verify via git diff that none of these lines were touched
        r = subprocess.run(
            ["git", "diff", "HEAD", "--", path],
            capture_output=True, text=True, cwd=REPO,
        )
        if not r.stdout.strip():
            # Try --cached in case changes are staged
            r = subprocess.run(
                ["git", "diff", "--cached", "--", path],
                capture_output=True, text=True, cwd=REPO,
            )
        diff_text = r.stdout
        for lineno, line in copied_lines:
            marker = line.strip()
            # If the diff removes or modifies a Copied from line, fail
            assert f"-{line}" not in diff_text and f"-{marker}" not in diff_text, (
                f"'# Copied from' block edited at {path}:{lineno} — "
                "this will be reverted by make fix-repo"
            )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:16 @ 44686173b26bb174f3c7eb6e59f08a338d1adf54
def test_no_new_test_files():
    """Tests should be added to existing files, not new ones (copilot-instructions.md:16).

    Verifies no new test_*.py files were created in the tests/ directory.
    """
    r = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=A", "HEAD"],
        capture_output=True, text=True, cwd=REPO,
    )
    if not r.stdout.strip():
        r = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=A", "--cached"],
            capture_output=True, text=True, cwd=REPO,
        )
    new_files = r.stdout.strip().splitlines()
    new_test_files = [f for f in new_files if f.startswith("tests/") and f.endswith(".py")]
    assert not new_test_files, (
        f"New test files created (should add to existing files instead): {new_test_files}"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def _count_code_changes(filepath):
    for ref in ["HEAD", "--cached", "HEAD~1"]:
        args = ["git", "diff"]
        if ref == "--cached":
            args.append("--cached")
        else:
            args.append(ref)
        args.extend(["--", filepath])
        result = subprocess.run(args, capture_output=True, text=True, cwd=REPO)
        if result.stdout.strip():
            lines = result.stdout.splitlines()
            code = [
                l
                for l in lines
                if (l.startswith("+") or l.startswith("-"))
                and not l.startswith("+++")
                and not l.startswith("---")
            ]
            meaningful = [
                l for l in code if l[1:].strip() and not l[1:].strip().startswith("#")
            ]
            return len(meaningful)
    return 0
