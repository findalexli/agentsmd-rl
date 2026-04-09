#!/bin/bash
set -e

cd /workspace/ant-design

# Idempotency check
if grep -q "'&:first-child':" components/notification/style/index.ts; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply fixes using Python for reliable text manipulation
python3 << 'EOF'
import re

# Fix 1: PurePanel.tsx - wrap title div in conditional
with open('components/notification/PurePanel.tsx', 'r') as f:
    content = f.read()

# Replace unconditional title div with conditional
old_pattern = r'''(\s+return \(\s+<div className=\{clsx\(\{ \[`\$\{prefixCls\}-with-icon`\]: iconNode \}\)\} role=\{role\}>)\s+\{iconNode\}\s+<div className=\{clsx\(`\$\{prefixCls\}-title`, pureContentCls\.title\)\} style=\{styles\.title\}>\s+\{title\}\s+</div>'''
new_replacement = r'''\1
      {iconNode}
      {
        title && (
          <div className={clsx(`${prefixCls}-title`, pureContentCls.title)} style={styles.title}>
            {title}
          </div>
        )
      }'''

content = re.sub(old_pattern, new_replacement, content)

with open('components/notification/PurePanel.tsx', 'w') as f:
    f.write(content)

print("PurePanel.tsx updated")

# Fix 2: style/index.ts - add &:first-child rule
with open('components/notification/style/index.ts', 'r') as f:
    content = f.read()

# Find the description block and add the first-child rule
old_pattern = r"(\[`\$\{noticeCls\}-description`\]: \{\s+fontSize,\s+color: colorText,\s+marginTop: token\.marginXS,)\s+(\},)"
new_replacement = r'''\1

      '&:first-child': {
        marginTop: 0,
        marginInlineEnd: token.marginSM,
      },
    },'''

content = re.sub(old_pattern, new_replacement, content)

with open('components/notification/style/index.ts', 'w') as f:
    f.write(content)

print("style/index.ts updated")

# Fix 3: Add blank line in test file
with open('components/notification/__tests__/index.test.tsx', 'r') as f:
    content = f.read()

# Add blank line after the specific test
old_pattern = r"(expect\(document\.querySelectorAll\('\.ant-notification-description'\)\.length\)\.toBe\(0\);\s+\}\))(\s+describe\('When closeIcon is null)"
new_replacement = r'''\1

  describe('When closeIcon is null'''

content = re.sub(old_pattern, new_replacement, content)

with open('components/notification/__tests__/index.test.tsx', 'w') as f:
    f.write(content)

print("index.test.tsx updated")
print("All fixes applied successfully")
EOF

echo "Patch applied successfully"
