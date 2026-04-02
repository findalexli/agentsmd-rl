"""
Task: sglang-tokenizer-cleanup
Repo: sgl-project/sglang @ f3970b17ef043c069e30a5cb9ffa83bd97f8679c
PR:   #21639

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: sglang imports torch at top level, so we cannot import modules directly.
Behavioral tests extract methods via AST and execute them in isolation.
"""

import ast
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


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for path in [IO_STRUCT, TM, HS]:
        source = Path(path).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_basereq_rid_uniqueness_validation():
    """BaseReq has a method that rejects duplicate rids in a batch and accepts valid inputs."""
    methods = _extract_method(
        IO_STRUCT, "BaseReq",
        predicate=lambda n: n not in ("__init__", "regenerate_rid", "__post_init__"),
    )
    assert methods, "BaseReq has no candidate validation methods"

    for name, method_src in methods:
        try:
            class_code = f"""
from collections import Counter
class FakeReq:
    def __init__(self, rid):
        self.rid = rid
{textwrap.indent(textwrap.dedent(method_src), '    ')}
"""
            ns = {}
            exec(class_code, ns)
            Cls = ns["FakeReq"]

            # Must RAISE ValueError on duplicate rids (two patterns)
            for dups in [["a", "b", "a"], ["x", "y", "z", "x", "y"]]:
                raised = False
                try:
                    getattr(Cls(dups), name)()
                except ValueError:
                    raised = True
                except Exception:
                    break
                if not raised:
                    break
            else:
                # Must NOT raise on valid inputs
                for valid in [["a", "b", "c"], "single", None, []]:
                    try:
                        getattr(Cls(valid), name)()
                    except Exception:
                        break
                else:
                    return  # All checks passed
        except Exception:
            continue

    raise AssertionError("No working rid uniqueness validator found on BaseReq")


# [pr_diff] fail_to_pass
def test_inflight_rid_separation():
    """TM in-flight check raises on conflicts but NOT on non-inflight duplicates."""
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
        try:
            dedented = textwrap.dedent(method_src)
            test_code = textwrap.dedent(f"""
from typing import Union

class FakeObj:
    def __init__(self, rid):
        self.rid = rid

GenerateReqInput = FakeObj
EmbeddingReqInput = FakeObj

class FakeTM:
    def __init__(self):
        self.rid_to_state = {{"existing_1": True, "existing_2": True}}
{textwrap.indent(dedented, '    ')}

tm = FakeTM()

# In-flight conflict MUST raise ValueError
raised = False
try:
    tm.{name}(FakeObj(["new_1", "existing_1"]))
except ValueError:
    raised = True
assert raised, "Did not raise on in-flight conflict"

# Single in-flight conflict MUST raise
raised2 = False
try:
    tm.{name}(FakeObj("existing_2"))
except ValueError:
    raised2 = True
assert raised2, "Did not raise on single in-flight conflict"

# Duplicate but non-conflicting rids MUST NOT raise
# (uniqueness check is now handled by BaseReq, not TM)
try:
    tm.{name}(FakeObj(["dup_a", "dup_a"]))
except ValueError as e:
    raise AssertionError(f"Incorrectly raised on non-inflight duplicates: {{e}}")

# None rid MUST NOT raise
try:
    tm.{name}(FakeObj(None))
except ValueError:
    raise AssertionError("Raised on None rid")

# Non-conflicting single rid MUST NOT raise
try:
    tm.{name}(FakeObj("safe_rid"))
except ValueError:
    raise AssertionError("Raised on non-conflicting single rid")
""")
            ns = {}
            exec(test_code, ns)
            return  # Passed
        except Exception:
            continue

    raise AssertionError("No TM rid method passes in-flight separation test")


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_regenerate_rid_preserved():
    """regenerate_rid on BaseReq still works for both list and single rids."""
    methods = _extract_method(IO_STRUCT, "BaseReq", method_name="regenerate_rid")
    assert methods, "regenerate_rid not found on BaseReq"

    _, method_src = methods[0]
    class_code = f"""
import uuid
class FakeReq:
    def __init__(self, rid):
        self.rid = rid
{textwrap.indent(textwrap.dedent(method_src), '    ')}
"""
    ns = {}
    exec(class_code, ns)
    Cls = ns["FakeReq"]

    # List of rids should regenerate to new list of same length
    obj = Cls(["a", "b"])
    result = obj.regenerate_rid()
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) == 2, f"Expected 2 rids, got {len(result)}"

    # Single rid should regenerate to new string
    obj2 = Cls("old")
    result2 = obj2.regenerate_rid()
    assert isinstance(result2, str), f"Expected str, got {type(result2)}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- structural checks
# ---------------------------------------------------------------------------

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
