#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lotti

# Idempotent: skip if already applied
if grep -q 'ProjectTasksSliverPanel' lib/features/projects/ui/widgets/project_tasks_panel.dart 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git fetch origin e0ed1461a20edea9ea57c49fda29fb89d72d7882 --depth=1
git checkout e0ed1461a20edea9ea57c49fda29fb89d72d7882 -- \
  lib/features/projects/README.md \
  lib/features/projects/ui/widgets/project_mobile_detail_content.dart \
  lib/features/projects/ui/widgets/project_tasks_panel.dart

echo "Patch applied successfully."
