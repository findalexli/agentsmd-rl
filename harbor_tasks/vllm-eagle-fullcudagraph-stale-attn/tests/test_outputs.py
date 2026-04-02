"""
Task: vllm-eagle-fullcudagraph-stale-attn
Repo: vllm-project/vllm @ 44a6528028ad79951de08b6a7928f6c05788d00d
PR:   #38311

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

AST-only because: speculator.py requires torch, CUDA, vllm GPU runtime —
cannot be imported or executed in a CPU-only Docker container.
"""

import ast
from pathlib import Path

REPO = "/repo"
FILE = Path(REPO) / "vllm/v1/worker/gpu/spec_decode/eagle/speculator.py"


def _parse_file():
    """Parse the speculator file and return (source, tree)."""
    src = FILE.read_text()
    tree = ast.parse(src)
    return src, tree


def _find_method(tree, class_name, method_name):
    """Find a method inside a class."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in ast.walk(node):
                if isinstance(child, ast.FunctionDef) and child.name == method_name:
                    return child
    return None


def _get_call_name(node):
    """Get the function/method name from a Call node."""
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    elif isinstance(node.func, ast.Name):
        return node.func.id
    return None


def _is_attn_build_call(name):
    """Check if a call name looks like an attention metadata build call."""
    if name is None:
        return False
    nl = name.lower()
    has_attn = "attn" in nl or "attention" in nl
    has_action = any(w in nl for w in ("build", "metadata", "prepare", "setup", "update", "create"))
    return has_attn and has_action


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    src = FILE.read_text()
    ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_early_return_before_attn_metadata():
    """FULL cudagraph path must NOT return before building attention metadata.

    The bug: an if-block checking CUDAGraphMode.FULL contains a return
    statement before any attention metadata build call. The fix removes
    this early return or moves attn metadata building before it.
    """
    src, tree = _parse_file()
    propose = _find_method(tree, "EagleSpeculator", "propose")
    assert propose is not None, "propose() method not found in EagleSpeculator"

    # Find all attn-build calls (direct + method-chain)
    attn_build_calls = []
    for node in ast.walk(propose):
        if isinstance(node, ast.Call):
            name = _get_call_name(node)
            if _is_attn_build_call(name):
                nargs = len(node.args) + len(node.keywords)
                attn_build_calls.append((node.lineno, nargs))
            # Also check method chains like self.attn_builder.build(...)
            if isinstance(node.func, ast.Attribute):
                chain_parts = []
                n = node.func
                while isinstance(n, ast.Attribute):
                    chain_parts.append(n.attr)
                    n = n.value
                if isinstance(n, ast.Name):
                    chain_parts.append(n.id)
                chain_str = ".".join(reversed(chain_parts)).lower()
                if ("attn" in chain_str or "attention" in chain_str) and \
                   any(w in chain_str for w in ("build", "metadata", "prepare", "setup")):
                    nargs = len(node.args) + len(node.keywords)
                    attn_build_calls.append((node.lineno, nargs))

    assert attn_build_calls, "No call to build/prepare attention metadata found in propose()"

    # Require at least one attn build call has >=3 arguments (not a stub)
    max_args = max(nargs for _, nargs in attn_build_calls)
    assert max_args >= 3, f"Attn build call has only {max_args} args — likely a stub"

    earliest_attn_build = min(line for line, _ in attn_build_calls)

    # Detect the BUG PATTERN: if-block checking CUDAGraphMode.FULL that
    # contains a return BEFORE any attn metadata building
    for node in ast.walk(propose):
        if isinstance(node, ast.If) and node.lineno < earliest_attn_build:
            test_src = ast.get_source_segment(src, node.test) or ""
            if "FULL" in test_src and ("cg_mode" in test_src or "cudagraph" in test_src.lower()):
                for child in ast.walk(node):
                    if isinstance(child, ast.Return) and child.lineno < earliest_attn_build:
                        assert False, (
                            "FULL cudagraph check returns before attention metadata "
                            "is built (BUG PRESENT)"
                        )


# [pr_diff] fail_to_pass
def test_attn_metadata_built_for_full_mode():
    """Attention metadata must be built for ALL cudagraph modes, including FULL.

    The build must not be inside a "not FULL" guard. Verifies that attn metadata
    is built before FULL cudagraph execution.
    """
    src, tree = _parse_file()
    propose = _find_method(tree, "EagleSpeculator", "propose")
    assert propose is not None, "propose() method not found in EagleSpeculator"

    # Collect fullgraph-related calls and attn build calls
    fullgraph_lines = []
    attn_build_lines = []
    for node in ast.walk(propose):
        if isinstance(node, ast.Call):
            name = _get_call_name(node)
            if name and "fullgraph" in name.lower():
                fullgraph_lines.append(node.lineno)
            if _is_attn_build_call(name):
                attn_build_lines.append(node.lineno)

    # Strategy A: fullgraph is called, attn build happens before it
    if fullgraph_lines:
        earliest_fullgraph = min(fullgraph_lines)
        before = [l for l in attn_build_lines if l < earliest_fullgraph]
        if before:
            return  # PASS
        # Check if a helper with attn build is called before fullgraph
        for node in ast.walk(propose):
            if isinstance(node, ast.Call) and node.lineno < earliest_fullgraph:
                name = _get_call_name(node)
                if name and _is_attn_build_call(name):
                    return  # PASS
        assert False, "Attention metadata not built before fullgraph execution"

    # Strategy B: no direct fullgraph call — acceptable if attn build exists
    if attn_build_lines:
        return  # PASS (code restructured)

    # Strategy C: dispatch + build pattern (heavy restructuring)
    dispatch_found = False
    build_found = False
    for node in ast.walk(propose):
        if isinstance(node, ast.Call):
            name = _get_call_name(node)
            if name:
                nl = name.lower()
                if "dispatch" in nl or "sync" in nl:
                    dispatch_found = True
                if ("build" in nl or "prepare" in nl) and \
                   len(node.args) + len(node.keywords) >= 3:
                    build_found = True

    assert dispatch_found and build_found, \
        "No attn metadata build found in any recognizable pattern"


# [pr_diff] pass_to_pass
def test_slot_mappings_computed():
    """Slot mappings must be computed in propose() for all cudagraph modes.

    The bug also causes stale slot mappings; the fix must rebuild them.
    """
    _, tree = _parse_file()
    propose = _find_method(tree, "EagleSpeculator", "propose")
    assert propose is not None, "propose() method not found in EagleSpeculator"

    slot_calls = []
    for node in ast.walk(propose):
        if isinstance(node, ast.Call):
            name = _get_call_name(node)
            if name and "slot_mapping" in name.lower():
                slot_calls.append(node.lineno)

    assert slot_calls, "No slot mapping computation found in propose()"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_core_class_structure():
    """EagleSpeculator class retains all required methods."""
    _, tree = _parse_file()

    eagle_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "EagleSpeculator":
            eagle_class = node
            break

    assert eagle_class is not None, "EagleSpeculator class not found"

    methods = {n.name for n in ast.walk(eagle_class) if isinstance(n, ast.FunctionDef)}
    required = {"propose", "generate_draft", "capture_model", "run_model", "load_model", "set_attn"}
    missing = required - methods
    assert not missing, f"Missing methods: {missing}"


# [static] pass_to_pass
def test_propose_not_stub():
    """propose() must have real logic — conditionals, calls, self attribute access."""
    _, tree = _parse_file()
    propose = _find_method(tree, "EagleSpeculator", "propose")
    assert propose is not None, "propose() not found"

    body_stmts = len(propose.body)
    assert body_stmts >= 15, f"propose() has only {body_stmts} statements — likely stubbed"

    ifs = sum(1 for n in ast.walk(propose) if isinstance(n, ast.If))
    assert ifs >= 3, f"propose() has only {ifs} if-statements — likely stubbed"

    calls = sum(1 for n in ast.walk(propose) if isinstance(n, ast.Call))
    assert calls >= 8, f"propose() has only {calls} calls — likely stubbed"

    # Must access self attributes (real logic, not synthetic stubs)
    self_attrs = set()
    for n in ast.walk(propose):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "self":
            self_attrs.add(n.attr)

    required_attrs = {"input_buffers", "block_tables", "draft_tokens"}
    found = required_attrs & self_attrs
    assert len(found) >= 2, f"propose() only references {found} of {required_attrs} — likely stubbed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:42 @ 44a6528028ad79951de08b6a7928f6c05788d00d
def test_no_bare_pip():
    """No bare pip usage in modified file (AGENTS.md:42)."""
    src = FILE.read_text()
    for i, line in enumerate(src.splitlines(), 1):
        stripped = line.strip()
        assert not stripped.startswith("pip install"), \
            f"Bare pip usage at line {i}: {stripped}"


# [static] pass_to_pass
def test_no_wildcard_imports():
    """No wildcard imports in modified file."""
    _, tree = _parse_file()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                assert alias.name != "*", f"Wildcard import from {node.module}"
