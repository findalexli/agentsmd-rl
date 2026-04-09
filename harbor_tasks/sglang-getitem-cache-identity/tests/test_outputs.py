"""
Task: sglang-getitem-cache-identity
Repo: sglang @ ef2d4013d77cf1267e032d7a7a745dc3a6f74880
PR:   22184

Tests that GenerateReqInput and EmbeddingReqInput cache sub-objects
returned by __getitem__ to ensure identity stability.
"""

import ast
from pathlib import Path

REPO = "/workspace/sglang"


def _get_io_struct_path():
    """Get path to io_struct.py"""
    return Path(f"{REPO}/python/sglang/srt/managers/io_struct.py")


def _get_tokenizer_manager_path():
    """Get path to tokenizer_manager.py"""
    return Path(f"{REPO}/python/sglang/srt/managers/tokenizer_manager.py")


def _find_class_and_method(tree, class_name, method_name):
    """Find a method in a class in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    return item
    return None


def _method_contains_pattern(method_node, pattern):
    """Check if method source contains a pattern string."""
    method_src = ast.unparse(method_node)
    return pattern in method_src


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified files must parse without errors."""
    io_struct_path = _get_io_struct_path()
    tokenizer_manager_path = _get_tokenizer_manager_path()

    # Check io_struct.py parses
    src = io_struct_path.read_text()
    ast.parse(src)

    # Check tokenizer_manager.py parses
    src2 = tokenizer_manager_path.read_text()
    ast.parse(src2)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via AST inspection
# ---------------------------------------------------------------------------

def test_generate_req_caching_implemented():
    """GenerateReqInput.__getitem__ implements identity caching with _sub_obj_cache."""
    io_struct_path = _get_io_struct_path()
    src = io_struct_path.read_text()
    tree = ast.parse(src)

    method = _find_class_and_method(tree, "GenerateReqInput", "__getitem__")
    assert method is not None, "GenerateReqInput.__getitem__ method not found"

    method_src = ast.unparse(method)

    # Check for the caching logic pattern
    assert "_sub_obj_cache" in method_src, (
        "GenerateReqInput.__getitem__ must use _sub_obj_cache for caching"
    )
    assert "setdefault" in method_src, (
        "GenerateReqInput.__getitem__ must use setdefault to initialize cache"
    )
    assert "cache[" in method_src or "cache.get" in method_src, (
        "GenerateReqInput.__getitem__ must check cache before creating sub-object"
    )
    # Should store in cache before returning
    assert "cache[i]" in method_src, (
        "GenerateReqInput.__getitem__ must store sub-object in cache[i]"
    )


def test_embedding_req_caching_implemented():
    """EmbeddingReqInput.__getitem__ implements identity caching with _sub_obj_cache."""
    io_struct_path = _get_io_struct_path()
    src = io_struct_path.read_text()
    tree = ast.parse(src)

    method = _find_class_and_method(tree, "EmbeddingReqInput", "__getitem__")
    assert method is not None, "EmbeddingReqInput.__getitem__ method not found"

    method_src = ast.unparse(method)

    # Check for the caching logic pattern
    assert "_sub_obj_cache" in method_src, (
        "EmbeddingReqInput.__getitem__ must use _sub_obj_cache for caching"
    )
    assert "setdefault" in method_src, (
        "EmbeddingReqInput.__getitem__ must use setdefault to initialize cache"
    )
    assert "cache[" in method_src or "cache.get" in method_src, (
        "EmbeddingReqInput.__getitem__ must check cache before creating sub-object"
    )
    # Should store in cache before returning
    assert "cache[i]" in method_src, (
        "EmbeddingReqInput.__getitem__ must store sub-object in cache[i]"
    )


def test_lora_id_propagation_to_cached_subobjects():
    """tokenizer_manager._resolve_lora_path propagates lora_id to cached sub-objects."""
    tokenizer_manager_path = _get_tokenizer_manager_path()
    src = tokenizer_manager_path.read_text()
    tree = ast.parse(src)

    # Find the _resolve_lora_path method (it's an async method, so AsyncFunctionDef)
    method = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_resolve_lora_path":
            method = node
            break

    assert method is not None, "_resolve_lora_path method not found"

    method_src = ast.unparse(method)

    # Check for propagation logic
    assert "_sub_obj_cache" in method_src, (
        "_resolve_lora_path must access _sub_obj_cache to propagate lora_id"
    )
    assert "lora_id" in method_src, (
        "_resolve_lora_path must handle lora_id assignment to sub-objects"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

def test_not_stub():
    """Modified __getitem__ methods have real caching logic, not just return statements."""
    io_struct_path = _get_io_struct_path()
    src = io_struct_path.read_text()
    tree = ast.parse(src)

    # Find GenerateReqInput class and its __getitem__ method
    found_generate_cache_logic = False
    found_embedding_cache_logic = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name == "GenerateReqInput":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__getitem__":
                        # Check for _sub_obj_cache reference in the method body
                        method_src = ast.unparse(item)
                        if "_sub_obj_cache" in method_src and "cache" in method_src:
                            found_generate_cache_logic = True

            elif node.name == "EmbeddingReqInput":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__getitem__":
                        # Check for _sub_obj_cache reference in the method body
                        method_src = ast.unparse(item)
                        if "_sub_obj_cache" in method_src and "cache" in method_src:
                            found_embedding_cache_logic = True

    assert found_generate_cache_logic, (
        "GenerateReqInput.__getitem__ must have _sub_obj_cache caching logic"
    )
    assert found_embedding_cache_logic, (
        "EmbeddingReqInput.__getitem__ must have _sub_obj_cache caching logic"
    )
