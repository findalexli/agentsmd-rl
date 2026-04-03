"""
Task: transformers-tokenizer-redundant-parse
Repo: huggingface/transformers @ 9dc8d8aa3090ab3f39e6086d02b712f9274bc795
PR:   44927

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import tempfile
import unittest.mock as mock

from tokenizers import Tokenizer as TokenizerFast
from tokenizers.models import BPE, WordLevel, WordPiece, Unigram
from transformers.tokenization_utils_tokenizers import TokenizersBackend

REPO = "/repo"
TARGET = f"{REPO}/src/transformers/tokenization_utils_tokenizers.py"


# ---------------------------------------------------------------------------
# Helpers — minimal tokenizer JSON fixtures
# ---------------------------------------------------------------------------

def _write_tokenizer_json(data: dict) -> str:
    """Write tokenizer JSON to a temp file and return the path."""
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, "tokenizer.json")
    with open(path, "w") as f:
        json.dump(data, f)
    return path


def _bpe_tokenizer_json(vocab=None, merges=None):
    return {
        "version": "1.0",
        "model": {
            "type": "BPE",
            "vocab": vocab or {"a": 0, "b": 1, "c": 2, "ab": 3},
            "merges": merges or ["a b"],
            "dropout": None,
            "unk_token": None,
            "continuing_subword_prefix": None,
            "end_of_word_suffix": None,
            "fuse_unk": False,
        },
        "added_tokens": [],
        "normalizer": None,
        "pre_tokenizer": None,
        "post_processor": None,
        "decoder": None,
    }


def _wordpiece_tokenizer_json():
    return {
        "version": "1.0",
        "model": {
            "type": "WordPiece",
            "vocab": {"[UNK]": 0, "hello": 1, "world": 2},
            "unk_token": "[UNK]",
            "continuing_subword_prefix": "##",
            "max_input_chars_per_word": 100,
        },
        "added_tokens": [],
        "normalizer": None,
        "pre_tokenizer": None,
        "post_processor": None,
        "decoder": None,
    }


def _unigram_tokenizer_json():
    return {
        "version": "1.0",
        "model": {
            "type": "Unigram",
            "vocab": [["<unk>", 0.0], ["a", -1.0], ["b", -2.0], ["ab", -1.5]],
            "unk_id": 0,
            "byte_fallback": False,
        },
        "added_tokens": [],
        "normalizer": None,
        "pre_tokenizer": None,
        "post_processor": None,
        "decoder": None,
    }


def _wordlevel_tokenizer_json():
    return {
        "version": "1.0",
        "model": {
            "type": "WordLevel",
            "vocab": {"[UNK]": 0, "hello": 1, "world": 2, "foo": 3},
            "unk_token": "[UNK]",
        },
        "added_tokens": [],
        "normalizer": None,
        "pre_tokenizer": None,
        "post_processor": None,
        "decoder": None,
    }


def _no_type_tokenizer_json():
    """Older tokenizer.json format that omits the 'type' field in 'model'."""
    return {
        "version": "1.0",
        "model": {
            "vocab": {"x": 0, "y": 1},
            "merges": [],
        },
        "added_tokens": [],
        "normalizer": None,
        "pre_tokenizer": None,
        "post_processor": None,
        "decoder": None,
    }


# Subclasses with custom __init__ to trigger the elif branch
class _CustomBPE(TokenizersBackend):
    model = BPE
    def __init__(self, *args, **kwargs):
        pass


class _CustomWordPiece(TokenizersBackend):
    model = WordPiece
    def __init__(self, *args, **kwargs):
        pass


class _CustomWordLevel(TokenizersBackend):
    model = WordLevel
    def __init__(self, *args, **kwargs):
        pass


class _CustomUnigram(TokenizersBackend):
    model = Unigram
    def __init__(self, *args, **kwargs):
        pass


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must be valid Python."""
    import py_compile
    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bpe_avoids_from_file():
    """BPE tokenizer with custom __init__ must not call TokenizerFast.from_file."""
    tok_path = _write_tokenizer_json(_bpe_tokenizer_json())

    from_file_calls = []
    original = TokenizerFast.from_file

    def tracking(path, *a, **kw):
        from_file_calls.append(path)
        return original(path, *a, **kw)

    with mock.patch.object(TokenizerFast, "from_file", side_effect=tracking):
        _CustomBPE.convert_to_native_format(
            trust_remote_code=False, tokenizer_file=tok_path
        )

    assert len(from_file_calls) == 0, (
        f"from_file called {len(from_file_calls)} time(s) for BPE — should use from_str"
    )


# [pr_diff] fail_to_pass
def test_wordpiece_avoids_from_file():
    """WordPiece tokenizer with custom __init__ must not call TokenizerFast.from_file."""
    tok_path = _write_tokenizer_json(_wordpiece_tokenizer_json())

    from_file_calls = []
    original = TokenizerFast.from_file

    def tracking(path, *a, **kw):
        from_file_calls.append(path)
        return original(path, *a, **kw)

    with mock.patch.object(TokenizerFast, "from_file", side_effect=tracking):
        _CustomWordPiece.convert_to_native_format(
            trust_remote_code=False, tokenizer_file=tok_path
        )

    assert len(from_file_calls) == 0, (
        f"from_file called {len(from_file_calls)} time(s) for WordPiece — should use from_str"
    )


# [pr_diff] fail_to_pass
def test_wordlevel_avoids_from_file():
    """WordLevel tokenizer with custom __init__ must not call TokenizerFast.from_file."""
    tok_path = _write_tokenizer_json(_wordlevel_tokenizer_json())

    from_file_calls = []
    original = TokenizerFast.from_file

    def tracking(path, *a, **kw):
        from_file_calls.append(path)
        return original(path, *a, **kw)

    with mock.patch.object(TokenizerFast, "from_file", side_effect=tracking):
        _CustomWordLevel.convert_to_native_format(
            trust_remote_code=False, tokenizer_file=tok_path
        )

    assert len(from_file_calls) == 0, (
        f"from_file called {len(from_file_calls)} time(s) for WordLevel — should use from_str"
    )


# [pr_diff] fail_to_pass
def test_bpe_output_without_from_file():
    """Optimized BPE path returns correct vocab, merges, and metadata."""
    tok_path = _write_tokenizer_json(
        _bpe_tokenizer_json(
            vocab={"p": 0, "q": 1, "r": 2, "pq": 3, "qr": 4},
            merges=["p q", "q r"],
        )
    )

    def blocked(*a, **kw):
        raise RuntimeError("from_file must not be called for BPE")

    with mock.patch.object(TokenizerFast, "from_file", side_effect=blocked):
        result = _CustomBPE.convert_to_native_format(
            trust_remote_code=False, tokenizer_file=tok_path
        )

    # Verify vocab
    vocab = result.get("vocab")
    assert isinstance(vocab, dict), f"vocab is {type(vocab).__name__}, expected dict"
    assert set(vocab.keys()) == {"p", "q", "r", "pq", "qr"}, f"vocab keys: {set(vocab.keys())}"

    # Verify merges
    merges = result.get("merges")
    assert merges is not None, "merges is None"
    assert len(merges) == 2, f"expected 2 merges, got {len(merges)}"

    # Verify metadata keys exist
    assert "post_processor" in result, "post_processor missing"
    assert "tokenizer_padding" in result, "tokenizer_padding missing"
    assert "tokenizer_truncation" in result, "tokenizer_truncation missing"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_unigram_uses_from_file_fallback():
    """Unigram tokenizers must still work via from_file fallback."""
    tok_path = _write_tokenizer_json(_unigram_tokenizer_json())

    result = _CustomUnigram.convert_to_native_format(
        trust_remote_code=False, tokenizer_file=tok_path
    )

    vocab = result.get("vocab")
    assert isinstance(vocab, list), f"vocab is {type(vocab).__name__}, expected list"
    assert len(vocab) == 4, f"expected 4 vocab entries, got {len(vocab)}"


# [pr_diff] pass_to_pass
def test_missing_type_field_fallback():
    """Tokenizer JSON without 'type' in model section must fall back to from_file."""
    tok_path = _write_tokenizer_json(_no_type_tokenizer_json())

    # Should not crash — falls back to from_file
    result = _CustomBPE.convert_to_native_format(
        trust_remote_code=False, tokenizer_file=tok_path
    )
    assert isinstance(result, dict), f"result is {type(result).__name__}, expected dict"


# [pr_diff] pass_to_pass
def test_base_class_path_unchanged():
    """Base class (no custom __init__) still returns tokenizer_object."""
    tok_path = _write_tokenizer_json(
        _bpe_tokenizer_json(vocab={"x": 0, "y": 1, "xy": 2}, merges=["x y"])
    )

    result = TokenizersBackend.convert_to_native_format(
        trust_remote_code=False, tokenizer_file=tok_path
    )
    assert "tokenizer_object" in result, "tokenizer_object not in result for base class path"


# ---------------------------------------------------------------------------
# Anti-stub (static)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:2 @ 9dc8d8aa3090ab3f39e6086d02b712f9274bc795
def test_ruff_clean():
    """Modified file passes ruff linting (make style enforced by CI)."""
    import shutil
    import subprocess

    if not shutil.which("ruff"):
        import pytest
        pytest.skip("ruff not available in this environment")

    result = subprocess.run(
        ["ruff", "check", TARGET],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"ruff found style errors in {TARGET}:\n{result.stdout}{result.stderr}"
    )


# [static] pass_to_pass
def test_not_stub():
    """Modified function has real logic — not a trivial stub."""
    import subprocess

    diff = subprocess.run(
        ["git", "diff", "HEAD", "--", "src/transformers/tokenization_utils_tokenizers.py"],
        cwd=REPO, capture_output=True, text=True,
    ).stdout

    if not diff:
        diff = subprocess.run(
            ["git", "diff", "--cached", "--", "src/transformers/tokenization_utils_tokenizers.py"],
            cwd=REPO, capture_output=True, text=True,
        ).stdout

    if not diff:
        diff = subprocess.run(
            ["git", "log", "-1", "-p", "--", "src/transformers/tokenization_utils_tokenizers.py"],
            cwd=REPO, capture_output=True, text=True,
        ).stdout

    added = sum(
        1 for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
        and line[1:].strip() and not line[1:].strip().startswith("#")
    )
    assert added >= 3, f"Only {added} non-comment lines added — likely a stub"
