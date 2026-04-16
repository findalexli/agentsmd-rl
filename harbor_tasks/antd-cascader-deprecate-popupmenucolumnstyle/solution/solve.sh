#!/bin/bash
set -e

cd /workspace/ant-design

# Update components/cascader/index.tsx
# 1. Update JSDoc for dropdownMenuColumnStyle to reference styles.popup.listItem
sed -i "s/@deprecated Please use \`popupMenuColumnStyle\` instead/@deprecated Please use \`styles.popup.listItem\` instead/g" components/cascader/index.tsx

# 2. Add JSDoc for popupMenuColumnStyle (add deprecation comment)
sed -i '/popupMenuColumnStyle\?: React.CSSProperties;/i\  /** @deprecated Please use \`styles.popup.listItem\` instead */' components/cascader/index.tsx

# 3. Update deprecation mapping: dropdownMenuColumnStyle -> styles.popup.listItem
sed -i "s/dropdownMenuColumnStyle: 'popupMenuColumnStyle'/dropdownMenuColumnStyle: 'styles.popup.listItem',\n      popupMenuColumnStyle: 'styles.popup.listItem'/g" components/cascader/index.tsx

# Update English documentation
sed -i "s/use \`popupMenuColumnStyle\` instead/use \`styles.popup.listItem\` instead/g" components/cascader/index.en-US.md
sed -i "s/| popupMenuColumnStyle | The style of the drop-down menu column |/| ~~popupMenuColumnStyle~~ | The style of the drop-down menu column, use \`styles.popup.listItem\` instead |/g" components/cascader/index.en-US.md

# Update Chinese documentation
sed -i "s/请使用 \`popupMenuColumnStyle\` 替换/请使用 \`styles.popup.listItem\` 替换/g" components/cascader/index.zh-CN.md
sed -i "s/| popupMenuColumnStyle | 下拉菜单列的样式 |/| ~~popupMenuColumnStyle~~ | 下拉菜单列的样式，请使用 \`styles.popup.listItem\` 替换 |/g" components/cascader/index.zh-CN.md

# Update migration docs (English and Chinese)
sed -i "s/\`dropdownMenuColumnStyle\` is deprecated and replaced by \`popupMenuColumnStyle\`./\`dropdownMenuColumnStyle\` is deprecated and replaced by \`styles.popup.listItem\`./g" docs/react/migration-v6.en-US.md
sed -i "s/\`dropdownMenuColumnStyle\` 弃用，变为 \`popupMenuColumnStyle\`./\`dropdownMenuColumnStyle\` 弃用，变为 \`styles.popup.listItem\`./g" docs/react/migration-v6.zh-CN.md

# Update unit test expectation - it should expect the new deprecation message
sed -i "s/Warning: \[antd: Cascader\] \`dropdownMenuColumnStyle\` is deprecated. Please use \`popupMenuColumnStyle\` instead./Warning: [antd: Cascader] \`dropdownMenuColumnStyle\` is deprecated. Please use \`styles.popup.listItem\` instead./g" components/cascader/__tests__/index.test.tsx

echo "Patch applied successfully"
