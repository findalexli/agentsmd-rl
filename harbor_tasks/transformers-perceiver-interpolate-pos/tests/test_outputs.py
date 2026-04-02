"""
Task: transformers-perceiver-interpolate-pos
Repo: huggingface/transformers @ c532659b8734b88d2bbaac2542c2a5a8b525f3f7
PR:   44899

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/transformers"
TARGET = Path(REPO) / "src/transformers/models/perceiver/modeling_perceiver.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    src = TARGET.read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interpolate_to_target_dims():
    """Interpolating from 4x4 to 8x8 produces 64 positions, not 16."""
    import torch
    from transformers.models.perceiver.modeling_perceiver import (
        PerceiverTrainablePositionEncoding,
    )

    num_channels = 64
    index_dims = (4, 4)  # 16 source positions

    pe = PerceiverTrainablePositionEncoding(
        index_dims=index_dims, num_channels=num_channels
    )
    pos_emb = pe.position_embeddings  # (16, 64)

    result = pe.interpolate_pos_encoding(pos_emb, height=8, width=8)

    assert result.shape[0] == 64, (
        f"Expected 64 positions (8x8), got {result.shape[0]}"
    )
    assert result.shape[1] == num_channels


# [pr_diff] fail_to_pass
def test_interpolate_multiple_resolutions():
    """Interpolation works for varied target sizes including non-square."""
    import torch
    from transformers.models.perceiver.modeling_perceiver import (
        PerceiverTrainablePositionEncoding,
    )

    num_channels = 32
    index_dims = (2, 2)  # 4 source positions

    pe = PerceiverTrainablePositionEncoding(
        index_dims=index_dims, num_channels=num_channels
    )
    pos_emb = pe.position_embeddings

    cases = [
        (4, 4, 16),
        (6, 6, 36),
        (8, 4, 32),  # non-square
        (3, 5, 15),  # non-square, odd
    ]
    for h, w, expected in cases:
        result = pe.interpolate_pos_encoding(pos_emb, h, w)
        assert result.shape[0] == expected, (
            f"target ({h}x{w}): expected {expected} positions, got {result.shape[0]}"
        )
        assert result.shape[1] == num_channels


# [pr_diff] fail_to_pass
def test_interpolate_values_change():
    """Interpolated embeddings differ from source when target dims differ."""
    import torch
    from transformers.models.perceiver.modeling_perceiver import (
        PerceiverTrainablePositionEncoding,
    )

    pe = PerceiverTrainablePositionEncoding(index_dims=(4, 4), num_channels=32)
    pos_emb = pe.position_embeddings  # (16, 32)

    result = pe.interpolate_pos_encoding(pos_emb, height=8, width=8)  # (64, 32)

    # On the buggy code, output has the same number of positions as input (16)
    # because it interpolates to the source dims, not the target dims.
    # On the fixed code, output has 64 positions.
    assert result.shape[0] != pos_emb.shape[0], (
        f"Output has same count as input ({result.shape[0]}) — interpolation is a no-op"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_perceiver_imports():
    """Core perceiver classes import successfully."""
    from transformers.models.perceiver.modeling_perceiver import (
        PerceiverTrainablePositionEncoding,
        PerceiverForImageClassificationLearned,
        PerceiverModel,
    )

    assert callable(PerceiverTrainablePositionEncoding)
    assert callable(PerceiverForImageClassificationLearned)
    assert callable(PerceiverModel)


# [static] pass_to_pass
def test_not_stub():
    """Modified file retains substantial content (not replaced with a stub)."""
    src = TARGET.read_text()
    lines = src.splitlines()

    assert len(lines) >= 500, f"File has only {len(lines)} lines — looks like a stub"
    assert "class PerceiverTrainablePositionEncoding" in src
    for method in ("interpolate_pos_encoding", "forward", "__init__"):
        assert f"def {method}(" in src, f"Method {method} missing"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:15 @ c532659b8734b88d2bbaac2542c2a5a8b525f3f7
def test_ruff_lint_changed_lines():
    """Agent's changes must not introduce new ruff lint violations."""
    # Get git diff to find changed line numbers, then only check those
    import re

    diff_r = subprocess.run(
        ["git", "diff", "HEAD", "--unified=0", "--", str(TARGET)],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    # If no diff (file unchanged), nothing to check
    if not diff_r.stdout.strip():
        return

    # Parse @@ hunk headers to find changed line ranges
    changed_lines = set()
    for m in re.finditer(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", diff_r.stdout):
        start = int(m.group(1))
        count = int(m.group(2)) if m.group(2) else 1
        for i in range(start, start + count):
            changed_lines.add(i)

    if not changed_lines:
        return

    # Run ruff on the whole file and filter to changed lines only
    r = subprocess.run(
        ["ruff", "check", "--select", "E,W", "--output-format", "text", str(TARGET)],
        capture_output=True,
        text=True,
    )
    if r.returncode == 0:
        return  # No violations at all

    # Filter ruff output to only lines the agent changed
    violations = []
    for line in r.stdout.splitlines():
        m2 = re.match(r".*:(\d+):\d+:", line)
        if m2 and int(m2.group(1)) in changed_lines:
            violations.append(line)

    assert not violations, f"ruff violations on changed lines:\n" + "\n".join(violations)
