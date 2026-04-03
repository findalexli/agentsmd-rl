#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lotti

# Idempotent: skip if already applied
if grep -q 'RenderAbstractViewport.maybeOf' lib/features/journal/ui/widgets/entry_details_widget.dart 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git fetch origin 1da86998cfa8f8bd27483b8e698fd38d88e6193f --depth=1
git checkout 1da86998cfa8f8bd27483b8e698fd38d88e6193f -- \
  AGENTS.md \
  CLAUDE.md \
  lib/features/journal/ui/widgets/entry_details/header/entry_detail_header.dart \
  lib/features/journal/ui/widgets/entry_details_widget.dart \
  lib/widgets/misc/collapsible_section.dart

echo "Patch applied successfully."
