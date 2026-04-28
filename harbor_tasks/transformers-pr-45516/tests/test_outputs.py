"""
Tests for T5Gemma2 prepare_decoder_input_ids_from_labels fix.

PR #45516: The method used 'input_ids' as its parameter name, but
DataCollatorForSeq2Seq passes labels as a keyword argument 'labels='.
This broke the interaction between the standard data collator and T5Gemma2.
"""

import pytest
import torch
import sys
import os
import subprocess

REPO = "/workspace/transformers"
sys.path.insert(0, os.path.join(REPO, "src"))

from transformers.models.t5gemma2.configuration_t5gemma2 import (
    T5Gemma2Config,
    T5Gemma2EncoderConfig,
    T5Gemma2DecoderConfig,
    T5Gemma2TextConfig,
)
from transformers.models.t5gemma2.modeling_t5gemma2 import (
    T5Gemma2ForConditionalGeneration,
)


def _make_config():
    """Create a minimal T5Gemma2Config for testing."""
    hidden_size = 32
    num_hidden_layers = 2
    num_attention_heads = 4
    num_key_value_heads = 2
    intermediate_size = 37
    vocab_size = 99
    head_dim = hidden_size // num_attention_heads
    layer_types = ["full_attention", "sliding_attention"]

    encoder_config = T5Gemma2EncoderConfig(
        text_config=T5Gemma2TextConfig(
            vocab_size=vocab_size,
            hidden_size=hidden_size,
            num_hidden_layers=num_hidden_layers,
            num_attention_heads=num_attention_heads,
            num_key_value_heads=num_key_value_heads,
            intermediate_size=intermediate_size,
            hidden_act="gelu",
            hidden_dropout_prob=0.1,
            attention_probs_dropout_prob=0.1,
            max_position_embeddings=512,
            layer_types=layer_types,
            type_vocab_size=16,
            is_decoder=False,
            initializer_range=0.02,
            head_dim=head_dim,
            bos_token_id=2,
            eos_token_id=1,
            pad_token_id=0,
        ),
        vision_config={
            "use_labels": True,
            "image_size": 20,
            "patch_size": 5,
            "num_channels": 3,
            "is_training": True,
            "hidden_size": 32,
            "num_key_value_heads": 1,
            "num_hidden_layers": 2,
            "num_attention_heads": 4,
            "intermediate_size": 37,
            "dropout": 0.1,
            "attention_dropout": 0.1,
            "initializer_range": 0.02,
        },
        image_token_index=4,
        boi_token_index=5,
        eoi_token_index=6,
        mm_tokens_per_image=2,
        hidden_size=hidden_size,
    )

    decoder_config = T5Gemma2DecoderConfig(
        vocab_size=vocab_size,
        hidden_size=hidden_size,
        num_hidden_layers=num_hidden_layers,
        num_attention_heads=num_attention_heads,
        num_key_value_heads=num_key_value_heads,
        intermediate_size=intermediate_size,
        cross_attention_hidden_size=hidden_size,
        hidden_act="gelu",
        hidden_dropout_prob=0.1,
        attention_probs_dropout_prob=0.1,
        max_position_embeddings=512,
        layer_types=layer_types,
        type_vocab_size=16,
        is_decoder=True,
        initializer_range=0.02,
        head_dim=head_dim,
        bos_token_id=2,
        eos_token_id=1,
        pad_token_id=0,
    )

    return T5Gemma2Config(
        encoder=encoder_config,
        decoder=decoder_config,
        is_encoder_decoder=True,
        image_token_index=4,
        num_attention_heads=num_attention_heads,
        num_key_value_heads=num_key_value_heads,
        vocab_size=vocab_size,
        hidden_size=hidden_size,
        num_hidden_layers=num_hidden_layers,
    )


@pytest.fixture(scope="module")
def model():
    config = _make_config()
    return T5Gemma2ForConditionalGeneration(config).eval()


def test_labels_kwarg_accepted(model):
    """Calling prepare_decoder_input_ids_from_labels with labels= keyword works."""
    labels = torch.tensor([[0, 1, 2, 3, 4]])
    result = model.prepare_decoder_input_ids_from_labels(labels=labels)
    assert result is not None


def test_labels_kwarg_output_shape(model):
    """Output shape matches input shape when called with labels= keyword."""
    labels = torch.tensor([[0, 1, 2, 3, 4]])
    result = model.prepare_decoder_input_ids_from_labels(labels=labels)
    assert result.shape == labels.shape


def test_labels_kwarg_shifts_right_and_prepends_bos(model):
    """Output is input shifted right with BOS token prepended at position 0."""
    bos_token_id = model.config.decoder.bos_token_id
    labels = torch.tensor([[10, 20, 30, 40, 50]])
    result = model.prepare_decoder_input_ids_from_labels(labels=labels)
    assert result[0, 0].item() == bos_token_id
    assert torch.equal(result[0, 1:], labels[0, :-1])


def test_labels_kwarg_replaces_neg100_with_pad(model):
    """-100 values in labels are replaced with pad_token_id after shifting."""
    pad_token_id = model.config.decoder.pad_token_id
    labels = torch.tensor([[10, -100, 30, -100, 50]])
    result = model.prepare_decoder_input_ids_from_labels(labels=labels)
    # After right-shift: pos0=bos, pos1=10, pos2=-100(→pad), pos3=30, pos4=-100(→pad)
    assert result[0, 2].item() == pad_token_id
    assert result[0, 4].item() == pad_token_id
    assert result[0, 1].item() == 10
    assert result[0, 3].item() == 30


def test_labels_kwarg_batch_handling(model):
    """Method works with batched inputs passed via labels= keyword."""
    labels = torch.tensor([
        [1, 2, 3, -100, -100],
        [4, 5, -100, -100, -100],
    ])
    result = model.prepare_decoder_input_ids_from_labels(labels=labels)
    assert result.shape == labels.shape
    assert result[0, 0].item() == model.config.decoder.bos_token_id
    assert result[1, 0].item() == model.config.decoder.bos_token_id


def test_ruff_check_passes():
    """Repo's linter (ruff) passes on the changed file (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "src/transformers/models/t5gemma2/modeling_t5gemma2.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
