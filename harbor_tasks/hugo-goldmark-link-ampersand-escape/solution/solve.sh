#!/bin/bash
set -e

cd /workspace/hugo

# Check if already applied (idempotency check)
if grep -q "util.EscapeHTML(util.EscapeHTML(dest))" markup/goldmark/render_hooks.go 2>/dev/null; then
    echo "Fix not yet applied. Applying patch..."
else
    # Check if the fix is already in place
    if grep -q "_, _ = w.Write(util.EscapeHTML(dest))" markup/goldmark/render_hooks.go 2>/dev/null; then
        # Could be the fixed version, check for double-escape pattern
        if ! grep -q "util.EscapeHTML(util.EscapeHTML(dest))" markup/goldmark/render_hooks.go 2>/dev/null; then
            echo "Fix already applied."
            exit 0
        fi
    fi
fi

# Apply the fix using sed
sed -i 's/util\.EscapeHTML(util\.EscapeHTML(dest))/util.EscapeHTML(dest)/g' markup/goldmark/render_hooks.go

echo "Fix applied successfully."
