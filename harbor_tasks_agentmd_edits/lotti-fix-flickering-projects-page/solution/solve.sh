#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lotti

# Idempotent: skip if already applied
if grep -q 'skipLoadingOnReload: true' lib/features/projects/ui/pages/project_details_page.dart 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git fetch origin fda7c15b3cd6b88a3d9d258d458ce202f4b025c8 --depth=1
git checkout fda7c15b3cd6b88a3d9d258d458ce202f4b025c8 -- \
  lib/features/projects/ui/pages/project_details_page.dart \
  lib/features/projects/README.md

echo "Patch applied successfully."
