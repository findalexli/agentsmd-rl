"""
Task: areal-socket-bind-failure-cleanup
Repo: inclusionAI/AReaL @ 7cad4dac2d1f230891f201dbbfa91403e621cec1
PR:   1032

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import sys
import textwrap
import types
import socket as socket_mod
from pathlib import Path

REPO = "/workspace/AReaL"

MODIFIED_FILES = [
    "areal/utils/network.py",
    "areal/trainer/rl_trainer.py",
    "areal/trainer/sft_trainer.py",
]


def _find_function(tree, name):
    """Find a top-level or class-level FunctionDef by name."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == name:
                    return item
    return None


def _extract_function(source, node):
    """Extract and dedent function source from AST node."""
    lines = source.splitlines(keepends=True)
    return textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for f in MODIFIED_FILES:
        src = Path(f"{REPO}/{f}").read_text()
        compile(src, f, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def _make_fake_socket_module(tcp_bind_fails=True, udp_bind_fails=True):
    """Build a fake socket module that tracks close() calls and counts."""
    state = {"tcp_closed": 0, "udp_closed": 0}

    class FakeSocket:
        def __init__(self, family=socket_mod.AF_INET, type_=socket_mod.SOCK_STREAM, *a, **kw):
            self._type = type_

        def bind(self, addr):
            if self._type == socket_mod.SOCK_STREAM and tcp_bind_fails:
                raise OSError("TCP bind refused")
            if self._type == socket_mod.SOCK_DGRAM and udp_bind_fails:
                raise OSError("UDP bind refused")

        def close(self):
            if self._type == socket_mod.SOCK_STREAM:
                state["tcp_closed"] += 1
            else:
                state["udp_closed"] += 1

        def __enter__(self):
            return self

        def __exit__(self, *a):
            self.close()

    fake_mod = types.SimpleNamespace(
        socket=FakeSocket,
        AF_INET=socket_mod.AF_INET,
        SOCK_STREAM=socket_mod.SOCK_STREAM,
        SOCK_DGRAM=socket_mod.SOCK_DGRAM,
    )
    return fake_mod, state


def _get_is_port_free_ns(fake_mod):
    """Extract is_port_free from source and exec with fake socket module."""
    # AST-only because: network.py imports torch.distributed and other heavy deps
    src = Path(f"{REPO}/areal/utils/network.py").read_text()
    tree = ast.parse(src)
    func = _find_function(tree, "is_port_free")
    assert func is not None, "is_port_free() not found in network.py"
    func_src = _extract_function(src, func)
    ns = {"__builtins__": __builtins__, "socket": fake_mod}
    exec(func_src, ns)
    return ns


# [pr_diff] fail_to_pass
def test_tcp_socket_closed_on_bind_failure():
    """TCP socket.close() is called even when bind() raises OSError."""
    for port in [9999, 8080, 12345]:
        fake_mod, state = _make_fake_socket_module(tcp_bind_fails=True, udp_bind_fails=True)
        ns = _get_is_port_free_ns(fake_mod)

        result = ns["is_port_free"](port)
        assert result is False, f"is_port_free({port}) should return False when TCP bind fails"
        assert state["tcp_closed"] >= 1, f"TCP socket.close() was NOT called after bind failure (port {port})"


# [pr_diff] fail_to_pass
def test_udp_socket_closed_on_bind_failure():
    """UDP socket.close() is called even when bind() raises OSError."""
    for port in [9999, 5000, 44100]:
        fake_mod, state = _make_fake_socket_module(tcp_bind_fails=False, udp_bind_fails=True)
        ns = _get_is_port_free_ns(fake_mod)

        result = ns["is_port_free"](port)
        assert result is False, f"is_port_free({port}) should return False when UDP bind fails"
        assert state["udp_closed"] >= 1, f"UDP socket.close() was NOT called after bind failure (port {port})"


# [pr_diff] fail_to_pass
def test_both_sockets_closed_on_success():
    """Both TCP and UDP sockets are closed even when both binds succeed."""
    for port in [9999, 7777, 3000]:
        fake_mod, state = _make_fake_socket_module(tcp_bind_fails=False, udp_bind_fails=False)
        ns = _get_is_port_free_ns(fake_mod)

        result = ns["is_port_free"](port)
        assert result is True, f"is_port_free({port}) should return True when both binds succeed"
        assert state["tcp_closed"] >= 1, f"TCP socket.close() was NOT called on success (port {port})"
        assert state["udp_closed"] >= 1, f"UDP socket.close() was NOT called on success (port {port})"


def _build_trainer_class(filepath):
    """Extract __exit__ from source and build a testable Trainer class."""
    # AST-only because: trainer modules import torch, FSDP, distributed
    src = Path(filepath).read_text()
    tree = ast.parse(src)
    exit_func = _find_function(tree, "__exit__")
    assert exit_func is not None, f"__exit__ not found in {filepath}"

    func_src = _extract_function(src, exit_func)
    test_class_src = (
        "class _TestTrainer:\n"
        "    def __init__(self): self.closed = False\n"
        "    def close(self): self.closed = True\n"
        "    def __enter__(self): return self\n"
    ) + textwrap.indent(func_src, "    ")

    class MockLogger:
        def error(self, *a, **kw): pass
        def warning(self, *a, **kw): pass
        def info(self, *a, **kw): pass

    ns = {"__builtins__": __builtins__, "logger": MockLogger()}
    exec(test_class_src, ns)
    return ns["_TestTrainer"]


def _test_exit_does_not_reraise(filepath, exc_class, exc_msg):
    """Test that __exit__ returns falsy instead of re-raising the exception.

    On base commit: __exit__ does 'raise exc_value' → raises → FAIL
    On fix: __exit__ returns False → passes
    """
    Trainer = _build_trainer_class(filepath)

    exc = exc_class(exc_msg)
    exc.__traceback__ = None  # simulate a clean exception
    trainer = Trainer()
    try:
        result = trainer.__exit__(exc_class, exc, None)
    except BaseException as e:
        raise AssertionError(
            f"__exit__ should not re-raise the exception — return False instead. "
            f"Got: {type(e).__name__}: {e}"
        )
    assert not result, (
        f"__exit__ should return falsy to let Python re-raise with original traceback, "
        f"got {result!r}"
    )


# [pr_diff] fail_to_pass
def test_rl_exit_does_not_reraise():
    """RLTrainer.__exit__ returns falsy instead of re-raising with 'raise exc_value'."""
    rl_path = f"{REPO}/areal/trainer/rl_trainer.py"
    for exc_cls, msg in [
        (ValueError, "bad learning rate"),
        (RuntimeError, "CUDA OOM"),
        (TypeError, "wrong argument type"),
    ]:
        _test_exit_does_not_reraise(rl_path, exc_cls, msg)


# [pr_diff] fail_to_pass
def test_sft_exit_does_not_reraise():
    """SFTTrainer.__exit__ returns falsy instead of re-raising with 'raise exc_value'."""
    sft_path = f"{REPO}/areal/trainer/sft_trainer.py"
    for exc_cls, msg in [
        (ValueError, "invalid batch size"),
        (RuntimeError, "distributed error"),
        (TypeError, "unexpected kwarg"),
    ]:
        _test_exit_does_not_reraise(sft_path, exc_cls, msg)


# [pr_diff] pass_to_pass
def test_rl_exit_calls_close():
    """RLTrainer.__exit__ calls self.close() for cleanup."""
    Trainer = _build_trainer_class(f"{REPO}/areal/trainer/rl_trainer.py")
    trainer = Trainer()
    trainer.__exit__(None, None, None)
    assert trainer.closed, "RLTrainer.__exit__ must call self.close()"


# [pr_diff] pass_to_pass
def test_sft_exit_calls_close():
    """SFTTrainer.__exit__ calls self.close() for cleanup."""
    Trainer = _build_trainer_class(f"{REPO}/areal/trainer/sft_trainer.py")
    trainer = Trainer()
    trainer.__exit__(None, None, None)
    assert trainer.closed, "SFTTrainer.__exit__ must call self.close()"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """Modified functions have real logic, not just pass/return."""
    targets = [
        (f"{REPO}/areal/utils/network.py", "is_port_free"),
        (f"{REPO}/areal/trainer/rl_trainer.py", "__exit__"),
        (f"{REPO}/areal/trainer/sft_trainer.py", "__exit__"),
    ]
    for path, func_name in targets:
        src = Path(path).read_text()
        tree = ast.parse(src)
        func = _find_function(tree, func_name)
        assert func is not None, f"{func_name} not found in {path}"
        stmts = [
            s
            for s in func.body
            if not isinstance(s, ast.Pass)
            and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))
        ]
        assert len(stmts) >= 3, f"{path}:{func_name} has only {len(stmts)} statements (likely stub)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md / CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:30 @ 7cad4dac
def test_no_wildcard_imports():
    """No wildcard imports (from x import *) in modified files."""
    for f in MODIFIED_FILES:
        src = Path(f"{REPO}/{f}").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and any(
                alias.name == "*" for alias in node.names
            ):
                raise AssertionError(f"Wildcard import found in {f}:{node.lineno}")


# [agent_config] pass_to_pass — AGENTS.md:89-91 @ 7cad4dac
def test_no_print_logging():
    """No bare print() calls for logging in modified files — use areal.utils.logging."""
    for f in MODIFIED_FILES:
        src = Path(f"{REPO}/{f}").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "print"
            ):
                raise AssertionError(
                    f"Bare print() call found in {f}:{node.lineno} — "
                    "use areal.utils.logging.getLogger() instead"
                )
