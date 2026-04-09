#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'export const enableViewTransition: boolean = true;' packages/shared/forks/ReactFeatureFlags.native-fb.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Update the three flag files using sed with correct line numbers
sed -i 's/export const enableViewTransition: boolean = false;/export const enableViewTransition: boolean = true;/' packages/shared/forks/ReactFeatureFlags.native-fb.js
sed -i 's/export const enableViewTransition = false;/export const enableViewTransition = true;/' packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js
sed -i 's/export const enableViewTransition: boolean = false;/export const enableViewTransition: boolean = true;/' packages/shared/forks/ReactFeatureFlags.test-renderer.www.js

echo "Patch applied successfully."
