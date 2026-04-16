#!/bin/sh
set -e

cd /workspace/hugo

# Fix 1: Update video ID in vimeo.html template (55073825 -> 19899678)
sed -i 's/55073825/19899678/g' tpl/tplimpl/embedded/templates/_shortcodes/vimeo.html

# Fix 2: Update video ID in the test file
sed -i 's/55073825/19899678/g' tpl/tplimpl/shortcodes_integration_test.go

# Fix 3: Update expected hash values for regular mode
sed -i 's/82566e6b8d04b53e/31c54d7f8c54f73d/g' tpl/tplimpl/shortcodes_integration_test.go
sed -i 's/2b5f9cc3167d1336/7c073565f380599b/g' tpl/tplimpl/shortcodes_integration_test.go

# Fix 4: Update expected hash for simple mode
sed -i 's/04d861fc957ee638/fb22905d5b100a5a/g' tpl/tplimpl/shortcodes_integration_test.go

# Fix 5: Uncomment the simple mode tests
# Remove the comment line
sed -i '/Commented out for now, see issue #14649/d' tpl/tplimpl/shortcodes_integration_test.go
# Remove the /* that starts the commented block
sed -i 's|/\*files = strings.ReplaceAll|files = strings.ReplaceAll|g' tpl/tplimpl/shortcodes_integration_test.go
# Remove the */ at the end
sed -i 's|b.AssertLogContains.*unable to retrieve.*\*/|b.AssertLogContains(`WARN  The "vimeo" shortcode was unable to retrieve the remote data.`)|g' tpl/tplimpl/shortcodes_integration_test.go

# Idempotency check: verify the patch was applied
grep -q "19899678" tpl/tplimpl/embedded/templates/_shortcodes/vimeo.html || exit 1
grep -q "fb22905d5b100a5a" tpl/tplimpl/shortcodes_integration_test.go || exit 1

echo "Patch applied successfully"
