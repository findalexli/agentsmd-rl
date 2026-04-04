"""
Task: react-devtools-suspense-unique-suspenders
Repo: facebook/react @ c6bb26bf833c5d91760daf28fa2750b81067ac30
PR:   #35736

Fix: printSuspense() must include `hasUniqueSuspenders` in its output so that
Suspense nodes with different uniqueSuspenders values are distinguishable in
snapshot tests and debug output.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
UTILS_FILE = f"{REPO}/packages/react-devtools-shared/src/devtools/utils.js"


def _extract_and_call(suspense_data: dict) -> str:
    """Extract printRects + printSuspense from utils.js, call via node subprocess."""
    src = Path(UTILS_FILE).read_text()

    # Extract function bodies (Flow types are only in signatures, bodies are plain JS)
    rects_match = re.search(
        r"function printRects\([^)]*\)[^{]*\{([\s\S]*?)\n\}", src
    )
    susp_match = re.search(
        r"function printSuspense\([^)]*\)[^{]*\{([\s\S]*?)\n\}", src
    )
    assert rects_match, "Could not find printRects function in utils.js"
    assert susp_match, "Could not find printSuspense function in utils.js"

    node_code = (
        "function printRects(rects) {"
        + rects_match.group(1)
        + "\n}\n"
        + "function printSuspense(suspense) {"
        + susp_match.group(1)
        + "\n}\n"
        + f"process.stdout.write(printSuspense({json.dumps(suspense_data)}));"
    )

    r = subprocess.run(
        ["node", "-e", node_code], capture_output=True, timeout=10
    )
    assert r.returncode == 0, f"Node execution failed:\n{r.stderr.decode()}"
    return r.stdout.decode()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """utils.js must be syntactically valid JavaScript."""
    r = subprocess.run(
        ["node", "--check", UTILS_FILE], capture_output=True, timeout=30
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_output_includes_unique_suspenders_true():
    """printSuspense must include uniqueSuspenders={true} when hasUniqueSuspenders is true."""
    result = _extract_and_call(
        {"name": "App", "hasUniqueSuspenders": True, "rects": None}
    )
    assert "uniqueSuspenders={true}" in result, (
        f"Expected 'uniqueSuspenders={{true}}' in output, got: {result}"
    )


# [pr_diff] fail_to_pass
def test_output_includes_unique_suspenders_false():
    """printSuspense must include uniqueSuspenders={false} when hasUniqueSuspenders is false."""
    result = _extract_and_call(
        {"name": "Wrapper", "hasUniqueSuspenders": False, "rects": None}
    )
    assert "uniqueSuspenders={false}" in result, (
        f"Expected 'uniqueSuspenders={{false}}' in output, got: {result}"
    )


# [pr_diff] fail_to_pass
def test_field_ordering():
    """uniqueSuspenders must appear between name and rects in the output string.

    Expected format: <Suspense name="..." uniqueSuspenders={...} rects={...}>
    Tests with both null rects and array rects to cover both code paths.
    """
    # Test with null rects
    r1 = _extract_and_call(
        {"name": "A", "hasUniqueSuspenders": True, "rects": None}
    )
    name_pos = r1.index('name=')
    unique_pos = r1.index('uniqueSuspenders=')
    rects_pos = r1.index('rects=')
    assert name_pos < unique_pos < rects_pos, (
        f"Fields out of order. name@{name_pos}, uniqueSuspenders@{unique_pos}, rects@{rects_pos}"
    )

    # Test with array rects
    r2 = _extract_and_call(
        {
            "name": "B",
            "hasUniqueSuspenders": False,
            "rects": [{"x": 1, "y": 2, "width": 10, "height": 5}],
        }
    )
    name_pos2 = r2.index('name=')
    unique_pos2 = r2.index('uniqueSuspenders=')
    rects_pos2 = r2.index('rects=')
    assert name_pos2 < unique_pos2 < rects_pos2, (
        f"Fields out of order with rects array: {r2}"
    )


# [pr_diff] fail_to_pass
def test_multiple_inputs():
    """printSuspense must include uniqueSuspenders for various input combinations."""
    cases = [
        ({"name": "X", "hasUniqueSuspenders": True, "rects": None}, "true"),
        ({"name": "Y", "hasUniqueSuspenders": False, "rects": None}, "false"),
        ({"name": None, "hasUniqueSuspenders": True, "rects": None}, "true"),
        (
            {
                "name": "Z",
                "hasUniqueSuspenders": False,
                "rects": [{"x": 0, "y": 0, "width": 1, "height": 1}],
            },
            "false",
        ),
    ]
    for data, expected_bool in cases:
        result = _extract_and_call(data)
        assert f"uniqueSuspenders={{{expected_bool}}}" in result, (
            f"For input {data}, expected uniqueSuspenders={{{expected_bool}}} "
            f"in output, got: {result}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_name_and_rects_preserved():
    """printSuspense must still include name and rects in the output."""
    r1 = _extract_and_call(
        {"name": "MyComp", "hasUniqueSuspenders": True, "rects": None}
    )
    assert 'name="MyComp"' in r1, f"Missing name in output: {r1}"
    assert "rects={null}" in r1, f"Missing rects in output: {r1}"

    r2 = _extract_and_call(
        {
            "name": "Other",
            "hasUniqueSuspenders": False,
            "rects": [{"x": 3, "y": 4, "width": 7, "height": 2}],
        }
    )
    assert 'name="Other"' in r2, f"Missing name in output: {r2}"
    assert "rects={[" in r2, f"Missing rects array in output: {r2}"


# [static] pass_to_pass
def test_unknown_name_fallback():
    """printSuspense must use 'Unknown' as default name when name is falsy."""
    for falsy_name in [None, "", 0, False]:
        result = _extract_and_call(
            {"name": falsy_name, "hasUniqueSuspenders": True, "rects": None}
        )
        assert 'name="Unknown"' in result, (
            f"Expected name='Unknown' for falsy input {falsy_name!r}, got: {result}"
        )
