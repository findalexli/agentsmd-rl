#!/bin/bash
set -e

cd /workspace/mantine

# Create the find-element-in-shadow-dom directory
mkdir -p packages/@mantine/core/src/core/utils/find-element-in-shadow-dom

# Get the correct utility file content from the merge commit
git show c3a53eb0c345037d0b5406e925ef5a5e2926022b:packages/@mantine/core/src/core/utils/find-element-in-shadow-dom/find-element-in-shadow-dom.ts > \
   packages/@mantine/core/src/core/utils/find-element-in-shadow-dom/find-element-in-shadow-dom.ts

# Get the actual merged index.ts content
git show c3a53eb0c345037d0b5406e925ef5a5e2926022b:packages/@mantine/core/src/core/utils/index.ts > \
   packages/@mantine/core/src/core/utils/index.ts

# Get the actual merged use-combobox.ts content
git show c3a53eb0c345037d0b5406e925ef5a5e2926022b:packages/@mantine/core/src/components/Combobox/use-combobox/use-combobox.ts > \
   packages/@mantine/core/src/components/Combobox/use-combobox/use-combobox.ts

echo "Solution applied successfully"