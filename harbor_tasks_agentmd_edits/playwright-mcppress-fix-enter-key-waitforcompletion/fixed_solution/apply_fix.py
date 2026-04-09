import re

# Fix keyboard.ts
with open('/workspace/playwright/packages/playwright/src/mcp/browser/tools/keyboard.ts', 'r') as f:
    content = f.read()

old_press_handler = '''  handle: async (tab, params, response) => {
    response.addCode(`// Press ${params.key}`);
    response.addCode(`await page.keyboard.press('${params.key}');`);
    await tab.page.keyboard.press(params.key);
  },'''

new_press_handler = '''  handle: async (tab, params, response) => {
    response.addCode(`// Press ${params.key}`);
    response.addCode(`await page.keyboard.press('${params.key}');`);
    if (params.key === 'Enter') {
      response.setIncludeSnapshot();
      await tab.waitForCompletion(async () => {
        await tab.page.keyboard.press('Enter');
      });
    } else {
      await tab.page.keyboard.press(params.key);
    }
  },'''

if old_press_handler in content:
    content = content.replace(old_press_handler, new_press_handler)
    with open('/workspace/playwright/packages/playwright/src/mcp/browser/tools/keyboard.ts', 'w') as f:
        f.write(content)
    print('keyboard.ts fixed successfully')
else:
    print('ERROR: Could not find pattern in keyboard.ts')
    # Show what we're looking for vs what's there
    print('Looking for:')
    print(repr(old_press_handler[:100]))

# Fix SKILL.md
with open('/workspace/playwright/packages/playwright/src/mcp/terminal/SKILL.md', 'r') as f:
    content = f.read()

old_workflow = '''## Core workflow

1. Navigate: `playwright-cli open https://example.com`
2. Snapshot: `playwright-cli snapshot` (returns elements with refs like `ref=e1`, `ref=e2`)
3. Interact using refs from the snapshot
4. Re-snapshot after navigation or significant DOM changes'''

new_workflow = '''## Core workflow

1. Navigate: `playwright-cli open https://example.com`
2. Interact using refs from the snapshot
3. Re-snapshot after significant changes'''

if old_workflow in content:
    content = content.replace(old_workflow, new_workflow)
    with open('/workspace/playwright/packages/playwright/src/mcp/terminal/SKILL.md', 'w') as f:
        f.write(content)
    print('SKILL.md fixed successfully')
else:
    print('ERROR: Could not find pattern in SKILL.md')
