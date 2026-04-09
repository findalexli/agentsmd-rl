"""
Task: sglang-detokenizer-unbound-fix
Repo: sgl-project/sglang @ 17f43d15187be710828a1ff6a4843fdddb0b1eb7
PR:   21471

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

P2P tests enriched from repo CI/CD:
- ruff, black, isort (existing)
- codespell (from pre-commit)
- AST check (from pre-commit check-ast)
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"
TARGET = f"{REPO}/python/sglang/srt/managers/detokenizer_manager.py"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python script in the repo directory."""
    script = Path(REPO) / "_eval_test.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# Shared harness injected into every subprocess script.
# Sets up AST extraction + lightweight mocks so the real function can run.
_HARNESS = '''
import ast, textwrap, types, signal, sys

TARGET = "/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py"

def extract_function(name="run_detokenizer_process"):
    with open(TARGET) as f:
        source = f.read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            lines = source.splitlines(keepends=True)
            return textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
    raise AssertionError(f"Function {name!r} not found")

class FailingManager:
    """Constructor always raises — simulates a broken DetokenizerManager."""
    def __init__(self, *a, **kw):
        raise RuntimeError("simulated constructor failure")
    def maybe_clear_socket_mapping(self):
        pass

class MockArgs:
    tokenizer_worker_num = 1

def make_globals(signal_log=None, manager_cls=FailingManager):
    sig_log = signal_log if signal_log is not None else []
    psutil_mock = types.ModuleType("psutil")
    class MockProcess:
        def parent(self):
            return types.SimpleNamespace(send_signal=lambda sig: sig_log.append(sig))
    psutil_mock.Process = MockProcess
    return {
        "DetokenizerManager": manager_cls,
        "ServerArgs": MockArgs,
        "PortArgs": MockArgs,
        "kill_itself_when_parent_died": lambda: None,
        "setproctitle": types.SimpleNamespace(setproctitle=lambda t: None),
        "psutil": psutil_mock,
        "logger": types.SimpleNamespace(
            error=lambda *a,**kw:None, info=lambda *a,**kw:None,
            warning=lambda *a,**kw:None, debug=lambda *a,**kw:None),
        "configure_logger": lambda *a, **kw: None,
        "get_exception_traceback": lambda: "mock traceback",
        "signal": signal,
        "__builtins__": __builtins__,
    }
'''


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Target file must parse as valid Python."""
    with open(TARGET) as f:
        ast.parse(f.read())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_no_unbound_error_on_constructor_failure():
    """When DetokenizerManager() raises, no UnboundLocalError should propagate."""
    r = _run_py(_HARNESS + '''
func_src = extract_function()
g = make_globals()
exec(func_src, g)
try:
    g["run_detokenizer_process"](MockArgs(), MockArgs(), FailingManager)
except UnboundLocalError as e:
    print(f"FAIL: UnboundLocalError: {e}")
    sys.exit(1)
except Exception:
    pass
print("PASS")
''')
    assert r.returncode == 0, f"UnboundLocalError raised:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


def test_sigquit_sent_on_constructor_failure():
    """SIGQUIT must be sent to the parent process even when the constructor fails."""
    r = _run_py(_HARNESS + '''
signal_log = []
func_src = extract_function()
g = make_globals(signal_log=signal_log)
exec(func_src, g)
try:
    g["run_detokenizer_process"](MockArgs(), MockArgs(), FailingManager)
except Exception:
    pass
if signal.SIGQUIT in signal_log:
    print("PASS")
else:
    print(f"FAIL: SIGQUIT not in signal_log: {signal_log}")
    sys.exit(1)
''')
    assert r.returncode == 0, f"SIGQUIT not sent:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


def test_no_unbound_error_with_type_error():
    """Same fix works when the constructor raises TypeError."""
    r = _run_py(_HARNESS + '''
class TypeErrorManager:
    def __init__(self, *a, **kw):
        raise TypeError("bad argument type")
    def maybe_clear_socket_mapping(self):
        pass

signal_log = []
func_src = extract_function()
g = make_globals(signal_log=signal_log, manager_cls=TypeErrorManager)
exec(func_src, g)
try:
    g["run_detokenizer_process"](MockArgs(), MockArgs(), TypeErrorManager)
except UnboundLocalError as e:
    print(f"FAIL: UnboundLocalError: {e}")
    sys.exit(1)
except Exception:
    pass

if signal.SIGQUIT not in signal_log:
    print(f"FAIL: SIGQUIT not sent: {signal_log}")
    sys.exit(1)
print("PASS")
''')
    assert r.returncode == 0, f"Failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + behavioral via subprocess
# ---------------------------------------------------------------------------

def test_cleanup_called_when_manager_succeeds():
    """When manager IS created but event_loop raises, cleanup must still be called."""
    r = _run_py(_HARNESS + '''
cleanup_log = []

class SuccessManager:
    def __init__(self, *a, **kw):
        pass
    def event_loop(self):
        raise RuntimeError("event loop crash")
    def event_loop_overlap(self):
        raise RuntimeError("event loop crash")
    def maybe_clear_socket_mapping(self):
        cleanup_log.append("cleared")

signal_log = []
func_src = extract_function()
g = make_globals(signal_log=signal_log, manager_cls=SuccessManager)
exec(func_src, g)
try:
    g["run_detokenizer_process"](MockArgs(), MockArgs(), SuccessManager)
except Exception:
    pass

if not cleanup_log:
    print("FAIL: maybe_clear_socket_mapping not called")
    sys.exit(1)
if signal.SIGQUIT not in signal_log:
    print(f"FAIL: SIGQUIT not sent: {signal_log}")
    sys.exit(1)
print("PASS")
''')
    assert r.returncode == 0, f"Cleanup check failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


def test_error_logged_on_constructor_failure():
    """An error must be logged when the constructor fails."""
    r = _run_py(_HARNESS + '''
error_messages = []
def capture_error(*a, **kw):
    error_messages.append(a)

func_src = extract_function()
g = make_globals()
g["logger"] = types.SimpleNamespace(
    error=capture_error, info=lambda *a,**kw:None,
    warning=lambda *a,**kw:None, debug=lambda *a,**kw:None)
exec(func_src, g)
try:
    g["run_detokenizer_process"](MockArgs(), MockArgs(), FailingManager)
except Exception:
    pass

if not error_messages:
    print("FAIL: no error logged")
    sys.exit(1)
msg = str(error_messages[0])
if "DetokenizerManager" not in msg and "traceback" not in msg.lower():
    print(f"FAIL: error message doesn't reference failure: {msg}")
    sys.exit(1)
print("PASS")
''')
    assert r.returncode == 0, f"Logging check failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_ruff_check():
    """Repo's ruff lint (F401, F821) passes on srt/managers (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821", f"{REPO}/python/sglang/srt/managers/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_black_check():
    """Repo's black formatting passes on srt/managers (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "black", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["black", "--check", f"{REPO}/python/sglang/srt/managers/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black check failed:\n{r.stderr}"


def test_repo_isort_check():
    """Repo's isort import ordering passes on srt/managers (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "isort", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["isort", "--check", f"{REPO}/python/sglang/srt/managers/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Isort check failed:\n{r.stderr}"


def test_repo_codespell_check():
    """Repo's codespell passes on srt/managers (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "codespell", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["codespell", f"{REPO}/python/sglang/srt/managers/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Codespell check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_precommit_ast_check():
    """Target file AST check (pass_to_pass) - from pre-commit check-ast."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{TARGET}').read())"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AST check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural checks
# ---------------------------------------------------------------------------

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


def test_not_stub():
    """run_detokenizer_process must have real logic, not just pass/return."""
    with open(TARGET) as f:
        source = f.read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_detokenizer_process":
            body_types = {type(s).__name__ for s in node.body}
            assert "Try" in body_types, "Function body missing try/except block"
            assert len(node.body) >= 3, (
                f"Function body too short ({len(node.body)} stmts) — likely a stub"
            )
            return
    raise AssertionError("run_detokenizer_process function not found")
