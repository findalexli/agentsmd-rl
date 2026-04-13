# Fix extract_config_hunks to handle renamed files in diff

The `extract_config_hunks` function in `taskforge/config.py` does not correctly handle diffs that contain renamed files. When a file is renamed (e.g., `diff --git a/old.md b/new.md`), the current implementation may:

1. Incorrectly extract the old filename instead of the new one
2. Miss config file hunks when the rename causes path confusion

Update the `extract_config_hunks` function to correctly handle renamed files in git diffs. The function should:
- Use the NEW filename (b/ path) consistently for tracking hunks
- Correctly identify config files even when renamed
- Preserve all existing functionality for non-renamed files

## Example

For a diff like:
```diff
diff --git a/old_name.md b/new_name.md
rename from old_name.md
rename to new_name.md
--- /dev/null
+++ b/new_name.md
@@ -0,0 +1 @@
+# New content
```

The function should return `{"new_name.md": "<full_hunk_text>"}` (assuming new_name.md matches config patterns).

## Files to modify

- `taskforge/config.py`: Fix the `extract_config_hunks` function

## Testing

Create behavioral tests that:
1. Test the function with real diffs containing renamed files
2. Test that the function correctly identifies config files after rename
3. Ensure existing non-rename functionality still works
