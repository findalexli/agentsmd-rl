# chore: updating unit testing cursor rules to prevent unnecessary mocking

Source: [MetaMask/metamask-mobile#25396](https://github.com/MetaMask/metamask-mobile/pull/25396)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/unit-testing-guidelines.mdc`

## What to add / change

## **Description**

Updated the Cursor rules for unit testing guidelines to focus on **testID-specific guidance** rather than prescribing general mocking philosophy. This change addresses team feedback about respecting MetaMask's support for both sociable and solitary unit testing approaches.

**Key changes:**

1. **Focused on testID usage** - Guidelines now specifically address the anti-pattern of mocking components just to inject testIDs
2. **Prefer data test IDs** - Added guidance to always use \`testID\` props for element selection instead of fragile text-based queries
3. **Prefer \`toBeOnTheScreen()\`** - Discourage weak matchers like \`toBeTruthy()\` and \`toBeDefined()\` for element assertions
4. **Child prop objects** - Document that ALL design system and component library components support testID via child prop objects (\`closeButtonProps\`, \`iconProps\`, etc.)
5. **Removed prescriptive mocking guidance** - No longer prescribes "avoid over-mocking" or "prefer real implementations" to respect different testing approaches

### Context from Team Discussion

From the Slack thread:
- **Joao**: MetaMask supports both sociable and solitary unit tests - shouldn't prescribe one over the other
- **Brian**: The specific problem is Cursor mocking components just to inject testIDs when components already support them
- **Nico**: Guidelines should be specific to testID usage, not general mocking philosophy

### Research Findings
- **84 test files** currently mock \`@metamask/des

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
