#!/bin/bash
set -e

REPO="/workspace/playwright"

cd "$REPO"

# Patch 1: Update tab.ts to support both CSS selectors and Playwright locators
TAB_FILE="packages/playwright-core/src/tools/backend/tab.ts"

if ! grep -q "locatorOrSelectorAsSelector" "$TAB_FILE"; then
    # Add the import for locatorOrSelectorAsSelector after the asLocator import
    sed -i "/import { asLocator } from '..\/.\.\/.\.utils\/isomorphic\/locatorGenerators';/a import { locatorOrSelectorAsSelector } from '../../utils/isomorphic/locatorParser';" "$TAB_FILE"

    # The original code block is:
    #   if (param.selector) {
    #     const locator = this.page.locator(param.selector);
    #     if (!await locator.isVisible())
    #       throw new Error(`Selector ${param.selector} does not match any elements.`);
    #     return { locator, resolved: asLocator('javascript', param.selector) };
    #   }
    #
    # Replace with:
    #   if (param.selector) {
    #     const selector = locatorOrSelectorAsSelector('javascript', param.selector, this.context.config.testIdAttribute || 'data-testid');
    #     const handle = await this.page.$(selector);
    #     if (!handle)
    #       throw new Error(`"${param.selector}" does not match any elements.`);
    #     handle.dispose().catch(() => {});
    #     return { locator: this.page.locator(selector), resolved: asLocator('javascript', selector) };
    #   }

    # Use a Python script for more reliable multi-line replacement
    python3 << 'PYTHON_EOF'
import re

with open("packages/playwright-core/src/tools/backend/tab.ts", "r") as f:
    content = f.read()

# Old pattern to match
old_pattern = r'''      if \(param\.selector\) \{
        const locator = this\.page\.locator\(param\.selector\);
        if \(!await locator\.isVisible\(\)\)
          throw new Error\(`Selector \$\{param\.selector\} does not match any elements\.`\);
        return \{ locator, resolved: asLocator\('javascript', param\.selector\) \};
      \}'''

# New replacement
new_code = '''      if (param.selector) {
        const selector = locatorOrSelectorAsSelector('javascript', param.selector, this.context.config.testIdAttribute || 'data-testid');
        const handle = await this.page.$(selector);
        if (!handle)
          throw new Error(`"${param.selector}" does not match any elements.`);
        handle.dispose().catch(() => {});
        return { locator: this.page.locator(selector), resolved: asLocator('javascript', selector) };
      }'''

# Try to replace
if re.search(old_pattern, content):
    content = re.sub(old_pattern, new_code, content)
    with open("packages/playwright-core/src/tools/backend/tab.ts", "w") as f:
        f.write(content)
    print("Replaced selector handling code in tab.ts")
else:
    print("WARNING: Could not find exact pattern to replace in tab.ts")
    # Print what we're looking for
    print("Looking for pattern around 'param.selector'...")
PYTHON_EOF
fi

# Patch 2: Update SKILL.md documentation to reflect new locator support
SKILL_FILE="packages/playwright-core/src/tools/cli-client/skill/SKILL.md"

if grep -q "css or role selectors" "$SKILL_FILE"; then
    # Update the text description
    sed -i 's/You can also use css or role selectors, for example when explicitly asked for it./You can also use css selectors or Playwright locators./' "$SKILL_FILE"

    # Update the role selector example to use Playwright locator syntax
    sed -i 's/playwright-cli click "role=button\[name=Submit\]"/playwright-cli click "getByRole('\''button'\'', { name: '\''Submit'\'' })"/' "$SKILL_FILE"

    # Update the comment and remove chaining example
    sed -i 's/# role selector/# role locator/' "$SKILL_FILE"
    sed -i 's/# chaining css and role selectors/# test id/' "$SKILL_FILE"
    sed -i 's/playwright-cli click "#footer >> role=button\[name=Submit\]"/playwright-cli click "getByTestId('\''submit-button'\'')"/' "$SKILL_FILE"
fi

# Rebuild to compile the TypeScript changes
npm run build

echo "Gold patch applied successfully"
