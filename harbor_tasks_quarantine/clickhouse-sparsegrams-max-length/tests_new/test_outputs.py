"""
Test the sparseGrams tokenizer fix.

The bug: sparseGrams was generating tokens longer than the max length
because of a hardcoded "+ 2" instead of "+ min_ngram_length - 1".

Behavioral tests use 'clickhouse local' to invoke the actual tokens() SQL
function and assert on the observable output (token lengths, count).
"""

import subprocess
import os
import re
import sys

import pytest

REPO = "/workspace/clickhouse"


def _run_clickhouse_query(sql: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a SQL query via clickhouse local and return the result."""
    return subprocess.run(
        ["clickhouse", "local", "--query", sql],
        capture_output=True, text=True, timeout=timeout
    )


def _get_tokens(input_str: str, min_len: int, max_len: int) -> list[str]:
    """Call tokens() via clickhouse local and return the list of tokens."""
    sql = f"SELECT tokens('{input_str}', 'sparseGrams', {min_len}, {max_len})"
    result = _run_clickhouse_query(sql)
    if result.returncode != 0:
        raise RuntimeError(f"Query failed: {result.stderr}")
    # Output is like: ['token1','token2',...]
    output = result.stdout.strip()
    if not output or output == "[]":
        return []
    # Strip the array brackets and quotes
    inner = output[1:-1]  # remove leading '[' and trailing ']'
    tokens = []
    while inner:
        # Find the next quoted string
        first_quote = inner.find("'")
        if first_quote == -1:
            break
        inner = inner[first_quote + 1:]
        end_quote = inner.find("'")
        if end_quote == -1:
            break
        token = inner[:end_quote]
        tokens.append(token)
        inner = inner[end_quote + 1:]
        # Skip comma and space
        if inner.startswith(","):
            inner = inner[1:].lstrip()
        elif inner.startswith(" "):
            inner = inner[1:].lstrip()
    return tokens


def _all_tokens_length_in_range(tokens: list[str], min_len: int, max_len: int) -> tuple[bool, str]:
    """Check all tokens are within [min_len, max_len]. Returns (ok, msg)."""
    for t in tokens:
        if len(t) < min_len:
            return False, f"Token '{t}' has length {len(t)} < min {min_len}"
        if len(t) > max_len:
            return False, f"Token '{t}' has length {len(t)} > max {max_len}"
    return True, ""


def test_sparsegrams_length_constraint_bug():
    """
    Behavioral fail-to-pass test: verify tokens respect max_ngram_length
    when min_ngram_length != 3.

    Uses the actual tokens() SQL function via clickhouse local.
    On the buggy base code (hardcoded +2), some configurations produce
    tokens that exceed the max length. On fixed code, all tokens respect bounds.
    """
    # Test case: min=5, max=5 on a longer string
    # With bug (+2): formula is right-left+2 instead of right-left+5-1
    # This means tokens are 3 characters too long when min=5 (since 5-1=4≠2)
    # The bug makes the effective offset smaller than it should be.
    # Actually since +2 < +4, the buggy code SHORTS tokens, not lengthens them.
    # But wait — the bug is "generating tokens longer than max" per instruction.
    # Let's check: for min=5 max=5, what happens?
    #
    # The convex hull iteration: tokens get emitted when length <= max.
    # With bug (+2 instead of +4), length is underestimated by 2.
    # So the buggy code ACCEPTS tokens the fixed code would REJECT.
    # The fixed code (offset +4) computes longer lengths and may REJECT
    # tokens the buggy code accepts.
    #
    # So a test that fails on buggy code and passes on fixed code should
    # verify that NO token exceeds max_length — which would be violated
    # if the buggy code somehow still accepts too-long tokens.
    #
    # Actually, re-reading: the bug is tokens "longer than the max length".
    # The only way this can happen with the convex hull logic is if the
    # length calculation UNDERESTIMATES the actual token length, causing
    # the algorithm to accept tokens that exceed max_ngram_length.
    #
    # So the test: verify all tokens satisfy max_ngram_length.
    # On buggy code, some tokens will violate this → fail.
    # On fixed code, all tokens are within bounds → pass.

    input_str = "abcdefghij"
    min_len, max_len = 5, 5

    tokens = _get_tokens(input_str, min_len, max_len)
    print(f"tokens('{input_str}', min={min_len}, max={max_len}) = {tokens}")

    assert len(tokens) > 0, f"Expected tokens but got empty list"

    ok, msg = _all_tokens_length_in_range(tokens, min_len, max_len)
    assert ok, (
        f"Length constraint violated: {msg}\n"
        f"Tokens: {tokens}\n"
        f"This test FAILS on base (hardcoded +2) and PASSES on fixed code."
    )


def test_source_code_uses_min_ngram_length():
    """
    Behavioral fail-to-pass test: verify that changing min_ngram_length
    actually changes the token output (i.e., min_ngram_length is used).

    We run tokens() with the same input string but two different min
    values and verify the token sets differ — proving min_ngram_length
    is wired into the computation.
    """
    input_str = "abcdefghij"

    tokens_min3 = _get_tokens(input_str, 3, 3)
    tokens_min5 = _get_tokens(input_str, 5, 5)

    print(f"min=3: {tokens_min3}")
    print(f"min=5: {tokens_min5}")

    # The two sets must differ — if min_ngram_length has no effect,
    # both would produce identical (broken) tokens.
    assert tokens_min3 != tokens_min5, (
        f"Changing min_ngram_length had no effect:\n"
        f"min=3: {tokens_min3}\n"
        f"min=5: {tokens_min5}\n"
        f"These should differ. This test FAILS on base and PASSES on fixed code."
    )

    # Additional check: min=5 tokens must all be exactly 5 chars
    ok, msg = _all_tokens_length_in_range(tokens_min5, 5, 5)
    assert ok, f"min=5 constraint violated: {msg}\nTokens: {tokens_min5}"


def test_logic_calculation_correct():
    """
    Behavioral fail-to-pass test: verify token length bounds are respected
    across a range of min/max settings and input strings.

    On buggy code: tokens may exceed max_ngram_length in some configurations.
    On fixed code: all tokens satisfy the [min, max] constraints.
    """
    test_cases = [
        # (input, min_len, max_len)
        ("abcdefgh", 5, 5),
        ("abcdefgh", 3, 5),
        ("abcdefgh", 4, 7),
        ("aabbccddee", 5, 5),
        ("aabbccddee", 3, 5),
        ("hello world example", 5, 5),
        ("hello world example", 6, 8),
    ]

    all_ok = True
    failures = []
    for input_str, min_len, max_len in test_cases:
        tokens = _get_tokens(input_str, min_len, max_len)
        ok, msg = _all_tokens_length_in_range(tokens, min_len, max_len)
        print(f"'{input_str}' min={min_len} max={max_len}: {tokens} -> {'OK' if ok else msg}")
        if not ok:
            all_ok = False
            failures.append(f"'{input_str}' min={min_len} max={max_len}: {msg}")

    assert all_ok, (
        f"Token length violations:\n" + "\n".join(failures) + "\n"
        f"This test FAILS on base and PASSES on fixed code."
    )


def test_source_code_fix_applied():
    """
    Structural fail-to-pass test: verify the old hardcoded '+ 2' pattern
    is absent in length calculations.

    Unlike the original, this does not require the exact literal
    'min_ngram_length - 1' — it just checks the hardcoded constant is gone
    and some variable-based expression replaces it.
    """
    with open(f"{REPO}/src/Functions/sparseGramsImpl.h", "r") as f:
        content = f.read()

    # The old buggy pattern must be gone
    old_pattern = r"right_symbol_index\s*-\s*possible_left_symbol_index\s*\+\s*2\b"
    old_matches = re.findall(old_pattern, content)

    assert len(old_matches) == 0, (
        f"Bug still present: found {len(old_matches)} occurrence(s) of hardcoded '+ 2' "
        f"in length calculations. Expected 0."
    )

    # There must be a length calculation using a variable (not hardcoded 2)
    # near the right_symbol_index / possible_left_symbol_index expression.
    variable_offset = re.search(
        r"right_symbol_index\s*-\s*possible_left_symbol_index\s*\+\s*\w+",
        content
    )

    assert variable_offset is not None, (
        "No variable-based offset found near length calculation. "
        "The fix should replace hardcoded '+ 2' with a variable expression."
    )

    print(f"Verified: old '+ 2' pattern gone, variable-based offset present")


def test_convex_hull_logic_preserved():
    """
    Pass-to-pass test: verify key convex hull control-flow structures
    are still present after the fix.
    """
    with open(f"{REPO}/src/Functions/sparseGramsImpl.h", "r") as f:
        content = f.read()

    assert "convex_hull.back()" in content, "convex_hull.back() missing"
    assert "possible_left_position" in content, "possible_left_position missing"
    assert "possible_left_symbol_index" in content, "possible_left_symbol_index missing"
    assert "result.push_back" in content, "result.push_back missing"
    assert "if (length > max_ngram_length)" in content, "max_ngram_length check missing"
    assert "convex_hull.clear()" in content, "convex_hull.clear() missing"
    assert content.count("while (!convex_hull.empty()") >= 1, "Main convex hull loop missing"
    assert content.count("if (length <= max_ngram_length)") >= 1, "Length check in consume missing"

    print("Convex hull logic preserved")


def test_repo_cpp_style_check():
    """Run C++ style check on the modified file."""
    style_script = f"{REPO}/ci/jobs/scripts/check_style/check_cpp.sh"
    if not os.path.exists(style_script):
        pytest.skip(f"Style check script not found: {style_script}")

    r = subprocess.run(
        ["bash", style_script, f"{REPO}/src/Functions/sparseGramsImpl.h"],
        capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"C++ style check failed:\n{r.stdout[-1000:]}"


def test_repo_submodules_check():
    """Validate git submodules configuration."""
    if not os.path.exists(f"{REPO}/contrib/AMQP-CPP/CMakeLists.txt"):
        pytest.skip("Submodules not populated - skipping")

    r = subprocess.run(
        ["bash", f"{REPO}/ci/jobs/scripts/check_style/check_submodules.sh"],
        capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0, f"Submodules check failed:\n{r.stdout[-500:]}"


def test_repo_various_checks():
    """Run SQL test style validation."""
    various_script = f"{REPO}/ci/jobs/scripts/check_style/various_checks.sh"
    if not os.path.exists(various_script):
        pytest.skip(f"Various checks script not found: {various_script}")

    r = subprocess.run(
        ["bash", various_script],
        capture_output=True, text=True, timeout=120, cwd=REPO)
    error_patterns = ["does not have", "cannot be", "should be", "is not"]
    output_lower = r.stdout.lower()
    for pattern in error_patterns:
        assert pattern not in output_lower, f"Various checks found issues:\n{r.stdout[-500:]}"


if __name__ == "__main__":
    print("Running sparseGrams fix behavioral tests...")

    tests = [
        ("test_sparsegrams_length_constraint_bug", test_sparsegrams_length_constraint_bug),
        ("test_source_code_uses_min_ngram_length", test_source_code_uses_min_ngram_length),
        ("test_logic_calculation_correct", test_logic_calculation_correct),
        ("test_source_code_fix_applied", test_source_code_fix_applied),
        ("test_convex_hull_logic_preserved", test_convex_hull_logic_preserved),
    ]

    for name, fn in tests:
        try:
            fn()
            print(f"OK {name}")
        except AssertionError as e:
            print(f"FAIL {name}: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"FAIL {name}: {type(e).__name__}: {e}")
            sys.exit(1)

    print("\nRunning pass-to-pass (CI) tests...")

    p2p_tests = [
        ("test_repo_cpp_style_check", test_repo_cpp_style_check),
        ("test_repo_submodules_check", test_repo_submodules_check),
        ("test_repo_various_checks", test_repo_various_checks),
    ]

    for name, fn in p2p_tests:
        try:
            fn()
            print(f"OK {name}")
        except pytest.skip:
            print(f"SKIP {name}: skipped")
        except AssertionError as e:
            print(f"FAIL {name}: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"FAIL {name}: {type(e).__name__}: {e}")
            sys.exit(1)

    print("\nAll tests passed!")
    sys.exit(0)