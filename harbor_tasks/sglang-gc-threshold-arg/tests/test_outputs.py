"""
Task: sglang-gc-threshold-arg
Repo: sgl-project/sglang @ 4e905febd2f9e96b4c114530a2379b084ad791af
PR:   21481

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"
SERVER_ARGS = f"{REPO}/python/sglang/srt/server_args.py"
ENGINE = f"{REPO}/python/sglang/srt/entrypoints/engine.py"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess within the repo directory."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _extract_func_source(filepath, func_name):
    """Return source text of `func_name` from `filepath`, or None."""
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return ast.get_source_segment(source, node)
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified files must parse without syntax errors."""
    for f in [SERVER_ARGS, ENGINE]:
        source = Path(f).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_gc_function_sets_thresholds():
    """GC-setting function calls gc.set_threshold correctly for 1, 2, and 3 args."""
    r = _run_py('''import ast, gc, textwrap
from pathlib import Path

source = Path("/workspace/sglang/python/sglang/srt/entrypoints/engine.py").read_text()
tree = ast.parse(source)

func_name = func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        src = ast.get_source_segment(source, node)
        if src and "set_threshold" in src:
            func_name, func_src = node.name, src
            break

assert func_src, "No gc.set_threshold function found in engine.py"

ServerArgs = type("ServerArgs", (), {})
ns = {"gc": gc, "__builtins__": __builtins__, "ServerArgs": ServerArgs}
exec(textwrap.dedent(func_src), ns)
fn = ns[func_name]

orig = gc.get_threshold()

class A3:
    gc_threshold = [500, 5, 5]
fn(A3())
assert gc.get_threshold() == (500, 5, 5), "3-arg: %s" % repr(gc.get_threshold())

gc.set_threshold(*orig)
class A1:
    gc_threshold = [50000]
fn(A1())
assert gc.get_threshold()[0] == 50000, "1-arg: %s" % repr(gc.get_threshold())

gc.set_threshold(*orig)
class A2:
    gc_threshold = [700, 10]
fn(A2())
t = gc.get_threshold()
assert t[0] == 700 and t[1] == 10, "2-arg: %s" % repr(t)

gc.set_threshold(*orig)
class AN:
    gc_threshold = None
fn(AN())
assert gc.get_threshold() == orig, "None should be no-op"

gc.set_threshold(*orig)
print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_cli_parser_accepts_gc_threshold():
    """CLI parser accepts --gc-threshold with varying numbers of int arguments."""
    r = _run_py('''import ast, argparse, textwrap
from pathlib import Path

source = Path("/workspace/sglang/python/sglang/srt/server_args.py").read_text()
tree = ast.parse(source)

add_cli_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "add_cli_args":
        add_cli_src = ast.get_source_segment(source, node)
        break

assert add_cli_src, "add_cli_args not found"
assert "--gc-threshold" in add_cli_src, "--gc-threshold not registered"

lines = add_cli_src.split("\\n")
gc_idx = None
for i, line in enumerate(lines):
    if "--gc-threshold" in line:
        gc_idx = i
        break
assert gc_idx is not None

start = gc_idx
for j in range(gc_idx, -1, -1):
    if "add_argument" in lines[j]:
        start = j
        break

block = []
depth = 0
for line in lines[start:]:
    block.append(line)
    depth += line.count("(") - line.count(")")
    if depth <= 0 and block:
        break

block_src = textwrap.dedent("\\n".join(block))
parser = argparse.ArgumentParser()
exec(block_src, {"parser": parser, "int": int, "str": str, "float": float, "bool": bool})

args = parser.parse_args(["--gc-threshold", "700", "10", "10"])
assert args.gc_threshold == [700, 10, 10], "3-int: %s" % args.gc_threshold

args = parser.parse_args(["--gc-threshold", "50000"])
assert args.gc_threshold == [50000], "1-int: %s" % args.gc_threshold

args = parser.parse_args([])
assert args.gc_threshold is None, "default: %s" % args.gc_threshold

args = parser.parse_args(["--gc-threshold", "100", "20"])
assert all(isinstance(v, int) for v in args.gc_threshold), "values not int"

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_validation_rejects_invalid_gc_threshold():
    """check_server_args rejects gc_threshold with 0 or 4+ values."""
    r = _run_py('''import ast, textwrap
from pathlib import Path

source = Path("/workspace/sglang/python/sglang/srt/server_args.py").read_text()
tree = ast.parse(source)

check_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "check_server_args":
        check_src = ast.get_source_segment(source, node)
        break

assert check_src, "check_server_args not found"
assert "gc_threshold" in check_src, "gc_threshold not validated in check_server_args"

lines = check_src.split("\\n")
gc_block = []
capturing = False
base_indent = None
for line in lines:
    if "gc_threshold" in line and not capturing:
        capturing = True
        base_indent = len(line) - len(line.lstrip())
    if capturing:
        stripped = line.strip()
        cur_indent = len(line) - len(line.lstrip()) if stripped else base_indent + 1
        if cur_indent >= base_indent or not stripped:
            gc_block.append(line)
        else:
            break

assert gc_block, "Could not locate gc_threshold validation block"
gc_code = textwrap.dedent("\\n".join(gc_block))

wrapper = """def _validate(gc_threshold):
    class _self:
        pass
    _self.gc_threshold = gc_threshold
    self = _self
""" + textwrap.indent(gc_code, "    ")

ns = {"__builtins__": __builtins__}
exec(wrapper, ns)
validate = ns["_validate"]

for v in ([700, 10, 10], [50000], [100, 20]):
    validate(v)

try:
    validate([1, 2, 3, 4])
    raise RuntimeError("Should have raised for 4 values")
except (ValueError, SystemExit, AssertionError):
    pass

try:
    validate([1, 2, 3, 4, 5])
    raise RuntimeError("Should have raised for 5 values")
except (ValueError, SystemExit, AssertionError):
    pass

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_server_args_structures_intact():
    """ServerArgs class and add_cli_args/check_server_args functions exist."""
    source = Path(SERVER_ARGS).read_text()
    tree = ast.parse(source)
    classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert "ServerArgs" in classes, "ServerArgs class missing"
    assert "add_cli_args" in funcs, "add_cli_args function missing"
    assert "check_server_args" in funcs, "check_server_args function missing"


# [static] pass_to_pass
def test_launch_subprocesses_intact():
    """_launch_subprocesses function exists in engine.py."""
    source = Path(ENGINE).read_text()
    tree = ast.parse(source)
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert "_launch_subprocesses" in funcs, "_launch_subprocesses missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — integration
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_gc_invoked_in_launch_subprocesses():
    """GC threshold logic is invoked within _launch_subprocesses."""
    source = Path(ENGINE).read_text()
    tree = ast.parse(source)

    gc_func_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_src = ast.get_source_segment(source, node)
            if func_src and "set_threshold" in func_src:
                gc_func_names.add(node.name)

    assert gc_func_names, "No function calls gc.set_threshold in engine.py"

    if "_launch_subprocesses" in gc_func_names:
        return

    launch_src = _extract_func_source(ENGINE, "_launch_subprocesses")
    assert launch_src is not None, "_launch_subprocesses not found"
    for gc_name in gc_func_names:
        if gc_name in launch_src:
            return

    raise AssertionError("GC threshold logic not invoked during subprocess launch")




# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff():
    """Ruff linting passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821", "python/sglang/srt/server_args.py", "python/sglang/srt/entrypoints/engine.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_compileall():
    """Modified files compile without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "compileall", "python/sglang/srt/server_args.py", "python/sglang/srt/entrypoints/engine.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Compileall failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_isort():
    """isort import ordering passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "isort", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["isort", "--check", "python/sglang/srt/server_args.py", "python/sglang/srt/entrypoints/engine.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_black():
    """Black formatting check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["black", "--check", "python/sglang/srt/server_args.py", "python/sglang/srt/entrypoints/engine.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black check failed:\n{r.stderr}"

# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — python/sglang/srt/server_args.py:287-290 @ 4e905feb
def test_gc_threshold_in_class_and_cli():
    """gc_threshold appears in both ServerArgs class body and add_cli_args (ordering rule)."""
    source = Path(SERVER_ARGS).read_text()
    tree = ast.parse(source)

    in_class = False
    in_cli = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ServerArgs":
            for item in node.body:
                targets = []
                if isinstance(item, ast.AnnAssign):
                    targets = [item.target]
                elif isinstance(item, ast.Assign):
                    targets = item.targets
                for t in targets:
                    if hasattr(t, "id") and t.id == "gc_threshold":
                        in_class = True
        if isinstance(node, ast.FunctionDef) and node.name == "add_cli_args":
            func_src = ast.get_source_segment(source, node)
            if func_src and "--gc-threshold" in func_src:
                in_cli = True

    assert in_class, "gc_threshold not found in ServerArgs class body"
    assert in_cli, "gc_threshold not found in add_cli_args"
