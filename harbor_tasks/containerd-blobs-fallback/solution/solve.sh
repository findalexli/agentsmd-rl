#!/bin/sh
# Apply the gold patch for containerd/containerd#13017

cd /workspace/containerd

# Check if already applied
if grep -q "firstErrPriority > 2" core/remotes/docker/resolver.go; then
    echo "Patch already applied"
    exit 0
fi

# Insert the fix after the "for _, u := range paths {" line
# The fix prevents falling back to /blobs on transient errors
sed -i '/^\tfor _, u := range paths {$/a\
\
\t\t// falling back to /blobs endpoint should happen in extreme cases - those to\n\t\t// support legacy registries. we want to limit the fallback to when /manifests endpoint\n\t\t// returned 404. Falling back on transient errors could do more harm, like polluting\n\t\t// the local content store with incorrectly typed descriptors as /blobs endpoint tends\n\t\t// always return with application/octet-stream.\n\t\tif firstErrPriority > 2 {\n\t\t\tbreak\n\t\t}' core/remotes/docker/resolver.go

if [ $? -eq 0 ]; then
    echo "Patch applied successfully"
else
    echo "Failed to apply patch"
    exit 1
fi
