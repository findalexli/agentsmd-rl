"""
Task: prime-rl-sft-messages-column-format
Repo: PrimeIntellect-ai/prime-rl @ 7e853195ea6c7ce0cdfd67f7f00e6fb755ad0e17
PR:   2074

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
from pathlib import Path

import pytest
from datasets import Dataset
from transformers import AutoTokenizer

from prime_rl.trainer.sft.data import SFTDataset

REPO = "/workspace"
DATA_FILE = Path(REPO) / "src/prime_rl/trainer/sft/data.py"
TEST_FILE = Path(REPO) / "tests/unit/train/sft/test_sft_dataset.py"


@pytest.fixture(scope="module")
def tokenizer():
    return AutoTokenizer.from_pretrained("PrimeIntellect/Qwen3-0.6B")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """data.py must be valid Python."""
    source = DATA_FILE.read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_messages_column_tokenized(tokenizer):
    """SFTDataset must accept a 'messages' column and produce valid tokenized output."""
    conversations = [
        [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ],
        [
            {"role": "system", "content": "You are a math tutor."},
            {"role": "user", "content": "What is 7*8?"},
            {"role": "assistant", "content": "56"},
        ],
        [
            {"role": "user", "content": "Translate 'hello' to French"},
            {"role": "assistant", "content": "Bonjour"},
        ],
    ]

    for msgs in conversations:
        ds = Dataset.from_list([{"messages": msgs}])
        sft_ds = SFTDataset(ds, tokenizer=tokenizer, max_examples=1)
        sample = next(iter(sft_ds))

        assert "input_ids" in sample and len(sample["input_ids"]) > 0
        assert "loss_mask" in sample and len(sample["loss_mask"]) > 0
        assert len(sample["input_ids"]) == len(sample["loss_mask"])
        assert any(sample["loss_mask"]), "Some tokens should be trainable"


# [pr_diff] fail_to_pass
def test_messages_precedence(tokenizer):
    """When both 'messages' and 'prompt'/'completion' are present, messages takes precedence."""
    row_both = {
        "messages": [
            {"role": "user", "content": "From messages"},
            {"role": "assistant", "content": "Response from messages"},
        ],
        "prompt": [{"role": "user", "content": "Ignored prompt"}],
        "completion": [{"role": "assistant", "content": "Ignored completion"}],
    }
    row_messages_only = {
        "messages": [
            {"role": "user", "content": "From messages"},
            {"role": "assistant", "content": "Response from messages"},
        ],
    }

    ds_both = SFTDataset(Dataset.from_list([row_both]), tokenizer=tokenizer, max_examples=1)
    ds_only = SFTDataset(Dataset.from_list([row_messages_only]), tokenizer=tokenizer, max_examples=1)

    sample_both = next(iter(ds_both))
    sample_only = next(iter(ds_only))

    assert sample_both["input_ids"] == sample_only["input_ids"], \
        "messages should take precedence over prompt/completion"


# [pr_diff] fail_to_pass
def test_error_mentions_messages(tokenizer):
    """ValueError when missing columns should inform users about the messages format."""
    for invalid_row in [
        {"text": "irrelevant"},
        {"prompt": [{"role": "user", "content": "hi"}]},
        {"completion": [{"role": "assistant", "content": "hi"}]},
    ]:
        ds = Dataset.from_list([invalid_row])
        sft_ds = SFTDataset(ds, tokenizer=tokenizer, max_examples=1)

        with pytest.raises(ValueError, match="(?i)messages"):
            next(iter(sft_ds))


# [pr_diff] fail_to_pass
def test_multiturn_messages(tokenizer):
    """Multi-turn messages must produce longer sequences than single-turn."""
    multi = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "The answer is 4."},
        {"role": "user", "content": "And 3+3?"},
        {"role": "assistant", "content": "The answer is 6."},
    ]
    single = [
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "The answer is 4."},
    ]

    ds_multi = SFTDataset(Dataset.from_list([{"messages": multi}]), tokenizer=tokenizer, max_examples=1)
    ds_single = SFTDataset(Dataset.from_list([{"messages": single}]), tokenizer=tokenizer, max_examples=1)

    sample_multi = next(iter(ds_multi))
    sample_single = next(iter(ds_single))

    assert len(sample_multi["input_ids"]) > len(sample_single["input_ids"]), \
        "Multi-turn should produce more tokens"


# [pr_diff] fail_to_pass
def test_messages_equivalent_to_empty_prompt_completion(tokenizer):
    """Messages column is semantically equivalent to empty prompt + messages as completion."""
    conversations = [
        [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ],
        [
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "Capital of France?"},
            {"role": "assistant", "content": "Paris."},
        ],
    ]

    for msgs in conversations:
        ds_messages = SFTDataset(
            Dataset.from_list([{"messages": msgs}]),
            tokenizer=tokenizer, max_examples=1,
        )
        ds_split = SFTDataset(
            Dataset.from_list([{"prompt": [], "completion": msgs}]),
            tokenizer=tokenizer, max_examples=1,
        )

        sample_msg = next(iter(ds_messages))
        sample_split = next(iter(ds_split))

        assert sample_msg["input_ids"] == sample_split["input_ids"], \
            "messages path should match empty-prompt + completion path"
        assert sample_msg["loss_mask"] == sample_split["loss_mask"], \
            "loss masks should match between messages and split paths"


# [pr_diff] fail_to_pass
def test_messages_with_tool_calls(tokenizer):
    """Messages containing tool calls must be tokenized correctly via messages path."""
    messages = [
        {"role": "user", "content": "What's the weather?"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "get_weather", "arguments": '{"location": "NYC"}'},
                }
            ],
        },
        {"role": "tool", "content": '{"temp": 72}', "tool_call_id": "call_1"},
        {"role": "assistant", "content": "It's 72 degrees in NYC."},
    ]

    ds = Dataset.from_list([{"messages": messages}])
    sft_ds = SFTDataset(ds, tokenizer=tokenizer, max_examples=1)
    sample = next(iter(sft_ds))

    assert len(sample["input_ids"]) > 0
    assert len(sample["input_ids"]) == len(sample["loss_mask"])
    assert any(sample["loss_mask"]), "Tool call messages should have trainable tokens"

    # Verify the output contains meaningful content by decoding and checking
    decoded = tokenizer.decode(sample["input_ids"])
    assert "weather" in decoded.lower(), "Tokenized output should contain message content"
    assert "72" in decoded, "Tokenized output should contain tool response content"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) -- regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_prompt_completion_still_works(tokenizer):
    """Existing prompt+completion format must continue working."""
    examples = [
        {
            "prompt": [{"role": "user", "content": "Hello"}],
            "completion": [{"role": "assistant", "content": "Hi there!"}],
        },
        {
            "prompt": [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Summarize this."},
            ],
            "completion": [{"role": "assistant", "content": "Here is the summary."}],
        },
    ]

    for ex in examples:
        ds = Dataset.from_list([ex])
        sft_ds = SFTDataset(ds, tokenizer=tokenizer, max_examples=1)
        sample = next(iter(sft_ds))

        assert "input_ids" in sample and len(sample["input_ids"]) > 0
        assert any(sample["loss_mask"]), "Some tokens should be trainable"


# [pr_diff] pass_to_pass
def test_valueerror_on_invalid_input(tokenizer):
    """Missing messages/prompt/completion must still raise ValueError."""
    ds = Dataset.from_list([{"text": "irrelevant"}])
    sft_ds = SFTDataset(ds, tokenizer=tokenizer, max_examples=1)

    with pytest.raises(ValueError):
        next(iter(sft_ds))


# [static] pass_to_pass
def test_resolve_messages_not_stub():
    """data.py must handle 'messages' column with branching logic, not a stub."""
    # AST-only because: checking structural property (non-trivial branching), not behavior
    source = DATA_FILE.read_text()
    tree = ast.parse(source)

    # Find _process method and check it handles "messages"
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_process":
            body_src = ast.get_source_segment(source, node) or ""
            assert "messages" in body_src, "_process must handle 'messages' column"
            # Must have at least 2 branches (messages vs prompt/completion vs error)
            ifs = [n for n in ast.walk(node) if isinstance(n, ast.If)]
            assert len(ifs) >= 2, "_process must branch on message format (messages vs prompt/completion)"
            raises = [n for n in ast.walk(node) if isinstance(n, ast.Raise)]
            assert len(raises) >= 1, "_process must raise on invalid input"
            return

    pytest.fail("_process method not found in data.py")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- AGENTS.md:5 @ 7e853195ea6c7ce0cdfd67f7f00e6fb755ad0e17
def test_no_tryexcept_in_process():
    """_process method should not use try/except (AGENTS.md: avoid unnecessary try/except)."""
    # AST-only because: checking structural property (absence of try/except), not behavior
    source = DATA_FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_process":
            for child in ast.walk(node):
                assert not isinstance(child, ast.Try), \
                    "Unnecessary try/except found in _process (AGENTS.md:5)"


# [agent_config] pass_to_pass -- AGENTS.md:54 @ 7e853195ea6c7ce0cdfd67f7f00e6fb755ad0e17
def test_no_class_based_tests():
    """Test file must use plain functions, not class-based tests (AGENTS.md: pytest fixtures)."""
    # AST-only because: checking structural property (no test classes), not behavior
    if not TEST_FILE.exists():
        return  # test file not modified by agent
    source = TEST_FILE.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            pytest.fail(f"Class-based test '{node.name}' found -- use plain functions (AGENTS.md:54)")
