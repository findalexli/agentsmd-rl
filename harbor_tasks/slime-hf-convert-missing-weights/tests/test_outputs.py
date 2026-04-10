"""
Task: slime-hf-convert-missing-weights
Repo: slime @ ce769774350ad70fe94f5ab17485177751793097
PR:   1812

Tests that save_tensors supports merging missing weights from an origin
HF checkpoint directory during Megatron-to-HF conversion.
"""

import subprocess
import sys
import os
import types
import json
import tempfile
import inspect
import unittest.mock as mock
from pathlib import Path

import torch
import safetensors
import safetensors.torch

REPO = "/workspace/slime"


# ---------------------------------------------------------------------------
# Module import with mocked heavy dependencies
# ---------------------------------------------------------------------------

def _import_convert_module():
    """Import tools/convert_torch_dist_to_hf.py with mocked slime/transformers."""
    mock_hf = types.ModuleType("slime.backends.megatron_utils.megatron_to_hf")
    mock_hf.convert_to_hf = lambda args, model_name, name, param: [(name, param)]
    mock_hf.remove_padding = lambda name, param, vocab_size: param

    saved = {}
    mocks = {
        "slime": types.ModuleType("slime"),
        "slime.backends": types.ModuleType("slime.backends"),
        "slime.backends.megatron_utils": types.ModuleType("slime.backends.megatron_utils"),
        "slime.backends.megatron_utils.megatron_to_hf": mock_hf,
        "transformers": mock.MagicMock(),
    }
    for k, v in mocks.items():
        saved[k] = sys.modules.get(k)
        sys.modules[k] = v

    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "convert_torch_dist_to_hf",
            os.path.join(REPO, "tools/convert_torch_dist_to_hf.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        for k, orig in saved.items():
            if orig is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = orig


_mod = _import_convert_module()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_safetensors_dir(tensors_dict, tmpdir, filename="origin.safetensors"):
    """Save a dict of {name: tensor} as a safetensors file in tmpdir."""
    safetensors.torch.save_file(tensors_dict, os.path.join(tmpdir, filename))


def _load_all_output_tensors(output_dir):
    """Load all tensors from the output safetensors files."""
    all_tensors = {}
    for f in sorted(os.listdir(output_dir)):
        if f.endswith(".safetensors"):
            loaded = safetensors.torch.load_file(os.path.join(output_dir, f))
            all_tensors.update(loaded)
    return all_tensors


def _call_save_tensors(state_dict, origin_hf_dir=None, chunk_size=10 * 1024**3):
    """Call save_tensors with mocked internals and CPU-safe safetensors patching."""
    args = mock.MagicMock()

    def mock_gnp(a, sd):
        for name, param in sd.items():
            yield name, param

    with tempfile.TemporaryDirectory() as output_dir:
        with mock.patch.object(_mod, "get_named_params", mock_gnp):
            _original_safe_open = safetensors.safe_open

            def _cpu_safe_open(*a, **kw):
                kw["device"] = "cpu"
                return _original_safe_open(*a, **kw)

            with mock.patch.object(safetensors, "safe_open", _cpu_safe_open):
                if origin_hf_dir is not None:
                    _mod.save_tensors(
                        args, "test_model", state_dict, output_dir,
                        chunk_size, vocab_size=None, origin_hf_dir=origin_hf_dir,
                    )
                else:
                    _mod.save_tensors(
                        args, "test_model", state_dict, output_dir,
                        chunk_size, vocab_size=None,
                    )

            tensors = _load_all_output_tensors(output_dir)
            index_path = os.path.join(output_dir, "model.safetensors.index.json")
            index = json.loads(Path(index_path).read_text()) if os.path.exists(index_path) else None
            return tensors, index


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    import py_compile

    py_compile.compile(
        os.path.join(REPO, "tools/convert_torch_dist_to_hf.py"), doraise=True
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI tests (gates)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Ruff linter passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        "pip install ruff -q 2>/dev/null && ruff check tools/convert_torch_dist_to_hf.py",
        cwd=REPO, capture_output=True, text=True, timeout=120, shell=True,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_black_format():
    """Black formatter check passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        "pip install black -q 2>/dev/null && black --check tools/convert_torch_dist_to_hf.py",
        cwd=REPO, capture_output=True, text=True, timeout=120, shell=True,
    )
    assert r.returncode == 0, f"Black check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_isort_check():
    """isort import order check passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        "pip install isort -q 2>/dev/null && isort --check-only --profile=black tools/convert_torch_dist_to_hf.py",
        cwd=REPO, capture_output=True, text=True, timeout=120, shell=True,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_plugin_generate_contracts():
    """Plugin generate contracts pass (pass_to_pass)."""
    deps = "pytest numpy packaging pyyaml omegaconf tqdm httpx pybase64 pylatexenc sympy aiohttp pillow"
    r = subprocess.run(
        f"pip install {deps} -q 2>/dev/null && pip install -e . --no-deps -q 2>/dev/null && python tests/plugin_contracts/test_plugin_generate_contracts.py",
        cwd=REPO, capture_output=True, text=True, timeout=120, shell=True,
    )
    assert r.returncode == 0, f"Plugin generate contracts failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_plugin_path_loading_contracts():
    """Plugin path loading contracts pass (pass_to_pass)."""
    deps = "pytest numpy packaging pyyaml omegaconf tqdm httpx pybase64 pylatexenc sympy aiohttp pillow"
    r = subprocess.run(
        f"pip install {deps} -q 2>/dev/null && pip install -e . --no-deps -q 2>/dev/null && python tests/plugin_contracts/test_plugin_path_loading_contracts.py",
        cwd=REPO, capture_output=True, text=True, timeout=120, shell=True,
    )
    assert r.returncode == 0, f"Plugin path loading contracts failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_plugin_rollout_contracts():
    """Plugin rollout contracts pass (pass_to_pass)."""
    deps = "pytest numpy packaging pyyaml omegaconf tqdm httpx pybase64 pylatexenc sympy aiohttp pillow"
    r = subprocess.run(
        f"pip install {deps} -q 2>/dev/null && pip install -e . --no-deps -q 2>/dev/null && python tests/plugin_contracts/test_plugin_rollout_contracts.py",
        cwd=REPO, capture_output=True, text=True, timeout=120, shell=True,
    )
    assert r.returncode == 0, f"Plugin rollout contracts failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_save_tensors_accepts_origin_hf_dir():
    """save_tensors function must accept an origin_hf_dir parameter."""
    sig = inspect.signature(_mod.save_tensors)
    params = list(sig.parameters.keys())
    assert "origin_hf_dir" in params, (
        f"save_tensors missing origin_hf_dir parameter. Got: {params}"
    )


# [pr_diff] fail_to_pass
def test_missing_weights_included_from_origin():
    """Weights present in origin HF checkpoint but absent from Megatron
    conversion must appear in the final output."""
    state_dict = {"megatron_weight": torch.randn(4, 4)}

    with tempfile.TemporaryDirectory() as origin_dir:
        _create_safetensors_dir(
            {
                "megatron_weight": torch.randn(4, 4),
                "hf_only_weight_a": torch.randn(8, 8),
                "hf_only_weight_b": torch.randn(2, 2),
            },
            origin_dir,
        )
        tensors, index = _call_save_tensors(state_dict, origin_hf_dir=origin_dir)

        assert "megatron_weight" in tensors, "Converted weight must still be present"
        assert "hf_only_weight_a" in tensors, "Missing weight A not added from origin"
        assert "hf_only_weight_b" in tensors, "Missing weight B not added from origin"
        assert tensors["hf_only_weight_a"].shape == (8, 8)
        assert tensors["hf_only_weight_b"].shape == (2, 2)

        assert "hf_only_weight_a" in index["weight_map"], "Missing weight A not in index"
        assert "hf_only_weight_b" in index["weight_map"], "Missing weight B not in index"


# [pr_diff] fail_to_pass
def test_converted_weights_not_duplicated():
    """Weights already produced by the Megatron conversion must NOT be
    overwritten by values from the origin checkpoint."""
    converted_val = torch.ones(3, 3) * 42.0
    state_dict = {"shared_weight": converted_val.clone()}

    with tempfile.TemporaryDirectory() as origin_dir:
        _create_safetensors_dir(
            {
                "shared_weight": torch.zeros(3, 3),  # different values
                "extra_weight": torch.randn(5, 5),
            },
            origin_dir,
        )
        tensors, _ = _call_save_tensors(state_dict, origin_hf_dir=origin_dir)

        assert torch.allclose(tensors["shared_weight"], converted_val), (
            "shared_weight must keep converted values, not be replaced by origin"
        )
        assert "extra_weight" in tensors, "Non-overlapping origin weight must be added"


# [pr_diff] fail_to_pass
def test_add_missing_from_origin_hf_cli_flag():
    """CLI parser must include the --add-missing-from-origin-hf flag."""
    setup = (
        "import sys, types, unittest.mock;"
        "sys.modules['slime']=types.ModuleType('s');"
        "sys.modules['slime.backends']=types.ModuleType('sb');"
        "sys.modules['slime.backends.megatron_utils']=types.ModuleType('sm');"
        "hf=types.ModuleType('hf');"
        "hf.convert_to_hf=lambda *a:[];"
        "hf.remove_padding=lambda *a:None;"
        "sys.modules['slime.backends.megatron_utils.megatron_to_hf']=hf;"
        "sys.modules['transformers']=unittest.mock.MagicMock();"
        "sys.argv=['x','--help'];"
        "exec(open('tools/convert_torch_dist_to_hf.py').read())"
    )
    r = subprocess.run(
        ["python3", "-c", setup],
        cwd=REPO, capture_output=True, timeout=30,
    )
    stdout = r.stdout.decode()
    assert "--add-missing-from-origin-hf" in stdout, (
        f"--add-missing-from-origin-hf not found in help:\n{stdout}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_multiple_origin_safetensors_shards():
    """Missing weights spread across multiple .safetensors shard files in the
    origin directory must all be included."""
    state_dict = {"base_w": torch.randn(4, 4)}

    with tempfile.TemporaryDirectory() as origin_dir:
        _create_safetensors_dir({"shard1_w": torch.randn(3, 3)}, origin_dir, "shard-001.safetensors")
        _create_safetensors_dir({"shard2_w": torch.randn(6, 6)}, origin_dir, "shard-002.safetensors")

        tensors, _ = _call_save_tensors(state_dict, origin_hf_dir=origin_dir)

        assert "base_w" in tensors
        assert "shard1_w" in tensors, "Weight from shard-001 not included"
        assert "shard2_w" in tensors, "Weight from shard-002 not included"


# ---------------------------------------------------------------------------
# Pass-to-pass — backward compatibility
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_save_tensors_without_origin():
    """save_tensors must still work when origin_hf_dir is not provided."""
    state_dict = {
        "layer.0.weight": torch.randn(10, 10),
        "layer.1.weight": torch.randn(5, 5),
    }
    tensors, index = _call_save_tensors(state_dict, origin_hf_dir=None)

    assert "layer.0.weight" in tensors
    assert "layer.1.weight" in tensors
    assert index is not None
    assert "weight_map" in index
    assert "layer.0.weight" in index["weight_map"]
    assert "layer.1.weight" in index["weight_map"]
