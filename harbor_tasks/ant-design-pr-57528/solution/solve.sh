#!/bin/bash
# Solution script for antd-popconfirm-icon-semantic task

set -e

cd /workspace/ant-design

# Check if patch already applied (idempotency)
if grep -q "classNames?.icon" components/popconfirm/PurePanel.tsx 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Use Python for reliable text replacement
python3 << 'PYTHON_SCRIPT'
import re

# ============================================
# Fix 1: Update components/popconfirm/index.tsx
# ============================================

with open('components/popconfirm/index.tsx', 'r') as f:
    content = f.read()

# Replace the import to use PopoverSemanticType instead of PopoverSemanticAllType
content = content.replace(
    "import type { PopoverProps, PopoverSemanticAllType } from '../popover';",
    "import type { PopoverProps, PopoverSemanticType } from '../popover';"
)

# Replace the simple type alias with a proper type definition
old_type = "export type PopconfirmSemanticType = PopoverSemanticAllType;"
new_type = """export type PopconfirmSemanticType = {
  classNames?: PopoverSemanticType['classNames'] & {
    icon?: string;
  };
  styles?: PopoverSemanticType['styles'] & {
    icon?: React.CSSProperties;
  };
};"""

content = content.replace(old_type, new_type)

with open('components/popconfirm/index.tsx', 'w') as f:
    f.write(content)

print("Fixed index.tsx")

# ============================================
# Fix 2: Update components/popconfirm/PurePanel.tsx
# ============================================

with open('components/popconfirm/PurePanel.tsx', 'r') as f:
    content = f.read()

# Remove the separate PopconfirmProps import and update the PopoverSemanticAllType import
content = content.replace(
    "import type { PopconfirmProps } from '.';\n",
    ""
)
content = content.replace(
    "import type { PopoverSemanticAllType } from '../popover';",
    "import type { PopconfirmProps, PopconfirmSemanticAllType } from '.';"
)

# Update OverlayProps type references
content = content.replace(
    "classNames?: PopoverSemanticAllType['classNames'];",
    "classNames?: PopconfirmSemanticAllType['classNames'];"
)
content = content.replace(
    "styles?: PopoverSemanticAllType['styles'];",
    "styles?: PopconfirmSemanticAllType['styles'];"
)

# Update the icon span to use classNames?.icon and styles?.icon
old_icon = "{icon && <span className={`${prefixCls}-message-icon`}>{icon}</span>}"
new_icon = """{icon && (
          <span
            className={clsx(`${prefixCls}-message-icon`, classNames?.icon)}
            style={styles?.icon}
          >
            {icon}
          </span>
        )}"""

content = content.replace(old_icon, new_icon)

with open('components/popconfirm/PurePanel.tsx', 'w') as f:
    f.write(content)

print("Fixed PurePanel.tsx")
print("Patch applied successfully.")
PYTHON_SCRIPT
