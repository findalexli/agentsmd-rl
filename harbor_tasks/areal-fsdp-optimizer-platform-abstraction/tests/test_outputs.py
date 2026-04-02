"""
Task: areal-fsdp-optimizer-platform-abstraction
Repo: inclusionAI/AReaL @ cbe35f5a4b866596d996d5690085eda0577708f5
PR:   1108

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import textwrap
from pathlib import Path

REPO = "/repo"
FILE = f"{REPO}/areal/engine/fsdp_utils/optimizer.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_source():
    return Path(FILE).read_text()


def _parse_source():
    """Read and parse the optimizer module."""
    source = _read_source()
    tree = ast.parse(source)
    return source, tree


def _find_class_method(tree, source, class_name, method_name):
    """Extract dedented source of a method from a class."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    lines = source.splitlines(keepends=True)
                    return textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
    return None


def _find_class_node(tree, class_name):
    """Find a ClassDef node by name."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


class _Permissive:
    """Mock that absorbs any operation without raising."""

    def __init__(self, *a, **kw):
        pass

    def __getattr__(self, name):
        return _Permissive()

    def __call__(self, *a, **kw):
        return _Permissive()

    def __bool__(self):
        return True

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def __iter__(self):
        return iter([])

    def __getitem__(self, k):
        return _Permissive()

    def __setitem__(self, k, v):
        pass

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

    def __len__(self):
        return 0

    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __repr__(self):
        return "_Permissive()"

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return False

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __add__(self, other):
        return 0

    def __radd__(self, other):
        return 0

    def __sub__(self, other):
        return 0


class _MockSelf(_Permissive):
    """Mock self with realistic attributes so loops execute."""

    def __init__(self, num_groups=3):
        super().__init__()
        object.__setattr__(self, '_layer_param_groups', [None] * num_groups)
        object.__setattr__(self, 'prefetch_layers', 1)
        object.__setattr__(self, 'device', 'cpu')


def _build_namespace(tree, tracker):
    """Build a namespace where current_platform is bound to tracker."""
    ns = {"torch": _Permissive(), "__builtins__": __builtins__}
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.names:
            for alias in n.names:
                bound = alias.asname or alias.name
                if alias.name == "current_platform":
                    ns[bound] = tracker
                elif bound not in ns:
                    ns[bound] = _Permissive()
        elif isinstance(n, ast.Import):
            for alias in n.names:
                bound = alias.asname or alias.name
                if bound not in ns:
                    ns[bound] = _Permissive()
    if "current_platform" not in ns:
        ns["current_platform"] = tracker
    return ns


def _run_init_streams_with_tracker(num_groups=3):
    """Execute _init_streams_and_events with a tracking current_platform.

    Uses a mock self with num_groups layer param groups so Event() list
    comprehensions actually iterate.
    """
    source, tree = _parse_source()
    func_src = _find_class_method(tree, source, "PerLayerOptimWrapper",
                                  "_init_streams_and_events")
    assert func_src is not None, "_init_streams_and_events not found"

    calls = []

    class _Tracker:
        def __getattr__(self, name):
            calls.append(name)
            return _Permissive()

    tracker = _Tracker()
    ns = _build_namespace(tree, tracker)

    mock_self = _MockSelf(num_groups=num_groups)

    try:
        exec(func_src, ns)
        fn = ns["_init_streams_and_events"]
        fn(mock_self)
    except Exception:
        pass  # partial execution fine — check what was called

    return calls


def _run_step_with_tracker():
    """Execute step() with a tracking current_platform."""
    source, tree = _parse_source()
    func_src = _find_class_method(tree, source, "PerLayerOptimWrapper", "step")
    assert func_src is not None, "step not found"

    calls = []

    class _Tracker:
        def __getattr__(self, name):
            calls.append(name)
            return _Permissive()

    tracker = _Tracker()
    ns = _build_namespace(tree, tracker)

    mock_self = _MockSelf(num_groups=3)
    # step() accesses self._h2d_stream, self._d2h_stream, etc.
    # _Permissive handles these via __getattr__

    try:
        exec(func_src, ns)
        fn = ns["step"]
        fn(mock_self)
    except Exception:
        pass

    return calls


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """optimizer.py must parse as valid Python."""
    source = _read_source()
    ast.parse(source)  # raises SyntaxError if invalid


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_init_streams_uses_platform():
    """_init_streams_and_events must route Stream/Event through current_platform.

    AST-only because: torch.cuda.Stream/Event require CUDA device; we extract
    the method and exec with mocked current_platform to verify delegation.
    """
    # Test with 3 groups — must see Stream AND Event calls
    calls = _run_init_streams_with_tracker(num_groups=3)
    stream_calls = [c for c in calls if c == "Stream"]
    event_calls = [c for c in calls if c == "Event"]
    assert len(stream_calls) >= 2, (
        f"Expected >= 2 current_platform.Stream() calls, got {len(stream_calls)}: {calls}"
    )
    assert len(event_calls) >= 3, (
        f"Expected >= 3 current_platform.Event() calls (for {3} groups), got {len(event_calls)}: {calls}"
    )

    # Verify with different group count to confirm it's not hardcoded
    calls5 = _run_init_streams_with_tracker(num_groups=5)
    event_calls5 = [c for c in calls5 if c == "Event"]
    assert len(event_calls5) >= 5, (
        f"Expected >= 5 Event calls for 5 groups, got {len(event_calls5)}"
    )


# [pr_diff] fail_to_pass
def test_step_uses_platform():
    """step() must route stream/cache ops through current_platform.

    AST-only because: step() depends on CUDA runtime. We extract and exec with
    mocks, checking that current_platform.current_stream/stream/empty_cache are called.
    """
    calls = _run_step_with_tracker()
    assert len(calls) > 0, "current_platform not called in step()"
    # Must see at least current_stream and empty_cache
    has_current_stream = "current_stream" in calls
    has_empty_cache = "empty_cache" in calls
    assert has_current_stream, (
        f"Expected current_platform.current_stream() in step(), got: {calls}"
    )
    assert has_empty_cache, (
        f"Expected current_platform.empty_cache() in step(), got: {calls}"
    )


# [pr_diff] fail_to_pass
def test_current_platform_import():
    """Module must import current_platform from areal.infra.platforms."""
    _, tree = _parse_source()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and "areal.infra.platforms" in node.module:
                for alias in node.names:
                    if alias.name == "current_platform":
                        return
    raise AssertionError("current_platform not imported from areal.infra.platforms")


# [pr_diff] fail_to_pass
def test_no_direct_cuda_calls():
    """PerLayerOptimWrapper must not use torch.cuda.{Stream,Event,current_stream,stream,empty_cache}.

    AST-only because: need to distinguish torch.cuda.X attribute chains from
    other uses of the same names; text search would false-positive on comments/strings.
    """
    source, tree = _parse_source()
    forbidden = {"Stream", "Event", "current_stream", "stream", "empty_cache"}

    class_node = _find_class_node(tree, "PerLayerOptimWrapper")
    assert class_node is not None, "PerLayerOptimWrapper class not found"

    class_source = ast.get_source_segment(source, class_node)
    assert class_source is not None, "Could not extract class source"
    class_tree = ast.parse(class_source)

    # Collect annotation node ids to skip (type annotations may reference torch.cuda types)
    ann_ids: set[int] = set()
    for child in ast.walk(class_tree):
        if isinstance(child, ast.arg) and child.annotation:
            for n in ast.walk(child.annotation):
                ann_ids.add(id(n))
        if isinstance(child, ast.FunctionDef) and child.returns:
            for n in ast.walk(child.returns):
                ann_ids.add(id(n))
        if isinstance(child, ast.AnnAssign) and child.annotation:
            for n in ast.walk(child.annotation):
                ann_ids.add(id(n))

    for n in ast.walk(class_tree):
        if isinstance(n, ast.Attribute) and n.attr in forbidden:
            if id(n) in ann_ids:
                continue
            if isinstance(n.value, ast.Attribute) and n.value.attr == "cuda":
                if isinstance(n.value.value, ast.Name) and n.value.value.id == "torch":
                    raise AssertionError(f"Found forbidden: torch.cuda.{n.attr}")


# [pr_diff] fail_to_pass
def test_todo_comments_removed():
    """TODO comments about current_platform abstraction must be resolved."""
    source = _read_source()
    for i, line in enumerate(source.splitlines(), 1):
        low = line.lower()
        if "todo" in low and "current_platform" in low:
            raise AssertionError(f"TODO comment at line {i}: {line.strip()}")


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """_init_streams_and_events and step must have real logic (not stubbed)."""
    _, tree = _parse_source()
    class_node = _find_class_node(tree, "PerLayerOptimWrapper")
    assert class_node is not None, "PerLayerOptimWrapper class not found"

    for method_name in ("_init_streams_and_events", "step"):
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == method_name:
                meaningful = [
                    s for s in item.body
                    if not isinstance(s, ast.Pass)
                    and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                    and not isinstance(s, ast.Raise)
                ]
                assert len(meaningful) >= 3, (
                    f"{method_name} has only {len(meaningful)} meaningful statements (stubbed)"
                )
                break
        else:
            raise AssertionError(f"{method_name} not found in PerLayerOptimWrapper")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:30 @ cbe35f5
def test_no_wildcard_imports():
    """No wildcard imports in optimizer.py (AGENTS.md hard rule)."""
    source = _read_source()
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("from ") and "import *" in stripped:
            raise AssertionError(f"Wildcard import at line {i}: {stripped}")


# [agent_config] pass_to_pass — AGENTS.md:90-92 @ cbe35f5
def test_no_print_statements():
    """No bare print() calls in optimizer.py — must use areal.utils.logging.

    AST-only because: need to distinguish print() calls from string mentions.
    """
    _, tree = _parse_source()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                raise AssertionError(
                    f"Bare print() call at line {node.lineno} — use areal.utils.logging"
                )


# [agent_config] pass_to_pass — AGENTS.md:96 @ cbe35f5
def test_no_gpu_cpu_sync():
    """No .item() or .tolist() GPU-CPU sync in PerLayerOptimWrapper hot paths.

    AST-only because: checking for method call patterns across the class body.
    """
    _, tree = _parse_source()
    class_node = _find_class_node(tree, "PerLayerOptimWrapper")
    assert class_node is not None, "PerLayerOptimWrapper class not found"

    forbidden_attrs = {"item", "tolist"}
    for child in ast.walk(class_node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
            if child.func.attr in forbidden_attrs:
                raise AssertionError(
                    f"GPU-CPU sync .{child.func.attr}() at line {child.lineno}"
                )


# [agent_config] pass_to_pass — AGENTS.md:100-101 @ cbe35f5
def test_no_heavy_toplevel_imports():
    """Heavy optional deps must be imported inside functions, not at module level.

    AGENTS.md: 'heavy optional deps inside functions'. Checks that the modified
    file doesn't add new top-level imports of heavy packages beyond what the
    base commit already had (torch is allowed as it's a core dep).
    """
    _, tree = _parse_source()
    # These are heavy optional deps that should only be imported inside functions
    heavy_packages = {"transformers", "datasets", "accelerate", "deepspeed", "triton"}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                pkg = alias.name.split(".")[0]
                if pkg in heavy_packages:
                    raise AssertionError(
                        f"Heavy dep '{alias.name}' imported at module level (line {node.lineno})"
                    )
        elif isinstance(node, ast.ImportFrom) and node.module:
            pkg = node.module.split(".")[0]
            if pkg in heavy_packages:
                raise AssertionError(
                    f"Heavy dep '{node.module}' imported at module level (line {node.lineno})"
                )
