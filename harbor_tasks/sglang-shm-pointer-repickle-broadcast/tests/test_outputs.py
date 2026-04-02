"""
Task: sglang-shm-pointer-repickle-broadcast
Repo: sgl-project/sglang @ fc9de157f9ea51e93dc58b8abacd688b5d5474b7
PR:   #21465

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import pickle
import textwrap
from multiprocessing import shared_memory
from pathlib import Path

import numpy as np
import pytest
import torch

REPO = "/workspace/sglang"
MM_UTILS = f"{REPO}/python/sglang/srt/managers/mm_utils.py"
SCHEDULER = f"{REPO}/python/sglang/srt/managers/scheduler.py"


# ---------------------------------------------------------------------------
# AST extraction — mm_utils.py can't be imported (heavy sglang runtime deps)
# ---------------------------------------------------------------------------


def _load_shm_code():
    """Extract ShmPointerMMData + wrap/unwrap via AST, exec with mocks.

    AST-only because: mm_utils.py imports sglang.srt.environ, schedule_batch,
    layers.multimodal, mem_cache, model_executor, etc. — none available without
    full sglang runtime.
    """
    source = Path(MM_UTILS).read_text()
    tree = ast.parse(source)

    target_names = {"ShmPointerMMData", "wrap_shm_features", "unwrap_shm_features"}
    parts = []
    for node in ast.iter_child_nodes(tree):
        name = getattr(node, "name", None)
        if name in target_names:
            parts.append((node.lineno, node.end_lineno))

    parts.sort()
    lines = source.splitlines(keepends=True)
    code = "\n".join("".join(lines[s - 1 : e]) for s, e in parts)

    class MockServerArgs:
        skip_tokenizer_init = False

    ns = {
        "__builtins__": __builtins__,
        "torch": torch,
        "np": np,
        "numpy": np,
        "shared_memory": shared_memory,
        "get_global_server_args": lambda: MockServerArgs(),
        "_get_is_default_transport": lambda: False,
    }
    exec(compile(code, MM_UTILS, "exec"), ns)
    return ns


_ns = _load_shm_code()
ShmPointerMMData = _ns["ShmPointerMMData"]
wrap_shm_features = _ns["wrap_shm_features"]
unwrap_shm_features = _ns["unwrap_shm_features"]

# Make ShmPointerMMData picklable — pickle needs to find it via __module__
ShmPointerMMData.__module__ = __name__
ShmPointerMMData.__qualname__ = "ShmPointerMMData"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class MockMMItem:
    def __init__(self, tensor):
        self.feature = tensor


class MockMMInputs:
    def __init__(self, items):
        self._items = items

    def get(self, key, default=None):
        return self._items if key == "mm_items" else default


class MockRequest:
    def __init__(self, tensor):
        self.mm_inputs = MockMMInputs([MockMMItem(tensor)])


class MockBatchRequest:
    def __init__(self, requests):
        self.batch = requests


def _get_tensor(obj):
    """Extract tensor from ShmPointerMMData via any available method."""
    for method in ("materialize", "to_tensor", "get_tensor", "resolve"):
        fn = getattr(obj, method, None)
        if fn is not None and callable(fn):
            return fn()
    if hasattr(obj, "tensor"):
        return obj.tensor.clone() if hasattr(obj.tensor, "clone") else obj.tensor
    raise RuntimeError("Cannot retrieve tensor from ShmPointerMMData")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile

    for path in [MM_UTILS, SCHEDULER]:
        py_compile.compile(path, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_repickle_stable_shm_name():
    """Multiple pickle cycles must reuse the same shm segment name."""
    for shape in [(4, 8), (1,), (2, 3, 4)]:
        t = torch.randn(*shape)
        obj = ShmPointerMMData(t)
        obj2 = pickle.loads(pickle.dumps(obj))
        name1 = getattr(obj2, "shm_name", None)
        obj3 = pickle.loads(pickle.dumps(obj2))
        name2 = getattr(obj3, "shm_name", None)
        assert name1 is not None, "No shm_name after first unpickle"
        assert name1 == name2, f"shm_name changed across pickles: {name1} -> {name2}"


# [pr_diff] fail_to_pass
def test_repickle_no_new_shm():
    """__getstate__ must not allocate new shm segments on re-pickle."""
    t = torch.randn(4, 8)
    obj = ShmPointerMMData(t)
    obj2 = pickle.loads(pickle.dumps(obj))

    created_shms = []
    _orig_init = shared_memory.SharedMemory.__init__

    def _tracking_init(self, *args, **kwargs):
        _orig_init(self, *args, **kwargs)
        if kwargs.get("create", False) or (len(args) > 1 and args[1]):
            created_shms.append(self.name)

    shared_memory.SharedMemory.__init__ = _tracking_init
    try:
        pickle.dumps(obj2)
    finally:
        shared_memory.SharedMemory.__init__ = _orig_init

    assert len(created_shms) == 0, (
        f"{len(created_shms)} new shm segment(s) created during re-pickle: {created_shms}"
    )


# [pr_diff] fail_to_pass
def test_batch_unwrap():
    """unwrap_shm_features must recurse into batch sub-requests."""
    t1 = torch.randn(2, 4)
    t2 = torch.randn(3, 5)
    req1 = MockRequest(ShmPointerMMData(t1))
    req2 = MockRequest(ShmPointerMMData(t2))
    batch = MockBatchRequest([req1, req2])

    batch2 = pickle.loads(pickle.dumps(batch))
    unwrap_shm_features(batch2)

    originals = [t1, t2]
    for i, sub_req in enumerate(batch2.batch):
        items = sub_req.mm_inputs.get("mm_items", [])
        feat = items[0].feature
        assert isinstance(feat, torch.Tensor), (
            f"batch[{i}].feature is {type(feat).__name__}, expected Tensor"
        )
        assert torch.allclose(feat, originals[i], atol=1e-6), (
            f"batch[{i}] data mismatch"
        )


# ---------------------------------------------------------------------------
# Structural — scheduler.py can't be imported (full sglang runtime)
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
# AST-only because: scheduler.py requires full sglang runtime (ZMQ, CUDA, distributed)
def test_unwrap_after_broadcast():
    """unwrap_shm_features must be called near end of recv_requests, after broadcasts."""
    source = Path(SCHEDULER).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "recv_requests":
            unwrap_lines = []
            return_lines = []
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    func = child.func
                    name = getattr(func, "id", None) or getattr(func, "attr", None)
                    if name == "unwrap_shm_features":
                        unwrap_lines.append(child.lineno)
                if isinstance(child, ast.Return):
                    return_lines.append(child.lineno)

            assert unwrap_lines, "No unwrap_shm_features call found in recv_requests"
            assert return_lines, "No return statement in recv_requests"
            last_unwrap = max(unwrap_lines)
            last_return = max(return_lines)
            assert last_return >= last_unwrap, (
                f"unwrap at line {last_unwrap} is after last return at {last_return}"
            )
            assert last_return - last_unwrap <= 15, (
                f"unwrap at {last_unwrap} too far from return at {last_return}"
            )
            return

    raise AssertionError("recv_requests function not found in scheduler.py")


# [pr_diff] fail_to_pass
# AST-only because: scheduler.py requires full sglang runtime (ZMQ, CUDA, distributed)
def test_unwrap_not_in_recv_loop():
    """unwrap_shm_features must NOT be called inside the ZMQ recv try/except block."""
    source = Path(SCHEDULER).read_text()
    tree = ast.parse(source)

    def _has_unwrap_in_zmq_try(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Try):
                catches_zmq = any(
                    "ZMQError"
                    in (getattr(h.type, "attr", "") or getattr(h.type, "id", ""))
                    for h in child.handlers
                    if h.type
                )
                if catches_zmq:
                    for inner in ast.walk(child):
                        if isinstance(inner, ast.Call):
                            name = getattr(inner.func, "id", None) or getattr(
                                inner.func, "attr", None
                            )
                            if name == "unwrap_shm_features":
                                return True
            if _has_unwrap_in_zmq_try(child):
                return True
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "recv_requests":
            assert not _has_unwrap_in_zmq_try(node), (
                "unwrap_shm_features called inside ZMQ recv try-block"
            )
            return

    raise AssertionError("recv_requests function not found")


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_materialize_correct_data():
    """Tensor data survives double pickle (ZMQ + broadcast) and retrieval."""
    test_tensors = [
        torch.randn(4, 8),
        torch.randint(0, 100, (10,)),
        torch.randn(2, 3, 4, dtype=torch.float64),
    ]
    for t in test_tensors:
        obj = ShmPointerMMData(t)
        obj2 = pickle.loads(pickle.dumps(obj))
        obj3 = pickle.loads(pickle.dumps(obj2))
        result = _get_tensor(obj3)
        assert result.shape == t.shape, f"shape {result.shape} != {t.shape}"
        assert result.dtype == t.dtype, f"dtype {result.dtype} != {t.dtype}"
        assert torch.allclose(result, t, atol=1e-6), "Data mismatch after double pickle"


# [pr_diff] pass_to_pass
def test_materialize_cleans_shm():
    """After materialization, the shm segment should be unlinked."""
    import time

    t = torch.randn(4, 8)
    obj = ShmPointerMMData(t)
    obj2 = pickle.loads(pickle.dumps(obj))
    shm_name = obj2.shm_name

    # Retrieve tensor (triggers cleanup in correct implementation)
    _get_tensor(obj2)
    # Also try manual cleanup for implementations that use _shm_handle
    for attr in ("_shm_handle", "shm", "_shm"):
        handle = getattr(obj2, attr, None)
        if handle is not None:
            try:
                handle.close()
            except Exception:
                pass
            try:
                handle.unlink()
            except Exception:
                pass

    time.sleep(0.05)
    try:
        check = shared_memory.SharedMemory(name=shm_name, create=False)
        check.close()
        raise AssertionError("shm segment still accessible after materialization")
    except FileNotFoundError:
        pass  # Expected — segment was cleaned up


# [pr_diff] pass_to_pass
def test_single_pickle_roundtrip():
    """Basic single pickle/unpickle must produce correct tensor across dtypes."""
    test_cases = [
        torch.randn(4, 8),
        torch.randint(0, 100, (10,)),
        torch.randn(2, 3, 4, dtype=torch.float64),
    ]
    for t in test_cases:
        obj2 = pickle.loads(pickle.dumps(ShmPointerMMData(t)))
        result = _get_tensor(obj2)
        assert result.shape == t.shape
        assert result.dtype == t.dtype
        assert torch.allclose(result, t, atol=1e-6)


# [pr_diff] pass_to_pass
def test_wrap_unwrap_identity():
    """wrap_shm_features then unwrap_shm_features returns original tensor."""
    for shape in [(3, 6), (1,), (4, 2, 3)]:
        t = torch.randn(*shape)
        req = MockRequest(t)
        wrap_shm_features(req)

        item = req.mm_inputs.get("mm_items")[0]
        assert isinstance(item.feature, ShmPointerMMData), (
            f"After wrap, expected ShmPointerMMData, got {type(item.feature).__name__}"
        )

        req2 = pickle.loads(pickle.dumps(req))
        unwrap_shm_features(req2)
        result = req2.mm_inputs.get("mm_items")[0].feature
        assert isinstance(result, torch.Tensor), (
            f"After unwrap, expected Tensor, got {type(result).__name__}"
        )
        assert torch.allclose(result, t, atol=1e-6), "Data mismatch after wrap+unwrap"
