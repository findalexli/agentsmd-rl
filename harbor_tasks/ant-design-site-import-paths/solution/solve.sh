#!/bin/bash
set -e

cd /workspace/ant-design

echo "Applying import path fixes..."

# Fix SiteContext.ts
python3 << 'PYEOF'
import re

with open('.dumi/theme/slots/SiteContext.ts', 'r') as f:
    content = f.read()

content = content.replace(
    "import type { ConfigComponentProps } from '../../../components/config-provider/context';",
    "import type { ConfigComponentProps } from 'antd/es/config-provider/context';"
)

with open('.dumi/theme/slots/SiteContext.ts', 'w') as f:
    f.write(content)
print("Fixed SiteContext.ts")
PYEOF

# Fix DesignPreviewer.tsx
python3 << 'PYEOF'
with open('.dumi/theme/builtins/Previewer/DesignPreviewer.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    "import copy from '../../../../components/_util/copy';",
    "import copy from 'antd/lib/_util/copy';"
)

with open('.dumi/theme/builtins/Previewer/DesignPreviewer.tsx', 'w') as f:
    f.write(content)
print("Fixed DesignPreviewer.tsx")
PYEOF

# Fix PromptDrawer.tsx
python3 << 'PYEOF'
with open('.dumi/theme/common/ThemeSwitch/PromptDrawer.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    "import copy from '../../../../components/_util/copy';",
    "import copy from 'antd/lib/_util/copy';"
)

with open('.dumi/theme/common/ThemeSwitch/PromptDrawer.tsx', 'w') as f:
    f.write(content)
print("Fixed PromptDrawer.tsx")
PYEOF

# Fix Theme/index.tsx
python3 << 'PYEOF'
with open('.dumi/pages/index/components/Theme/index.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    "import copy from '../../../../../components/_util/copy';",
    "import copy from 'antd/lib/_util/copy';"
)

with open('.dumi/pages/index/components/Theme/index.tsx', 'w') as f:
    f.write(content)
print("Fixed Theme/index.tsx")
PYEOF

# Fix ThemePreview/index.tsx
python3 << 'PYEOF'
with open('.dumi/pages/index/components/ThemePreview/index.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    "import copy from '../../../../../components/_util/copy';",
    "import copy from 'antd/lib/_util/copy';"
)

with open('.dumi/pages/index/components/ThemePreview/index.tsx', 'w') as f:
    f.write(content)
print("Fixed ThemePreview/index.tsx")
PYEOF

# Fix useThemeAnimation.ts - need to remove blank line between imports
python3 << 'PYEOF'
with open('.dumi/hooks/useThemeAnimation.ts', 'r') as f:
    lines = f.readlines()

new_lines = []
prev_line = None
for line in lines:
    # Check if this is the theme import we want to replace
    if "import theme from '../../components/theme';" in line:
        # Replace with the new import (no blank line before it)
        new_lines.append("import { theme } from 'antd';\n")
        prev_line = "import { theme } from 'antd';\n"
        continue

    # Skip blank lines that come after @rc-component import and before the old theme import
    if prev_line and "@rc-component/util" in prev_line and line.strip() == '':
        # Check if next non-blank line would be the theme import we replaced
        # Since we already handled theme import, just skip consecutive blank lines
        continue

    new_lines.append(line)
    prev_line = line

# Now clean up: if there's a blank line after @rc-component and before the new antd import
final_lines = []
for i, line in enumerate(new_lines):
    if i > 0 and line.strip() == '' and 'import { theme } from' in new_lines[i-1]:
        # Skip this blank line if the previous line is the theme import
        continue
    final_lines.append(line)

with open('.dumi/hooks/useThemeAnimation.ts', 'w') as f:
    f.writelines(final_lines)
print("Fixed useThemeAnimation.ts")
PYEOF

# Fix AffixTabs.tsx
python3 << 'PYEOF'
with open('.dumi/theme/layouts/ResourceLayout/AffixTabs.tsx', 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if "import scrollTo from '../../../../components/_util/scrollTo';" in line:
        new_lines.append("import scrollTo from 'antd/lib/_util/scrollTo';\n")
        # Skip the next blank line if present
        if i + 1 < len(lines) and lines[i + 1].strip() == '':
            continue
    else:
        new_lines.append(line)

# Clean up consecutive blank lines after the scrollTo import
final_lines = []
for i, line in enumerate(new_lines):
    if i > 0 and line.strip() == '' and 'import scrollTo from' in new_lines[i-1]:
        continue
    final_lines.append(line)

with open('.dumi/theme/layouts/ResourceLayout/AffixTabs.tsx', 'w') as f:
    f.writelines(final_lines)
print("Fixed AffixTabs.tsx")
PYEOF

echo "Gold patch applied successfully"
