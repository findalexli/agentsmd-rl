"""
Task: sglang-tokenizer-cleanup
Repo: sgl-project/sglang @ f3970b17ef043c069e30a5cb9ffa83bd97f8679c
PR:   #21639

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral tests use subprocess.run() to execute actual code.
Heavy dependencies (torch) are mocked to enable imports.
"""

import ast
import subprocess
import sys
import textwrap
from pathlib import Path

REPO = "/workspace/sglang"
IO_STRUCT = f"{REPO}/python/sglang/srt/managers/io_struct.py"
TM = f"{REPO}/python/sglang/srt/managers/tokenizer_manager.py"
HS = f"{REPO}/python/sglang/srt/entrypoints/http_server.py"


def _extract_method(filepath, class_name, method_name=None, predicate=None):
    """Extract method source from a class. Returns list of (name, source) tuples."""
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if not isinstance(item, ast.FunctionDef):
                    continue
                if method_name and item.name != method_name:
                    continue
                if predicate and not predicate(item.name):
                    continue
                lines = source.splitlines()
                method_src = "\n".join(lines[item.lineno - 1 : item.end_lineno])
                results.append((item.name, method_src))
    return results


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code with mocked torch/sglang heavy deps."""
    mock_prelude = '''
import sys
from unittest.mock import MagicMock

# Mock heavy dependencies that require GPU/native libs
for mod in ["torch", "torch.nn", "vllm", "sgl_kernel", "flashinfer"]:
    sys.modules[mod] = MagicMock()
    parts = mod.split(".")
    for i in range(1, len(parts)):
        sys.modules[".".join(parts[:i])] = MagicMock()

# Now we can import the actual code
'''
    full_code = mock_prelude + code
    return subprocess.run(
        [sys.executable, "-c", full_code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# -----------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for path in [IO_STRUCT, TM, HS]:
        source = Path(path).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass -- BEHAVIORAL via subprocess
# This test EXECUTES actual code: it finds the _validate_rid_uniqueness method
# on BaseReq, creates a mock implementation, and tests it with real inputs.
def test_basereq_rid_uniqueness_validation():
    """BaseReq._validate_rid_uniqueness raises ValueError on duplicate rids, accepts valid inputs."""
    # Find the method source
    methods = _extract_method(
        IO_STRUCT, "BaseReq",
        predicate=lambda n: n not in ("__init__", "regenerate_rid", "__post_init__"),
    )
    assert methods, "BaseReq has no candidate validation methods"

    for name, method_src in methods:
        test_code = f'''
from collections import Counter

class FakeReq:
    def __init__(self, rid):
        self.rid = rid
{textwrap.indent(textwrap.dedent(method_src), "    ")}

# Test cases
obj1 = FakeReq(["a", "b", "a"])  # duplicates
try:
    obj1.{name}()
    print("FAIL: Should have raised on duplicates")
    sys.exit(1)
except ValueError as e:
    if "Duplicate request IDs" in str(e):
        print("PASS: Correctly raised on duplicates")
    else:
        print(f"FAIL: Wrong error message: {{e}}")
        sys.exit(1)

obj2 = FakeReq(["a", "b", "c"])  # valid list
try:
    obj2.{name}()
    print("PASS: Accepted valid list")
except Exception as e:
    print(f"FAIL: Should not raise on valid list: {{e}}")
    sys.exit(1)

obj3 = FakeReq("single")  # single string
try:
    obj3.{name}()
    print("PASS: Accepted single string")
except Exception as e:
    print(f"FAIL: Should not raise on single string: {{e}}")
    sys.exit(1)

obj4 = FakeReq(None)  # None
try:
    obj4.{name}()
    print("PASS: Accepted None")
except Exception as e:
    print(f"FAIL: Should not raise on None: {{e}}")
    sys.exit(1)

print("ALL_PASSED")
'''
        r = _run_py(test_code)
        if r.returncode == 0 and "ALL_PASSED" in r.stdout:
            return  # Test passed
        # Try next candidate method

    raise AssertionError("No BaseReq method passes rid uniqueness validation test")


# [pr_diff] fail_to_pass -- BEHAVIORAL via subprocess
# This test EXECUTES actual code: it tests the renamed _validate_rid_not_in_flight
# method with real mock inputs, verifying both error and success paths.
def test_inflight_rid_separation():
    """TM._validate_rid_not_in_flight raises on in-flight conflicts but NOT on non-inflight duplicates."""
    source = Path(TM).read_text()
    tree = ast.parse(source)

    candidates = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TokenizerManager":
            for item in node.body:
                if not isinstance(item, ast.FunctionDef):
                    continue
                lines = source.splitlines()
                method_text = "\n".join(lines[item.lineno - 1 : item.end_lineno])
                if "rid_to_state" in method_text and (
                    "ValueError" in method_text or "raise" in method_text
                ):
                    candidates.append((item.name, method_text))

    assert candidates, "No rid validation method found on TokenizerManager"

    for name, method_src in candidates:
        test_code = f'''
from typing import Union

class FakeObj:
    def __init__(self, rid):
        self.rid = rid

class FakeTM:
    def __init__(self):
        self.rid_to_state = {{"existing_1": True, "existing_2": True}}
{textwrap.indent(textwrap.dedent(method_src), "    ")}

tm = FakeTM()

# Test 1: In-flight conflict with list MUST raise
raised = False
try:
    tm.{name}(FakeObj(["new_1", "existing_1"]))
except ValueError as e:
    if "existing_1" in str(e):
        raised = True
if not raised:
    print("FAIL: Did not raise on in-flight conflict (list)")
    sys.exit(1)
print("PASS: Raised on in-flight conflict (list)")

# Test 2: Single in-flight conflict MUST raise
raised2 = False
try:
    tm.{name}(FakeObj("existing_2"))
except ValueError as e:
    if "existing_2" in str(e):
        raised2 = True
if not raised2:
    print("FAIL: Did not raise on single in-flight conflict")
    sys.exit(1)
print("PASS: Raised on single in-flight conflict")

# Test 3: Duplicate but non-conflicting rids MUST NOT raise
# (uniqueness check is now handled by BaseReq, not TM)
try:
    tm.{name}(FakeObj(["dup_a", "dup_a"]))
except ValueError as e:
    print(f"FAIL: Incorrectly raised on non-inflight duplicates: {{e}}")
    sys.exit(1)
print("PASS: Did not raise on non-inflight duplicates")

# Test 4: None rid MUST NOT raise
try:
    tm.{name}(FakeObj(None))
except ValueError as e:
    print("FAIL: Raised on None rid")
    sys.exit(1)
print("PASS: Did not raise on None rid")

# Test 5: Non-conflicting single rid MUST NOT raise
try:
    tm.{name}(FakeObj("safe_rid"))
except ValueError as e:
    print("FAIL: Raised on non-conflicting single rid")
    sys.exit(1)
print("PASS: Did not raise on non-conflicting single rid")

print("ALL_PASSED")
'''
        r = _run_py(test_code)
        if r.returncode == 0 and "ALL_PASSED" in r.stdout:
            return  # Test passed
        # Try next candidate

    raise AssertionError("No TM rid method passes in-flight separation test")


# -----------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- regression
# -----------------------------------------------------------------------------

# [pr_diff] pass_to_pass -- BEHAVIORAL via subprocess
def test_regenerate_rid_preserved():
    """regenerate_rid on BaseReq still works for both list and single rids."""
    methods = _extract_method(IO_STRUCT, "BaseReq", method_name="regenerate_rid")
    assert methods, "regenerate_rid not found on BaseReq"

    _, method_src = methods[0]

    test_code = f'''
import uuid

class FakeReq:
    def __init__(self, rid):
        self.rid = rid
{textwrap.indent(textwrap.dedent(method_src), "    ")}

# Test list of rids
obj1 = FakeReq(["a", "b"])
result1 = obj1.regenerate_rid()
if not isinstance(result1, list):
    print(f"FAIL: Expected list, got {{type(result1)}}")
    sys.exit(1)
if len(result1) != 2:
    print(f"FAIL: Expected 2 rids, got {{len(result1)}}")
    sys.exit(1)
print("PASS: List regeneration works")

# Test single rid
obj2 = FakeReq("old")
result2 = obj2.regenerate_rid()
if not isinstance(result2, str):
    print(f"FAIL: Expected str, got {{type(result2)}}")
    sys.exit(1)
print("PASS: Single rid regeneration works")

print("ALL_PASSED")
'''
    r = _run_py(test_code)
    assert r.returncode == 0 and "ALL_PASSED" in r.stdout, f"Test failed: {r.stdout}\n{r.stderr}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- AST-based structural checks (these remain AST-based
# because they verify code structure/placement which cannot be tested via runtime)
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: normalize_batch_and_arguments has heavy deps (sglang runtime, model configs)
def test_normalize_calls_rid_validation():
    """Both GenerateReqInput and EmbeddingReqInput call a BaseReq validation method from normalize_batch_and_arguments."""
    source = Path(IO_STRUCT).read_text()
    tree = ast.parse(source)

    # Collect BaseReq method names (excluding builtins and regenerate_rid)
    base_req_methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "BaseReq":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith("__") and item.name != "regenerate_rid":
                    base_req_methods.add(item.name)

    assert base_req_methods, "BaseReq has no validation methods"

    found = {"GenerateReqInput": False, "EmbeddingReqInput": False}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in found:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "normalize_batch_and_arguments":
                    for subnode in ast.walk(item):
                        if (isinstance(subnode, ast.Call)
                                and isinstance(subnode.func, ast.Attribute)
                                and isinstance(subnode.func.value, ast.Name)
                                and subnode.func.value.id == "self"
                                and subnode.func.attr in base_req_methods):
                            found[node.name] = True

    assert found["GenerateReqInput"], "GenerateReqInput.normalize_batch_and_arguments doesn't call BaseReq validation"
    assert found["EmbeddingReqInput"], "EmbeddingReqInput.normalize_batch_and_arguments doesn't call BaseReq validation"


# [pr_diff] fail_to_pass
# AST-only because: _req_stats_init requires full TokenizerManager with server_args, metrics, etc.
def test_trace_header_priority():
    """Explicit trace context (obj.external_trace_header) is checked before HTTP request headers."""
    source = Path(TM).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_req_stats_init":
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.If):
                    test_dump = ast.dump(stmt.test)
                    if "enable_trace" in test_dump:
                        block_lines = source.splitlines()[stmt.lineno - 1 : stmt.end_lineno]
                        block_src = "\n".join(block_lines)
                        ext_pos = block_src.find("external_trace_header")
                        req_pos = block_src.find("extract_trace_headers")
                        if req_pos < 0:
                            req_pos = block_src.find("request.headers")
                        assert ext_pos >= 0, "external_trace_header not found in enable_trace block"
                        assert req_pos < 0 or ext_pos < req_pos, \
                            "HTTP request checked before explicit trace context"
                        return

    raise AssertionError("Could not find enable_trace block in _req_stats_init")


# [pr_diff] fail_to_pass
# AST-only because: checking absence of attributes — no behavior to call
def test_dead_code_removed():
    """is_image_gen, current_load, current_load_lock removed from TM and http_server."""
    tm_src = Path(TM).read_text()
    hs_src = Path(HS).read_text()

    fails = []
    if "self.is_image_gen" in tm_src:
        fails.append("is_image_gen still set on TokenizerManager")
    if "self.current_load" in tm_src:
        fails.append("current_load still on TokenizerManager")
    if "is_image_gen" in hs_src:
        fails.append("is_image_gen still referenced in http_server.py")

    # Old monolithic _validate_rid must be gone
    tree = ast.parse(tm_src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TokenizerManager":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "_validate_rid":
                    fails.append("old monolithic _validate_rid still exists")

    assert not fails, "; ".join(fails)


# [pr_diff] fail_to_pass
# AST-only because: checking function placement across methods — no callable behavior
def test_cpu_monitor_placement():
    """start_cpu_monitor_thread is in init_metric_collector_watchdog, not __init__."""
    source = Path(TM).read_text()
    tree = ast.parse(source)

    in_metric_init = False
    in_init = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TokenizerManager":
            for item in node.body:
                if not isinstance(item, ast.FunctionDef):
                    continue
                for subnode in ast.walk(item):
                    if isinstance(subnode, ast.Call):
                        func = subnode.func
                        fname = None
                        if isinstance(func, ast.Name):
                            fname = func.id
                        elif isinstance(func, ast.Attribute):
                            fname = func.attr
                        if fname == "start_cpu_monitor_thread":
                            if item.name == "init_metric_collector_watchdog":
                                in_metric_init = True
                            elif item.name == "__init__":
                                in_init = True

    assert in_metric_init, "start_cpu_monitor_thread not found in init_metric_collector_watchdog"
    assert not in_init, "start_cpu_monitor_thread still directly in __init__ (should only be in init_metric_collector_watchdog)"
