#!/bin/bash
set -e

cd /workspace/ant-design

# Check if patch was already applied (idempotency check)
if grep -q "marginInlineEnd: token.marginSM," components/notification/style/index.ts; then
    echo "Patch already applied, skipping..."
    exit 0
fi

echo "Applying fix to PurePanel.tsx..."

# Fix PurePanel.tsx - conditionally render title
# Use sed to replace the title div with conditional rendering
cat > /tmp/purepanel_fix.py << 'EOF'
import re

with open('components/notification/PurePanel.tsx', 'r') as f:
    content = f.read()

# Pattern to find and replace the title div
old_pattern = r'<div className=\{clsx\(`\$\{prefixCls\}-title`, pureContentCls\.title\)\} style=\{styles\.title\}>\s*\{title\}\s*</div>'
new_code = '''{
        title && (
          <div className={clsx(`${prefixCls}-title`, pureContentCls.title)} style={styles.title}>
            {title}
          </div>
        )
      }'''

content = re.sub(old_pattern, new_code, content)

with open('components/notification/PurePanel.tsx', 'w') as f:
    f.write(content)

print("PurePanel.tsx updated successfully")
EOF
python3 /tmp/purepanel_fix.py

echo "Applying fix to style/index.ts..."

# Fix style/index.ts - add &:first-child rule for description
cat > /tmp/style_fix.py << 'EOF'
import re

with open('components/notification/style/index.ts', 'r') as f:
    content = f.read()

# Find the description section and add the first-child rule
old_pattern = r"(\[`\$\{noticeCls\}-description`\]:\s*\{\s*fontSize,\s*color: colorText,\s*marginTop: token\.marginXS,)"
new_code = r'''\1

      '&:first-child': {
        marginTop: 0,
        marginInlineEnd: token.marginSM,
      },'''

content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)

with open('components/notification/style/index.ts', 'w') as f:
    f.write(content)

print("style/index.ts updated successfully")
EOF
python3 /tmp/style_fix.py

echo "Patch applied successfully"
