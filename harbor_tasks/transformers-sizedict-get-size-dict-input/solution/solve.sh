#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if SizeDict is already handled in get_size_dict, skip
if grep -q 'isinstance(size, dict | SizeDict)' src/transformers/image_processing_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/image_processing_utils.py b/src/transformers/image_processing_utils.py
index dcdb46603d7e..64191c6e19f4 100644
--- a/src/transformers/image_processing_utils.py
+++ b/src/transformers/image_processing_utils.py
@@ -547,8 +547,11 @@ def is_valid_size_dict(size_dict):


 def convert_to_size_dict(
-    size, max_size: int | None = None, default_to_square: bool = True, height_width_order: bool = True
-):
+    size: int | Iterable[int] | None = None,
+    max_size: int | None = None,
+    default_to_square: bool = True,
+    height_width_order: bool = True,
+) -> dict[str, int]:
     # By default, if size is an int we assume it represents a tuple of (size, size).
     if isinstance(size, int) and default_to_square:
         if max_size is not None:
@@ -575,7 +578,7 @@ def convert_to_size_dict(


 def get_size_dict(
-    size: int | Iterable[int] | dict[str, int] | None = None,
+    size: int | Iterable[int] | dict[str, int] | SizeDict | None = None,
     max_size: int | None = None,
     height_width_order: bool = True,
     default_to_square: bool = True,
@@ -591,23 +594,29 @@ def get_size_dict(
     - If `size` is an int, and `default_to_square` is `True`, it is converted to `{"height": size, "width": size}`.
     - If `size` is an int and `default_to_square` is False, it is converted to `{"shortest_edge": size}`. If `max_size`
       is set, it is added to the dict as `{"longest_edge": max_size}`.
+    - If `size` is `None` and `default_to_square` is False, the result is `{"longest_edge": max_size}` (requires
+      `max_size` to be set). Tuple/list/SizeDict/dict `size` values do not use `max_size`.

     Args:
-        size (`int | Iterable[int] | dict[str, int]`, *optional*):
+        size (`int | Iterable[int] | dict[str, int] | SizeDict`, *optional*):
             The `size` parameter to be cast into a size dictionary.
         max_size (`int | None`, *optional*):
-            The `max_size` parameter to be cast into a size dictionary.
+            With `default_to_square=False`, sets `longest_edge` when `size` is an int or `None`; unused for dict,
+            `SizeDict`, or tuple/list `size`. Raises if set with `default_to_square=True` when `size` is an int or `None`.
         height_width_order (`bool`, *optional*, defaults to `True`):
             If `size` is a tuple, whether it's in (height, width) or (width, height) order.
         default_to_square (`bool`, *optional*, defaults to `True`):
             If `size` is an int, whether to default to a square image or not.
     """
-    if not isinstance(size, dict):
+    if not isinstance(size, dict | SizeDict):
         size_dict = convert_to_size_dict(size, max_size, default_to_square, height_width_order)
         logger.info(
-            f"{param_name} should be a dictionary on of the following set of keys: {VALID_SIZE_DICT_KEYS}, got {size}."
+            f"{param_name} should be a dictionary with one of the following sets of keys: {VALID_SIZE_DICT_KEYS}, got {size}."
             f" Converted to {size_dict}.",
         )
+    # Some remote code bypasses or overrides `_standardize_kwargs`, so handle `SizeDict` `size` here too.
+    elif isinstance(size, SizeDict):
+        size_dict = dict(size)
     else:
         size_dict = size

PATCH

echo "Patch applied successfully."
