#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency check: if _get_auto_docstring_names already exists, patch is applied
if grep -q '_get_auto_docstring_names' utils/check_docstrings.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/tests/repo_utils/test_check_docstrings.py b/tests/repo_utils/test_check_docstrings.py
index f761514a084d..0fafd386d4f2 100644
--- a/tests/repo_utils/test_check_docstrings.py
+++ b/tests/repo_utils/test_check_docstrings.py
@@ -12,16 +12,26 @@
 # See the License for the specific language governing permissions and
 # limitations under the License.

+import ast
 import inspect
 import os
 import sys
+import tempfile
+import textwrap
 import unittest


 git_repo_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
 sys.path.append(os.path.join(git_repo_path, "utils"))

-from check_docstrings import get_default_description, replace_default_in_arg_description  # noqa: E402
+from check_docstrings import (  # noqa: E402
+    _build_ast_indexes,
+    _find_typed_dict_classes,
+    _get_auto_docstring_names,
+    get_default_description,
+    has_auto_docstring_decorator,
+    replace_default_in_arg_description,
+)


 class CheckDostringsTested(unittest.TestCase):
@@ -96,3 +106,242 @@ def _fake_function(a, b: int, c=1, d: float = 2.0, e: str = "blob"):
         assert get_default_description(params["c"]) == "`<fill_type>`, *optional*, defaults to 1"
         assert get_default_description(params["d"]) == "`float`, *optional*, defaults to 2.0"
         assert get_default_description(params["e"]) == '`str`, *optional*, defaults to `"blob"`'
+
+
+class TestGetAutoDocstringNames(unittest.TestCase):
+    """Tests for _get_auto_docstring_names and has_auto_docstring_decorator."""
+
+    def setUp(self):
+        self.cache = {}
+
+    def _write_temp(self, source):
+        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
+            f.write(source)
+        self.addCleanup(os.unlink, f.name)
+        return f.name
+
+    def test_detects_simple_decorator(self):
+        """Test that a class decorated with @auto_docstring is detected."""
+        path = self._write_temp(
+            textwrap.dedent("""\
+            from transformers import auto_docstring
+
+            @auto_docstring
+            class Foo:
+                pass
+        """)
+        )
+        names = _get_auto_docstring_names(path, cache=self.cache)
+        self.assertEqual(names, {"Foo"})
+
+    def test_detects_decorator_with_call(self):
+        """Test that a class decorated with @auto_docstring(args) (called form) is detected."""
+        path = self._write_temp(
+            textwrap.dedent("""\
+            @auto_docstring(custom_args='x')
+            class Bar:
+                pass
+        """)
+        )
+        names = _get_auto_docstring_names(path, cache=self.cache)
+        self.assertEqual(names, {"Bar"})
+
+    def test_ignores_other_decorators(self):
+        """Test that classes with non-auto_docstring decorators are not detected."""
+        path = self._write_temp(
+            textwrap.dedent("""\
+            @dataclass
+            class Baz:
+                pass
+        """)
+        )
+        names = _get_auto_docstring_names(path, cache=self.cache)
+        self.assertEqual(names, set())
+
+    def test_multiple_classes(self):
+        """Test that only decorated classes and functions are returned when multiple definitions exist."""
+        path = self._write_temp(
+            textwrap.dedent("""\
+            @auto_docstring
+            class A:
+                pass
+
+            class B:
+                pass
+
+            @auto_docstring()
+            def func_c():
+                pass
+        """)
+        )
+        names = _get_auto_docstring_names(path, cache=self.cache)
+        self.assertEqual(names, {"A", "func_c"})
+
+    def test_caching(self):
+        """Test that repeated calls for the same file return the cached (identical) result object."""
+        path = self._write_temp(
+            textwrap.dedent("""\
+            @auto_docstring
+            class X:
+                pass
+        """)
+        )
+        result1 = _get_auto_docstring_names(path, cache=self.cache)
+        result2 = _get_auto_docstring_names(path, cache=self.cache)
+        self.assertIs(result1, result2)
+
+    def test_syntax_error_returns_empty(self):
+        """Test that a file with a syntax error returns an empty set instead of raising."""
+        path = self._write_temp("def broken(\n")
+        names = _get_auto_docstring_names(path, cache=self.cache)
+        self.assertEqual(names, set())
+
+    def test_has_auto_docstring_decorator_uses_cache(self):
+        """Test that has_auto_docstring_decorator looks up names from the pre-populated cache."""
+        from unittest.mock import patch
+
+        path = self._write_temp(
+            textwrap.dedent("""\
+            @auto_docstring
+            class Cached:
+                pass
+        """)
+        )
+        self.cache[path] = {"Cached"}
+
+        # Create classes whose __name__ matches/doesn't match the cache
+        Cached = type("Cached", (), {})
+        Other = type("Other", (), {})
+
+        with patch.object(inspect, "getfile", return_value=path):
+            self.assertTrue(has_auto_docstring_decorator(Cached, cache=self.cache))
+            self.assertFalse(has_auto_docstring_decorator(Other, cache=self.cache))
+
+
+class TestBuildAstIndexes(unittest.TestCase):
+    """Tests for _build_ast_indexes with pre-parsed tree."""
+
+    def test_finds_decorated_items(self):
+        """Test that _build_ast_indexes finds a decorated class and extracts its __init__ args."""
+        source = textwrap.dedent("""\
+            @auto_docstring
+            class MyModel:
+                def __init__(self, hidden_size=768):
+                    self.hidden_size = hidden_size
+        """)
+        items = _build_ast_indexes(source)
+        self.assertEqual(len(items), 1)
+        self.assertEqual(items[0].name, "MyModel")
+        self.assertEqual(items[0].kind, "class")
+        self.assertIn("hidden_size", items[0].args)
+
+    def test_shared_tree(self):
+        """Test that passing a pre-parsed AST tree produces the same results as letting the function parse internally."""
+        source = textwrap.dedent("""\
+            @auto_docstring
+            class A:
+                pass
+        """)
+        tree = ast.parse(source)
+        items_with_tree = _build_ast_indexes(source, tree=tree)
+        items_without = _build_ast_indexes(source)
+        self.assertEqual(len(items_with_tree), len(items_without))
+        self.assertEqual(items_with_tree[0].name, items_without[0].name)
+
+    def test_no_decorated_items(self):
+        """Test that a class without the auto_docstring decorator is not indexed."""
+        source = textwrap.dedent("""\
+            class Plain:
+                pass
+        """)
+        items = _build_ast_indexes(source)
+        self.assertEqual(items, [])
+
+    def test_function_decorated(self):
+        """Test that a decorated function is indexed with its arguments."""
+        source = textwrap.dedent("""\
+            @auto_docstring
+            def my_func(x, y=10):
+                pass
+        """)
+        items = _build_ast_indexes(source)
+        self.assertEqual(len(items), 1)
+        self.assertEqual(items[0].name, "my_func")
+        self.assertEqual(items[0].kind, "function")
+        self.assertIn("x", items[0].args)
+        self.assertIn("y", items[0].args)
+
+    def test_custom_args_from_variable(self):
+        """Test that custom_args passed as a module-level variable are resolved to their string value."""
+        source = textwrap.dedent("""\
+            MY_ARGS = "custom param docs"
+
+            @auto_docstring(custom_args=MY_ARGS)
+            class WithCustom:
+                def __init__(self):
+                    pass
+        """)
+        items = _build_ast_indexes(source)
+        self.assertEqual(len(items), 1)
+        self.assertEqual(items[0].custom_args_text, "custom param docs")
+
+
+class TestFindTypedDictClasses(unittest.TestCase):
+    """Tests for _find_typed_dict_classes with pre-parsed tree."""
+
+    def test_finds_typed_dict(self):
+        """Test that a TypedDict subclass is found and its public fields are extracted."""
+        source = textwrap.dedent("""\
+            from typing import TypedDict
+
+            class MyKwargs(TypedDict):
+                field_a: str
+                field_b: int
+        """)
+        result = _find_typed_dict_classes(source)
+        self.assertEqual(len(result), 1)
+        self.assertEqual(result[0]["name"], "MyKwargs")
+        self.assertIn("field_a", result[0]["all_fields"])
+        self.assertIn("field_b", result[0]["all_fields"])
+
+    def test_shared_tree(self):
+        """Test that passing a pre-parsed AST tree produces the same results as internal parsing."""
+        source = textwrap.dedent("""\
+            class MyKwargs(TypedDict):
+                x: int
+        """)
+        tree = ast.parse(source)
+        r1 = _find_typed_dict_classes(source, tree=tree)
+        r2 = _find_typed_dict_classes(source)
+        self.assertEqual(len(r1), len(r2))
+        self.assertEqual(r1[0]["name"], r2[0]["name"])
+
+    def test_skips_standard_kwargs(self):
+        """Test that well-known kwargs TypedDicts (e.g. TextKwargs) are excluded from results."""
+        source = textwrap.dedent("""\
+            class TextKwargs(TypedDict):
+                field: str
+        """)
+        result = _find_typed_dict_classes(source)
+        self.assertEqual(result, [])
+
+    def test_no_typed_dicts(self):
+        """Test that source with no TypedDict subclasses returns an empty list."""
+        source = textwrap.dedent("""\
+            class Regular:
+                pass
+        """)
+        result = _find_typed_dict_classes(source)
+        self.assertEqual(result, [])
+
+    def test_skips_private_fields(self):
+        """Test that fields starting with an underscore are excluded from the extracted TypedDict fields."""
+        source = textwrap.dedent("""\
+            class MyKwargs(TypedDict):
+                public: int
+                _private: str
+        """)
+        result = _find_typed_dict_classes(source)
+        self.assertEqual(len(result), 1)
+        self.assertIn("public", result[0]["all_fields"])
+        self.assertNotIn("_private", result[0]["all_fields"])
diff --git a/utils/check_docstrings.py b/utils/check_docstrings.py
index 245ee407f198..582e9fb513b1 100644
--- a/utils/check_docstrings.py
+++ b/utils/check_docstrings.py
@@ -385,21 +385,45 @@ class DecoratedItem:
 }


-def has_auto_docstring_decorator(obj) -> bool:
+def _get_auto_docstring_names(file_path: str, cache: dict[str, set[str]] | None = None) -> set[str]:
+    """
+    Parse a source file once and return the set of class/function names decorated with @auto_docstring.
+    Walks top-level definitions and one level into class bodies (methods).
+    Results can be cached per file path.
+    """
+    if cache is not None and file_path in cache:
+        return cache[file_path]
+
+    names = set()
     try:
-        # Get the source lines for the object
-        source_lines = inspect.getsourcelines(obj)[0]
-
-        # Check the lines before the definition for @auto_docstring decorator
-        for line in source_lines[:10]:  # Check first 10 lines (decorators come before def/class)
-            line = line.strip()
-            if line.startswith("@auto_docstring"):
-                return True
-    except (TypeError, OSError):
-        # Some objects don't have source code available
+        with open(file_path) as f:
+            source = f.read()
+        tree = ast.parse(source, filename=file_path)
+        for node in tree.body:
+            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
+                if any(_is_auto_docstring_decorator(dec) for dec in node.decorator_list):
+                    names.add(node.name)
+                # Also check methods inside classes
+                if isinstance(node, ast.ClassDef):
+                    for class_item in node.body:
+                        if isinstance(class_item, (ast.FunctionDef, ast.AsyncFunctionDef)):
+                            if any(_is_auto_docstring_decorator(dec) for dec in class_item.decorator_list):
+                                names.add(class_item.name)
+    except (OSError, SyntaxError):
         pass

-    return False
+    if cache is not None:
+        cache[file_path] = names
+    return names
+
+
+def has_auto_docstring_decorator(obj, cache: dict[str, set[str]] | None = None) -> bool:
+    try:
+        source_file = inspect.getfile(obj)
+    except (TypeError, OSError):
+        return False
+    decorated_names = _get_auto_docstring_names(source_file, cache=cache)
+    return obj.__name__ in decorated_names


 def find_indent(line: str) -> int:
@@ -1359,13 +1383,14 @@ def generate_new_docstring_for_class(
     )


-def _build_ast_indexes(source: str) -> list[DecoratedItem]:
+def _build_ast_indexes(source: str, tree: ast.Module | None = None) -> list[DecoratedItem]:
     """Parse source once and return list of all @auto_docstring decorated items.

     Returns:
         List of DecoratedItem objects, one for each @auto_docstring decorated function or class.
     """
-    tree = ast.parse(source)
+    if tree is None:
+        tree = ast.parse(source)
     # First pass: collect top-level string variables (for resolving custom_args variable references)
     var_to_string: dict[str, str] = {}
     for node in tree.body:
@@ -1380,9 +1405,9 @@ def _build_ast_indexes(source: str) -> list[DecoratedItem]:
             if isinstance(node.value.value, str) and isinstance(node.target, ast.Name):
                 var_to_string[node.target.id] = node.value.value
     # Second pass: find all @auto_docstring decorated functions/classes
-    # First, identify processor classes to track method context
+    # First, identify processor classes to track method context (only top-level classes)
     processor_classes: set[str] = set()
-    for node in ast.walk(tree):
+    for node in tree.body:
         if isinstance(node, ast.ClassDef):
             for base in node.bases:
                 if isinstance(base, ast.Name) and ("ProcessorMixin" in base.id or "Processor" in base.id):
@@ -1525,7 +1550,7 @@ def _extract_type_name(annotation) -> str | None:
     return None


-def _find_typed_dict_classes(source: str) -> list[dict]:
+def _find_typed_dict_classes(source: str, tree: ast.Module | None = None) -> list[dict]:
     """
     Find all custom TypedDict kwargs classes in the source.

@@ -1534,7 +1559,8 @@ def _find_typed_dict_classes(source: str) -> list[dict]:
         - fields: fields that need custom documentation (not in standard args, not nested TypedDicts)
         - all_fields: all fields including those in standard args (for redundancy checking)
     """
-    tree = ast.parse(source)
+    if tree is None:
+        tree = ast.parse(source)

     # Get standard args that are already documented in source classes
     standard_args = set()
@@ -1543,32 +1569,21 @@ def _find_typed_dict_classes(source: str) -> list[dict]:
     except Exception as e:
         logger.debug(f"Could not get standard args from source: {e}")

-    # Collect all TypedDict class names first (for excluding nested TypedDicts)
+    # Collect TypedDict class names and nodes (TypedDicts are always top-level)
     typed_dict_names = set()
-    for node in ast.walk(tree):
+    typed_dict_nodes = []
+    for node in tree.body:
         if isinstance(node, ast.ClassDef):
             for base in node.bases:
                 if isinstance(base, ast.Name) and ("TypedDict" in base.id or "Kwargs" in base.id):
                     typed_dict_names.add(node.name)
+                    typed_dict_nodes.append(node)
                     break

     typed_dicts = []

     # Check each TypedDict class
-    for node in ast.walk(tree):
-        if not isinstance(node, ast.ClassDef):
-            continue
-
-        # Check if this is a TypedDict
-        is_typed_dict = False
-        for base in node.bases:
-            if isinstance(base, ast.Name) and ("TypedDict" in base.id or "Kwargs" in base.id):
-                is_typed_dict = True
-                break
-
-        if not is_typed_dict:
-            continue
-
+    for node in typed_dict_nodes:
         # Skip standard kwargs classes
         if node.name in ["TextKwargs", "ImagesKwargs", "VideosKwargs", "AudioKwargs", "ProcessingKwargs"]:
             continue
@@ -1632,6 +1647,7 @@ def _find_typed_dict_classes(source: str) -> list[dict]:
 def _process_typed_dict_docstrings(
     candidate_file: str,
     overwrite: bool = False,
+    tree: ast.Module | None = None,
 ) -> tuple[list[str], list[str], list[str]]:
     """
     Check and optionally fix TypedDict docstrings.
@@ -1640,6 +1656,7 @@ def _process_typed_dict_docstrings(
     Args:
         candidate_file: Path to the file to process
         overwrite: Whether to fix issues by writing to the file
+        tree: Pre-parsed AST tree to avoid re-parsing the file

     Returns:
         Tuple of (missing_warnings, fill_warnings, redundant_warnings)
@@ -1647,7 +1664,7 @@ def _process_typed_dict_docstrings(
     with open(candidate_file, "r", encoding="utf-8") as f:
         content = f.read()

-    typed_dicts = _find_typed_dict_classes(content)
+    typed_dicts = _find_typed_dict_classes(content, tree=tree)
     if not typed_dicts:
         return [], [], []

@@ -1925,11 +1942,20 @@ def update_file_with_new_docstrings(
     )


-def check_auto_docstrings(overwrite: bool = False, check_all: bool = False):
+def check_auto_docstrings(overwrite: bool = False, check_all: bool = False, cache: dict[str, set[str]] | None = None):
     """
     Check docstrings of all public objects that are decorated with `@auto_docstrings`.
     This function orchestrates the process by finding relevant files, scanning for decorators,
     generating new docstrings, and updating files as needed.
+
+    Args:
+        overwrite (`bool`, *optional*, defaults to `False`):
+            Whether to fix inconsistencies or not.
+        check_all (`bool`, *optional*, defaults to `False`):
+            Whether to check all files.
+        cache (Dictionary `str` to `Set[str]`, *optional*):
+            To speed up auto-docstring detection if it was previously called on a file, the cache of all previously
+            computed results.
     """
     # 1. Find all model files to check
     matching_files = find_matching_model_files(check_all)
@@ -1947,8 +1973,12 @@ def check_auto_docstrings(overwrite: bool = False, check_all: bool = False):
             content = f.read()
         lines = content.split("\n")

-        # Parse file once to find all @auto_docstring decorated items
-        decorated_items = _build_ast_indexes(content)
+        # Parse file once and share the AST tree across all analysis passes
+        tree = ast.parse(content)
+        decorated_items = _build_ast_indexes(content, tree=tree)
+
+        # Warm the cache so check_docstrings() won't re-parse this file
+        _get_auto_docstring_names(candidate_file, cache=cache)

         missing_docstring_args_warnings = []
         fill_docstring_args_warnings = []
@@ -1975,7 +2005,7 @@ def check_auto_docstrings(overwrite: bool = False, check_all: bool = False):
         # Process TypedDict kwargs (separate pass to avoid line number conflicts)
         # This runs AFTER @auto_docstring processing is complete
         typed_dict_missing_warnings, typed_dict_fill_warnings, typed_dict_redundant_warnings = (
-            _process_typed_dict_docstrings(candidate_file, overwrite=overwrite)
+            _process_typed_dict_docstrings(candidate_file, overwrite=overwrite, tree=tree)
         )

         # Report TypedDict errors
@@ -2035,7 +2065,7 @@ def check_auto_docstrings(overwrite: bool = False, check_all: bool = False):
         )


-def check_docstrings(overwrite: bool = False, check_all: bool = False):
+def check_docstrings(overwrite: bool = False, check_all: bool = False, cache: dict[str, set[str]] | None = None):
     """
     Check docstrings of all public objects that are callables and are documented. By default, only checks the diff.

@@ -2044,6 +2074,9 @@ def check_docstrings(overwrite: bool = False, check_all: bool = False):
             Whether to fix inconsistencies or not.
         check_all (`bool`, *optional*, defaults to `False`):
             Whether to check all files.
+        cache (Dictionary `str` to `Set[str]`, *optional*):
+            To speed up auto-docstring detection if it was previously called on a file, the cache of all previously
+            computed results.
     """
     module_diff_files = None
     if not check_all:
@@ -2077,10 +2110,6 @@ def check_docstrings(overwrite: bool = False, check_all: bool = False):
         if not callable(obj) or not isinstance(obj, type) or getattr(obj, "__doc__", None) is None:
             continue

-        # Skip objects decorated with @auto_docstring - they have auto-generated documentation
-        if has_auto_docstring_decorator(obj):
-            continue
-
         # If we are checking against the diff, we skip objects that are not part of the diff.
         if module_diff_files is not None:
             object_file = find_source_file(getattr(transformers, name))
@@ -2088,6 +2117,10 @@ def check_docstrings(overwrite: bool = False, check_all: bool = False):
             if object_file_relative_path not in module_diff_files:
                 continue

+        # Skip objects decorated with @auto_docstring - they have auto-generated documentation
+        if has_auto_docstring_decorator(obj, cache=cache):
+            continue
+
         # Check docstring
         try:
             result = match_docstring_with_signature(obj)
@@ -2142,5 +2175,6 @@ def check_docstrings(overwrite: bool = False, check_all: bool = False):
         "--check_all", action="store_true", help="Whether to check all files. By default, only checks the diff"
     )
     args = parser.parse_args()
-    check_auto_docstrings(overwrite=args.fix_and_overwrite, check_all=args.check_all)
-    check_docstrings(overwrite=args.fix_and_overwrite, check_all=args.check_all)
+    auto_docstring_cache: dict[str, set[str]] = {}
+    check_auto_docstrings(overwrite=args.fix_and_overwrite, check_all=args.check_all, cache=auto_docstring_cache)
+    check_docstrings(overwrite=args.fix_and_overwrite, check_all=args.check_all, cache=auto_docstring_cache)

PATCH

echo "Patch applied successfully."
