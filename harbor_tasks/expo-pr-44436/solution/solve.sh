#!/bin/bash
set -e

cd /workspace/expo

# Apply the gold patch (patch command handles fuzz better than git apply)
patch -p1 --fuzz=3 < /solution/gold.patch

# Verify idempotency: check the unique method name is present
grep -q "define_singleton_method(:generate_available_uuid_list)" packages/expo-modules-autolinking/scripts/ios/cocoapods/installer.rb