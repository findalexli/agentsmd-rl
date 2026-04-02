"""
Task: slime-rollout-make-group-router-params
Repo: THUDM/slime @ 6f11313004dbe71f4194536335b891371eefd0e9

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import inspect
import sys
import textwrap
from pathlib import Path

REPO = "/workspace/slime"
FILE = f"{REPO}/slime/ray/rollout.py"


# ---------------------------------------------------------------------------
# Helpers — shared mock infrastructure
# ---------------------------------------------------------------------------

def _extract_make_group():
    """Parse rollout.py, extract _make_group source and AST node."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_make_group":
            lines = source.splitlines(keepends=True)
            func_lines = lines[node.lineno - 1 : node.end_lineno]
            func_src = textwrap.dedent("".join(func_lines))
            return func_src, node, source
    raise AssertionError("_make_group function not found in rollout.py")


def _build_exec_namespace(closure_ip="STALE_IP", closure_port=99999):
    """Build a namespace for exec'ing _make_group with mock objects."""
    captured = []

    class MockServerGroup:
        def __init__(self, **kwargs):
            captured.append(dict(kwargs))

    class MockBox:
        def __getattr__(self, name):
            if name == "hf_checkpoint":
                return "/fake/model"
            if name == "num_gpus_per_node":
                return 8
            if name == "offload_rollout":
                return False
            return MockBox()

    class MockGroupCfg:
        num_gpus_per_engine = 1
        num_gpus = 2
        worker_type = "decode"
        overrides = {}

    class MockLogger:
        def info(self, *a, **kw): pass
        def warning(self, *a, **kw): pass

    ns = {
        "__builtins__": __builtins__,
        "ServerGroup": MockServerGroup,
        "args": MockBox(),
        "pg": None,
        "logger": MockLogger(),
        "router_ip": closure_ip,
        "router_port": closure_port,
        "engine_offset": 0,
        "gpu_offset": 0,
        "rollout_pg_offset": 0,
        "megatron_num_gpus": 0,
    }
    return ns, captured, MockGroupCfg


def _get_make_group_fn(func_src, ns):
    """Exec _make_group in a wrapper function to satisfy nonlocal declarations."""
    # _make_group uses 'nonlocal engine_offset, gpu_offset' which requires
    # an enclosing function scope — can't exec at module level.
    tree = ast.parse(func_src)
    nonlocal_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Nonlocal):
            nonlocal_names.extend(node.names)

    if nonlocal_names:
        indented = textwrap.indent(func_src, "    ")
        var_inits = "\n".join(f"    {n} = {ns.get(n, 0)}" for n in nonlocal_names)
        wrapper = (
            f"def _outer_wrapper():\n"
            f"{var_inits}\n"
            f"{indented}\n"
            f"    return _make_group\n"
        )
        exec(wrapper, ns)
        fn = ns["_outer_wrapper"]()
    else:
        exec(func_src, ns)
        fn = ns.get("_make_group")

    assert fn is not None, "_make_group not defined after exec"
    return fn


def _build_router_kwargs(fn, node, ip, port):
    """Build keyword args to pass router info to _make_group."""
    sig = inspect.signature(fn)
    param_names = list(sig.parameters.keys())
    kw = {}
    for pname in param_names:
        if "router_ip" in pname:
            kw[pname] = ip
        elif "router_port" in pname:
            kw[pname] = port
        elif pname in ("router_config", "router_info"):
            kw[pname] = {"ip": ip, "port": port}
    if node.args.kwarg:
        kw.setdefault("router_ip", ip)
        kw.setdefault("router_port", port)
    return kw


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """rollout.py must parse without syntax errors."""
    source = Path(FILE).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_make_group_accepts_router_params():
    """_make_group must accept router_ip and router_port as explicit parameters,
    not rely on closure variables."""
    # AST-only because: signature check — behavioral tests below verify the values propagate
    func_src, node, _ = _extract_make_group()
    params = [a.arg for a in node.args.args]
    has_router_params = (
        any("router" in p for p in params)
        or any(p in ("router_config", "router_info", "router_kwargs") for p in params)
        or node.args.kwarg is not None
    )
    assert has_router_params, (
        f"_make_group params {params} — no way to receive router info as arguments"
    )


# [pr_diff] fail_to_pass
def test_make_group_uses_param_router_not_closure():
    """When _make_group is called with explicit router params, ServerGroup must
    receive those values — not stale closure values."""
    func_src, node, _ = _extract_make_group()
    ns, captured, MockGroupCfg = _build_exec_namespace(
        closure_ip="CLOSURE_STALE_IP", closure_port=99999
    )
    fn = _get_make_group_fn(func_src, ns)

    param_ip = "10.0.0.42"
    param_port = 8080
    kw = _build_router_kwargs(fn, node, param_ip, param_port)
    fn(MockGroupCfg(), **kw)

    assert len(captured) >= 1, "ServerGroup was never constructed"
    sg = captured[0]

    # ServerGroup must have received the param values, not closure values
    all_vals = str(sg)
    assert param_ip in all_vals and str(param_port) in all_vals, (
        f"ServerGroup did not receive correct router values. Got: {sg}"
    )
    assert "CLOSURE_STALE_IP" not in all_vals and "99999" not in all_vals, (
        f"ServerGroup received stale closure values. Got: {sg}"
    )


# [pr_diff] fail_to_pass
def test_multi_model_router_independence():
    """Two _make_group calls with different router params must each produce
    a ServerGroup with its own correct router coordinates (EPD multi-model scenario)."""
    func_src, node, _ = _extract_make_group()

    model_a_ip, model_a_port = "192.168.1.10", 5000
    model_b_ip, model_b_port = "192.168.1.20", 6000

    # Closure has model B's values (simulating second loop iteration)
    ns, captured, MockGroupCfg = _build_exec_namespace(
        closure_ip=model_b_ip, closure_port=model_b_port
    )
    fn = _get_make_group_fn(func_src, ns)

    # Call 1: pass model A's router params explicitly
    kw_a = _build_router_kwargs(fn, node, model_a_ip, model_a_port)
    fn(MockGroupCfg(), **kw_a)

    # Call 2: pass model B's router params explicitly
    ns["engine_offset"] = 0
    ns["gpu_offset"] = 0
    kw_b = _build_router_kwargs(fn, node, model_b_ip, model_b_port)
    fn(MockGroupCfg(), **kw_b)

    assert len(captured) >= 2, f"Expected 2 ServerGroup constructions, got {len(captured)}"

    cap1, cap2 = str(captured[0]), str(captured[1])
    # Call 1 must have model A's values, NOT model B's
    assert model_a_ip in cap1 and str(model_a_port) in cap1, (
        f"Call 1 missing model A router values. Got: {captured[0]}"
    )
    assert model_b_ip not in cap1, (
        f"Call 1 has model B's IP (closure leak). Got: {captured[0]}"
    )
    # Call 2 must have model B's values
    assert model_b_ip in cap2 and str(model_b_port) in cap2, (
        f"Call 2 missing model B router values. Got: {captured[1]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_start_rollout_servers_signature():
    """start_rollout_servers must still accept (args, pg) parameters."""
    # AST-only because: start_rollout_servers requires Ray cluster to call
    source = Path(FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "start_rollout_servers":
            params = [a.arg for a in node.args.args]
            assert "args" in params and "pg" in params, (
                f"start_rollout_servers signature changed: {params}"
            )
            return
    raise AssertionError("start_rollout_servers not found")


# [pr_diff] fail_to_pass
def test_all_call_sites_pass_router_info():
    """Every _make_group() call inside start_rollout_servers must pass
    router info (not just group_cfg alone)."""
    # AST-only because: start_rollout_servers requires Ray cluster + GPU placement groups
    source = Path(FILE).read_text()
    tree = ast.parse(source)

    class CallFinder(ast.NodeVisitor):
        def __init__(self):
            self.calls = []
            self.in_target = False

        def visit_FunctionDef(self, node):
            if node.name == "start_rollout_servers":
                self.in_target = True
                self.generic_visit(node)
                self.in_target = False
            elif self.in_target:
                self.generic_visit(node)

        def visit_Call(self, node):
            if self.in_target and isinstance(node.func, ast.Name) and node.func.id == "_make_group":
                self.calls.append(node)
            self.generic_visit(node)

    finder = CallFinder()
    finder.visit(tree)
    assert len(finder.calls) >= 3, (
        f"Expected at least 3 _make_group call sites, found {len(finder.calls)}"
    )

    for i, call in enumerate(finder.calls):
        n_pos = len(call.args)
        kw_names = [kw.arg for kw in call.keywords if kw.arg is not None]
        has_router = (
            n_pos >= 2
            or any("router" in (k or "") for k in kw_names)
            or any(kw.arg is None for kw in call.keywords)
        )
        assert has_router, (
            f"Call site {i+1} passes only {n_pos} positional arg(s) and keywords "
            f"{kw_names} — no router info"
        )


# [static] pass_to_pass
def test_make_group_not_stub():
    """_make_group must have real logic (not just pass/return)."""
    func_src, node, _ = _extract_make_group()
    # Count meaningful statements (not pass, not docstrings)
    meaningful = [
        s for s in node.body
        if not isinstance(s, ast.Pass)
        and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
    ]
    assert len(meaningful) >= 5, (
        f"_make_group body has only {len(meaningful)} meaningful statements — likely a stub"
    )


# [pr_diff] pass_to_pass
def test_nonlocal_offset_tracking_preserved():
    """_make_group must still use nonlocal for engine_offset/gpu_offset tracking."""
    # AST-only because: checking nonlocal declaration, can't test offset tracking without Ray
    _, node, _ = _extract_make_group()
    for child in ast.walk(node):
        if isinstance(child, ast.Nonlocal):
            if "engine_offset" in child.names or "gpu_offset" in child.names:
                return
    raise AssertionError("nonlocal offset declaration missing in _make_group")
