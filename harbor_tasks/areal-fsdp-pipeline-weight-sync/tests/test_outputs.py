"""
Task: areal-fsdp-pipeline-weight-sync
Repo: inclusionAI/AReaL @ 61281ba8851e6d1cf8c30794a5391359b4e324b7

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: All tests use AST analysis because the code under test requires
a NCCL multi-rank distributed runtime which cannot run on a single CPU.
"""

import ast
from pathlib import Path

FILE = Path("/repo/areal/engine/fsdp_engine.py")


def _parse():
    return ast.parse(FILE.read_text())


def _find_class(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _find_method(cls_node, name):
    for item in cls_node.body:
        if isinstance(item, ast.FunctionDef) and item.name == name:
            return item
    return None


def _count_meaningful(node):
    return sum(
        1
        for n in ast.walk(node)
        if isinstance(
            n,
            (ast.Assign, ast.AugAssign, ast.For, ast.While, ast.If, ast.With, ast.Try, ast.Return, ast.Call),
        )
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """fsdp_engine.py must parse as valid Python."""
    import py_compile

    py_compile.compile(str(FILE), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_pipelined_main_loop():
    """Main update loop overlaps bucket broadcast with next bucket preparation.

    The core bug is fully synchronous bucket processing. A correct fix must
    assign a pending state from a self.method() call AND read it back within
    the same loop (deferred-wait pattern), with try/finally for error safety.
    """
    tree = _parse()
    engine = _find_class(tree, "FSDPEngine")
    assert engine, "FSDPEngine class not found"

    fn = _find_method(engine, "_update_weights_from_distributed")
    assert fn, "_update_weights_from_distributed not found"

    # Must have a for loop iterating over parameters/buckets
    for_loops = [n for n in ast.walk(fn) if isinstance(n, ast.For)]
    assert for_loops, "No for loop — not iterating over buckets"
    main_loop = for_loops[0]

    # Pipeline pattern: a variable is assigned from self.method() AND read back
    # in the same loop body (deferred wait across iterations)
    dispatch_targets = set()
    for stmt in ast.walk(main_loop):
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name) and call.func.value.id == "self":
                for tgt in stmt.targets:
                    if isinstance(tgt, ast.Name):
                        dispatch_targets.add(tgt.id)

    read_in_loop = {
        stmt.id for stmt in ast.walk(main_loop) if isinstance(stmt, ast.Name) and isinstance(stmt.ctx, ast.Load)
    }
    pipeline_vars = dispatch_targets & read_in_loop
    assert pipeline_vars, "No deferred-wait pipeline pattern: no variable is both dispatched and read across iterations"

    # Must have try/finally for error safety
    has_drain_finally = False
    for child in ast.walk(fn):
        if isinstance(child, ast.Try) and child.finalbody:
            non_pass = [s for s in child.finalbody if not isinstance(s, ast.Pass)]
            if non_pass:
                has_drain_finally = True
    assert has_drain_finally, "No try/finally with drain logic for error safety"

    # Anti-stub: method must be substantial
    meaningful = _count_meaningful(fn)
    assert meaningful >= 15, f"Method too simple ({meaningful} meaningful nodes, need >=15) — likely stubbed"


# [pr_diff] fail_to_pass
def test_async_bucket_method():
    """An async bucket broadcast method exists that returns pending state.

    Must contain real distributed logic (broadcast/async_op) with >=8
    meaningful statements, and return a non-None value.
    """
    tree = _parse()
    engine = _find_class(tree, "FSDPEngine")
    assert engine, "FSDPEngine class not found"

    skip_names = {"_update_bucket_weights_from_distributed", "_update_weights_from_distributed", "__init__"}
    for item in engine.body:
        if not isinstance(item, ast.FunctionDef):
            continue
        if item.name in skip_names or item.name.startswith("_init"):
            continue

        # Must return a non-None value
        returns_value = any(
            isinstance(child, ast.Return)
            and child.value is not None
            and not (isinstance(child.value, ast.Constant) and child.value.value is None)
            for child in ast.walk(item)
        )
        if not returns_value:
            continue

        # Must have real distributed logic
        has_dist = any(
            (isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute) and child.func.attr in ("broadcast", "all_reduce", "_broadcast_coalesced", "broadcast_object_list"))
            or (isinstance(child, ast.keyword) and child.arg == "async_op")
            for child in ast.walk(item)
        )
        if not has_dist:
            continue

        if _count_meaningful(item) >= 8:
            return  # PASS

    assert False, "No async bucket broadcast method found with real distributed logic"


# [pr_diff] fail_to_pass
def test_pending_state_dataclass():
    """A data structure with >=3 fields tracks in-flight broadcast state and is used in FSDPEngine."""
    tree = _parse()

    # Find candidate classes with >=3 annotated fields (pending state)
    candidates = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name != "FSDPEngine":
            fields = {
                item.target.id for item in node.body if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)
            }
            if len(fields) >= 3:
                candidates.append(node.name)

    assert candidates, "No data structure with >=3 annotated fields for tracking in-flight state"

    # Must be instantiated (called) in FSDPEngine
    engine = _find_class(tree, "FSDPEngine")
    assert engine, "FSDPEngine class not found"

    for call_node in ast.walk(engine):
        if isinstance(call_node, ast.Call):
            func = call_node.func
            if isinstance(func, ast.Name) and func.id in candidates:
                return  # PASS
            if isinstance(func, ast.Attribute) and func.attr in candidates:
                return  # PASS

    assert False, f"Candidate classes {candidates} exist but are never instantiated in FSDPEngine"


# [pr_diff] fail_to_pass
def test_error_safety_drain():
    """try/finally in main method drains pending broadcasts on error."""
    tree = _parse()
    engine = _find_class(tree, "FSDPEngine")
    assert engine, "FSDPEngine class not found"

    fn = _find_method(engine, "_update_weights_from_distributed")
    assert fn, "_update_weights_from_distributed not found"

    for child in ast.walk(fn):
        if isinstance(child, ast.Try) and child.finalbody:
            # Finally must contain at least one Call or attribute access (real drain logic)
            has_action = any(
                isinstance(stmt, (ast.Call, ast.Attribute))
                for stmt in ast.walk(ast.Module(body=child.finalbody, type_ignores=[]))
            )
            if has_action:
                return  # PASS

    assert False, "No drain logic in finally block of _update_weights_from_distributed"


# [pr_diff] fail_to_pass
def test_cuda_stream_usage():
    """CUDA stream is used for broadcast overlap in weight update methods."""
    tree = _parse()
    engine = _find_class(tree, "FSDPEngine")
    assert engine, "FSDPEngine class not found"

    # Collect all weight update methods
    target_methods = {
        item.name
        for item in engine.body
        if isinstance(item, ast.FunctionDef) and "update" in item.name.lower() and "weight" in item.name.lower()
    }
    assert target_methods, "No weight update methods found"

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in target_methods:
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                    if child.func.attr in ("Stream", "stream"):
                        return  # PASS

    assert False, "No CUDA Stream usage in weight update methods"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_sync_wrapper_preserved():
    """_update_bucket_weights_from_distributed still exists with a real body."""
    tree = _parse()
    engine = _find_class(tree, "FSDPEngine")
    assert engine, "FSDPEngine class not found"

    fn = _find_method(engine, "_update_bucket_weights_from_distributed")
    assert fn, "_update_bucket_weights_from_distributed not found — backward compat broken"

    body_stmts = [s for s in fn.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
    assert len(body_stmts) >= 2, f"Only {len(body_stmts)} statements — method appears stubbed"


# [pr_diff] pass_to_pass
def test_init_method_preserved():
    """_init_weight_update_from_distributed still present with real body."""
    tree = _parse()
    engine = _find_class(tree, "FSDPEngine")
    assert engine, "FSDPEngine class not found"

    fn = None
    for item in ast.walk(engine):
        if isinstance(item, ast.FunctionDef) and item.name == "_init_weight_update_from_distributed":
            fn = item
            break
    assert fn, "_init_weight_update_from_distributed not found"
    assert _count_meaningful(fn) >= 3, "Method appears stubbed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:30 @ 61281ba
def test_no_wildcard_imports():
    """No wildcard imports (from x import *)."""
    tree = _parse()
    wildcards = [
        (node.module, alias.name)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
        if alias.name == "*"
    ]
    assert not wildcards, f"Wildcard imports found: {wildcards}"


# [agent_config] pass_to_pass — AGENTS.md:194 @ 61281ba
def test_broadcast_explicit_src():
    """All broadcast() calls specify src rank explicitly."""
    tree = _parse()
    found_any = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "broadcast":
            found_any = True
            kw_names = [kw.arg for kw in node.keywords]
            assert "src" in kw_names or len(node.args) >= 2, "broadcast() without explicit src"

    if not found_any:
        # Accept: some implementations use broadcast_object_list or _broadcast_coalesced
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and "broadcast" in node.func.attr.lower():
                return
        assert False, "No broadcast calls found"


# [agent_config] pass_to_pass — AGENTS.md:90-91 @ 61281ba
def test_no_print_calls():
    """No bare print() calls — use areal.utils.logging.getLogger() instead.
    # AST-only because: distributed engine code requires NCCL runtime
    """
    tree = _parse()
    prints = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "print":
                prints.append(node.lineno)
    assert not prints, f"print() calls found at lines {prints} — use areal.utils.logging instead"


# [agent_config] pass_to_pass — AGENTS.md:189 @ 61281ba
def test_no_module_level_process_groups():
    """No global process group creation at module level.
    # AST-only because: distributed engine code requires NCCL runtime
    """
    tree = _parse()
    # Check top-level statements (not inside class/function)
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            call = node.value
        else:
            continue
        func = call.func
        # dist.new_group() or dist.init_process_group() at module level
        if isinstance(func, ast.Attribute) and func.attr in ("new_group", "init_process_group"):
            assert False, f"Module-level process group creation: {func.attr}() at line {node.lineno}"


# [agent_config] pass_to_pass — AGENTS.md:96 @ 61281ba
def test_no_gpu_cpu_sync_in_weight_update():
    """No .item() or .tolist() in weight update methods (GPU-CPU sync in hot paths).
    # AST-only because: distributed engine code requires NCCL runtime
    """
    tree = _parse()
    engine = _find_class(tree, "FSDPEngine")
    assert engine, "FSDPEngine class not found"

    violations = []
    for item in engine.body:
        if not isinstance(item, ast.FunctionDef):
            continue
        if "update" not in item.name.lower() or "weight" not in item.name.lower():
            continue
        for child in ast.walk(item):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                if child.func.attr in ("item", "tolist"):
                    violations.append(f"{item.name}:{child.lineno} .{child.func.attr}()")
    assert not violations, f"GPU-CPU sync in weight update hot paths: {violations}"
