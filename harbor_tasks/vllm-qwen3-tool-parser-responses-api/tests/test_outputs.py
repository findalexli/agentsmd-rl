"""
Task: vllm-qwen3-tool-parser-responses-api
Repo: vllm-project/vllm @ 7b80cd8ac382851527225ed1f3475c138a4b7c01
PR:   38848

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/vllm"

UTILS_FILE = Path(f"{REPO}/vllm/tool_parsers/utils.py")
CODER_PARSER_FILE = Path(f"{REPO}/vllm/tool_parsers/qwen3coder_tool_parser.py")
XML_PARSER_FILE = Path(f"{REPO}/vllm/tool_parsers/qwen3xml_tool_parser.py")


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess in the repo directory."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _extract_func(src: str, name: str) -> str | None:
    """Extract a function's source from a Python file, dedented."""
    tree = ast.parse(src)
    lines = src.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            raw = "\n".join(lines[node.lineno - 1 : node.end_lineno])
            return textwrap.dedent(raw)
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """All modified source files must parse without syntax errors."""
    for fpath in [UTILS_FILE, CODER_PARSER_FILE, XML_PARSER_FILE]:
        src = fpath.read_text()
        compile(src, str(fpath), "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_coder_param_lookup_handles_function_tool():
    """Qwen3Coder parser's tool property lookup must handle FunctionTool objects.

    Bug: _get_arguments_config used hasattr(config, 'function') which returns
    False for FunctionTool (Responses API), so all param types fell back to string.
    Fix: Use find_tool_properties (or equivalent) that handles both tool formats.
    """
    r = _run_py(textwrap.dedent('''\
    import ast, sys, textwrap
    from typing import Any
    from pathlib import Path
    from openai.types.responses.function_tool import FunctionTool

    AREA_PARAMS = {
        "type": "object",
        "properties": {
            "shape": {"type": "string"},
            "dimensions": {"type": "object"},
            "precision": {"type": "integer"},
        },
    }

    WEATHER_PARAMS = {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "The city name"},
            "unit": {"type": "string", "enum": ["fahrenheit", "celsius"]},
        },
    }

    tool_area = FunctionTool(
        type="function", name="calculate_area",
        description="Calculate area", parameters=AREA_PARAMS,
    )
    tool_weather = FunctionTool(
        type="function", name="get_weather",
        description="Get weather", parameters=WEATHER_PARAMS,
    )

    utils_src = Path("vllm/tool_parsers/utils.py").read_text()
    parser_src = Path("vllm/tool_parsers/qwen3coder_tool_parser.py").read_text()

    def extract(src, name):
        tree = ast.parse(src)
        lines = src.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return textwrap.dedent("\\n".join(lines[node.lineno-1:node.end_lineno]))
        return None

    # Type stubs for annotations in extracted code
    class _DummyCCTP: pass
    _type_ns = {"FunctionTool": FunctionTool, "ChatCompletionToolsParam": _DummyCCTP,
                "Tool": FunctionTool, "Any": Any}

    # Try the new utility first, fall back to old parser method
    ftp_src = extract(utils_src, "find_tool_properties")
    eti_src = extract(utils_src, "_extract_tool_info")

    if ftp_src and eti_src:
        ns = dict(_type_ns)
        exec(compile(eti_src, "<eti>", "exec"), ns)
        exec(compile(ftp_src, "<ftp>", "exec"), ns)
        result = ns["find_tool_properties"]([tool_area, tool_weather], "calculate_area")
    else:
        gac_src = extract(parser_src, "_get_arguments_config")
        if not gac_src:
            print("FAIL: No tool property lookup found")
            sys.exit(1)
        logger_mock = type("L", (), {"debug": lambda *a, **kw: None})()
        ns = dict(_type_ns, logger=logger_mock)
        exec(compile(gac_src, "<gac>", "exec"), ns)
        result = ns["_get_arguments_config"](None, "calculate_area", [tool_area, tool_weather])

    assert isinstance(result, dict), f"Expected dict, got {type(result)}: {result}"
    assert "shape" in result, f"Expected 'shape' in properties, got {result}"
    assert "dimensions" in result, f"Expected 'dimensions' in properties, got {result}"
    assert "precision" in result, f"Expected 'precision' in properties, got {result}"
    assert result["precision"]["type"] == "integer", f"Wrong precision type: {result['precision']}"
    assert result["dimensions"]["type"] == "object", f"Wrong dimensions type: {result['dimensions']}"

    print("PASS")
    '''))
    assert r.returncode == 0, f"Failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_xml_type_resolution_with_function_tool():
    """Qwen3XML parser's _get_param_type must resolve types for FunctionTool objects.

    Bug: inline code in _get_param_type used tool.function.name which doesn't exist
    on FunctionTool (Responses API), causing all params to return "string".
    Fix: Use find_tool_properties (or equivalent) that handles both tool formats.
    """
    r = _run_py(textwrap.dedent('''\
    import ast, sys, textwrap
    from typing import Any
    from pathlib import Path
    from openai.types.responses.function_tool import FunctionTool

    TOOL = FunctionTool(
        type="function", name="calculate_area", description="Calc area",
        parameters={"type": "object", "properties": {
            "shape": {"type": "string"},
            "dimensions": {"type": "object"},
            "precision": {"type": "integer"},
        }},
    )

    parser_src = Path("vllm/tool_parsers/qwen3xml_tool_parser.py").read_text()
    utils_src = Path("vllm/tool_parsers/utils.py").read_text()

    def extract(src, name):
        tree = ast.parse(src)
        lines = src.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return textwrap.dedent("\\n".join(lines[node.lineno-1:node.end_lineno]))
        return None

    # Type stubs for annotations in extracted code
    class _DummyCCTP: pass
    _type_ns = {"FunctionTool": FunctionTool, "ChatCompletionToolsParam": _DummyCCTP,
                "Tool": FunctionTool, "Any": Any}

    gpt_src = extract(parser_src, "_get_param_type")
    assert gpt_src, "_get_param_type not found in qwen3xml parser"

    # Also extract repair_param_type (used by _get_param_type)
    rpt_src = extract(parser_src, "repair_param_type")

    # Check if _get_param_type uses find_tool_properties (fixed) or inline code (buggy)
    uses_ftp = "find_tool_properties" in gpt_src

    ns = dict(_type_ns)
    if uses_ftp:
        # Extract find_tool_properties and _extract_tool_info from utils
        ftp_src = extract(utils_src, "find_tool_properties")
        eti_src = extract(utils_src, "_extract_tool_info")
        assert ftp_src and eti_src, "Utility functions missing from utils.py"
        exec(compile(eti_src, "<eti>", "exec"), ns)
        exec(compile(ftp_src, "<ftp>", "exec"), ns)

    # Create a mock self object to call _get_param_type
    class MockSelf:
        tools = [TOOL]
        current_function_name = "calculate_area"

    if rpt_src:
        exec(compile(rpt_src, "<rpt>", "exec"), ns)
        MockSelf.repair_param_type = ns["repair_param_type"]

    exec(compile(gpt_src, "<gpt>", "exec"), ns)

    # Test: integer param should return "integer", not "string"
    result_precision = ns["_get_param_type"](MockSelf(), "precision")
    assert result_precision == "integer", (
        f"Expected 'integer' for precision, got '{result_precision}' "
        "(FunctionTool properties not resolved)"
    )

    result_dimensions = ns["_get_param_type"](MockSelf(), "dimensions")
    assert result_dimensions == "object", (
        f"Expected 'object' for dimensions, got '{result_dimensions}'"
    )

    result_shape = ns["_get_param_type"](MockSelf(), "shape")
    assert result_shape == "string", f"Expected 'string' for shape, got '{result_shape}'"

    print("PASS")
    '''))
    assert r.returncode == 0, f"Failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_coder_param_lookup_selects_correct_tool():
    """Property lookup must select the correct tool by name from multiple FunctionTools.

    Tests with three different FunctionTool objects and various lookup names
    to ensure the right tool's properties are returned.
    """
    r = _run_py(textwrap.dedent('''\
    import ast, sys, textwrap
    from typing import Any
    from pathlib import Path
    from openai.types.responses.function_tool import FunctionTool

    tools = [
        FunctionTool(
            type="function", name="get_weather",
            description="Get weather",
            parameters={"type": "object", "properties": {
                "city": {"type": "string"},
                "unit": {"type": "string"},
            }},
        ),
        FunctionTool(
            type="function", name="calculate_area",
            description="Calc area",
            parameters={"type": "object", "properties": {
                "shape": {"type": "string"},
                "precision": {"type": "integer"},
            }},
        ),
        FunctionTool(
            type="function", name="send_email",
            description="Send email",
            parameters={"type": "object", "properties": {
                "to": {"type": "string"},
                "body": {"type": "string"},
                "priority": {"type": "integer"},
            }},
        ),
    ]

    utils_src = Path("vllm/tool_parsers/utils.py").read_text()
    parser_src = Path("vllm/tool_parsers/qwen3coder_tool_parser.py").read_text()

    # Type stubs for annotations in extracted code
    class _DummyCCTP: pass
    _type_ns = {"FunctionTool": FunctionTool, "ChatCompletionToolsParam": _DummyCCTP,
                "Tool": FunctionTool, "Any": Any}

    def extract(src, name):
        tree = ast.parse(src)
        lines = src.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return textwrap.dedent("\\n".join(lines[node.lineno-1:node.end_lineno]))
        return None

    ftp_src = extract(utils_src, "find_tool_properties")
    eti_src = extract(utils_src, "_extract_tool_info")

    if ftp_src and eti_src:
        ns = dict(_type_ns)
        exec(compile(eti_src, "<eti>", "exec"), ns)
        exec(compile(ftp_src, "<ftp>", "exec"), ns)
        lookup = lambda name: ns["find_tool_properties"](tools, name)
    else:
        gac_src = extract(parser_src, "_get_arguments_config")
        assert gac_src, "No tool property lookup found"
        logger_mock = type("L", (), {"debug": lambda *a, **kw: None})()
        gac_ns = dict(_type_ns, logger=logger_mock)
        exec(compile(gac_src, "<gac>", "exec"), gac_ns)
        lookup = lambda name: gac_ns["_get_arguments_config"](None, name, tools)

    # Lookup weather tool
    weather = lookup("get_weather")
    assert "city" in weather, f"Expected city in weather props: {weather}"
    assert "unit" in weather, f"Expected unit in weather props: {weather}"
    assert "shape" not in weather, f"Got area props in weather lookup: {weather}"

    # Lookup area tool
    area = lookup("calculate_area")
    assert "shape" in area, f"Expected shape in area props: {area}"
    assert "precision" in area, f"Expected precision in area props: {area}"

    # Lookup email tool
    email = lookup("send_email")
    assert "to" in email, f"Expected 'to' in email props: {email}"
    assert "priority" in email, f"Expected priority in email props: {email}"
    assert email["priority"]["type"] == "integer"

    # Unknown tool returns empty
    unknown = lookup("nonexistent_tool")
    assert unknown == {}, f"Expected empty dict for unknown tool, got {unknown}"

    print("PASS")
    '''))
    assert r.returncode == 0, f"Failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static)
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_extract_tool_info_handles_function_tool():
    """_extract_tool_info in utils.py must handle FunctionTool objects.

    This utility already existed before the fix and correctly handles
    both ChatCompletionToolsParam and FunctionTool.
    """
    r = _run_py(textwrap.dedent('''\
    import ast, sys, textwrap
    from typing import Any
    from pathlib import Path
    from openai.types.responses.function_tool import FunctionTool

    utils_src = Path("vllm/tool_parsers/utils.py").read_text()

    def extract(src, name):
        tree = ast.parse(src)
        lines = src.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return textwrap.dedent("\\n".join(lines[node.lineno-1:node.end_lineno]))
        return None

    eti_src = extract(utils_src, "_extract_tool_info")
    assert eti_src, "_extract_tool_info not found in utils.py"

    class _DummyCCTP: pass
    ns = {"FunctionTool": FunctionTool, "ChatCompletionToolsParam": _DummyCCTP,
          "Tool": FunctionTool, "Any": Any}
    exec(compile(eti_src, "<eti>", "exec"), ns)

    tool = FunctionTool(
        type="function", name="test_func", description="Test",
        parameters={"type": "object", "properties": {"x": {"type": "integer"}}},
    )

    name, params = ns["_extract_tool_info"](tool)
    assert name == "test_func", f"Expected name='test_func', got '{name}'"
    assert isinstance(params, dict), f"Expected dict params, got {type(params)}"
    assert "properties" in params, f"Expected 'properties' in params: {params}"
    assert "x" in params["properties"], f"Expected 'x' in properties: {params}"

    # Test with a second tool to vary inputs
    tool2 = FunctionTool(
        type="function", name="another_func", description="Another",
        parameters={"type": "object", "properties": {
            "a": {"type": "string"},
            "b": {"type": "number"},
        }},
    )

    name2, params2 = ns["_extract_tool_info"](tool2)
    assert name2 == "another_func"
    assert params2["properties"]["b"]["type"] == "number"

    print("PASS")
    '''))
    assert r.returncode == 0, f"Failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_not_stub():
    """Modified parser files must not be stubs."""
    for fpath in [CODER_PARSER_FILE, XML_PARSER_FILE, UTILS_FILE]:
        src = fpath.read_text()
        line_count = len(src.splitlines())
        assert line_count >= 100, f"{fpath.name} too small ({line_count} lines)"

        tree = ast.parse(src)
        funcs = sum(
            1 for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        assert funcs >= 3, f"{fpath.name} only has {funcs} functions"
