"""
Task: slime-misc-bugfix-cleanup
Repo: THUDM/slime @ 64e1e68f524e1da6ca646606c22e785eeb845268
PR:   1756

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/slime"
CHECKPOINT = f"{REPO}/slime/backends/megatron_utils/checkpoint.py"
DATA = f"{REPO}/slime/backends/megatron_utils/data.py"
PROCESSING = f"{REPO}/slime/utils/processing_utils.py"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess in the repo directory."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# Shared preamble: extracts build_processor_kwargs as callable fn()
_EXTRACT_PROCESSOR = """\
import ast
from pathlib import Path

src = Path("/workspace/slime/slime/utils/processing_utils.py").read_text()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "build_processor_kwargs":
        func_src = ast.get_source_segment(src, node)
        ns = {}
        exec(func_src, ns)
        fn = ns["build_processor_kwargs"]
        break
else:
    raise AssertionError("build_processor_kwargs not found")
"""


def _extract_build_processor_kwargs():
    """Extract and exec build_processor_kwargs from source (for p2p tests)."""
    src = Path(PROCESSING).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "build_processor_kwargs":
            func_src = ast.get_source_segment(src, node)
            assert func_src is not None, "Could not extract function source"
            ns = {}
            exec(func_src, ns)
            return ns["build_processor_kwargs"]
    assert False, "build_processor_kwargs not found"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified files must parse without errors."""
    for path in [CHECKPOINT, DATA, PROCESSING]:
        src = Path(path).read_text()
        ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_checkpoint_uses_load_path():
    """_load_checkpoint_hf must pass load_path (not args.hf_checkpoint) to from_hf_pretrained."""
    r = _run_py("""\
import ast
from pathlib import Path

src = Path("/workspace/slime/slime/backends/megatron_utils/checkpoint.py").read_text()
tree = ast.parse(src)

func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_load_checkpoint_hf":
        func = node
        break
assert func is not None, "_load_checkpoint_hf not found"

found_call = False
for node in ast.walk(func):
    if isinstance(node, ast.Call):
        if not (isinstance(node.func, ast.Attribute) and node.func.attr == "from_hf_pretrained"):
            continue
        found_call = True
        assert node.args, "from_hf_pretrained has no positional args"
        first = node.args[0]
        if isinstance(first, ast.Attribute):
            assert not (
                isinstance(first.value, ast.Name)
                and first.value.id == "args"
                and first.attr == "hf_checkpoint"
            ), "Still uses args.hf_checkpoint -- bug not fixed"
        if isinstance(first, ast.Name):
            assert first.id == "load_path", f"Expected load_path, got {first.id}"
        break

assert found_call, "from_hf_pretrained call not found"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_data_no_multimodal_num_items():
    """get_batch multimodal processing must not set multimodal_num_items on batch."""
    r = _run_py("""\
import ast, sys, types, textwrap
from pathlib import Path

# Minimal torch mock for executing the multimodal processing block
torch = types.ModuleType('torch')
class _FT:
    def __init__(self, n=3):
        self._n = n
    def size(self, dim):
        return self._n
def _cat(tensors, dim=0):
    return _FT(sum(t._n for t in tensors))
torch.cat = _cat
sys.modules['torch'] = torch

src = Path("/workspace/slime/slime/backends/megatron_utils/data.py").read_text()
tree = ast.parse(src)

func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_batch":
        func = node
        break
assert func is not None, "get_batch not found"
func_src = ast.get_source_segment(src, func)

# Extract the multimodal processing block from get_batch
lines = func_src.split('\\n')
start = None
for i, line in enumerate(lines):
    if 'multimodal_train_inputs = batch.get' in line:
        start = i
        break
assert start is not None, "multimodal processing block not found"

end = len(lines)
for i in range(start + 1, len(lines)):
    if lines[i].strip().startswith('return '):
        end = i
        break

block = textwrap.dedent('\\n'.join(lines[start:end]))

# Execute with mock multimodal data
batch = {
    "multimodal_train_inputs": [
        {"image": _FT(3), "audio": _FT(2)},
        {"image": _FT(4), "audio": _FT(5)},
    ]
}
exec(block)

assert "multimodal_num_items" not in batch, \\
    f"batch still has multimodal_num_items: {list(batch.keys())}"
assert "multimodal_train_inputs" in batch
assert isinstance(batch["multimodal_train_inputs"], dict)
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_processor_kwargs_mm_token_type_ids_none_input():
    """build_processor_kwargs(None) must include return_mm_token_type_ids=False in text_kwargs."""
    r = _run_py(_EXTRACT_PROCESSOR + """\
result = fn(None)
tk = result["text_kwargs"]
assert tk.get("return_mm_token_type_ids") is False, f"not False: {tk}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_processor_kwargs_mm_token_type_ids_with_existing():
    """build_processor_kwargs preserves existing text_kwargs while adding return_mm_token_type_ids."""
    r = _run_py(_EXTRACT_PROCESSOR + """\
result = fn({"text_kwargs": {"padding": True, "truncation": True}})
tk = result["text_kwargs"]
assert tk.get("return_mm_token_type_ids") is False
assert tk.get("padding") is True, "Existing padding kwarg lost"
assert tk.get("truncation") is True, "Existing truncation kwarg lost"
assert tk.get("return_tensors") is None, "return_tensors should be None"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_processor_kwargs_mm_token_type_ids_empty_input():
    """build_processor_kwargs({}) must include return_mm_token_type_ids=False."""
    r = _run_py(_EXTRACT_PROCESSOR + """\
result = fn({})
tk = result["text_kwargs"]
assert tk.get("return_mm_token_type_ids") is False, f"not False with empty dict: {tk}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_processor_kwargs_overrides_existing_mm_token_type_ids():
    """If text_kwargs has return_mm_token_type_ids=True, it must be overridden to False."""
    r = _run_py(_EXTRACT_PROCESSOR + """\
result = fn({"text_kwargs": {"return_mm_token_type_ids": True, "max_length": 512}})
tk = result["text_kwargs"]
assert tk["return_mm_token_type_ids"] is False, "return_mm_token_type_ids=True not overridden"
assert tk["max_length"] == 512, "Existing max_length kwarg lost"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — preserved behavior + anti-stub
# ---------------------------------------------------------------------------

def test_data_multimodal_data_preserved():
    """get_batch must still create multimodal_data dict and assign to batch['multimodal_train_inputs']."""
    src = Path(DATA).read_text()
    tree = ast.parse(src)

    func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_batch":
            func = node
            break
    assert func is not None, "get_batch not found"

    has_mm_data_init = False
    has_batch_assign = False

    for node in ast.walk(func):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "multimodal_data":
                    has_mm_data_init = True
                if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                    if target.value.id == "batch" and isinstance(target.slice, ast.Constant):
                        if target.slice.value == "multimodal_train_inputs":
                            has_batch_assign = True

    assert has_mm_data_init, "multimodal_data dict not initialized"
    assert has_batch_assign, "batch['multimodal_train_inputs'] not set from multimodal_data"


def test_processor_kwargs_modality_forced():
    """build_processor_kwargs still sets return_tensors='pt' for modality kwargs."""
    fn = _extract_build_processor_kwargs()
    for input_val in [None, {"images_kwargs": {"size": 224}}]:
        result = fn(input_val)
        for key in ("audio_kwargs", "images_kwargs", "videos_kwargs"):
            assert key in result, f"{key} missing from result"
            assert result[key]["return_tensors"] == "pt", f"{key} missing return_tensors=pt"


def test_processor_kwargs_return_tensors_none_for_text():
    """text_kwargs must have return_tensors=None (not 'pt')."""
    fn = _extract_build_processor_kwargs()
    for input_val in [None, {}, {"text_kwargs": {"padding": True}}]:
        result = fn(input_val)
        assert result["text_kwargs"]["return_tensors"] is None, \
            f"text_kwargs return_tensors should be None, got {result['text_kwargs']['return_tensors']}"


def test_not_stub():
    """Modified functions must have meaningful body (not just pass/return None)."""
    checks = [
        (CHECKPOINT, "_load_checkpoint_hf"),
        (DATA, "get_batch"),
        (PROCESSING, "build_processor_kwargs"),
    ]
    for path, func_name in checks:
        tree = ast.parse(Path(path).read_text())
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                found = True
                real = [s for s in node.body if not isinstance(s, ast.Pass)]
                real = [s for s in real
                        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)
                                and isinstance(s.value.value, str))]
                assert len(real) >= 3, f"{func_name} appears to be a stub ({len(real)} stmts)"
                break
        assert found, f"{func_name} not found in {path}"
