#!/bin/bash
set -e

REPO="/workspace/hugo"
cd "$REPO"

# Check if already patched (idempotency check)
if grep -q "owner-write permission" commands/server.go 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the fix using sed - replace the old chmodFilter with the new one
# First, find the line number of the chmodFilter function
echo "Applying chmodFilter fix..."

# Read the file and replace the chmodFilter function
python3 << 'PYEOF'
import re

with open("commands/server.go", "r") as f:
    content = f.read()

# Define the old function pattern
old_func = '''func chmodFilter(dst, src os.FileInfo) bool {
	// Hugo publishes data from multiple sources, potentially
	// with overlapping directory structures. We cannot sync permissions
	// for directories as that would mean that we might end up with write-protected
	// directories inside /public.
	// One example of this would be syncing from the Go Module cache,
	// which have 0555 directories.
	return src.IsDir()
}'''

# Define the new function
new_func = '''// chmodFilter is a ChmodFilter for static syncing.
// Returns true to skip syncing permissions for directories and files without
// owner-write permission. The primary use case is files from the module cache (0444).
func chmodFilter(dst, src os.FileInfo) bool {
	if src.IsDir() {
		return true
	}
	return src.Mode().Perm()&0o200 == 0
}'''

# Check if the old function exists
if old_func not in content:
    # Try to match a more flexible pattern
    print("Warning: Exact old function not found, trying to find chmodFilter...")
    # Find and replace using regex
    pattern = r'func chmodFilter\(dst, src os\.FileInfo\) bool \{[^}]+return src\.IsDir\(\)[^}]*\}'
    if not re.search(pattern, content):
        print("ERROR: Could not find chmodFilter function to replace")
        exit(1)
    new_content = re.sub(pattern, new_func, content, flags=re.DOTALL)
else:
    new_content = content.replace(old_func, new_func)

with open("commands/server.go", "w") as f:
    f.write(new_content)

print("chmodFilter fix applied successfully!")
PYEOF

echo "Patch applied successfully"
