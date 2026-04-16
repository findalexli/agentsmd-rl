#!/bin/bash
set -e

cd /workspace/hugo

# Use Python for reliable file modification
cat > /tmp/apply_patch.py << 'PYEOF'
import re

# Read the file
with open('tpl/internal/templatefuncsRegistry.go', 'r') as f:
    content = f.read()

# 1. Add "go/ast" import after "fmt"
content = content.replace(
    '"fmt"',
    '"fmt"\n\t"go/ast"'
)

# 2. Replace parser.ParseDir with parseDir helper
# Using actual tab characters
old_code = '''d, err := parser.ParseDir(fset, packagePath, nil, parser.ParseComments)
\t\t\tif err != nil {
\t\t\t\tlog.Fatal(err)
\t\t\t}

\t\t\tfor _, f := range d {
\t\t\t\tp := doc.New(f, "./", 0)'''

new_code = '''astFiles, err := parseDir(fset, packagePath)
\t\t\tif err != nil {
\t\t\t\tlog.Fatal(err)
\t\t\t}

\t\t\tif len(astFiles) > 0 {
\t\t\t\tp, err := doc.NewFromFiles(fset, astFiles, "./")
\t\t\t\tif err != nil {
\t\t\t\t\tlog.Fatal(err)
\t\t\t\t}'''

content = content.replace(old_code, new_code)

# Write intermediate result
with open('tpl/internal/templatefuncsRegistry.go', 'w') as f:
    f.write(content)

print("Phase 1 complete - replaced ParseDir and doc.New")
PYEOF

python3 /tmp/apply_patch.py

# 3. Add parseDir function at the end
cat > /tmp/add_func.py << 'PYEOF'
import re

with open('tpl/internal/templatefuncsRegistry.go', 'r') as f:
    content = f.read()

# Define the parseDir function with proper tabs
parse_func = '''\n\nfunc parseDir(fset *token.FileSet, dir string) ([]*ast.File, error) {
\tentries, err := os.ReadDir(dir)
\tif err != nil {
\t\treturn nil, err
\t}
\tvar files []*ast.File
\tfor _, e := range entries {
\t\tif e.IsDir() || !strings.HasSuffix(e.Name(), ".go") {
\t\t\tcontinue
\t\t}
\t\tf, err := parser.ParseFile(fset, filepath.Join(dir, e.Name()), nil, parser.ParseComments)
\t\tif err != nil {
\t\t\treturn nil, err
\t\t}
\t\tfiles = append(files, f)
\t}
\treturn files, nil
}
'''

# Add the function at the end of the file
if content.rstrip().endswith('}'):
    content = content.rstrip() + parse_func
else:
    content = content.rstrip() + '\n' + parse_func

with open('tpl/internal/templatefuncsRegistry.go', 'w') as f:
    f.write(content)

print("Phase 2 complete - added parseDir function")
PYEOF

python3 /tmp/add_func.py

# Verify the patch was applied
echo "=== Verifying patch ==="
if grep -q '"go/ast"' tpl/internal/templatefuncsRegistry.go; then
    echo "✓ go/ast import added"
else
    echo "✗ go/ast import missing"
    exit 1
fi

if grep -q 'func parseDir(fset \*token.FileSet, dir string)' tpl/internal/templatefuncsRegistry.go; then
    echo "✓ parseDir function added"
else
    echo "✗ parseDir function missing"
    exit 1
fi

if grep -q 'doc.NewFromFiles' tpl/internal/templatefuncsRegistry.go; then
    echo "✓ doc.NewFromFiles used"
else
    echo "✗ doc.NewFromFiles not used"
    exit 1
fi

if grep -q 'parser.ParseDir' tpl/internal/templatefuncsRegistry.go; then
    echo "✗ parser.ParseDir still present"
    exit 1
else
    echo "✓ parser.ParseDir removed"
fi

if grep -q 'doc.New(f,' tpl/internal/templatefuncsRegistry.go; then
    echo "✗ doc.New still present"
    exit 1
else
    echo "✓ doc.New removed"
fi

echo "Patch applied successfully!"
