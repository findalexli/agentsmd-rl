"""
Task: vllm-cohere-embed-system-prompt
Repo: vllm-project/vllm @ aa4eb0db78ec469438a7a18147b0372fe2eb7cf4
PR:   #38362

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import inspect
import textwrap
from pathlib import Path

REPO = "/workspace/vllm"
TARGET = f"{REPO}/vllm/entrypoints/pooling/embed/io_processor.py"


# ---------------------------------------------------------------------------
# Helpers — extract _mixed_input_to_messages and build a mock namespace
# so we can call it without importing the full vllm stack.
# ---------------------------------------------------------------------------

def _build_mock_namespace():
    ns = {"__builtins__": __builtins__}
    exec(textwrap.dedent("""
        from dataclasses import dataclass
        from typing import Optional, List, Dict, Any, Union

        ChatCompletionContentPartParam = Any
        ChatCompletionMessageParam = Any

        @dataclass
        class CohereEmbedContent:
            type: str
            text: Optional[str] = None
            image_url: Optional[Dict] = None

        @dataclass
        class CohereEmbedInput:
            content: List['CohereEmbedContent']

        @dataclass
        class ChatCompletionContentPartTextParam:
            type: str
            text: str

        @dataclass
        class ImageURL:
            url: str

        @dataclass
        class ChatCompletionContentPartImageParam:
            type: str
            image_url: 'ImageURL'

        @dataclass
        class CustomChatCompletionMessageParam:
            role: str
            content: Any
    """), ns)
    return ns


def _extract_method(source, class_name, method_name):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name == method_name:
                        lines = source.splitlines(keepends=True)
                        func_lines = lines[item.lineno - 1 : item.end_lineno]
                        clean = [l for l in func_lines if not l.strip().startswith("@")]
                        return textwrap.dedent("".join(clean))
    return None


def _load_mixed_input_to_messages():
    """Extract and compile _mixed_input_to_messages, return (callable, namespace)."""
    source = Path(TARGET).read_text()
    ns = _build_mock_namespace()
    func_src = _extract_method(source, "EmbedIOProcessor", "_mixed_input_to_messages")
    assert func_src is not None, "_mixed_input_to_messages not found in EmbedIOProcessor"
    exec(func_src, ns)
    fn = ns["_mixed_input_to_messages"]
    return fn, ns


def _call(fn, *args, **kwargs):
    sig = inspect.signature(fn)
    params = list(sig.parameters.keys())
    if params and params[0] == "self":
        dummy = type("Self", (), {})()
        return fn(dummy, *args, **kwargs)
    return fn(*args, **kwargs)


def _roles(messages):
    return [m.role for m in messages]


def _texts_for_role(messages, role):
    texts = []
    for m in messages:
        if m.role != role:
            continue
        if isinstance(m.content, str):
            texts.append(m.content)
        elif isinstance(m.content, list):
            texts.extend(p.text for p in m.content if hasattr(p, "text"))
    return texts


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """io_processor.py must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_task_prefix_as_system_prompt():
    """When task_prefix is given, it must appear as a system-role message
    and must NOT be prepended to the user text content."""
    fn, ns = _load_mixed_input_to_messages()
    CI, CC = ns["CohereEmbedInput"], ns["CohereEmbedContent"]

    for prefix in ["query: ", "search_document: ", "classify: "]:
        inp = CI(content=[CC(type="text", text="hello world")])
        result = _call(fn, inp, task_prefix=prefix)

        roles = _roles(result)
        assert "system" in roles, f"prefix={prefix!r}: no system message, got roles={roles}"
        assert "user" in roles, f"prefix={prefix!r}: no user message, got roles={roles}"

        sys_texts = _texts_for_role(result, "system")
        assert any(prefix.strip().rstrip(": ") in t for t in sys_texts), (
            f"prefix={prefix!r}: system message should contain the task instruction, got {sys_texts}"
        )

        user_texts = _texts_for_role(result, "user")
        for t in user_texts:
            assert not t.startswith(prefix), (
                f"prefix={prefix!r}: user text should not be prefixed, got {t!r}"
            )


# [pr_diff] fail_to_pass
def test_mixed_content_system_prompt():
    """Mixed text+image input with task_prefix: system prompt present,
    text not prefixed, image part preserved."""
    fn, ns = _load_mixed_input_to_messages()
    CI, CC = ns["CohereEmbedInput"], ns["CohereEmbedContent"]

    inp = CI(content=[
        CC(type="text", text="describe this"),
        CC(type="image_url", image_url={"url": "http://example.com/img.png"}),
    ])
    result = _call(fn, inp, task_prefix="caption: ")

    assert "system" in _roles(result), "mixed input with prefix should have system message"
    user_texts = _texts_for_role(result, "user")
    for t in user_texts:
        assert not t.startswith("caption: "), f"user text should not be prefixed: {t!r}"
        assert t == "describe this", f"user text should be 'describe this', got {t!r}"

    # Image part preserved in user message
    user_msgs = [m for m in result if m.role == "user"]
    assert user_msgs, "should have user message"
    content = user_msgs[0].content
    assert isinstance(content, list), "user content should be a list of parts"
    image_parts = [p for p in content if hasattr(p, "image_url")]
    assert len(image_parts) >= 1, "image part should be preserved in user message"


# [pr_diff] fail_to_pass
def test_multiple_texts_not_prefixed():
    """Multiple text items with task_prefix: none should be prefixed."""
    fn, ns = _load_mixed_input_to_messages()
    CI, CC = ns["CohereEmbedInput"], ns["CohereEmbedContent"]

    inp = CI(content=[
        CC(type="text", text="first sentence"),
        CC(type="text", text="second sentence"),
    ])
    result = _call(fn, inp, task_prefix="search: ")

    assert "system" in _roles(result), "multi-text with prefix should have system message"
    user_texts = _texts_for_role(result, "user")
    for t in user_texts:
        assert not t.startswith("search: "), f"text should not be prefixed: {t!r}"
    assert "first sentence" in user_texts
    assert "second sentence" in user_texts


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_no_prefix_no_system_message():
    """Without task_prefix, no system message should be generated."""
    fn, ns = _load_mixed_input_to_messages()
    CI, CC = ns["CohereEmbedInput"], ns["CohereEmbedContent"]

    inp = CI(content=[CC(type="text", text="just text")])
    result = _call(fn, inp, task_prefix=None)

    assert "system" not in _roles(result), "no system message expected without prefix"
    assert "user" in _roles(result), "should have user message"
    user_texts = _texts_for_role(result, "user")
    assert "just text" in user_texts


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — routing: text-only with prefix uses chat path
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_has_chat_template_method():
    """The fix must add a _has_chat_template helper to EmbedIOProcessor.
    # AST-only because: EmbedIOProcessor requires GPU-bound vllm engine internals"""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "EmbedIOProcessor":
            method_names = {
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            assert "_has_chat_template" in method_names, (
                "EmbedIOProcessor must have a _has_chat_template method "
                f"(found: {sorted(method_names)})"
            )
            return
    raise AssertionError("EmbedIOProcessor class not found")


# [pr_diff] fail_to_pass
def test_preprocess_cohere_text_completion_exists():
    """The fix must extract a _preprocess_cohere_text_completion helper
    to avoid duplicating the completion proxy logic.
    # AST-only because: EmbedIOProcessor requires GPU-bound vllm engine internals"""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "EmbedIOProcessor":
            method_names = {
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            assert "_preprocess_cohere_text_completion" in method_names, (
                "EmbedIOProcessor must have a _preprocess_cohere_text_completion method "
                f"(found: {sorted(method_names)})"
            )
            return
    raise AssertionError("EmbedIOProcessor class not found")


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """_mixed_input_to_messages and _pre_process_cohere_online are not stubs."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "EmbedIOProcessor":
            methods = {
                item.name: item
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            break
    else:
        raise AssertionError("EmbedIOProcessor class not found")

    for name, min_stmts in [("_mixed_input_to_messages", 5), ("_pre_process_cohere_online", 8)]:
        assert name in methods, f"{name} not found"
        meaningful = sum(
            1 for child in ast.walk(methods[name])
            if isinstance(child, (ast.Assign, ast.AugAssign, ast.Return,
                                  ast.If, ast.For, ast.While, ast.With,
                                  ast.Assert, ast.Raise, ast.AnnAssign))
        )
        assert meaningful >= min_stmts, (
            f"{name} looks like a stub ({meaningful} statements, need >={min_stmts})"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD validation
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_spdx_header():
    """Target file must have SPDX license header (pass_to_pass)."""
    source = Path(TARGET).read_text()
    assert "SPDX-License-Identifier" in source, "Missing SPDX-License-Identifier header"
    assert "SPDX-FileCopyrightText" in source, "Missing SPDX-FileCopyrightText header"


# [repo_tests] pass_to_pass
def test_repo_imports_structure():
    """Target file has expected import structure (pass_to_pass)."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)

    # Check for expected key imports
    assert any("typing" in (i or "") for i in imports), "Missing typing imports"


# [repo_tests] pass_to_pass
def test_repo_test_file_structure():
    """Repo's embed test files exist with expected structure (pass_to_pass)."""
    test_dir = Path(REPO) / "tests" / "entrypoints" / "pooling" / "embed"
    assert test_dir.exists(), f"Test directory not found: {test_dir}"

    # Check for expected test files
    expected_files = ["test_io_processor.py", "test_protocol.py"]
    for fname in expected_files:
        fpath = test_dir / fname
        assert fpath.exists(), f"Expected test file not found: {fname}"
        # Verify it has pytest imports
        source = fpath.read_text()
        assert "import pytest" in source or "from pytest" in source, f"{fname} missing pytest import"


# [repo_tests] pass_to_pass
def test_repo_io_processor_methods_exist():
    """EmbedIOProcessor has expected method signatures (pass_to_pass)."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    expected_methods = [
        "__init__",
        "pre_process_online",
        "post_process_online",
        "_mixed_input_to_messages",
        "_pre_process_cohere_online",
        "_resolve_cohere_truncation",
    ]

    found_methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "EmbedIOProcessor":
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    found_methods.add(item.name)
            break
    else:
        raise AssertionError("EmbedIOProcessor class not found")

    for method in expected_methods:
        assert method in found_methods, f"Missing expected method: {method}"
