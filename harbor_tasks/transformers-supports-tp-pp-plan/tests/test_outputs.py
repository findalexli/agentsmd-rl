"""
Task: transformers-supports-tp-pp-plan
Repo: huggingface/transformers @ 09fea1e6e970a1051b1141ce320a3d696b2c15ed
PR:   44696

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import subprocess
import sys
import textwrap
from pathlib import Path

REPO = "/workspace/transformers"
TARGET = f"{REPO}/src/transformers/modeling_utils.py"


def _run_in_subprocess(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run Python code in a subprocess with proper PYTHONPATH."""
    env = os.environ.copy()
    env["PYTHONPATH"] = REPO
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
        env=env,
    )


def _read_source():
    return Path(TARGET).read_text()


def _extract_method(source, method_name, *, is_setter=False):
    """Extract a method from PreTrainedModel, dedented.
    AST-only because: transformers requires torch/CUDA; we extract then exec with mocks.
    """
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "PreTrainedModel":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    if is_setter:
                        for dec in item.decorator_list:
                            dec_src = ast.get_source_segment(source, dec)
                            if dec_src and "setter" in dec_src:
                                start = min(d.lineno for d in item.decorator_list)
                                return textwrap.dedent(
                                    "".join(lines[start - 1 : item.end_lineno])
                                )
                    else:
                        if item.decorator_list:
                            start = min(d.lineno for d in item.decorator_list)
                        else:
                            start = item.lineno
                        return textwrap.dedent(
                            "".join(lines[start - 1 : item.end_lineno])
                        )
    raise AssertionError(f"PreTrainedModel.{method_name} not found")


def _build_supports_tp_harness(prop_src, *, tp_plan, base_tp_plan, config_tp_plan):
    """Build exec code for supports_tp_plan with given mock values."""
    lines = [
        "class Cfg:",
        f"    base_model_tp_plan = {config_tp_plan!r}",
        "class Base:",
        f"    _tp_plan = {base_tp_plan!r}",
        "class M:",
        f"    _tp_plan = {tp_plan!r}",
        "    config = Cfg()",
        "    base_model = Base()",
    ]
    indented_prop = textwrap.indent(prop_src, "    ")
    lines.append(indented_prop)
    lines.append("result = M().supports_tp_plan")
    return "\n".join(lines)


def _build_supports_pp_harness(prop_src, *, pp_plan, base_pp_plan, config_pp_plan):
    """Build exec code for supports_pp_plan with given mock values."""
    lines = [
        "class Cfg:",
        "    base_model_tp_plan = None",
        f"    base_model_pp_plan = {config_pp_plan!r}",
        "class Base:",
        f"    _pp_plan = {base_pp_plan!r}",
        "class M:",
        f"    _pp_plan = {pp_plan!r}",
        "    config = Cfg()",
        "    base_model = Base()",
    ]
    indented_prop = textwrap.indent(prop_src, "    ")
    lines.append(indented_prop)
    lines.append("result = M().supports_pp_plan")
    return "\n".join(lines)


def _build_pp_setter_harness(setter_src):
    """Build exec code for pp_plan setter tests."""
    lines = [
        "class M:",
        "    _pp_plan = None",
        "    @property",
        "    def pp_plan(self):",
        "        return self._pp_plan",
    ]
    indented_setter = textwrap.indent(setter_src, "    ")
    return "\n".join(lines) + "\n" + indented_setter


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without syntax errors."""
    source = _read_source()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests (using subprocess)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_supports_tp_plan_empty_dict_false():
    """supports_tp_plan returns False when all plans are empty/None."""
    source = _read_source()
    prop = _extract_method(source, "supports_tp_plan")

    # All these combos should return False — empty dicts are falsy after fix
    cases = [
        ({}, None, None),    # model has empty dict, rest None
        ({}, {}, None),      # model + base both empty
        ({}, {}, {}),        # all empty dicts
    ]
    for tp, base_tp, cfg_tp in cases:
        harness = _build_supports_tp_harness(
            prop, tp_plan=tp, base_tp_plan=base_tp, config_tp_plan=cfg_tp
        )
        code = harness + "\nprint('RESULT:', result)"
        r = _run_in_subprocess(code)
        assert r.returncode == 0, f"Harness failed: {r.stderr}"
        # Parse result from output
        for line in r.stdout.strip().split("\n"):
            if line.startswith("RESULT:"):
                result_str = line.replace("RESULT:", "").strip()
                result = result_str == "True"
                assert result is False, (
                    f"supports_tp_plan should be False for tp={tp!r}, base={base_tp!r}, config={cfg_tp!r}"
                )
                break
        else:
            raise AssertionError(f"Could not find RESULT in output: {r.stdout}")


# [pr_diff] fail_to_pass
def test_supports_pp_plan_empty_dict_false():
    """supports_pp_plan returns False when all plans are empty/None."""
    source = _read_source()
    prop = _extract_method(source, "supports_pp_plan")

    cases = [
        ({}, None, None),
        ({}, {}, None),
        ({}, {}, {}),
    ]
    for pp, base_pp, cfg_pp in cases:
        harness = _build_supports_pp_harness(
            prop, pp_plan=pp, base_pp_plan=base_pp, config_pp_plan=cfg_pp
        )
        code = harness + "\nprint('RESULT:', result)"
        r = _run_in_subprocess(code)
        assert r.returncode == 0, f"Harness failed: {r.stderr}"
        for line in r.stdout.strip().split("\n"):
            if line.startswith("RESULT:"):
                result_str = line.replace("RESULT:", "").strip()
                result = result_str == "True"
                assert result is False, (
                    f"supports_pp_plan should be False for pp={pp!r}, base={base_pp!r}, config={cfg_pp!r}"
                )
                break
        else:
            raise AssertionError(f"Could not find RESULT in output: {r.stdout}")


# [pr_diff] fail_to_pass
def test_supports_pp_plan_checks_config():
    """supports_pp_plan returns True when config.base_model_pp_plan is set."""
    source = _read_source()
    prop = _extract_method(source, "supports_pp_plan")

    config_values = [
        {"layer": ("in", "out")},
        {"block.0": ("input", "output"), "block.1": ("input", "output")},
        {"single": ("a", "b")},
    ]
    for cfg_val in config_values:
        harness = _build_supports_pp_harness(
            prop, pp_plan=None, base_pp_plan=None, config_pp_plan=cfg_val
        )
        code = harness + "\nprint('RESULT:', result)"
        r = _run_in_subprocess(code)
        assert r.returncode == 0, f"Harness failed: {r.stderr}"
        for line in r.stdout.strip().split("\n"):
            if line.startswith("RESULT:"):
                result_str = line.replace("RESULT:", "").strip()
                result = result_str == "True"
                assert result is True, (
                    f"supports_pp_plan should be True when config has pp_plan={cfg_val!r}"
                )
                break
        else:
            raise AssertionError(f"Could not find RESULT in output: {r.stdout}")


# [pr_diff] fail_to_pass
def test_pp_setter_rejects_non_dict():
    """pp_plan setter raises ValueError for non-dict input."""
    source = _read_source()
    setter = _extract_method(source, "pp_plan", is_setter=True)
    base = _build_pp_setter_harness(setter)

    bad_inputs = ["not a dict", 42, ["a", "b"], True, (1, 2)]
    for bad in bad_inputs:
        code = base + (
            f"\nraised = False\n"
            f"try:\n"
            f"    M().pp_plan = {bad!r}\n"
            f"except (ValueError, TypeError):\n"
            f"    raised = True\n"
            f"print('RESULT:', raised)"
        )
        r = _run_in_subprocess(code)
        assert r.returncode == 0, f"Harness failed: {r.stderr}"
        for line in r.stdout.strip().split("\n"):
            if line.startswith("RESULT:"):
                result_str = line.replace("RESULT:", "").strip()
                raised = result_str == "True"
                assert raised, f"pp_plan setter should reject {type(bad).__name__} input: {bad!r}"
                break
        else:
            raise AssertionError(f"Could not find RESULT in output: {r.stdout}")


# [pr_diff] fail_to_pass
def test_pp_setter_handles_none():
    """pp_plan setter converts None to empty dict instead of storing None."""
    source = _read_source()
    setter = _extract_method(source, "pp_plan", is_setter=True)
    base = _build_pp_setter_harness(setter)

    code = base + (
        "\nm = M()\n"
        "m.pp_plan = None\n"
        "print('RESULT:', repr(m._pp_plan))"
    )
    r = _run_in_subprocess(code)
    assert r.returncode == 0, f"Harness failed: {r.stderr}"
    for line in r.stdout.strip().split("\n"):
        if line.startswith("RESULT:"):
            result_str = line.replace("RESULT:", "").strip()
            assert result_str == "{}", (
                f"pp_plan setter should convert None to {{}}, got {result_str!r}"
            )
            break
    else:
        raise AssertionError(f"Could not find RESULT in output: {r.stdout}")


# [pr_diff] fail_to_pass
def test_pipeline_parallel_enum_removed():
    """PipelineParallel enum class must not exist in modeling_utils.py."""
    source = _read_source()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "PipelineParallel":
            raise AssertionError("PipelineParallel enum class still exists")


# ---------------------------------------------------------------------------
# Pass-to-pass — anti-stub + regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_supports_tp_plan_nonempty_true():
    """supports_tp_plan returns True for non-empty plans (any source)."""
    source = _read_source()
    prop = _extract_method(source, "supports_tp_plan")

    # True from model's own plan
    for tp in [{"layer0": "col"}, {"a": "row", "b": "col"}]:
        harness = _build_supports_tp_harness(
            prop, tp_plan=tp, base_tp_plan=None, config_tp_plan=None
        )
        code = harness + "\nprint('RESULT:', result)"
        r = _run_in_subprocess(code)
        assert r.returncode == 0, f"Harness failed: {r.stderr}"
        for line in r.stdout.strip().split("\n"):
            if line.startswith("RESULT:"):
                result_str = line.replace("RESULT:", "").strip()
                result = result_str == "True"
                assert result is True, f"should be True for tp_plan={tp!r}"
                break
        else:
            raise AssertionError(f"Could not find RESULT in output: {r.stdout}")

    # True from base model's plan
    harness = _build_supports_tp_harness(
        prop, tp_plan={}, base_tp_plan={"x": "col"}, config_tp_plan=None
    )
    code = harness + "\nprint('RESULT:', result)"
    r = _run_in_subprocess(code)
    assert r.returncode == 0, f"Harness failed: {r.stderr}"
    for line in r.stdout.strip().split("\n"):
        if line.startswith("RESULT:"):
            result_str = line.replace("RESULT:", "").strip()
            result = result_str == "True"
            assert result is True, "should be True when base_model has tp plan"
            break
    else:
        raise AssertionError(f"Could not find RESULT in output: {r.stdout}")

    # True from config
    harness = _build_supports_tp_harness(
        prop, tp_plan={}, base_tp_plan=None, config_tp_plan={"y": "row"}
    )
    code = harness + "\nprint('RESULT:', result)"
    r = _run_in_subprocess(code)
    assert r.returncode == 0, f"Harness failed: {r.stderr}"
    for line in r.stdout.strip().split("\n"):
        if line.startswith("RESULT:"):
            result_str = line.replace("RESULT:", "").strip()
            result = result_str == "True"
            assert result is True, "should be True when config has tp plan"
            break
    else:
        raise AssertionError(f"Could not find RESULT in output: {r.stdout}")


# [pr_diff] pass_to_pass
def test_supports_pp_plan_nonempty_true():
    """supports_pp_plan returns True for non-empty plans (any source)."""
    source = _read_source()
    prop = _extract_method(source, "supports_pp_plan")

    # True from model's own plan
    for pp in [{"layer0": ("input", "output")}, {"a": ("i", "o"), "b": ("i", "o")}]:
        harness = _build_supports_pp_harness(
            prop, pp_plan=pp, base_pp_plan=None, config_pp_plan=None
        )
        code = harness + "\nprint('RESULT:', result)"
        r = _run_in_subprocess(code)
        assert r.returncode == 0, f"Harness failed: {r.stderr}"
        for line in r.stdout.strip().split("\n"):
            if line.startswith("RESULT:"):
                result_str = line.replace("RESULT:", "").strip()
                result = result_str == "True"
                assert result is True, f"should be True for pp_plan={pp!r}"
                break
        else:
            raise AssertionError(f"Could not find RESULT in output: {r.stdout}")

    # True from base model's plan
    harness = _build_supports_pp_harness(
        prop, pp_plan={}, base_pp_plan={"x": ("i", "o")}, config_pp_plan=None
    )
    code = harness + "\nprint('RESULT:', result)"
    r = _run_in_subprocess(code)
    assert r.returncode == 0, f"Harness failed: {r.stderr}"
    for line in r.stdout.strip().split("\n"):
        if line.startswith("RESULT:"):
            result_str = line.replace("RESULT:", "").strip()
            result = result_str == "True"
            assert result is True, "should be True when base_model has pp plan"
            break
    else:
        raise AssertionError(f"Could not find RESULT in output: {r.stdout}")

    # True from config
    harness = _build_supports_pp_harness(
        prop, pp_plan={}, base_pp_plan=None, config_pp_plan={"y": ("i", "o")}
    )
    code = harness + "\nprint('RESULT:', result)"
    r = _run_in_subprocess(code)
    assert r.returncode == 0, f"Harness failed: {r.stderr}"
    for line in r.stdout.strip().split("\n"):
        if line.startswith("RESULT:"):
            result_str = line.replace("RESULT:", "").strip()
            result = result_str == "True"
            assert result is True, "should be True when config has pp plan"
            break
    else:
        raise AssertionError(f"Could not find RESULT in output: {r.stdout}")


# [pr_diff] pass_to_pass
def test_pp_setter_accepts_valid_dict():
    """pp_plan setter accepts valid dicts and stores them correctly."""
    source = _read_source()
    setter = _extract_method(source, "pp_plan", is_setter=True)
    base = _build_pp_setter_harness(setter)

    valid_dicts = [
        {"layer1": ("input", "output")},
        {"a": ("x", "y"), "b": ("p", "q")},
        {},
    ]
    for d in valid_dicts:
        code = base + (
            f"\nm = M()\n"
            f"m.pp_plan = {d!r}\n"
            f"print('RESULT:', repr(m._pp_plan))"
        )
        r = _run_in_subprocess(code)
        assert r.returncode == 0, f"Harness failed: {r.stderr}"
        for line in r.stdout.strip().split("\n"):
            if line.startswith("RESULT:"):
                result_str = line.replace("RESULT:", "").strip()
                expected = repr(d)
                assert result_str == expected, f"pp_plan setter should store {d!r}, got {result_str!r}"
                break
        else:
            raise AssertionError(f"Could not find RESULT in output: {r.stdout}")


# [static] pass_to_pass
def test_ruff_imports_clean():
    """Changed file passes ruff import sorting check."""
    r = subprocess.run(
        ["ruff", "check", "--select", "I", TARGET],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ruff import check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [agent_config] pass_to_pass — AGENTS.md:2 @ 09fea1e6e970a1051b1141ce320a3d696b2c15ed
def test_ruff_check_clean():
    """Changed file passes ruff check (all default rules) as required by make style."""
    r = subprocess.run(
        ["ruff", "check", TARGET],
        capture_output=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [repo_tests] pass_to_pass — basic syntax validation via Python parser
def test_syntax_parse_subprocess():
    """Python subprocess can parse the modified file without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{TARGET}').read())"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Python syntax parsing failed:\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass — documentation TOC check
def test_doc_toc_check():
    """Documentation TOC check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_doc_toc.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Documentation TOC check failed:\n{r.stderr[-500:]}"
    )