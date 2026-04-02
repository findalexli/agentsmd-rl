"""
Task: vllm-mistral-processor-mm-dispatch
Repo: vllm-project/vllm @ 43cc5138e5145752413235a2a8aa303886077327
PR:   #38410

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import inspect
import textwrap
from pathlib import Path

REPO = "/repo"

PIXTRAL_PROC = f"{REPO}/vllm/transformers_utils/processors/pixtral.py"
VOXTRAL_PROC = f"{REPO}/vllm/transformers_utils/processors/voxtral.py"
PIXTRAL_MODEL = f"{REPO}/vllm/model_executor/models/pixtral.py"
VOXTRAL_MODEL = f"{REPO}/vllm/model_executor/models/voxtral.py"
MODIFIED_FILES = [PIXTRAL_PROC, VOXTRAL_PROC, PIXTRAL_MODEL, VOXTRAL_MODEL]


class Mock:
    """Universal mock for heavy deps (torch, transformers, mistral_common)."""

    def __init__(self, *a, **kw):
        pass

    def __getattr__(self, name):
        return Mock()

    def __call__(self, *a, **kw):
        return Mock()

    def __bool__(self):
        return True

    def __iter__(self):
        return iter([])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_init(source: str, class_name: str) -> str:
    """AST-extract __init__ from class_name. Returns dedented source."""
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    return textwrap.dedent(
                        "".join(lines[item.lineno - 1 : item.end_lineno])
                    )
    assert False, f"{class_name}.__init__ not found"


def _build_processor_class(source: str, class_name: str, extra_ns: dict):
    """Extract __init__ from class_name, exec it in a synthetic class, return the class."""
    func_src = _extract_init(source, class_name)
    # Prepend future annotations so type hints become lazy strings —
    # avoids NameError for types not in the exec namespace (e.g. MistralTokenizer).
    class_src = (
        "from __future__ import annotations\n"
        "class TestProc:\n" + textwrap.indent(func_src, "    ")
    )
    ns = {"__builtins__": __builtins__}
    ns.update(extra_ns)
    exec(class_src, ns)
    return ns["TestProc"]


def _find_class_with_methods(source: str, required_methods: list):
    """Find a class containing all required methods, return (name, {name: node})."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        methods = {
            item.name: item
            for item in node.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        if all(m in methods for m in required_methods):
            return node.name, methods
    return None, None


def _extract_methods(source: str, cls_name: str, method_names: list) -> str:
    """AST-extract named methods from a class, return as dedented class body."""
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            parts = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name in method_names:
                    parts.append(textwrap.dedent(
                        "".join(lines[item.lineno - 1 : item.end_lineno])
                    ))
            return "\n".join(parts)
    return ""


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """All 4 modified files must parse without syntax errors."""
    for path in MODIFIED_FILES:
        src = Path(path).read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — processor signature tests
# These verify Transformers v5 can discover components via signature introspection.
# AST-extract + exec justified: modules import torch, mistral_common,
# transformers CUDA internals — cannot be imported in test environment.
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_pixtral_processor_init_signature():
    """MistralCommonPixtralProcessor.__init__ must have image_processor as a named parameter.

    Transformers v5 inspects the constructor signature to discover which
    processor components exist. If image_processor isn't a named parameter
    (e.g. absorbed by **kwargs), the image processor is silently skipped.
    """
    source = Path(PIXTRAL_PROC).read_text()
    TestProc = _build_processor_class(source, "MistralCommonPixtralProcessor", {
        "MistralCommonImageProcessor": Mock,
        "ProcessorMixin": type("PM", (), {}),
    })
    sig = inspect.signature(TestProc.__init__)
    assert "image_processor" in sig.parameters, (
        "image_processor must be a named parameter in __init__ "
        "(not absorbed by **kwargs) for Transformers v5 signature introspection"
    )


# [pr_diff] fail_to_pass
def test_voxtral_processor_init_signature():
    """MistralCommonVoxtralProcessor.__init__ must have feature_extractor as a named parameter."""
    source = Path(VOXTRAL_PROC).read_text()
    TestProc = _build_processor_class(source, "MistralCommonVoxtralProcessor", {
        "MistralCommonFeatureExtractor": Mock,
        "ProcessorMixin": type("PM", (), {}),
    })
    sig = inspect.signature(TestProc.__init__)
    assert "feature_extractor" in sig.parameters, (
        "feature_extractor must be a named parameter in __init__ "
        "(not absorbed by **kwargs) for Transformers v5 signature introspection"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — processor stores component from parameter
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_pixtral_processor_stores_image_processor():
    """MistralCommonPixtralProcessor.__init__ must store image_processor from the parameter."""
    source = Path(PIXTRAL_PROC).read_text()
    TestProc = _build_processor_class(source, "MistralCommonPixtralProcessor", {
        "MistralCommonImageProcessor": Mock,
        "ProcessorMixin": type("PM", (), {}),
    })

    # Sentinel with unique marker — distinguishes param-passed from internally-created
    class Sentinel:
        mm_encoder = Mock()
        def __getattr__(self, name):
            return Mock()

    sentinel = Sentinel()
    sentinel._is_sentinel = True

    obj = object.__new__(TestProc)
    TestProc.__init__(obj, Mock(), image_processor=sentinel)

    assert hasattr(obj, "image_processor"), "self.image_processor not set"
    assert getattr(obj.image_processor, "_is_sentinel", False), (
        "self.image_processor was created internally, not stored from parameter"
    )

    # Verify with a second distinct sentinel to ensure it's not hardcoded
    sentinel2 = Sentinel()
    sentinel2._is_sentinel2 = True
    obj2 = object.__new__(TestProc)
    TestProc.__init__(obj2, Mock(), image_processor=sentinel2)
    assert getattr(obj2.image_processor, "_is_sentinel2", False), (
        "self.image_processor doesn't reflect the passed parameter"
    )


# [pr_diff] fail_to_pass
def test_voxtral_processor_stores_feature_extractor():
    """MistralCommonVoxtralProcessor.__init__ must store feature_extractor from the parameter."""
    source = Path(VOXTRAL_PROC).read_text()
    TestProc = _build_processor_class(source, "MistralCommonVoxtralProcessor", {
        "MistralCommonFeatureExtractor": Mock,
        "ProcessorMixin": type("PM", (), {}),
    })

    class Sentinel:
        audio_encoder = Mock()
        def __getattr__(self, name):
            return Mock()

    sentinel = Sentinel()
    sentinel._is_sentinel = True

    obj = object.__new__(TestProc)
    TestProc.__init__(obj, Mock(), feature_extractor=sentinel)

    assert hasattr(obj, "feature_extractor"), "self.feature_extractor not set"
    assert getattr(obj.feature_extractor, "_is_sentinel", False), (
        "self.feature_extractor was created internally, not stored from parameter"
    )

    sentinel2 = Sentinel()
    sentinel2._is_sentinel2 = True
    obj2 = object.__new__(TestProc)
    TestProc.__init__(obj2, Mock(), feature_extractor=sentinel2)
    assert getattr(obj2.feature_extractor, "_is_sentinel2", False), (
        "self.feature_extractor doesn't reflect the passed parameter"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — model integration (exec-based)
# AST-extract + exec justified: model files import torch, vllm CUDA internals.
# We extract the relevant methods, exec them in a mock env, and verify
# that get_hf_processor passes the component to the processor constructor.
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_pixtral_model_passes_image_processor():
    """Pixtral model's get_hf_processor must pass image_processor to the processor constructor."""
    source = Path(PIXTRAL_MODEL).read_text()
    cls_name, methods = _find_class_with_methods(source, ["get_hf_processor"])
    assert cls_name is not None, "No class with get_hf_processor found in pixtral model"

    # Determine which methods to extract
    to_extract = ["get_hf_processor"]
    if "get_image_processor" in methods:
        to_extract.append("get_image_processor")

    body = _extract_methods(source, cls_name, to_extract)
    class_src = (
        "from __future__ import annotations\n"
        "class TestModel:\n" + textwrap.indent(body, "    ")
    )

    # Recording mock captures kwargs passed to the processor constructor
    captured = {}

    class RecordingProcessor:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    ns = {
        "__builtins__": __builtins__,
        "MistralCommonPixtralProcessor": RecordingProcessor,
        "MistralCommonImageProcessor": Mock,
    }
    exec(class_src, ns)

    obj = object.__new__(ns["TestModel"])
    obj.get_tokenizer = lambda: Mock()
    obj.ctx = Mock()  # base commit uses self.ctx.init_processor

    obj.get_hf_processor()
    assert "image_processor" in captured, (
        "get_hf_processor must pass image_processor= to MistralCommonPixtralProcessor"
    )


# [pr_diff] fail_to_pass
def test_voxtral_model_passes_feature_extractor():
    """Voxtral model's get_hf_processor must pass feature_extractor to the processor constructor."""
    source = Path(VOXTRAL_MODEL).read_text()
    cls_name, methods = _find_class_with_methods(source, ["get_hf_processor"])
    assert cls_name is not None, "No class with get_hf_processor found in voxtral model"

    to_extract = ["get_hf_processor"]
    if "get_feature_extractor" in methods:
        to_extract.append("get_feature_extractor")

    body = _extract_methods(source, cls_name, to_extract)
    class_src = (
        "from __future__ import annotations\n"
        "class TestModel:\n" + textwrap.indent(body, "    ")
    )

    captured = {}

    class RecordingProcessor:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    ns = {
        "__builtins__": __builtins__,
        "MistralCommonVoxtralProcessor": RecordingProcessor,
        "MistralCommonFeatureExtractor": Mock,
    }
    exec(class_src, ns)

    obj = object.__new__(ns["TestModel"])
    obj.get_tokenizer = lambda: Mock()
    obj.ctx = Mock()

    obj.get_hf_processor()
    assert "feature_extractor" in captured, (
        "get_hf_processor must pass feature_extractor= to MistralCommonVoxtralProcessor"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_get_hf_processor_preserved():
    """get_hf_processor must exist in both pixtral and voxtral model files."""
    for path in [PIXTRAL_MODEL, VOXTRAL_MODEL]:
        source = Path(path).read_text()
        tree = ast.parse(source)
        found = any(
            isinstance(node, ast.FunctionDef) and node.name == "get_hf_processor"
            for node in ast.walk(tree)
        )
        assert found, f"{path} missing get_hf_processor"


# [static] pass_to_pass
def test_not_stub():
    """Modified files must not be trivially small (>= 50 lines each)."""
    for path in MODIFIED_FILES:
        lines = len(Path(path).read_text().splitlines())
        assert lines >= 50, f"{path} too short ({lines} lines) — likely a stub"
