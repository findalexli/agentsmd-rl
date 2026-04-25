#!/bin/bash
set -e

cd /workspace/mantine

# Create directory for new utility
mkdir -p packages/@mantine/core/src/core/utils/get-single-element-child

# Get the fixed files from the merge commit
git show 57df830379fae3bb58ff3daa47442eeeb2689c69:packages/@mantine/core/src/core/utils/get-single-element-child/get-single-element-child.ts > packages/@mantine/core/src/core/utils/get-single-element-child/get-single-element-child.ts

# Update the index file
INDEX_CONTENT=$(git show 57df830379fae3bb58ff3daa47442eeeb2689c69:packages/@mantine/core/src/core/utils/index.ts)
echo "$INDEX_CONTENT" > packages/@mantine/core/src/core/utils/index.ts

# Update all the component files
for file in \
    packages/@mantine/core/src/components/Combobox/ComboboxEventsTarget/ComboboxEventsTarget.tsx \
    packages/@mantine/core/src/components/Combobox/ComboboxTarget/ComboboxTarget.tsx \
    packages/@mantine/core/src/components/FocusTrap/FocusTrap.tsx \
    packages/@mantine/core/src/components/HoverCard/HoverCardTarget/HoverCardTarget.tsx \
    packages/@mantine/core/src/components/Menu/MenuTarget/MenuTarget.tsx \
    packages/@mantine/core/src/components/Popover/PopoverTarget/PopoverTarget.tsx \
    packages/@mantine/core/src/components/Tooltip/Tooltip.tsx \
    packages/@mantine/core/src/components/Tooltip/TooltipFloating/TooltipFloating.tsx
do
    mkdir -p "$(dirname "$file")"
    git show 57df830379fae3bb58ff3daa47442eeeb2689c69:$file > "$file"
done

echo "All fixed files applied from merge commit"