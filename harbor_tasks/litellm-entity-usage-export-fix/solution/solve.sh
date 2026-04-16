#!/bin/bash
set -e

# Apply the gold patch by copying pre-fetched fixed files directly
cp /solution/fixed_utils.ts /workspace/litellm-dashboard/src/components/EntityUsageExport/utils.ts
cp /solution/fixed_utils.test.ts /workspace/litellm-dashboard/src/components/EntityUsageExport/utils.test.ts

# Verify the fix was applied
grep -q "resolveEntityDisplay" /workspace/litellm-dashboard/src/components/EntityUsageExport/utils.ts