"""
Task: gradio-file-sanitize-empty-stem
Repo: gradio-app/gradio @ f1cd0644d2608b493db07cd204c0831a111f9fb2
PR:   12979

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/gradio"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    import py_compile

    py_compile.compile(
        f"{REPO}/client/python/gradio_client/utils.py", doraise=True
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_empty_stem_gets_fallback():
    """Filename with entirely-stripped stem preserves the extension."""
    import re
    from gradio_client.utils import strip_invalid_filename_characters

    INVALID = re.compile(r"[^a-zA-Z0-9._\-, ]")

    for fname, expected_suffix in [("#.txt", ".txt"), ("###.pdf", ".pdf"), ("@!$.csv", ".csv")]:
        result = strip_invalid_filename_characters(fname)
        p = Path(result)
        # Sanitization must have removed invalid chars
        assert not INVALID.search(result), (
            f"{fname}: invalid chars remain in {result!r}"
        )
        # Extension must be preserved
        assert p.suffix == expected_suffix, (
            f"{fname}: expected suffix {expected_suffix}, got {p.suffix!r} from {result!r}"
        )
        # Stem must not be empty
        assert p.stem != "", f"{fname}: stem should not be empty, got {result!r}"


# [pr_diff] pass_to_pass
def test_partial_strip_keeps_original_stem():
    """When some stem chars survive sanitization, no fallback is injected."""
    from gradio_client.utils import strip_invalid_filename_characters

    assert strip_invalid_filename_characters("a#.txt") == "a.txt"
    assert strip_invalid_filename_characters("1#2.csv") == "12.csv"
    assert strip_invalid_filename_characters("hello#world.py") == "helloworld.py"


# [pr_diff] fail_to_pass
def test_bare_dotfile_not_produced():
    """Result is never just the extension (a bare dotfile)."""
    import re
    from gradio_client.utils import strip_invalid_filename_characters

    INVALID = re.compile(r"[^a-zA-Z0-9._\-, ]")

    for fname in ["#.txt", "!!!.json", "&&&.tar.gz"]:
        result = strip_invalid_filename_characters(fname)
        # Must have sanitized invalid chars
        assert not INVALID.search(result), (
            f"{fname}: invalid chars remain in {result!r}"
        )
        # A bare dotfile like ".txt" has no suffix in pathlib
        assert Path(result).suffix != "", (
            f"{fname}: produced bare dotfile {result!r} (suffix is empty)"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_strip_behavior():
    """Existing sanitization cases still produce correct results."""
    from gradio_client.utils import strip_invalid_filename_characters

    cases = [
        ("abc", "abc"),
        ("$$AAabc&3", "AAabc3"),
        ("$$AAa&..b-c3_", "AAa..b-c3_"),
        ("hello world.txt", "hello world.txt"),
        ("normal-file_v2.py", "normal-file_v2.py"),
    ]
    for inp, expected in cases:
        result = strip_invalid_filename_characters(inp)
        assert result == expected, f"{inp!r}: expected {expected!r}, got {result!r}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """strip_invalid_filename_characters has real logic, not just pass/return."""
    import ast

    src = Path(f"{REPO}/client/python/gradio_client/utils.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "strip_invalid_filename_characters":
            body_stmts = [
                n for n in node.body
                if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))
                and not isinstance(n, ast.Pass)
            ]
            assert len(body_stmts) > 2, (
                f"Function body looks stubbed ({len(body_stmts)} real stmts)"
            )
            return
    raise AssertionError("Function strip_invalid_filename_characters not found")


