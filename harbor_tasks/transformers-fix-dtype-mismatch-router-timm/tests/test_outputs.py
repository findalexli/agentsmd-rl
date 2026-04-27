"""Tests for the dtype-mismatch fix in SwitchTransformers and TimmWrapper."""
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/transformers")
SRC = REPO / "src"

# Make the editable transformers source importable.
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import torch  # noqa: E402

# ---------------------------------------------------------------------------
# Behavioral fail-to-pass tests (the bug must trigger at base, fix unblocks).
# ---------------------------------------------------------------------------

def _make_router(num_experts=4, hidden_size=8):
    """Build a SwitchTransformersTop1Router with a minimal config."""
    from transformers.models.switch_transformers.configuration_switch_transformers import (
        SwitchTransformersConfig,
    )
    from transformers.models.switch_transformers.modeling_switch_transformers import (
        SwitchTransformersTop1Router,
    )

    config = SwitchTransformersConfig(
        num_experts=num_experts,
        expert_capacity=num_experts,
        d_model=hidden_size,
        router_bias=False,
        router_jitter_noise=0.0,
        router_ignore_padding_tokens=False,
        router_dtype="float32",
    )
    return SwitchTransformersTop1Router(config), config


def test_switch_transformers_router_module_cast_to_bfloat16():
    """When the router module is cast to bfloat16, forward must succeed.

    Repro:
      router = SwitchTransformersTop1Router(config)
      router = router.to(torch.bfloat16)         # casts classifier weights
      router(hidden_states)                       # raises dtype mismatch at base
    """
    router, _ = _make_router()
    router = router.to(torch.bfloat16)
    router.eval()

    # router.dtype is set in __init__ from config.router_dtype ("float32")
    # — it does NOT track .to(bf16). This divergence is the bug surface.
    assert router.dtype == torch.float32

    hidden = torch.randn(2, 4, 8, dtype=torch.float32)
    with torch.no_grad():
        probs, expert_index, logits = router(hidden)

    assert probs.shape == (2, 4, 1)
    assert expert_index.shape == (2, 4, 1, 4)
    assert logits.shape == (2, 4, 1)


def test_switch_transformers_router_module_cast_to_float16():
    """Same defect, with float16 instead of bfloat16 — must also work after fix."""
    router, _ = _make_router(num_experts=8, hidden_size=16)
    router = router.to(torch.float16)
    router.eval()

    hidden = torch.randn(1, 3, 16, dtype=torch.float32)
    with torch.no_grad():
        probs, expert_index, logits = router(hidden)

    assert probs.shape == (1, 3, 1)
    assert torch.isfinite(probs).all().item()


def test_switch_transformers_router_input_dtype_preserved():
    """Output router_probs must match input dtype (selective-precision contract)."""
    router, _ = _make_router()
    router = router.to(torch.bfloat16)
    router.eval()

    hidden_bf16 = torch.randn(2, 4, 8, dtype=torch.bfloat16)
    with torch.no_grad():
        probs, _, _ = router(hidden_bf16)
    # router_probs are softmax cast back to input_dtype
    assert probs.dtype == torch.bfloat16


def test_timm_wrapper_module_cast_to_bfloat16():
    """TimmWrapperModel cast to bfloat16 must accept default-dtype pixel_values.

    Repro:
      model = TimmWrapperModel(config).to(torch.bfloat16).eval()
      model(pixel_values_float32)        # raises dtype mismatch at base
    """
    from transformers import TimmWrapperConfig, TimmWrapperModel

    config = TimmWrapperConfig(architecture="resnet18", model_args={})
    model = TimmWrapperModel(config=config).to(torch.bfloat16).eval()
    pixel_values = torch.randn(1, 3, 64, 64, dtype=torch.float32)

    with torch.no_grad():
        outputs = model(pixel_values)

    last_hidden_state = outputs.last_hidden_state
    assert last_hidden_state.dtype == torch.bfloat16
    assert not torch.isnan(last_hidden_state).any().item()


def test_timm_wrapper_pixel_values_explicitly_cast_to_model_dtype():
    """The wrapper must promote pixel_values to model dtype, not just device."""
    from transformers import TimmWrapperConfig, TimmWrapperModel

    config = TimmWrapperConfig(architecture="resnet18", model_args={})
    model = TimmWrapperModel(config=config).to(torch.float16).eval()
    pixel_values = torch.randn(1, 3, 64, 64, dtype=torch.float32)

    with torch.no_grad():
        outputs = model(pixel_values)

    # If the bug were present, the bfloat16 weights would error before producing output.
    # A correctly fixed wrapper produces fp16 output here.
    assert outputs.last_hidden_state.dtype == torch.float16


# ---------------------------------------------------------------------------
# Agent-config (CLAUDE.md / AGENTS.md) compliance: modular sync rule.
# ---------------------------------------------------------------------------

def _extract_router_forward_body(text: str) -> list[str]:
    """Return the SwitchTransformersTop1Router.forward body (executable lines only)."""
    lines = text.splitlines()
    in_class = False
    in_forward = False
    forward_indent = None
    body: list[str] = []
    for line in lines:
        stripped = line.strip()
        if line.startswith("class SwitchTransformersTop1Router"):
            in_class = True
            continue
        if in_class and not in_forward and re.match(r"^\s+def\s+forward\s*\(", line):
            in_forward = True
            forward_indent = len(line) - len(line.lstrip())
            continue
        if in_forward:
            if not stripped:
                body.append("")
                continue
            indent = len(line) - len(line.lstrip())
            if indent <= forward_indent and stripped:
                break
            # Strip comment-only lines & docstring lines for robustness against
            # minor wording differences between modular & modeling.
            if stripped.startswith("#"):
                continue
            body.append(stripped)
    # Drop the leading docstring (triple-quoted block).
    cleaned: list[str] = []
    state = "before_doc"   # before_doc -> in_doc -> after_doc
    for s in body:
        if state == "before_doc":
            if s.startswith('"""') or s.startswith('r"""'):
                # one-line docstring? "..."""\n
                if s.count('"""') >= 2 and len(s) > 3:
                    state = "after_doc"
                else:
                    state = "in_doc"
                continue
            # Not a docstring → skip leading blank, fall through.
            if not s:
                continue
            state = "after_doc"
        if state == "in_doc":
            if '"""' in s:
                state = "after_doc"
            continue
        if s:
            cleaned.append(s)
    return cleaned


def test_modular_and_modeling_router_forward_bodies_match():
    """CLAUDE.md / AGENTS.md: when a `modular_*.py` exists, the modular file is
    the source of truth — code changes must be reflected in both modular and
    the generated modeling file (e.g. via `make fix-repo`). Editing only one
    leaves the pair out of sync.

    This test extracts the router's forward body from each file and asserts
    they are line-equivalent (ignoring comments/whitespace), so any fix the
    agent applies must appear in both files.

    Source: CLAUDE.md §"Copies and Modular Models", base commit
    ade7a05a42bf53b183bb78c181743be063c5ff14.
    """
    sw_dir = SRC / "transformers" / "models" / "switch_transformers"
    modular = (sw_dir / "modular_switch_transformers.py").read_text()
    modeling = (sw_dir / "modeling_switch_transformers.py").read_text()

    modular_body = _extract_router_forward_body(modular)
    modeling_body = _extract_router_forward_body(modeling)

    assert modular_body, "Could not extract router.forward body from modular file"
    assert modeling_body, "Could not extract router.forward body from modeling file"
    assert modular_body == modeling_body, (
        "modular_switch_transformers.py and modeling_switch_transformers.py "
        "have diverging SwitchTransformersTop1Router.forward bodies. Per "
        "CLAUDE.md, the modular file is the source of truth and the modeling "
        "file is generated — they must stay in sync.\n"
        f"\nmodular:\n  " + "\n  ".join(modular_body)
        + f"\n\nmodeling:\n  " + "\n  ".join(modeling_body)
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: repo-level sanity that should pass before AND after the fix.
# ---------------------------------------------------------------------------

def test_transformers_package_imports():
    """`import transformers` must work — guards against accidental syntax breakage."""
    r = subprocess.run(
        [sys.executable, "-c", "import transformers; print(transformers.__version__)"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"transformers import failed:\n{r.stderr}"


def test_switch_transformers_module_imports():
    """The patched module must remain importable."""
    r = subprocess.run(
        [
            sys.executable,
            "-c",
            "from transformers.models.switch_transformers.modeling_switch_transformers "
            "import SwitchTransformersTop1Router; print('ok')",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"import failed:\n{r.stderr}"


def test_timm_wrapper_module_imports():
    """The patched timm_wrapper module must remain importable."""
    r = subprocess.run(
        [
            sys.executable,
            "-c",
            "from transformers.models.timm_wrapper.modeling_timm_wrapper "
            "import TimmWrapperModel; print('ok')",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"import failed:\n{r.stderr}"


def test_ruff_format_clean_on_changed_files():
    """CLAUDE.md mandates `make style` (ruff) before opening a PR.

    Source: CLAUDE.md §"Useful commands", base commit
    ade7a05a42bf53b183bb78c181743be063c5ff14.
    """
    files = [
        str(
            SRC
            / "transformers"
            / "models"
            / "switch_transformers"
            / "modeling_switch_transformers.py"
        ),
        str(
            SRC
            / "transformers"
            / "models"
            / "switch_transformers"
            / "modular_switch_transformers.py"
        ),
        str(
            SRC
            / "transformers"
            / "models"
            / "timm_wrapper"
            / "modeling_timm_wrapper.py"
        ),
    ]
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", *files],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if r.returncode == 127 or "No module named ruff" in (r.stderr or ""):
        pytest.skip("ruff not installed in this environment")
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout}\n{r.stderr}"
