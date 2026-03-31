#!/usr/bin/env bash
set +e

IO_STRUCT="/workspace/sglang/python/sglang/srt/managers/io_struct.py"
TM="/workspace/sglang/python/sglang/srt/managers/tokenizer_manager.py"
HS="/workspace/sglang/python/sglang/srt/entrypoints/http_server.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

SCORE=0

# ====== GATE: syntax check ======
python3 -c "import ast; ast.parse(open('$IO_STRUCT').read()); ast.parse(open('$TM').read()); ast.parse(open('$HS').read())" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; echo "GATE FAIL: syntax error"; exit 0; fi
echo "GATE PASS"

# ====== F2P BEHAVIORAL 1 (0.30): BaseReq has a working intra-batch duplicate rid validator ======
# [pr_diff] (0.30): Duplicate rid detection moved to request class and works correctly
# WHY AST EXTRACTION: sglang top-level imports torch; can't import directly on CPU
python3 << 'PYEOF'
import ast, sys, textwrap

with open("/workspace/sglang/python/sglang/srt/managers/io_struct.py") as f:
    source = f.read()
tree = ast.parse(source)

# Find ALL methods on BaseReq (skip __init__, regenerate_rid, __post_init__)
# and test each to find a working rid uniqueness validator — no name requirement
base_req_methods = []
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "BaseReq":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name not in (
                "__init__", "regenerate_rid", "__post_init__"
            ):
                lines = source.splitlines()
                method_src = "\n".join(lines[item.lineno - 1 : item.end_lineno])
                base_req_methods.append((item.name, method_src))

if not base_req_methods:
    print("FAIL: BaseReq has no candidate validation methods")
    sys.exit(1)

found = False
for name, method_src in base_req_methods:
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

        # Must RAISE ValueError on duplicate rids
        raised = False
        try:
            getattr(Cls(["a", "b", "a"]), name)()
        except ValueError:
            raised = True
        except Exception:
            continue
        if not raised:
            continue

        # Must NOT raise on unique rids
        try:
            getattr(Cls(["a", "b", "c"]), name)()
        except Exception:
            continue

        # Must NOT raise on single string rid
        try:
            getattr(Cls("single"), name)()
        except Exception:
            continue

        # Must NOT raise on None
        try:
            getattr(Cls(None), name)()
        except Exception:
            continue

        # Must NOT raise on empty list
        try:
            getattr(Cls([]), name)()
        except Exception:
            continue

        found = True
        print(f"PASS: BaseReq.{name} correctly validates rid uniqueness")
        break
    except Exception:
        continue

if not found:
    print("FAIL: No working rid uniqueness validator found on BaseReq")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && SCORE=$(python3 -c "print(round($SCORE + 0.30, 4))")
echo "After F2P_rid_validation: $SCORE"

# ====== F2P BEHAVIORAL 2 (0.15): TM in-flight check is separated from uniqueness check ======
# [pr_diff] (0.15): In-flight validation no longer rejects intra-batch duplicates
# WHY AST EXTRACTION: TokenizerManager requires asyncio, fastapi, torch — can't instantiate
python3 << 'PYEOF'
import ast, sys, textwrap

with open("/workspace/sglang/python/sglang/srt/managers/tokenizer_manager.py") as f:
    source = f.read()
tree = ast.parse(source)

# Find methods on TokenizerManager that reference rid_to_state (the in-flight store)
candidates = []
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "TokenizerManager":
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                lines = source.splitlines()
                method_text = "\n".join(lines[item.lineno - 1 : item.end_lineno])
                if "rid_to_state" in method_text and "validate" in item.name.lower():
                    candidates.append((item.name, method_text))

if not candidates:
    # Broader search: any method with rid_to_state that raises ValueError
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TokenizerManager":
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    lines = source.splitlines()
                    method_text = "\n".join(lines[item.lineno - 1 : item.end_lineno])
                    if "rid_to_state" in method_text and "ValueError" in method_text:
                        candidates.append((item.name, method_text))

if not candidates:
    print("FAIL: No rid validation method found on TokenizerManager")
    sys.exit(1)

passed = False
for name, method_src in candidates:
    try:
        dedented = textwrap.dedent(method_src)
        test_code = textwrap.dedent(f"""
from typing import Union

class FakeObj:
    def __init__(self, rid):
        self.rid = rid

# Stub the types referenced in annotations
GenerateReqInput = FakeObj
EmbeddingReqInput = FakeObj

class FakeTM:
    def __init__(self):
        self.rid_to_state = {{"existing_1": True, "existing_2": True}}
{textwrap.indent(dedented, '    ')}

tm = FakeTM()

# Test 1: in-flight conflict MUST raise ValueError
raised = False
try:
    tm.{name}(FakeObj(["new_1", "existing_1"]))
except ValueError:
    raised = True
if not raised:
    raise Exception("Did not raise on in-flight conflict")

# Test 2: duplicate but non-conflicting rids MUST NOT raise
# (uniqueness check should be handled elsewhere now)
try:
    tm.{name}(FakeObj(["dup_a", "dup_a"]))
except ValueError as e:
    raise Exception(f"Incorrectly raised on non-inflight duplicates: {{e}}")

# Test 3: None rid MUST NOT raise
try:
    tm.{name}(FakeObj(None))
except ValueError:
    raise Exception("Raised on None rid")

# Test 4: non-conflicting single rid MUST NOT raise
try:
    tm.{name}(FakeObj("safe_rid"))
except ValueError:
    raise Exception("Raised on non-conflicting single rid")
""")
        ns = {}
        exec(test_code, ns)
        print(f"PASS: TM.{name} correctly separates in-flight from uniqueness check")
        passed = True
        break
    except Exception as e:
        print(f"  TM.{name} failed: {e}")
        continue

if not passed:
    print("FAIL: No TM rid method passes in-flight separation test")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && SCORE=$(python3 -c "print(round($SCORE + 0.15, 4))")
echo "After F2P_inflight_separation: $SCORE"

# ====== P2P BEHAVIORAL (0.05): regenerate_rid still works ======
# [pr_diff] (0.05): Existing regenerate_rid preserved and functional
python3 << 'PYEOF'
import ast, sys, textwrap

with open("/workspace/sglang/python/sglang/srt/managers/io_struct.py") as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "BaseReq":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "regenerate_rid":
                lines = source.splitlines()
                method_src = "\n".join(lines[item.lineno - 1 : item.end_lineno])
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

                # Test: list of rids should regenerate
                obj = Cls(["a", "b"])
                result = obj.regenerate_rid()
                assert isinstance(result, list), f"Expected list, got {type(result)}"
                assert len(result) == 2, f"Expected 2 rids, got {len(result)}"

                # Test: single rid should regenerate
                obj2 = Cls("old")
                result2 = obj2.regenerate_rid()
                assert isinstance(result2, str), f"Expected str, got {type(result2)}"

                print("PASS: regenerate_rid works correctly")
                sys.exit(0)

print("FAIL: regenerate_rid not found on BaseReq")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && SCORE=$(python3 -c "print(round($SCORE + 0.05, 4))")
echo "After P2P_regenerate_rid: $SCORE"

# ====== P2P (0.05): is_generation still referenced in health check ======
# [pr_diff] (0.05): is_generation path preserved
grep -q 'is_generation' "$HS" 2>/dev/null
[ $? -eq 0 ] && SCORE=$(python3 -c "print(round($SCORE + 0.05, 4))") && echo "TEST P2P_is_generation: PASS" || echo "TEST P2P_is_generation: FAIL"
echo "After P2P_is_generation: $SCORE"

# ====== F2P STRUCTURAL (0.10): normalize_batch_and_arguments calls a BaseReq validation method ======
# [pr_diff] (0.10): rid validation integrated into request normalization
# WHY AST: Can't call normalize_batch_and_arguments (needs full sglang runtime with torch)
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/managers/io_struct.py") as f:
    source = f.read()
tree = ast.parse(source)

# Collect ALL BaseReq method names (excluding builtins and regenerate_rid)
base_req_methods = set()
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "BaseReq":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith("__") and item.name != "regenerate_rid":
                base_req_methods.add(item.name)

if not base_req_methods:
    print("FAIL: BaseReq has no validation methods to call")
    sys.exit(1)

# Check that BOTH GenerateReqInput and EmbeddingReqInput call ANY BaseReq method
# from their normalize_batch_and_arguments (not narrow to a specific method name)
gen_ok = False
embed_ok = False

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name in ("GenerateReqInput", "EmbeddingReqInput"):
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "normalize_batch_and_arguments":
                for subnode in ast.walk(item):
                    if isinstance(subnode, ast.Call) and isinstance(subnode.func, ast.Attribute):
                        if isinstance(subnode.func.value, ast.Name) and subnode.func.value.id == "self":
                            if subnode.func.attr in base_req_methods:
                                if node.name == "GenerateReqInput":
                                    gen_ok = True
                                else:
                                    embed_ok = True

if not gen_ok:
    print("FAIL: GenerateReqInput.normalize_batch_and_arguments doesn't call any BaseReq validation method")
    sys.exit(1)
if not embed_ok:
    print("FAIL: EmbeddingReqInput.normalize_batch_and_arguments doesn't call any BaseReq validation method")
    sys.exit(1)
print("PASS: Both request types call BaseReq validation from normalize_batch_and_arguments")
PYEOF
[ $? -eq 0 ] && SCORE=$(python3 -c "print(round($SCORE + 0.10, 4))")
echo "After normalize_integration: $SCORE"

# ====== F2P STRUCTURAL (0.10): Trace header priority — explicit context before HTTP ======
# [pr_diff] (0.10): gRPC/Engine trace context takes priority over HTTP headers
# WHY AST: _req_stats_init requires full server stack (asyncio, fastapi, torch)
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/managers/tokenizer_manager.py") as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_req_stats_init":
        # Find the enable_trace guard
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.If):
                test_dump = ast.dump(stmt.test)
                if "enable_trace" in test_dump:
                    if not stmt.body:
                        print("FAIL: empty enable_trace block"); sys.exit(1)
                    first = stmt.body[0]
                    if isinstance(first, ast.If):
                        cond = ast.dump(first.test)
                        if "external_trace_header" in cond:
                            print("PASS: explicit trace context has priority")
                            sys.exit(0)
                        elif "request" in cond:
                            print("FAIL: HTTP request checked before explicit trace context")
                            sys.exit(1)
                    # Fallback: check source ordering
                    block_lines = source.splitlines()[stmt.lineno - 1 : stmt.end_lineno]
                    block_src = "\n".join(block_lines)
                    ext_pos = block_src.find("external_trace_header")
                    req_pos = block_src.find("extract_trace_headers")
                    if req_pos < 0:
                        req_pos = block_src.find("request.headers")
                    if ext_pos >= 0 and (req_pos < 0 or ext_pos < req_pos):
                        print("PASS: explicit trace context has priority")
                        sys.exit(0)
                    else:
                        print("FAIL: HTTP request checked before explicit trace context")
                        sys.exit(1)

print("FAIL: Could not find enable_trace block in _req_stats_init")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && SCORE=$(python3 -c "print(round($SCORE + 0.10, 4))")
echo "After trace_priority: $SCORE"

# ====== STRUCTURAL (0.15): Dead code removed ======
# [pr_diff] (0.15): is_image_gen and current_load removed from codebase
python3 << 'PYEOF'
import sys

with open("/workspace/sglang/python/sglang/srt/managers/tokenizer_manager.py") as f:
    tm = f.read()
with open("/workspace/sglang/python/sglang/srt/entrypoints/http_server.py") as f:
    hs = f.read()

fails = []
if "self.is_image_gen" in tm:
    fails.append("is_image_gen still set on TokenizerManager")
if "self.current_load" in tm:
    fails.append("current_load still on TokenizerManager")
if "is_image_gen" in hs:
    fails.append("is_image_gen still referenced in http_server.py")

if fails:
    print("FAIL: " + "; ".join(fails)); sys.exit(1)
print("PASS: dead code removed")
PYEOF
[ $? -eq 0 ] && SCORE=$(python3 -c "print(round($SCORE + 0.15, 4))")
echo "After dead_code: $SCORE"

# ====== F2P STRUCTURAL (0.05): Old monolithic _validate_rid removed from TokenizerManager ======
# [pr_diff] (0.05): Monolithic _validate_rid (which mixed uniqueness + in-flight) is gone
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/managers/tokenizer_manager.py") as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "TokenizerManager":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "_validate_rid":
                print("FAIL: old monolithic _validate_rid still exists on TokenizerManager")
                sys.exit(1)

print("PASS: old _validate_rid removed")
PYEOF
[ $? -eq 0 ] && SCORE=$(python3 -c "print(round($SCORE + 0.05, 4))")
echo "After old_method_removed: $SCORE"

# ====== F2P STRUCTURAL (0.05): CPU monitor thread in metric collector ======
# [pr_diff] (0.05): start_cpu_monitor_thread moved to init_metric_collector_watchdog
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/managers/tokenizer_manager.py") as f:
    source = f.read()
tree = ast.parse(source)

in_metric_init = False
in_init = False

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "TokenizerManager":
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
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

if in_init and not in_metric_init:
    print("FAIL: start_cpu_monitor_thread still directly in __init__")
    sys.exit(1)
if in_metric_init:
    print("PASS: CPU monitor thread in metric collector init")
    sys.exit(0)
# If not found anywhere, agent may have removed it — check it's at least not in __init__
if not in_init:
    print("PASS: start_cpu_monitor_thread not in __init__")
    sys.exit(0)
print("FAIL: unexpected state")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && SCORE=$(python3 -c "print(round($SCORE + 0.05, 4))")
echo "After cpu_monitor: $SCORE"

# ====== COMPUTE REWARD ======
echo ""
echo "=== TOTAL REWARD: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
