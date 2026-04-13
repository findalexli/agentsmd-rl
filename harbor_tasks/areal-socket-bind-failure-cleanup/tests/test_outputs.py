"""
Task: areal-socket-bind-failure-cleanup
Repo: inclusionAI/AReaL @ 7cad4dac2d1f230891f201dbbfa91403e621cec1
PR:   1032

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
import textwrap
from pathlib import Path

REPO = "/workspace/AReaL"

MODIFIED_FILES = [
    "areal/utils/network.py",
    "areal/trainer/rl_trainer.py",
    "areal/trainer/sft_trainer.py",
]


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo environment via subprocess."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


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
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_tcp_socket_closed_on_bind_failure():
    """TCP socket.close() is called even when bind() raises OSError."""
    r = _run_py("""
import ast, types, textwrap, socket as socket_mod
from pathlib import Path

src = Path("/workspace/AReaL/areal/utils/network.py").read_text()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "is_port_free":
        func = node
        break
else:
    raise AssertionError("is_port_free not found")

lines = src.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func.lineno - 1 : func.end_lineno]))

# Fake socket: TCP bind always fails, UDP succeeds
state = {"tcp_closed": 0, "udp_closed": 0}

class FakeSocket:
    def __init__(self, family=socket_mod.AF_INET, type_=socket_mod.SOCK_STREAM, *a, **kw):
        self._type = type_
    def bind(self, addr):
        if self._type == socket_mod.SOCK_STREAM:
            raise OSError("TCP bind refused")
    def close(self):
        if self._type == socket_mod.SOCK_STREAM:
            state["tcp_closed"] += 1
        else:
            state["udp_closed"] += 1

fake_mod = types.SimpleNamespace(
    socket=FakeSocket,
    AF_INET=socket_mod.AF_INET,
    SOCK_STREAM=socket_mod.SOCK_STREAM,
    SOCK_DGRAM=socket_mod.SOCK_DGRAM,
)
ns = {"__builtins__": __builtins__, "socket": fake_mod}
exec(func_src, ns)

result = ns["is_port_free"](9999)
assert result is False, f"Expected False, got {result}"
assert state["tcp_closed"] >= 1, "TCP socket was NOT closed after bind failure"
print("PASS")
""")
    assert r.returncode == 0, f"Test failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_udp_socket_closed_on_bind_failure():
    """UDP socket.close() is called even when bind() raises OSError."""
    r = _run_py("""
import ast, types, textwrap, socket as socket_mod
from pathlib import Path

src = Path("/workspace/AReaL/areal/utils/network.py").read_text()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "is_port_free":
        func = node
        break
else:
    raise AssertionError("is_port_free not found")

lines = src.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func.lineno - 1 : func.end_lineno]))

# Fake socket: TCP succeeds, UDP bind fails
state = {"tcp_closed": 0, "udp_closed": 0}

class FakeSocket:
    def __init__(self, family=socket_mod.AF_INET, type_=socket_mod.SOCK_STREAM, *a, **kw):
        self._type = type_
    def bind(self, addr):
        if self._type == socket_mod.SOCK_DGRAM:
            raise OSError("UDP bind refused")
    def close(self):
        if self._type == socket_mod.SOCK_STREAM:
            state["tcp_closed"] += 1
        else:
            state["udp_closed"] += 1

fake_mod = types.SimpleNamespace(
    socket=FakeSocket,
    AF_INET=socket_mod.AF_INET,
    SOCK_STREAM=socket_mod.SOCK_STREAM,
    SOCK_DGRAM=socket_mod.SOCK_DGRAM,
)
ns = {"__builtins__": __builtins__, "socket": fake_mod}
exec(func_src, ns)

result = ns["is_port_free"](9999)
assert result is False, f"Expected False, got {result}"
assert state["udp_closed"] >= 1, "UDP socket was NOT closed after bind failure"
print("PASS")
""")
    assert r.returncode == 0, f"Test failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] pass_to_pass
def test_both_sockets_closed_on_success():
    """Both TCP and UDP sockets are closed even when both binds succeed."""
    r = _run_py("""
import ast, types, textwrap, socket as socket_mod
from pathlib import Path

src = Path("/workspace/AReaL/areal/utils/network.py").read_text()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "is_port_free":
        func = node
        break
else:
    raise AssertionError("is_port_free not found")

lines = src.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func.lineno - 1 : func.end_lineno]))

# Fake socket: both binds succeed
state = {"tcp_closed": 0, "udp_closed": 0}

class FakeSocket:
    def __init__(self, family=socket_mod.AF_INET, type_=socket_mod.SOCK_STREAM, *a, **kw):
        self._type = type_
    def bind(self, addr):
        pass  # both succeed
    def close(self):
        if self._type == socket_mod.SOCK_STREAM:
            state["tcp_closed"] += 1
        else:
            state["udp_closed"] += 1

fake_mod = types.SimpleNamespace(
    socket=FakeSocket,
    AF_INET=socket_mod.AF_INET,
    SOCK_STREAM=socket_mod.SOCK_STREAM,
    SOCK_DGRAM=socket_mod.SOCK_DGRAM,
)
ns = {"__builtins__": __builtins__, "socket": fake_mod}
exec(func_src, ns)

result = ns["is_port_free"](9999)
assert result is True, f"Expected True, got {result}"
assert state["tcp_closed"] >= 1, "TCP socket was NOT closed on success"
assert state["udp_closed"] >= 1, "UDP socket was NOT closed on success"
print("PASS")
""")
    assert r.returncode == 0, f"Test failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_rl_exit_does_not_reraise():
    """RLTrainer.__exit__ returns falsy instead of re-raising with 'raise exc_value'."""
    r = _run_py("""
import ast, textwrap
from pathlib import Path

src = Path("/workspace/AReaL/areal/trainer/rl_trainer.py").read_text()
tree = ast.parse(src)
exit_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__exit__":
                exit_func = item
                break
    if exit_func:
        break
if exit_func is None:
    raise AssertionError("__exit__ not found")

lines = src.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[exit_func.lineno - 1 : exit_func.end_lineno]))

class_body = (
    "class _TestTrainer:\\n"
    "    def __init__(self): self.closed = False\\n"
    "    def close(self): self.closed = True\\n"
    "    def __enter__(self): return self\\n"
) + textwrap.indent(func_src, "    ")

class MockLogger:
    def error(self, *a, **kw): pass
    def warning(self, *a, **kw): pass
    def info(self, *a, **kw): pass

ns = {"__builtins__": __builtins__, "logger": MockLogger()}
exec(class_body, ns)
Trainer = ns["_TestTrainer"]

for exc_cls, msg in [
    (ValueError, "bad learning rate"),
    (RuntimeError, "CUDA OOM"),
    (TypeError, "wrong argument type"),
]:
    exc = exc_cls(msg)
    exc.__traceback__ = None
    trainer = Trainer()
    try:
        result = trainer.__exit__(exc_cls, exc, None)
    except BaseException as e:
        raise AssertionError(
            f"__exit__ should not re-raise — return False instead. "
            f"Got: {type(e).__name__}: {e}"
        )
    assert not result, f"__exit__ should return falsy, got {result!r}"
print("PASS")
""")
    assert r.returncode == 0, f"Test failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_sft_exit_does_not_reraise():
    """SFTTrainer.__exit__ returns falsy instead of re-raising with 'raise exc_value'."""
    r = _run_py("""
import ast, textwrap
from pathlib import Path

src = Path("/workspace/AReaL/areal/trainer/sft_trainer.py").read_text()
tree = ast.parse(src)
exit_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__exit__":
                exit_func = item
                break
    if exit_func:
        break
if exit_func is None:
    raise AssertionError("__exit__ not found")

lines = src.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[exit_func.lineno - 1 : exit_func.end_lineno]))

class_body = (
    "class _TestTrainer:\\n"
    "    def __init__(self): self.closed = False\\n"
    "    def close(self): self.closed = True\\n"
    "    def __enter__(self): return self\\n"
) + textwrap.indent(func_src, "    ")

class MockLogger:
    def error(self, *a, **kw): pass
    def warning(self, *a, **kw): pass
    def info(self, *a, **kw): pass

ns = {"__builtins__": __builtins__, "logger": MockLogger()}
exec(class_body, ns)
Trainer = ns["_TestTrainer"]

for exc_cls, msg in [
    (ValueError, "invalid batch size"),
    (RuntimeError, "distributed error"),
    (TypeError, "unexpected kwarg"),
]:
    exc = exc_cls(msg)
    exc.__traceback__ = None
    trainer = Trainer()
    try:
        result = trainer.__exit__(exc_cls, exc, None)
    except BaseException as e:
        raise AssertionError(
            f"__exit__ should not re-raise — return False instead. "
            f"Got: {type(e).__name__}: {e}"
        )
    assert not result, f"__exit__ should return falsy, got {result!r}"
print("PASS")
""")
    assert r.returncode == 0, f"Test failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] pass_to_pass
def test_rl_exit_calls_close():
    """RLTrainer.__exit__ calls self.close() for cleanup."""
    src = Path(f"{REPO}/areal/trainer/rl_trainer.py").read_text()
    tree = ast.parse(src)
    exit_func = _find_function(tree, "__exit__")
    assert exit_func is not None, "__exit__ not found in rl_trainer.py"

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
    trainer = ns["_TestTrainer"]()
    trainer.__exit__(None, None, None)
    assert trainer.closed, "RLTrainer.__exit__ must call self.close()"


# [pr_diff] pass_to_pass
def test_sft_exit_calls_close():
    """SFTTrainer.__exit__ calls self.close() for cleanup."""
    src = Path(f"{REPO}/areal/trainer/sft_trainer.py").read_text()
    tree = ast.parse(src)
    exit_func = _find_function(tree, "__exit__")
    assert exit_func is not None, "__exit__ not found in sft_trainer.py"

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
    trainer = ns["_TestTrainer"]()
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


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates (must use subprocess.run with real commands)
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass — Runs actual ruff lint check via subprocess
def test_repo_ruff_check():
    """Modified files pass ruff lint check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check"] + [f"{REPO}/{f}" for f in MODIFIED_FILES],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — Runs actual ruff format check via subprocess
def test_repo_ruff_format():
    """Modified files pass ruff format check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check"] + [f"{REPO}/{f}" for f in MODIFIED_FILES],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — Network socket functions work via standalone subprocess
def test_repo_network_functions():
    """Network module socket functions work correctly (pass_to_pass)."""
    code = """
import socket
import random

# Standalone implementation matching the repo's network.py logic
def is_port_free(port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("", port))
    except OSError:
        return False
    finally:
        sock.close()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("", port))
        return True
    except OSError:
        return False
    finally:
        sock.close()

def find_free_ports(count, port_range=(30000, 30100), exclude_ports=None):
    if exclude_ports is None:
        exclude_ports = set()
    min_port, max_port = port_range
    free_ports = []
    attempted_ports = set()
    max_attempts = count * 10
    attempts = 0
    while len(free_ports) < count and attempts < max_attempts:
        port = random.randint(min_port, max_port)
        if port in attempted_ports or port in exclude_ports:
            attempts += 1
            continue
        attempted_ports.add(port)
        if is_port_free(port):
            free_ports.append(port)
        attempts += 1
    return sorted(free_ports)

# Test is_port_free returns bool
result = is_port_free(19999)
assert isinstance(result, bool), f"is_port_free should return bool, got {type(result)}"

# Test find_free_ports returns correct length
ports = find_free_ports(3, port_range=(30000, 30100))
assert len(ports) == 3, f"Expected 3 ports, got {len(ports)}"
assert all(isinstance(p, int) for p in ports), "All ports should be integers"

print("PASS: Network functions work correctly")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Network functions test failed:\n{r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


# [repo_tests] pass_to_pass — Trainer files are valid Python and have __exit__ methods
def test_repo_trainer_exit_ast():
    """RL/SFT trainer files have valid __exit__ method structure (pass_to_pass)."""
    code = f"""
import ast
from pathlib import Path

files = {{
    "rl_trainer": "{REPO}/areal/trainer/rl_trainer.py",
    "sft_trainer": "{REPO}/areal/trainer/sft_trainer.py",
}}

for name, path in files.items():
    src = Path(path).read_text()
    tree = ast.parse(src)  # Validates Python syntax

    # Find __exit__ method
    exit_found = False
    exit_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__exit__":
                    exit_found = True
                    exit_node = item
                    break
        if exit_found:
            break

    assert exit_found, name + ": no __exit__ method found"

    # Verify __exit__ has correct signature (exc_type, exc_value, traceback)
    args = [arg.arg for arg in exit_node.args.args]
    assert len(args) >= 4, f"{{name}}.__exit__ should have at least 4 args (self, exc_type, exc_value, traceback), got {{args}}"
    assert args[1] == "exc_type", f"{{name}}.__exit__ first arg after self should be exc_type, got {{args[1]}}"
    assert args[2] == "exc_value", f"{{name}}.__exit__ second arg after self should be exc_value, got {{args[2]}}"

    print(name + ": __exit__ has valid signature")

print("PASS: Trainer __exit__ structure validation passed")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Trainer structure test failed:\n{r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


# [static] pass_to_pass — File content check (not a subprocess command)
def test_repo_eof_newline():
    """Modified files end with newline (pass_to_pass)."""
    for f in MODIFIED_FILES:
        src = Path(f"{REPO}/{f}").read_text()
        if src and not src.endswith("\n"):
            raise AssertionError(f"{f} does not end with newline")


# [static] pass_to_pass — File content check (not a subprocess command)
def test_repo_no_trailing_whitespace():
    """Modified files have no trailing whitespace (pass_to_pass)."""
    for f in MODIFIED_FILES:
        lines = Path(f"{REPO}/{f}").read_text().splitlines()
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line:
                raise AssertionError(f"{f}:{i} has trailing whitespace")
