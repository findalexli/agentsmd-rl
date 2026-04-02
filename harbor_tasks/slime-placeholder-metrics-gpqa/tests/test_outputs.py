"""
Task: slime-placeholder-metrics-gpqa
Repo: THUDM/slime @ 5996c6881e484fe0985ff3c8b8c8ce1af4e32632
PR:   1746

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import textwrap
from pathlib import Path

REPO = "/workspace/slime"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for f in [
        "slime/rollout/rm_hub/gpqa.py",
        "slime/router/router.py",
        "slime/ray/rollout.py",
    ]:
        src = Path(f"{REPO}/{f}").read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — GPQA letter range
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_gpqa_label_8_letter_i():
    """Integer label 8 (letter I, 9th option) must score correctly."""
    import sys
    sys.path.insert(0, REPO)
    from slime.rollout.rm_hub.gpqa import compute_gpqa_reward

    # Correct answer for label 8 (letter I)
    assert compute_gpqa_reward("The answer is I", 8) == 1.0
    # Wrong answers for label 8
    assert compute_gpqa_reward("The answer is A", 8) == 0.0
    assert compute_gpqa_reward("The answer is H", 8) == 0.0


# [pr_diff] fail_to_pass
def test_gpqa_label_9_letter_j():
    """Integer label 9 (letter J, 10th option) must score correctly."""
    import sys
    sys.path.insert(0, REPO)
    from slime.rollout.rm_hub.gpqa import compute_gpqa_reward

    # Correct answer for label 9 (letter J)
    assert compute_gpqa_reward("The answer is J", 9) == 1.0
    # Wrong answers for label 9
    assert compute_gpqa_reward("The answer is A", 9) == 0.0
    assert compute_gpqa_reward("The answer is I", 9) == 0.0


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — GPQA regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_gpqa_existing_labels_a_through_h():
    """Existing A-H labels must still return correct rewards."""
    import sys
    sys.path.insert(0, REPO)
    from slime.rollout.rm_hub.gpqa import compute_gpqa_reward

    for idx, letter in enumerate("ABCDEFGH"):
        reward = compute_gpqa_reward(f"The answer is {letter}", idx)
        assert reward == 1.0, f"Expected 1.0 for label={idx} ({letter}), got {reward}"

    # Wrong answers should score 0 — test multiple pairs
    assert compute_gpqa_reward("The answer is A", 1) == 0.0
    assert compute_gpqa_reward("The answer is C", 5) == 0.0
    assert compute_gpqa_reward("The answer is H", 0) == 0.0


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — WorkerType PLACEHOLDER enum
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_workertype_placeholder_enum():
    """WorkerType enum must include PLACEHOLDER with value 'placeholder'."""
    # AST-only because: router.py imports ray at module level
    import enum

    source = Path(f"{REPO}/slime/router/router.py").read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "WorkerType":
            start = node.lineno - 1
            end = node.end_lineno
            lines = source.splitlines()[start:end]
            cls_source = "\n".join(lines)
            ns = {"Enum": enum.Enum, "str": str}
            exec(cls_source, ns)
            WorkerType = ns["WorkerType"]
            assert "PLACEHOLDER" in WorkerType.__members__, (
                f"WorkerType missing PLACEHOLDER, has: {list(WorkerType.__members__)}"
            )
            assert WorkerType.PLACEHOLDER.value == "placeholder"
            # Existing members still present
            for name in ("REGULAR", "PREFILL", "DECODE"):
                assert name in WorkerType.__members__, f"Missing existing member {name}"
            return

    raise AssertionError("WorkerType class not found in router.py")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — nodes_per_engine filters placeholders
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_nodes_per_engine_ignores_placeholder():
    """nodes_per_engine must exclude placeholder groups to avoid ValueError."""
    # AST-only because: rollout.py imports ray, torch at module level
    source = Path(f"{REPO}/slime/ray/rollout.py").read_text()
    tree = ast.parse(source)

    prop_source = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if (
                    isinstance(item, ast.FunctionDef)
                    and item.name == "nodes_per_engine"
                    and any(
                        isinstance(d, ast.Name) and d.id == "property"
                        for d in item.decorator_list
                    )
                ):
                    src = ast.get_source_segment(source, item)
                    if src and "self.server_groups" in src:
                        prop_source = src
                        break
        if prop_source:
            break

    assert prop_source is not None, "Could not find RolloutServer.nodes_per_engine"

    class FakeGroup:
        def __init__(self, npe, wtype):
            self.nodes_per_engine = npe
            self.worker_type = wtype

    class FakeSelf:
        def __init__(self, groups):
            self.server_groups = groups

    func_lines = prop_source.splitlines()
    body_lines = [l for l in func_lines if not l.strip().startswith("@")]
    func_code = textwrap.dedent("\n".join(body_lines))

    exec_ns = {}
    exec(func_code, exec_ns)
    method = exec_ns["nodes_per_engine"]

    # Regular (npe=1) + placeholder (npe=4) → should return 1, not raise
    self_obj = FakeSelf([FakeGroup(1, "regular"), FakeGroup(4, "placeholder")])
    result = method(self_obj)
    assert result == 1, f"Expected 1 (ignoring placeholder), got {result}"

    # Two active groups (same npe) + placeholder with different npe → return 2
    self_obj2 = FakeSelf([
        FakeGroup(2, "regular"),
        FakeGroup(2, "prefill"),
        FakeGroup(8, "placeholder"),
    ])
    result2 = method(self_obj2)
    assert result2 == 2, f"Expected 2 (ignoring placeholder), got {result2}"

    # Single regular + multiple placeholders with varied npe
    self_obj3 = FakeSelf([
        FakeGroup(4, "regular"),
        FakeGroup(1, "placeholder"),
        FakeGroup(2, "placeholder"),
    ])
    result3 = method(self_obj3)
    assert result3 == 4, f"Expected 4 (ignoring all placeholders), got {result3}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — init_tracking moved after server launch
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_init_tracking_after_server_launch():
    """init_tracking must be called after start_rollout_servers in RolloutManager.__init__."""
    # AST-only because: rollout.py imports ray, torch at module level
    source = Path(f"{REPO}/slime/ray/rollout.py").read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RolloutManager":
            init_method = None
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    init_method = item
                    break
            assert init_method is not None, "RolloutManager.__init__ not found"

            init_tracking_line = None
            server_setup_line = None

            for child in ast.walk(init_method):
                if isinstance(child, ast.Call):
                    func = child.func
                    if isinstance(func, ast.Name) and func.id == "init_tracking":
                        init_tracking_line = child.lineno
                    if isinstance(func, ast.Name) and func.id == "start_rollout_servers":
                        server_setup_line = child.lineno
                    if isinstance(func, ast.Name) and func.id == "init_http_client":
                        if server_setup_line is None:
                            server_setup_line = child.lineno

            assert init_tracking_line is not None, "init_tracking not found in __init__"
            assert server_setup_line is not None, "start_rollout_servers not found in __init__"
            assert init_tracking_line > server_setup_line, (
                f"init_tracking (line {init_tracking_line}) must be after "
                f"start_rollout_servers (line {server_setup_line})"
            )
            return

    raise AssertionError("RolloutManager class not found")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — _get_metrics_router_addr behavior
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_get_metrics_router_addr_behavior():
    """_get_metrics_router_addr must return correct URL or None based on config."""
    # AST-only because: rollout.py imports ray, torch at module level
    import logging

    source = Path(f"{REPO}/slime/ray/rollout.py").read_text()
    tree = ast.parse(source)

    method_src = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RolloutManager":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "_get_metrics_router_addr":
                    method_src = ast.get_source_segment(source, item)
                    break
            break

    assert method_src is not None, "_get_metrics_router_addr not found in RolloutManager"

    func_lines = method_src.splitlines()
    body_lines = [l for l in func_lines if not l.strip().startswith("@")]
    func_code = textwrap.dedent("\n".join(body_lines))

    ns = {"logger": logging.getLogger("test")}
    exec(func_code, ns)
    method = ns["_get_metrics_router_addr"]

    class MockArgs:
        def __init__(self, enable_metrics=False, use_slime_router=False):
            self.sglang_enable_metrics = enable_metrics
            self.use_slime_router = use_slime_router

    class MockServer:
        def __init__(self, ip, port):
            self.router_ip = ip
            self.router_port = port

    class MockSelf:
        def __init__(self, args, server=None):
            self.args = args
            self.server = server

    # Metrics disabled → None
    obj = MockSelf(MockArgs(enable_metrics=False))
    assert method(obj) is None, "Should return None when metrics disabled"

    # Metrics enabled, slime router → None
    obj = MockSelf(MockArgs(enable_metrics=True, use_slime_router=True))
    assert method(obj) is None, "Should return None with slime router"

    # Metrics enabled, no server → None
    obj = MockSelf(MockArgs(enable_metrics=True), server=None)
    assert method(obj) is None, "Should return None with no server"

    # Metrics enabled, server with null IP → None
    obj = MockSelf(MockArgs(enable_metrics=True), server=MockServer(None, 8080))
    assert method(obj) is None, "Should return None with null router_ip"

    # Metrics enabled, server available → URL
    obj = MockSelf(MockArgs(enable_metrics=True), server=MockServer("10.0.0.1", 8080))
    assert method(obj) == "http://10.0.0.1:8080"

    # Different IP/port
    obj = MockSelf(MockArgs(enable_metrics=True), server=MockServer("192.168.1.1", 9090))
    assert method(obj) == "http://192.168.1.1:9090"
