#!/bin/bash
set -e

cd /workspace/containerd

# Remove deprecated Int type file
rm -f internal/cri/setutils/int.go

# Remove deprecated String type file
rm -f internal/cri/setutils/string.go

# Remove the cast function from set.go
sed -i '/^\/\/ cast transforms specified set to generic Set\[T\]\.$/,/^func cast\[T comparable\](s map\[T\]Empty) Set\[T\] { return s }$/d' internal/cri/setutils/set.go
# Also remove the blank line left behind
sed -i '/^$/N;/^\n$/d' internal/cri/setutils/set.go

# Update MergeStringSlices to use generic Set
sed -i 's/set := setutils.NewString(a...)/return setutils.New(a...).Insert(b...).UnsortedList()/' internal/cri/util/strings.go
sed -i '/set.Insert(b...)/d' internal/cri/util/strings.go
sed -i '/return set.UnsortedList()/d' internal/cri/util/strings.go

# Verify changes
if [ -f internal/cri/setutils/int.go ]; then
    echo "ERROR: int.go still exists"
    exit 1
fi
if [ -f internal/cri/setutils/string.go ]; then
    echo "ERROR: string.go still exists"
    exit 1
fi
echo "Gold solution applied successfully"
