"""
Task: slime-opd-multimodal-image-payload
Repo: THUDM/slime @ f3a86d51d9efbb5575a9d87839a81135a51d6233
PR:   1760

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import asyncio
import base64
import inspect
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from PIL import Image

REPO = "/workspace/slime"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_session(captured_payload: dict):
    """Return a mock aiohttp.ClientSession context manager that captures POST payloads."""
    mock_resp = AsyncMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = AsyncMock(return_value={"reward": 0.0})

    mock_post_ctx = AsyncMock()
    mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_post_ctx.__aexit__ = AsyncMock(return_value=False)

    def capture_post(url, json=None):
        captured_payload.update(json or {})
        return mock_post_ctx

    mock_session = AsyncMock()
    mock_session.post = capture_post

    mock_session_ctx = AsyncMock()
    mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

    return mock_session_ctx


def _run_reward_func(sample):
    """Call reward_func with a mocked HTTP session and return the captured payload."""
    from slime.rollout.on_policy_distillation import reward_func

    args = MagicMock()
    args.rm_url = "http://localhost:9999/v1/reward"

    captured = {}

    async def _go():
        with patch("aiohttp.ClientSession", return_value=_make_mock_session(captured)):
            await reward_func(args, sample)

    asyncio.run(_go())
    return captured


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """on_policy_distillation.py must parse without syntax errors."""
    src = Path(f"{REPO}/slime/rollout/on_policy_distillation.py").read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_payload_includes_image_data():
    """reward_func includes encoded image_data in payload for multimodal samples."""
    from slime.utils.types import Sample

    # Test with varied image sizes and colors
    test_cases = [
        (Image.new("RGB", (4, 4), color="red"), [10, 20, 30]),
        (Image.new("RGB", (16, 8), color="blue"), [1, 2]),
        (Image.new("L", (2, 2), color=128), [5, 6, 7, 8, 9]),
    ]

    for img, tokens in test_cases:
        sample = Sample(tokens=tokens, multimodal_inputs={"images": [img]})
        payload = _run_reward_func(sample)

        assert "image_data" in payload, f"image_data missing for {img.size} {img.mode} image"
        assert isinstance(payload["image_data"], list), "image_data should be a list"
        assert len(payload["image_data"]) == 1, "image_data should have 1 entry"
        # Verify it's a base64 data URI that decodes to non-empty bytes
        uri = payload["image_data"][0]
        assert isinstance(uri, str) and "base64" in uri or uri.startswith("data:image/"), \
            "image should be a base64-encoded string"
        raw = base64.b64decode(uri.split(",", 1)[1])
        assert len(raw) > 0, "decoded image data should be non-empty"


# [pr_diff] fail_to_pass
def test_multiple_images_encoded():
    """Each image in multimodal_inputs is individually encoded."""
    from slime.utils.types import Sample

    imgs = [Image.new("RGB", (4, 4), color=c) for c in ["red", "green", "blue"]]
    sample = Sample(tokens=[1, 2, 3], multimodal_inputs={"images": imgs})

    payload = _run_reward_func(sample)

    assert "image_data" in payload, "image_data missing"
    assert len(payload["image_data"]) == 3, f"Expected 3 images, got {len(payload['image_data'])}"
    # Each different-color image should produce a unique encoding
    assert len(set(payload["image_data"])) == 3, "Each image should produce a unique encoding"
    # Each must decode
    for entry in payload["image_data"]:
        raw = base64.b64decode(entry.split(",", 1)[1])
        assert len(raw) > 0, "Each decoded image should be non-empty"

    # Also verify count scales: 5 images → 5 entries
    imgs5 = [Image.new("RGB", (4, 4), color=(i * 50, 0, 0)) for i in range(5)]
    sample5 = Sample(tokens=[1], multimodal_inputs={"images": imgs5})
    payload5 = _run_reward_func(sample5)
    assert len(payload5["image_data"]) == 5, f"Expected 5 images, got {len(payload5['image_data'])}"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_text_only_no_image_data():
    """Text-only samples must not include image_data in payload."""
    from slime.utils.types import Sample

    # Case 1: no multimodal_inputs at all
    sample1 = Sample(tokens=[1, 2, 3, 4, 5])
    payload1 = _run_reward_func(sample1)
    assert "image_data" not in payload1, "image_data should NOT be in text-only payload"
    assert "input_ids" in payload1, "input_ids should be in payload"

    # Case 2: multimodal_inputs is None explicitly
    sample2 = Sample(tokens=[10, 20], multimodal_inputs=None)
    payload2 = _run_reward_func(sample2)
    assert "image_data" not in payload2, "image_data should NOT appear when multimodal_inputs is None"


# [pr_diff] pass_to_pass
def test_empty_images_no_image_data():
    """Samples with empty images list should not include image_data in payload."""
    from slime.utils.types import Sample

    # Empty images list
    sample1 = Sample(tokens=[1, 2, 3], multimodal_inputs={"images": []})
    payload1 = _run_reward_func(sample1)
    assert "image_data" not in payload1, "image_data should NOT appear for empty images list"

    # multimodal_inputs with no "images" key
    sample2 = Sample(tokens=[4, 5, 6], multimodal_inputs={"videos": ["placeholder"]})
    payload2 = _run_reward_func(sample2)
    assert "image_data" not in payload2, "image_data should NOT appear when no images key"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """reward_func has a substantial implementation (not just pass/return)."""
    # AST-only because: we need to inspect function body structure, not runtime behavior
    src = Path(f"{REPO}/slime/rollout/on_policy_distillation.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "reward_func":
            body_stmts = [
                n for n in ast.walk(node)
                if isinstance(n, (ast.Assign, ast.AugAssign, ast.Expr, ast.If, ast.For, ast.Return, ast.Await))
            ]
            assert len(body_stmts) >= 5, f"reward_func body too shallow ({len(body_stmts)} stmts)"
            return

    raise AssertionError("reward_func not found as async function")


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .claude/skills/add-reward-function/SKILL.md:83 @ f3a86d5
def test_reward_func_is_async():
    """reward_func must remain async (no blocking network calls)."""
    from slime.rollout.on_policy_distillation import reward_func

    assert inspect.iscoroutinefunction(reward_func), \
        "reward_func must be an async function (use 'async def')"
