"""
Task: sglang-session-mm-leak
Repo: sgl-project/sglang @ c2b3e42ad64521c018443f7efe294658a0b1da3b
PR:   #21501

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: sglang modules import torch/CUDA at module level, so we cannot
import them directly on a CPU-only container.  Tests use subprocess to
extract and execute the relevant code with mocks.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace"
BATCH_FILE = f"{REPO}/python/sglang/srt/managers/schedule_batch.py"
SESSION_FILE = f"{REPO}/python/sglang/srt/managers/session_controller.py"
SCHEDULER_FILE = f"{REPO}/python/sglang/srt/managers/scheduler.py"
OUTPUT_PROC_FILE = f"{REPO}/python/sglang/srt/managers/scheduler_output_processor_mixin.py"

ALL_FILES = [BATCH_FILE, SESSION_FILE, SCHEDULER_FILE, OUTPUT_PROC_FILE]


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess in the repo directory."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All four modified files must parse without syntax errors."""
    for filepath in ALL_FILES:
        source = Path(filepath).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_release_features_clears_all():
    """MultimodalInputs.release_features() sets feature=None on every mm_item."""
    r = _run_py("""\
import ast, textwrap
from pathlib import Path

source = Path('python/sglang/srt/managers/schedule_batch.py').read_text()
tree = ast.parse(source)
method_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'MultimodalInputs':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'release_features':
                method_src = ast.get_source_segment(source, item)
                break

assert method_src is not None, "release_features method not found on MultimodalInputs"

env = {}
exec(textwrap.dedent(f'''
class MockItem:
    def __init__(self, feature):
        self.feature = feature

class MultimodalInputs:
    def __init__(self, mm_items):
        self.mm_items = mm_items

{textwrap.indent(method_src, '    ')}
'''), env)

MI = env['MultimodalInputs']
MockItem = env['MockItem']

# Multiple items
items = [MockItem('tensor_a'), MockItem('tensor_b'), MockItem('tensor_c')]
MI(items).release_features()
for i, item in enumerate(items):
    assert item.feature is None, f'item {i} feature not released'

# Empty list must not crash
MI([]).release_features()

# Idempotent — calling twice must not crash
items2 = [MockItem('x')]
mm = MI(items2)
mm.release_features()
mm.release_features()
assert items2[0].feature is None

# Attribute must still exist (set to None, not deleted)
items3 = [MockItem('data')]
MI(items3).release_features()
assert hasattr(items3[0], 'feature'), 'feature attr deleted instead of set to None'

print('PASS')
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_close_releases_session_mm_features():
    """SessionController._close() releases multimodal features from session requests."""
    r = _run_py("""\
import ast, textwrap
from pathlib import Path

source = Path('python/sglang/srt/managers/session_controller.py').read_text()
tree = ast.parse(source)
close_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SessionController':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '_close':
                close_src = ast.get_source_segment(source, item)
                break

assert close_src is not None, "SessionController._close method not found"

env = {}
exec(textwrap.dedent('''
import logging

class SessionAwareCache:
    pass

class MockTreeCache(SessionAwareCache):
    def release_session(self, sid):
        pass

class MockMMItem:
    def __init__(self):
        self.feature = "gpu_tensor_data"

class MockMMInputs:
    def __init__(self, items):
        self.mm_items = items
    def release_features(self):
        for item in self.mm_items:
            item.feature = None

class MockReq:
    def __init__(self, mm_inputs=None):
        self.multimodal_inputs = mm_inputs
        self.session = "active_session"
    def finished(self):
        return True

class MockNode:
    def __init__(self, req):
        self.req = req

class Session:
    def __init__(self, nodes):
        self.req_nodes = nodes
        self.streaming = False

class SessionController:
    def __init__(self, session, sid):
        self.sessions = {sid: session}
        self.tree_cache = MockTreeCache()
'''), env)

exec(textwrap.dedent(f'''
class SessionControllerTest(SessionController):
{textwrap.indent(close_src, '    ')}
'''), env)

MockMMItem = env['MockMMItem']
MockMMInputs = env['MockMMInputs']
MockReq = env['MockReq']
MockNode = env['MockNode']
Session = env['Session']
TestCtrl = env['SessionControllerTest']

# Two requests share one MMInputs, one has its own, one has none
shared_items = [MockMMItem(), MockMMItem()]
shared_mm = MockMMInputs(shared_items)
own_items = [MockMMItem()]
own_mm = MockMMInputs(own_items)

nodes = {
    "r1": MockNode(MockReq(shared_mm)),
    "r2": MockNode(MockReq(shared_mm)),
    "r3": MockNode(MockReq(own_mm)),
    "r4": MockNode(MockReq(None)),
}
session = Session(nodes)
controller = TestCtrl(session, "s1")

# Pre-check: features alive
assert all(i.feature is not None for i in shared_items + own_items)

controller._close("s1")

# All features released
for label, items in [("shared", shared_items), ("own", own_items)]:
    for i, item in enumerate(items):
        assert item.feature is None, f"{label} item {i} feature not released"

# multimodal_inputs cleared on every request
for key, node in nodes.items():
    assert node.req.multimodal_inputs is None, f"{key} multimodal_inputs not cleared"

# Session removed
assert "s1" not in controller.sessions, "session not deleted after _close"

print('PASS')
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_bos_offset_clamping():
    """BOS offset adjustment in Session.create_req doesn't produce negative values."""
    r = _run_py("""\
import ast
from pathlib import Path

source = Path('python/sglang/srt/managers/session_controller.py').read_text()
tree = ast.parse(source)

create_req_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'Session':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'create_req':
                create_req_node = item
                break

assert create_req_node is not None, "Session.create_req not found"

found = False
for node in ast.walk(create_req_node):
    if not isinstance(node, ast.Assign):
        continue
    for target in node.targets:
        if not (isinstance(target, ast.Attribute) and target.attr == 'offsets'):
            continue
        if not any(isinstance(n, ast.Sub) for n in ast.walk(node.value)):
            continue

        rhs_src = ast.get_source_segment(source, node.value)
        if rhs_src is None:
            continue

        if isinstance(node.value, ast.ListComp):
            for gen in node.value.generators:
                iter_src = ast.get_source_segment(source, gen.iter)
                if iter_src is None:
                    continue
                test_expr = rhs_src.replace(iter_src, 'test_offsets')

                cases = [
                    [(0, 5)],         # BOS edge: s=0
                    [(0, 0)],         # double-zero
                    [(1, 10)],        # normal
                    [(0, 5), (3, 8)], # mixed
                    [(5, 10)],        # should subtract
                ]
                for offsets in cases:
                    ns = {'test_offsets': offsets, 'max': max, 'min': min}
                    result = eval(test_expr, ns)
                    for s, e in result:
                        assert s >= 0 and e >= 0, (
                            f'Negative offset from {offsets}: got {result}'
                        )

                # Verify it actually subtracts for non-zero
                ns = {'test_offsets': [(5, 10)], 'max': max, 'min': min}
                result = eval(test_expr, ns)
                assert result[0][0] < 5, (
                    f'Offset not adjusted downward: (5,10) -> {result}'
                )
                found = True
                break
    if found:
        break

assert found, 'No clamped offset adjustment found in create_req'
print('PASS')
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_callers_use_release_features():
    """scheduler.py and output_processor call .release_features() instead of inline loop."""
    for filepath in [SCHEDULER_FILE, OUTPUT_PROC_FILE]:
        source = Path(filepath).read_text()
        tree = ast.parse(source)

        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "release_features":
                    found = True
                    break

        assert found, f"{filepath} does not call .release_features()"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_class_structure_preserved():
    """Core classes and methods unchanged across all modified files."""
    checks = {
        BATCH_FILE: {
            "MultimodalInputs": None,
            "MultimodalDataItem": None,
        },
        SESSION_FILE: {
            "SessionReqNode": ["clear_children", "clear", "abort"],
            "Session": ["create_req", "is_timed_out"],
            "SessionController": ["open", "close", "_close", "maybe_reap"],
        },
    }
    for filepath, classes in checks.items():
        source = Path(filepath).read_text()
        tree = ast.parse(source)

        found_classes: dict[str, set[str]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in classes:
                found_classes[node.name] = {
                    n.name for n in node.body if isinstance(n, ast.FunctionDef)
                }

        for cls_name, methods in classes.items():
            assert cls_name in found_classes, f"{cls_name} missing from {filepath}"
            if methods:
                for m in methods:
                    assert m in found_classes[cls_name], (
                        f"{cls_name}.{m} missing from {filepath}"
                    )
