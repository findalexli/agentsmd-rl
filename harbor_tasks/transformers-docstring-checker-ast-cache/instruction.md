# Performance: Docstring checker is slow due to redundant AST parsing

## Problem

The `utils/check_docstrings.py` utility script is significantly slower than it needs to be. When running `python utils/check_docstrings.py --check_all`, the script takes roughly 2-3x longer than expected.

The root causes are:

1. **Redundant AST parsing**: Several internal functions (`_build_ast_indexes`, `_find_typed_dict_classes`, `_process_typed_dict_docstrings`) each call `ast.parse()` independently on the same source content. When processing a single file, the same source string gets parsed into an AST tree multiple times instead of being parsed once and shared.

2. **Inefficient decorator detection**: The `has_auto_docstring_decorator()` function uses `inspect.getsourcelines()` to read source lines for *every single object* it checks. This is extremely slow because it re-reads and re-parses the file for each callable. A much better approach would be to parse each source file once, extract the set of decorated names, and cache that result.

3. **Unnecessary full-tree walks**: Functions like `_find_typed_dict_classes` and the processor-class detection in `_build_ast_indexes` use `ast.walk(tree)` to traverse the entire AST, including deeply nested nodes. However, the entities they're looking for (TypedDict classes, processor classes) are always defined at the module's top level, so a full recursive walk is overkill.

4. **No shared state between checker passes**: The two main entry points (`check_auto_docstrings` and `check_docstrings`) both independently determine which objects have the `@auto_docstring` decorator, with no way to share results between them.

## Relevant files

- `utils/check_docstrings.py` — the main utility
  - `has_auto_docstring_decorator()` (~line 388)
  - `_build_ast_indexes()` (~line 1362)
  - `_find_typed_dict_classes()` (~line 1528)
  - `_process_typed_dict_docstrings()` (~line 1635)
  - `check_auto_docstrings()` (~line 1928)
  - `check_docstrings()` (~line 2038)

## Expected outcome

Refactor the checker to:
- Parse each file's AST once and share the tree across all analysis passes
- Replace per-object `inspect.getsourcelines()` decorator detection with a file-level AST scan that caches results
- Limit AST traversal scope where only top-level definitions are relevant
- Allow the two main checker functions to share a cache of decorator detection results

The refactoring should be backward-compatible — all functions should continue to work when called without the new optional parameters.
