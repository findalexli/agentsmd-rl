"""
Task: transformers-processor-deepcopy-perf
Repo: huggingface/transformers @ 55cc1a7fb8e53a5e7e35ca9cf9759498f20abb93
PR:   44894

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import copy
import sys
from pathlib import Path

sys.path.insert(0, "/workspace/transformers")

REPO = "/workspace/transformers"
TARGET = f"{REPO}/src/transformers/processing_utils.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / import checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """processing_utils.py must parse without errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# [static] pass_to_pass
def test_import_processor_mixin():
    """ProcessorMixin.to_dict must be importable."""
    from transformers.processing_utils import ProcessorMixin
    assert hasattr(ProcessorMixin, "to_dict"), "ProcessorMixin missing to_dict"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

def _make_processor(tokenizer_vocab_size=10000, num_image_attrs=1):
    """Helper: build a TestProcessor with configurable mock components."""
    from transformers.processing_utils import ProcessorMixin

    class MockTokenizer:
        def __init__(self, size):
            self.vocab = {f"tok_{i}": i for i in range(size)}
            self.name_or_path = "mock/tokenizer"

    class MockImageProcessor:
        def __init__(self):
            self.size = {"height": 224, "width": 224}
            self.name_or_path = "mock/image_processor"

    class TestProcessor(ProcessorMixin):
        attributes = ["tokenizer", "image_processor"]

        @classmethod
        def get_attributes(cls):
            return cls.attributes

        def __init__(self, vocab_size):
            self.tokenizer = MockTokenizer(vocab_size)
            self.image_processor = MockImageProcessor()
            self.chat_template = None
            self._processor_class = "TestProcessor"

    return TestProcessor(tokenizer_vocab_size)


# [pr_diff] fail_to_pass
def test_tokenizer_not_deepcopied():
    """Tokenizer attributes must be excluded from deepcopy."""
    deepcopy_types = []
    original = copy.deepcopy

    def tracking_deepcopy(obj, *args, **kwargs):
        deepcopy_types.append(type(obj).__name__)
        return original(obj, *args, **kwargs)

    copy.deepcopy = tracking_deepcopy
    try:
        processor = _make_processor(tokenizer_vocab_size=500)
        deepcopy_types.clear()
        processor.to_dict()
    finally:
        copy.deepcopy = original

    tokenizer_copied = any("MockTokenizer" in t for t in deepcopy_types)
    assert not tokenizer_copied, (
        f"tokenizer was deepcopied; deepcopy called on: {deepcopy_types}"
    )
    # Something must still be deepcopied (non-tokenizer attrs)
    assert len(deepcopy_types) > 0, "deepcopy not called at all -- must still copy non-tokenizer attrs"


# [pr_diff] fail_to_pass
def test_tokenizer_excluded_varied_vocabs():
    """Tokenizer excluded regardless of vocabulary size (small and large)."""
    for size in [10, 5000, 50000]:
        deepcopy_types = []
        original = copy.deepcopy

        def tracking_deepcopy(obj, *args, **kwargs):
            deepcopy_types.append(type(obj).__name__)
            return original(obj, *args, **kwargs)

        copy.deepcopy = tracking_deepcopy
        try:
            processor = _make_processor(tokenizer_vocab_size=size)
            deepcopy_types.clear()
            processor.to_dict()
        finally:
            copy.deepcopy = original

        tokenizer_copied = any("MockTokenizer" in t for t in deepcopy_types)
        assert not tokenizer_copied, (
            f"tokenizer deepcopied with vocab_size={size}; types: {deepcopy_types}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- output correctness
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_output_excludes_tokenizer():
    """to_dict() output must not contain tokenizer key."""
    processor = _make_processor()
    result = processor.to_dict()
    assert isinstance(result, dict)
    assert "tokenizer" not in result, f"tokenizer found in output: {list(result.keys())}"


# [pr_diff] pass_to_pass
def test_output_excludes_chat_template():
    """to_dict() output must not contain chat_template."""
    processor = _make_processor()
    result = processor.to_dict()
    assert "chat_template" not in result, "chat_template should be excluded"


# [pr_diff] pass_to_pass
def test_output_has_processor_class():
    """to_dict() output must contain processor_class."""
    processor = _make_processor()
    result = processor.to_dict()
    assert "processor_class" in result, f"missing processor_class; keys: {list(result.keys())}"
    assert result["processor_class"] == "TestProcessor"


# [pr_diff] pass_to_pass
def test_tokenizer_only_processor():
    """Processor with only tokenizer attribute still produces valid output."""
    from transformers.processing_utils import ProcessorMixin

    class MockTokenizer:
        def __init__(self):
            self.vocab = {"a": 1}
            self.name_or_path = "mock/tok"

    class TokOnlyProcessor(ProcessorMixin):
        attributes = ["tokenizer"]

        @classmethod
        def get_attributes(cls):
            return cls.attributes

        def __init__(self):
            self.tokenizer = MockTokenizer()
            self.chat_template = None
            self._processor_class = "TokOnlyProcessor"

    result = TokOnlyProcessor().to_dict()
    assert isinstance(result, dict)
    assert "tokenizer" not in result
    assert "processor_class" in result


# ---------------------------------------------------------------------------
# Anti-stub (static) -- real implementation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """to_dict must have substantial logic (not a stub)."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ProcessorMixin":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "to_dict":
                    stmts = [
                        s for s in item.body
                        if not isinstance(s, (ast.Pass, ast.Expr))
                        or (isinstance(s, ast.Expr) and not isinstance(s.value, ast.Constant))
                    ]
                    assert len(stmts) >= 5, f"to_dict has only {len(stmts)} statements -- looks like a stub"
                    has_logic = any(
                        isinstance(c, (ast.For, ast.If, ast.comprehension, ast.DictComp))
                        for c in ast.walk(item)
                    )
                    assert has_logic, "to_dict lacks control structures"
                    return
    assert False, "ProcessorMixin.to_dict not found"
