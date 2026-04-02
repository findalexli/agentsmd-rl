"""
Task: ruff-ty-nonterminal-call-shortcut
Repo: astral-sh/ruff @ 7973118f777bee32466a4fdb54f0816268f942ea
PR:   astral-sh/ruff#24185 (restore IsNonTerminalCall shortcut optimization)

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
from pathlib import Path

import pytest

REPO = "/repo"

# ---------------------------------------------------------------------------
# Test input files (written to tmp_path per test)
# ---------------------------------------------------------------------------

# Triggers combinatorial explosion: sequential TypeIs narrowing on large Literal
# unions + match/assert_never. Hangs for minutes on buggy code, seconds on fix.
TYPEIS_NARROWING_CODE = '''\
from typing import Any, Literal, assert_never
from typing_extensions import TypeIs

Kind = Literal[
    "alpha_one", "alpha_two", "alpha_three", "alpha_four",
    "bravo_one", "bravo_two", "bravo_three", "bravo_four",
    "bravo_five", "bravo_six", "bravo_seven", "bravo_eight",
    "charlie_one", "charlie_two", "charlie_three", "charlie_four",
    "charlie_five", "charlie_six", "charlie_seven", "charlie_eight",
    "delta_one", "delta_two", "delta_three", "delta_four",
    "delta_five", "delta_six", "delta_seven", "delta_eight",
    "echo_one", "echo_two", "echo_three", "echo_four",
    "echo_five", "echo_six", "echo_seven", "echo_eight",
    "foxtrot_one", "foxtrot_two", "foxtrot_three", "foxtrot_four",
    "golf_one", "golf_two", "golf_three", "golf_four",
    "golf_five", "golf_six", "golf_seven", "golf_eight",
    "hotel_one", "hotel_two", "hotel_three", "hotel_four", "hotel_five",
]

CHARLIE = Literal[
    "charlie_one", "charlie_two", "charlie_three", "charlie_four",
    "charlie_five", "charlie_six", "charlie_seven",
]
DELTA = Literal[
    "delta_one", "delta_two", "delta_three", "delta_four",
    "delta_five", "delta_six",
]
ECHO = Literal[
    "echo_one", "echo_two", "echo_three", "echo_four",
    "echo_five", "echo_six",
]
FOXTROT = Literal["foxtrot_one", "foxtrot_two"]
ALPHA = Literal[
    "alpha_one", "alpha_two", "alpha_three", "alpha_four",
    "bravo_one", "bravo_two", "bravo_three", "bravo_four",
    "bravo_five", "bravo_six", "bravo_seven", "bravo_eight",
    "delta_seven", "delta_eight", "echo_seven", "echo_eight",
]
GOLF = Literal[
    "golf_one", "golf_two", "golf_three", "golf_four",
    "golf_five", "golf_six", "golf_seven", "golf_eight",
]

def is_charlie(t: Kind) -> TypeIs[CHARLIE]:
    return t.startswith("charlie")

def is_delta(t: Kind) -> TypeIs[DELTA]:
    return t.startswith("delta")

def is_echo(t: Kind) -> TypeIs[ECHO]:
    return t.startswith("echo")

def is_foxtrot(t: Kind) -> TypeIs[FOXTROT]:
    return t.startswith("foxtrot")

def is_alpha(t: Kind) -> TypeIs[ALPHA]:
    return t.startswith("alpha") or t.startswith("bravo")

def is_golf(t: Kind) -> TypeIs[GOLF]:
    return t.startswith("golf")

Action = Literal[
    "act_one", "act_two", "act_three", "act_four", "act_five",
    "act_six", "act_seven", "act_eight", "act_nine", "act_ten",
    "act_eleven", "act_twelve", "act_thirteen", "act_fourteen",
    "act_fifteen", "act_sixteen", "act_seventeen", "act_eighteen",
    "act_nineteen", "act_twenty",
]

def process(kind: Kind, action: Action | None, params: dict[str, Any]) -> str:
    if is_golf(kind):
        raise ValueError
    if is_alpha(kind) and action not in ["act_two", "act_five"]:
        raise ValueError

    if action is None:
        if is_foxtrot(kind):
            return "foxtrot"
        if is_echo(kind):
            return "echo"
        if is_delta(kind):
            return "delta"
        if is_charlie(kind):
            return "charlie"
        if kind == "bravo_one":
            action = "act_one"
        elif kind == "bravo_two":
            action = "act_eight"
        else:
            action = "act_one"
    else:
        match action:
            case "act_three":
                if kind != "bravo_three":
                    raise ValueError
            case "act_one" | "act_two":
                pass
            case "act_four" | "act_five":
                pass
            case "act_six":
                pass
            case "act_seven":
                pass
            case "act_eight":
                pass
            case "act_nine" | "act_ten":
                if not is_charlie(kind):
                    raise ValueError
            case "act_eleven" | "act_twelve":
                if not is_delta(kind):
                    raise ValueError
            case "act_thirteen" | "act_fourteen":
                if not is_delta(kind):
                    raise ValueError
            case "act_fifteen" | "act_sixteen":
                if not is_echo(kind):
                    raise ValueError
            case "act_seventeen":
                if not is_charlie(kind):
                    raise ValueError
            case "act_eighteen":
                if not is_delta(kind):
                    raise ValueError
            case "act_nineteen":
                if not is_echo(kind):
                    raise ValueError
            case "act_twenty":
                if not is_foxtrot(kind):
                    raise ValueError
            case _ as never:
                assert_never(never)

    return kind
'''

# Variant with different structure — also triggers combinatorial explosion.
TYPEIS_VARIANT_CODE = '''\
from typing import Literal, assert_never
from typing_extensions import TypeIs

Color = Literal[
    "red_light", "red_dark", "red_bright",
    "blue_light", "blue_dark", "blue_bright",
    "green_light", "green_dark", "green_bright",
    "yellow_light", "yellow_dark", "yellow_bright",
    "purple_light", "purple_dark", "purple_bright",
    "orange_light", "orange_dark", "orange_bright",
    "pink_light", "pink_dark", "pink_bright",
    "brown_light", "brown_dark", "brown_bright",
    "gray_light", "gray_dark", "gray_bright",
    "white_light", "white_dark", "white_bright",
    "black_light", "black_dark", "black_bright",
    "cyan_light", "cyan_dark", "cyan_bright",
    "magenta_light", "magenta_dark", "magenta_bright",
    "lime_light", "lime_dark", "lime_bright",
    "teal_light", "teal_dark", "teal_bright",
]

RED = Literal["red_light", "red_dark", "red_bright"]
BLUE = Literal["blue_light", "blue_dark", "blue_bright"]
GREEN = Literal["green_light", "green_dark", "green_bright"]
YELLOW = Literal["yellow_light", "yellow_dark", "yellow_bright"]
PURPLE = Literal["purple_light", "purple_dark", "purple_bright"]
ORANGE = Literal["orange_light", "orange_dark", "orange_bright"]
PINK = Literal["pink_light", "pink_dark", "pink_bright"]

def is_red(c: Color) -> TypeIs[RED]:
    return c.startswith("red")

def is_blue(c: Color) -> TypeIs[BLUE]:
    return c.startswith("blue")

def is_green(c: Color) -> TypeIs[GREEN]:
    return c.startswith("green")

def is_yellow(c: Color) -> TypeIs[YELLOW]:
    return c.startswith("yellow")

def is_purple(c: Color) -> TypeIs[PURPLE]:
    return c.startswith("purple")

def is_orange(c: Color) -> TypeIs[ORANGE]:
    return c.startswith("orange")

def is_pink(c: Color) -> TypeIs[PINK]:
    return c.startswith("pink")

Op = Literal[
    "op_a", "op_b", "op_c", "op_d", "op_e",
    "op_f", "op_g", "op_h", "op_i", "op_j",
    "op_k", "op_l",
]

def handle(color: Color, op: Op | None) -> str:
    if is_red(color):
        raise ValueError
    if is_blue(color):
        raise ValueError

    if op is None:
        if is_green(color):
            return "green"
        if is_yellow(color):
            return "yellow"
        if is_purple(color):
            return "purple"
        if is_orange(color):
            return "orange"
        if is_pink(color):
            return "pink"
        return "other"

    match op:
        case "op_a" | "op_b":
            pass
        case "op_c":
            if not is_green(color):
                raise ValueError
        case "op_d" | "op_e":
            if not is_yellow(color):
                raise ValueError
        case "op_f" | "op_g":
            if not is_purple(color):
                raise ValueError
        case "op_h":
            if not is_orange(color):
                raise ValueError
        case "op_i":
            if not is_pink(color):
                raise ValueError
        case "op_j" | "op_k" | "op_l":
            pass
        case _ as never:
            assert_never(never)

    return color
'''

NORETURN_CODE = '''\
import sys
from typing import NoReturn

def exit_fn() -> NoReturn:
    sys.exit(1)

def maybe_exit(flag: bool) -> None:
    if flag:
        exit_fn()
    x: int = 42
    reveal_type(x)
'''

MANY_CALLS_CODE = '''\
def helper_a() -> str:
    return "a"

def helper_b() -> int:
    return 1

def helper_c() -> float:
    return 1.0

def main() -> None:
    helper_a()
    helper_b()
    helper_c()
    helper_a()
    helper_b()
    helper_c()
    helper_a()
    helper_b()
    helper_c()
    helper_a()
    helper_b()
    helper_c()
    x: int = 42
'''


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def ty_binary():
    """Build ty and return path to the binary."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"cargo build --bin ty failed:\n{r.stderr.decode()[-3000:]}"
    binary = Path(REPO) / "target" / "debug" / "ty"
    assert binary.exists(), "ty binary not found after build"
    return str(binary)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_build_compiles(ty_binary):
    """All Rust changes must compile (cargo build --bin ty)."""
    assert Path(ty_binary).exists()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core performance regression tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_typeis_narrowing_performance(ty_binary, tmp_path):
    """ty check on TypeIs narrowing + match/assert_never completes within 60s.

    On the buggy base commit, IsNonTerminalCall forces full call-expression
    inference for every statement-level call, causing combinatorial explosion
    with sequential TypeIs guards on large Literal unions. This hangs for
    minutes+. Any correct fix avoids this and completes in seconds.
    """
    test_file = tmp_path / "typeis_perf.py"
    test_file.write_text(TYPEIS_NARROWING_CODE)
    # TimeoutExpired → test fails (bug still present)
    subprocess.run(
        [ty_binary, "check", str(test_file)],
        capture_output=True, timeout=60,
    )


# [pr_diff] fail_to_pass
def test_typeis_variant_performance(ty_binary, tmp_path):
    """Variant TypeIs narrowing pattern also completes within 45s.

    Different structure (7 TypeIs guards, 12-variant Op union) that also
    triggers the combinatorial explosion on buggy code.
    """
    test_file = tmp_path / "typeis_variant.py"
    test_file.write_text(TYPEIS_VARIANT_CODE)
    subprocess.run(
        [ty_binary, "check", str(test_file)],
        capture_output=True, timeout=45,
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — correctness preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_noreturn_detection(ty_binary, tmp_path):
    """NoReturn/Never narrowing still works correctly after optimization."""
    test_file = tmp_path / "noreturn.py"
    test_file.write_text(NORETURN_CODE)
    r = subprocess.run(
        [ty_binary, "check", str(test_file)],
        capture_output=True, timeout=30, text=True,
    )
    # reveal_type(x) should show int — confirms reachability analysis works
    assert "int" in r.stdout, (
        f"Expected reveal_type(x) to show 'int' in output:\n{r.stdout}\n{r.stderr}"
    )


# [pr_diff] pass_to_pass
def test_many_statement_calls(ty_binary, tmp_path):
    """Many statement-level function calls don't cause hang."""
    test_file = tmp_path / "many_calls.py"
    test_file.write_text(MANY_CALLS_CODE)
    r = subprocess.run(
        [ty_binary, "check", str(test_file)],
        capture_output=True, timeout=30, text=True,
    )
    # Must complete successfully — no errors, no diagnostics
    assert r.returncode == 0, (
        f"ty check failed on many-calls file:\n{r.stdout}\n{r.stderr}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — upstream regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_upstream_narrowing_mdtests(ty_binary):
    """Existing narrowing mdtests still pass."""
    env = {**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"}
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--", "mdtest::narrow"],
        cwd=REPO, capture_output=True, timeout=300, env=env,
    )
    stdout = r.stdout.decode()
    stderr = r.stderr.decode()
    assert r.returncode == 0 or "0 failed" in stdout, (
        f"Narrowing mdtests failed:\n{stderr[-2000:]}\n{stdout[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_upstream_reachability_tests(ty_binary):
    """Reachability-related tests still pass."""
    env = {**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"}
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--", "reachability"],
        cwd=REPO, capture_output=True, timeout=300, env=env,
    )
    stdout = r.stdout.decode()
    stderr = r.stderr.decode()
    assert r.returncode == 0 or "0 failed" in stdout, (
        f"Reachability tests failed:\n{stderr[-2000:]}\n{stdout[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:76 @ 7973118f
def test_no_local_imports():
    """Rust imports at top of file, never locally in functions (AGENTS.md:76)."""
    r = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO, capture_output=True, text=True,
    )
    changed_rs = [f for f in r.stdout.strip().split("\n") if f.endswith(".rs") and f.strip()]
    for filepath in changed_rs:
        full = Path(REPO) / filepath
        if not full.exists():
            continue
        lines = full.read_text().splitlines()
        in_fn = False
        fn_indent = 0
        for lineno, line in enumerate(lines, 1):
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            if re.match(r"(pub\s+)?(async\s+)?fn\s", stripped) or re.match(r"impl\s", stripped):
                in_fn = True
                fn_indent = indent
            elif in_fn and indent <= fn_indent and stripped and not stripped.startswith("//"):
                if stripped.startswith("}"):
                    in_fn = False
            if in_fn and indent > fn_indent and stripped.startswith("use "):
                pytest.fail(f"Local import in {filepath}:{lineno}: {stripped}")


# [agent_config] pass_to_pass — AGENTS.md:81 @ 7973118f
def test_prefer_expect_over_allow():
    """Use #[expect()] over #[allow()] for Clippy lint suppression (AGENTS.md:81)."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        cwd=REPO, capture_output=True, text=True,
    )
    for line in r.stdout.split("\n"):
        if not line.startswith("+") or line.startswith("+++"):
            continue
        content = line[1:].strip()
        if content.startswith("//"):
            continue
        if "#[allow(" in content and "#[allow(unused" not in content:
            pytest.fail(
                f"Use #[expect()] instead of #[allow()] (AGENTS.md:81): {line.strip()}"
            )


# [agent_config] pass_to_pass — AGENTS.md:79 @ 7973118f
def test_no_panic_unwrap():
    """No new panic!/unwrap()/unreachable!() in changes (AGENTS.md:79)."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        cwd=REPO, capture_output=True, text=True,
    )
    forbidden = [".unwrap()", "panic!(", "unreachable!("]
    for line in r.stdout.split("\n"):
        if not line.startswith("+") or line.startswith("+++"):
            continue
        content = line[1:].strip()
        if content.startswith("//") or content.startswith("///"):
            continue
        # Allow in test files
        if content.startswith("#[test]") or content.startswith("#[cfg(test)]"):
            continue
        for pattern in forbidden:
            if pattern in line:
                pytest.fail(f"Forbidden pattern '{pattern}' in added line: {line.strip()}")
