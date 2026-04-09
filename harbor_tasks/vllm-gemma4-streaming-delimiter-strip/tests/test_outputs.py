"""
Task: vllm-gemma4-streaming-delimiter-strip
Repo: vllm @ 1af6f78ae5a1bd3d70f32d47fe4901bda5c97fdd
PR:   38992

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/vllm"
PARSER_FILE = Path(f"{REPO}/vllm/tool_parsers/gemma4_tool_parser.py")


def _extract_strip_chars():
    """Extract the character set from _emit_argument_diff's safe_json while loop.

    Parses the AST to find:
        while safe_json and safe_json[-1] in (...):
    and returns the set of characters in the tuple.
    """
    src = PARSER_FILE.read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_emit_argument_diff":
            for child in ast.walk(node):
                if not isinstance(child, ast.While):
                    continue
                test = child.test
                if not isinstance(test, ast.BoolOp) or not isinstance(test.op, ast.And):
                    continue
                for value in test.values:
                    if isinstance(value, ast.Compare):
                        for comp in value.comparators:
                            if isinstance(comp, ast.Tuple):
                                return {ast.literal_eval(e) for e in comp.elts}

    raise AssertionError(
        "Could not find safe_json stripping loop in _emit_argument_diff"
    )


def _apply_strip(json_str, chars):
    """Replicate the stripping logic from _emit_argument_diff."""
    safe = json_str
    while safe and safe[-1] in chars:
        safe = safe[:-1]
    return safe


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "vllm/tool_parsers/gemma4_tool_parser.py"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_partial_delimiter_chars_stripped():
    """Partial STRING_DELIM fragments (<, |, >) must be stripped from safe JSON.

    When streaming splits <|"|> at a token boundary, the parsed value gets a
    trailing fragment like '<|'. After json.dumps the stripping loop must
    remove those chars so they never appear in the streamed output.
    """
    chars = _extract_strip_chars()

    # Each tuple: (raw dict → json.dumps, description)
    # We vary the trailing fragment to avoid single-value hardcoding.
    cases = [
        ({"content": "Buy milk<|"}, "trailing <|"),
        ({"content": "hello|"}, "trailing |"),
        ({"value": "test>"}, "trailing >"),
        ({"name": "foo<"}, "trailing <"),
        ({"x": "bar>|<"}, "trailing >|<"),
    ]
    for obj, desc in cases:
        json_str = json.dumps(obj, ensure_ascii=False)
        safe = _apply_strip(json_str, chars)
        for c in "<|>":
            assert not safe.endswith(c), (
                f"Delimiter char '{c}' leaked at end of safe JSON ({desc}): "
                f"{safe!r} (from {json_str!r})"
            )


# [pr_diff] fail_to_pass
def test_streaming_split_delimiter_end_to_end():
    """End-to-end: parse partial Gemma4 args with split delimiter, strip, verify.

    Extracts _parse_gemma4_args from source (avoids importing torch/vllm),
    runs the full pipeline parse → json.dumps → strip, and checks the safe
    prefix is free of delimiter fragments.
    """
    script = textwrap.dedent(r'''
        import ast, json, sys

        with open("vllm/tool_parsers/gemma4_tool_parser.py") as f:
            src = f.read()
        tree = ast.parse(src)

        # --- Extract pure-Python functions from module source ---
        needed = {"STRING_DELIM", "_parse_gemma4_args", "_parse_gemma4_array"}
        segments = []
        for node in tree.body:
            name = None
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id in needed:
                        name = t.id
            elif isinstance(node, ast.FunctionDef) and node.name in needed:
                name = node.name
            if name:
                seg = ast.get_source_segment(src, node)
                if seg:
                    segments.append(seg)

        code = "import regex as re\nimport json\n\n" + "\n\n".join(segments)
        ns = {}
        exec(code, ns)
        parse_args = ns["_parse_gemma4_args"]

        # --- Extract strip char set from _emit_argument_diff ---
        strip_chars = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_emit_argument_diff":
                for child in ast.walk(node):
                    if isinstance(child, ast.While):
                        test = child.test
                        if isinstance(test, ast.BoolOp):
                            for val in test.values:
                                if isinstance(val, ast.Compare):
                                    for comp in val.comparators:
                                        if isinstance(comp, ast.Tuple):
                                            strip_chars = {
                                                ast.literal_eval(e) for e in comp.elts
                                            }
        assert strip_chars, "Could not find strip char set in _emit_argument_diff"

        # --- Simulate streaming with split delimiter ---
        # Token boundary splits <|"|> so parser sees 'Buy milk<|' as an
        # unterminated string value.
        partial_inputs = [
            ('content:<|"|>Buy milk<|', "Buy milk"),
            ('task:<|"|>Write code<|"|', "Write code"),
            ('item:<|"|>eggs>|', "eggs"),
        ]
        for raw_args, expected_clean_value in partial_inputs:
            result = parse_args(raw_args)
            json_str = json.dumps(result, ensure_ascii=False)

            safe = json_str
            while safe and safe[-1] in strip_chars:
                safe = safe[:-1]

            # No partial delimiter chars at the end of safe prefix
            for c in "<|>\\":
                assert not safe.endswith(c), (
                    f"FAIL: '{c}' leaked in safe prefix: {safe!r} "
                    f"(input: {raw_args!r})"
                )

        print("PASS")
    ''')

    r = subprocess.run(
        ["python3", "-c", script],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    stdout, stderr = r.stdout.decode(), r.stderr.decode()
    assert r.returncode == 0 and "PASS" in stdout, (
        f"End-to-end test failed:\nstdout: {stdout}\nstderr: {stderr}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_parse_args_basic_regression():
    """_parse_gemma4_args still correctly parses normal Gemma4 arg strings."""
    script = textwrap.dedent(r'''
        import ast, json, sys

        with open("vllm/tool_parsers/gemma4_tool_parser.py") as f:
            src = f.read()
        tree = ast.parse(src)

        needed = {"STRING_DELIM", "_parse_gemma4_args", "_parse_gemma4_array"}
        segments = []
        for node in tree.body:
            name = None
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id in needed:
                        name = t.id
            elif isinstance(node, ast.FunctionDef) and node.name in needed:
                name = node.name
            if name:
                seg = ast.get_source_segment(src, node)
                if seg:
                    segments.append(seg)

        code = "import regex as re\nimport json\n\n" + "\n\n".join(segments)
        ns = {}
        exec(code, ns)
        parse_args = ns["_parse_gemma4_args"]

        # These must always work regardless of the fix
        assert parse_args('location:<|"|>Paris<|"|>') == {"location": "Paris"}
        assert parse_args('count:42,flag:true') == {"count": 42, "flag": True}
        assert parse_args('a:<|"|>hello<|"|>,b:<|"|>world<|"|>') == {
            "a": "hello", "b": "world"
        }
        assert parse_args('') == {}
        assert parse_args('score:3.14') == {"score": 3.14}
        assert parse_args('nested:{x:<|"|>v<|"|>}') == {"nested": {"x": "v"}}

        print("PASS")
    ''')

    r = subprocess.run(
        ["python3", "-c", script],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    stdout, stderr = r.stdout.decode(), r.stderr.decode()
    assert r.returncode == 0 and "PASS" in stdout, (
        f"Regression test failed:\nstdout: {stdout}\nstderr: {stderr}"
    )


# [static] pass_to_pass
def test_not_stub():
    """_emit_argument_diff has real logic, not just pass/return."""
    src = PARSER_FILE.read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_emit_argument_diff":
            found = True
            stmts = [
                s
                for s in node.body
                if not isinstance(s, (ast.Pass, ast.Expr))
            ]
            assert len(stmts) >= 3, (
                f"_emit_argument_diff body has only {len(stmts)} statements — "
                "looks like a stub"
            )
            has_while = any(isinstance(s, ast.While) for s in ast.walk(node))
            assert has_while, (
                "_emit_argument_diff missing while loop (stripping logic)"
            )
            break

    assert found, "_emit_argument_diff method not found in parser module"
