"""Behavioral tests for T5Gemma2 prepare_decoder_input_ids_from_labels fix."""

from __future__ import annotations

import inspect
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO = Path("/workspace/transformers")
MODEL_DIR = REPO / "src" / "transformers" / "models" / "t5gemma2"


def _import_pretrained_class():
    """Import T5Gemma2PreTrainedModel from the editable install."""
    sys.path.insert(0, str(REPO / "src"))
    from transformers.models.t5gemma2.modeling_t5gemma2 import (
        T5Gemma2PreTrainedModel,
    )

    return T5Gemma2PreTrainedModel


def _make_mock_self(bos_token_id: int, pad_token_id: int):
    mock_self = MagicMock()
    mock_self.config.decoder.bos_token_id = bos_token_id
    mock_self.config.decoder.pad_token_id = pad_token_id
    return mock_self


# --- f2p tests: should fail at base, pass at gold ----------------------------

def test_method_accepts_labels_kwarg_in_modeling_file():
    """DataCollatorForSeq2Seq calls the method with labels=... kwarg.

    On the broken base, the parameter is named input_ids so the kwarg
    call raises TypeError. On the fix, labels is the parameter name.
    """
    import torch

    cls = _import_pretrained_class()
    mock_self = _make_mock_self(bos_token_id=0, pad_token_id=1)
    labels = torch.tensor([[10, 20, 30, 40]])

    result = cls.prepare_decoder_input_ids_from_labels(mock_self, labels=labels)
    assert result.tolist() == [[0, 10, 20, 30]]


def test_method_accepts_labels_kwarg_in_modular_file():
    """Modular file must also use labels= kwarg (transformers code-sync rule).

    huggingface/transformers requires modular_<name>.py and
    modeling_<name>.py to be kept consistent — since the fix updates the
    modeling file, the modular source must match.
    """
    modular_path = MODEL_DIR / "modular_t5gemma2.py"
    src = modular_path.read_text()
    # Compile and exec the source into a namespace, then introspect.
    # This avoids importing the full modular machinery (it isn't designed
    # to be importable).
    import re

    m = re.search(
        r"def prepare_decoder_input_ids_from_labels\(self, ([A-Za-z_][A-Za-z_0-9]*)",
        src,
    )
    assert m is not None, "method not found in modular_t5gemma2.py"
    param = m.group(1)
    assert param == "labels", (
        f"modular_t5gemma2.py prepare_decoder_input_ids_from_labels uses "
        f"first parameter {param!r}, but it must be 'labels' to match the "
        f"DataCollatorForSeq2Seq call site"
    )


def test_signature_uses_labels_parameter():
    """inspect.signature confirms the runtime parameter is named labels."""
    cls = _import_pretrained_class()
    sig = inspect.signature(cls.prepare_decoder_input_ids_from_labels)
    params = list(sig.parameters)
    assert params == ["self", "labels"], (
        f"expected (self, labels), got {params}"
    )


def test_shift_correctness_across_inputs():
    """The shift behavior must be unchanged: shift right + BOS + replace -100."""
    import torch

    cls = _import_pretrained_class()

    cases = [
        # (bos, pad, input, expected)
        (0, 1, [[5, 6, 7]], [[0, 5, 6]]),
        (2, 9, [[10, 20, 30, 40]], [[2, 10, 20, 30]]),
        # -100 in a non-leading position becomes pad after shifting
        (0, 7, [[1, 2, -100, 4]], [[0, 1, 2, 7]]),
        # batch dim
        (3, 5, [[8, 9], [10, 11]], [[3, 8], [3, 10]]),
    ]
    for bos, pad, inp, expected in cases:
        mock_self = _make_mock_self(bos_token_id=bos, pad_token_id=pad)
        result = cls.prepare_decoder_input_ids_from_labels(
            mock_self, labels=torch.tensor(inp)
        )
        assert result.tolist() == expected, (
            f"shift mismatch for bos={bos} pad={pad} input={inp}: got "
            f"{result.tolist()}, expected {expected}"
        )


def test_modeling_file_uses_labels_parameter_name_in_body():
    """The function body must reference `labels`, not `input_ids`, to be
    coherent with the new parameter name. Stops a stub fix where only the
    signature is renamed but the body still uses input_ids (NameError)."""
    import torch

    cls = _import_pretrained_class()
    mock_self = _make_mock_self(bos_token_id=0, pad_token_id=1)
    labels = torch.tensor([[3, 4, 5]])
    # Will raise NameError if body still uses input_ids while param is labels.
    result = cls.prepare_decoder_input_ids_from_labels(mock_self, labels=labels)
    assert result.tolist() == [[0, 3, 4]]


# --- p2p tests: pre-existing repo behavior that must keep passing ------------

def test_repo_imports_clean():
    """transformers package must still import without error after the fix."""
    r = subprocess.run(
        [sys.executable, "-c", "import transformers"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"import failed:\n{r.stderr[-800:]}"


def test_data_collator_passes_labels_kwarg():
    """Sanity-check the call site DataCollatorForSeq2Seq uses (assertion that
    motivated the PR). This is a behavioral grep against the upstream caller
    file at the base commit, NOT against the file the agent edits — so it
    cannot be gamed by editing the target."""
    collator_path = REPO / "src" / "transformers" / "data" / "data_collator.py"
    src = collator_path.read_text()
    assert "prepare_decoder_input_ids_from_labels(labels=" in src, (
        "DataCollatorForSeq2Seq must still call the method with labels= kwarg "
        "(this confirms the call-site that the fix targets is unchanged)"
    )


def test_ci_regression():
    """Repo's own test suite for the affected model must still pass.

    Runs the existing test_shift_right test from the upstream test file,
    which exercises prepare_decoder_input_ids_from_labels with positional
    args. This is the CI gate that ran on the original PR — it must keep
    passing after the parameter rename (the shift behavior is preserved).
    """
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/models/t5gemma2/test_modeling_t5gemma2.py",
            "-k", "test_shift_right",
            "--override-ini=addopts=",
            "-o", "filterwarnings=ignore",
            "--no-header", "-q",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"CI regression test failed (returncode={r.returncode}):\n"
        f"stdout:\n{r.stdout[-800:]}\nstderr:\n{r.stderr[-800:]}"
    )
