"""
Task: sglang-detokenizer-unbound-fix
Repo: sgl-project/sglang @ 17f43d15187be710828a1ff6a4843fdddb0b1eb7
PR:   21471

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import signal
import textwrap
import types

TARGET = "/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py"


# ---------------------------------------------------------------------------
# Helpers — extract and exec the target function with mocks
# ---------------------------------------------------------------------------

def _extract_function_source(name="run_detokenizer_process"):
    """Parse the target file and return the dedented source of the named function."""
    with open(TARGET) as f:
        source = f.read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            lines = source.splitlines(keepends=True)
            return textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
    raise AssertionError(f"Function {name!r} not found in {TARGET}")


class _FailingManager:
    """Constructor always raises — simulates a broken DetokenizerManager."""
    def __init__(self, *args, **kwargs):
        raise RuntimeError("simulated constructor failure")
    def maybe_clear_socket_mapping(self):
        pass


class _MockArgs:
    tokenizer_worker_num = 1


def _make_exec_globals(*, logger=None, parent_signal_log=None):
    """Build the namespace for exec'ing run_detokenizer_process."""
    signal_log = parent_signal_log if parent_signal_log is not None else []

    psutil_mock = types.ModuleType("psutil")

    class MockProcess:
        def __init__(self):
            pass
        def parent(self):
            ns = types.SimpleNamespace()
            ns.send_signal = lambda sig: signal_log.append(sig)
            return ns
        def send_signal(self, sig):
            signal_log.append(sig)

    psutil_mock.Process = MockProcess

    if logger is None:
        logger = types.SimpleNamespace(
            error=lambda *a, **kw: None,
            info=lambda *a, **kw: None,
            warning=lambda *a, **kw: None,
            debug=lambda *a, **kw: None,
        )

    return {
        "DetokenizerManager": _FailingManager,
        "ServerArgs": _MockArgs,
        "PortArgs": _MockArgs,
        "kill_itself_when_parent_died": lambda: None,
        "setproctitle": types.SimpleNamespace(setproctitle=lambda t: None),
        "psutil": psutil_mock,
        "logger": logger,
        "configure_logger": lambda *a, **kw: None,
        "get_exception_traceback": lambda: "mock traceback",
        "signal": signal,
        "__builtins__": __builtins__,
    }


def _exec_function(exec_globals):
    """Compile and exec the function, then call it with the failing manager."""
    func_src = _extract_function_source()
    exec(func_src, exec_globals)
    try:
        exec_globals["run_detokenizer_process"](_MockArgs(), _MockArgs(), _FailingManager)
    except (SystemExit, Exception):
        pass


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse as valid Python."""
    with open(TARGET) as f:
        ast.parse(f.read())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_unbound_error_on_constructor_failure():
    """When DetokenizerManager() raises, no UnboundLocalError should propagate."""
    func_src = _extract_function_source()
    g = _make_exec_globals()
    exec(func_src, g)

    raised_unbound = False
    try:
        g["run_detokenizer_process"](_MockArgs(), _MockArgs(), _FailingManager)
    except (UnboundLocalError, NameError) as e:
        if isinstance(e, UnboundLocalError) or "manager" in str(e):
            raised_unbound = True
    except (SystemExit, Exception):
        pass

    assert not raised_unbound, "UnboundLocalError raised when constructor fails"


# [pr_diff] fail_to_pass
def test_sigquit_sent_on_constructor_failure():
    """SIGQUIT must be sent to the parent process even when the constructor fails."""
    signal_log = []
    g = _make_exec_globals(parent_signal_log=signal_log)
    _exec_function(g)
    assert signal.SIGQUIT in signal_log, (
        f"SIGQUIT not sent to parent. Signals sent: {signal_log}"
    )


# [pr_diff] fail_to_pass
def test_no_unbound_error_with_type_error():
    """Same fix works when the constructor raises TypeError (varied exception type)."""
    class TypeErrorManager:
        def __init__(self, *args, **kwargs):
            raise TypeError("bad argument type")
        def maybe_clear_socket_mapping(self):
            pass

    signal_log = []
    g = _make_exec_globals(parent_signal_log=signal_log)
    # Override the manager class to use TypeError variant
    g["DetokenizerManager"] = TypeErrorManager
    func_src = _extract_function_source()
    exec(func_src, g)

    raised_unbound = False
    try:
        g["run_detokenizer_process"](_MockArgs(), _MockArgs(), TypeErrorManager)
    except (UnboundLocalError, NameError) as e:
        if isinstance(e, UnboundLocalError) or "manager" in str(e):
            raised_unbound = True
    except (SystemExit, Exception):
        pass

    assert not raised_unbound, "UnboundLocalError raised with TypeError constructor"
    assert signal.SIGQUIT in signal_log, "SIGQUIT not sent with TypeError constructor"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_cleanup_called_when_manager_succeeds():
    """When manager IS created but event_loop raises, cleanup must still be called."""
    cleanup_log = []

    class SuccessManager:
        def __init__(self, *args, **kwargs):
            pass  # Constructor succeeds
        def event_loop(self):
            raise RuntimeError("event loop crash")
        def event_loop_overlap(self):
            raise RuntimeError("event loop crash")
        def maybe_clear_socket_mapping(self):
            cleanup_log.append("cleared")

    signal_log = []
    g = _make_exec_globals(parent_signal_log=signal_log)
    g["DetokenizerManager"] = SuccessManager
    func_src = _extract_function_source()
    exec(func_src, g)

    try:
        g["run_detokenizer_process"](_MockArgs(), _MockArgs(), SuccessManager)
    except (SystemExit, Exception):
        pass

    assert len(cleanup_log) > 0, "maybe_clear_socket_mapping not called when manager was created"
    assert signal.SIGQUIT in signal_log, "SIGQUIT not sent when event_loop fails"


# [static] pass_to_pass
def test_error_logged_on_constructor_failure():
    """An error must be logged when the constructor fails."""
    error_messages = []
    logger = types.SimpleNamespace(
        error=lambda *a, **kw: error_messages.append(a),
        info=lambda *a, **kw: None,
        warning=lambda *a, **kw: None,
        debug=lambda *a, **kw: None,
    )
    g = _make_exec_globals(logger=logger)
    _exec_function(g)
    assert len(error_messages) > 0, "No error was logged when constructor failed"
    msg = str(error_messages[0])
    assert "DetokenizerManager" in msg or "traceback" in msg.lower(), (
        f"Error message doesn't reference the failure: {msg}"
    )

# [static] pass_to_pass
def test_function_signature_intact():
    """run_detokenizer_process must still exist with expected parameters."""
    with open(TARGET) as f:
        source = f.read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_detokenizer_process":
            param_names = [a.arg for a in node.args.args]
            assert "server_args" in param_names, "Missing server_args parameter"
            assert "port_args" in param_names, "Missing port_args parameter"
            return
    raise AssertionError("run_detokenizer_process function not found")


# [static] pass_to_pass
def test_not_stub():
    """run_detokenizer_process must have real logic, not just pass/return."""
    with open(TARGET) as f:
        source = f.read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_detokenizer_process":
            # Must have a try/except and multiple statements
            body_types = {type(s).__name__ for s in node.body}
            assert "Try" in body_types, "Function body missing try/except block"
            assert len(node.body) >= 3, (
                f"Function body too short ({len(node.body)} stmts) — likely a stub"
            )
            return
    raise AssertionError("run_detokenizer_process function not found")
