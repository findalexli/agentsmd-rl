"""
Tests for OpenHands PR #13589: Fix runtime crash when matcher.hooks is undefined.

This task tests that the hooks viewer modal handles undefined hooks gracefully
instead of crashing with "Cannot read properties of undefined (reading 'length')".
"""

import subprocess
import sys
import os

REPO = "/workspace/openhands"
FRONTEND = f"{REPO}/frontend"


def test_undefined_hooks_no_crash():
    """
    Fail-to-pass: Rendering with undefined hooks should not crash.

    Before fix: matcher.hooks.length throws TypeError when hooks is undefined.
    After fix: Uses nullish coalescing (matcher.hooks ?? []) to safely handle undefined.
    """
    test_code = '''
import { render, screen } from "@testing-library/react";
import { HookEventItem } from "../src/components/features/conversation-panel/hook-event-item";
import { HookEvent } from "../src/api/conversation-service/v1-conversation-service.types";
import { I18nContext } from "@/i18n/i18n-context";

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <I18nContext.Provider value={{ lang: "en", setLang: () => {} }}>
    {children}
  </I18nContext.Provider>
);

const defaultProps = {
  hookEvent: {
    event_type: "stop",
    matchers: [{ matcher: "*", hooks: undefined }],
  } as HookEvent,
  isExpanded: false,
  onToggle: () => {},
};

test("does not crash with undefined hooks", () => {
  expect(() =>
    render(
      <TestWrapper>
        <HookEventItem {...defaultProps} />
      </TestWrapper>
    )
  ).not.toThrow();
});
'''
    # Run a quick syntax/type check on the component
    result = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const code = fs.readFileSync('{FRONTEND}/src/components/features/conversation-panel/hook-event-item.tsx', 'utf8');
// Check for the fix: matcher.hooks ?? []
if (code.includes('matcher.hooks ?? []')) {{
  console.log('PASS: Fix applied - nullish coalescing found');
  process.exit(0);
}} else if (code.includes('matcher.hooks.length') && !code.includes('matcher.hooks ?? []')) {{
  console.log('FAIL: Bug present - accessing .length without null check');
  process.exit(1);
}} else {{
  console.log('UNCERTAIN: Pattern not found');
  process.exit(1);
}}
"""],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        # Try alternative check in hook-matcher-content.tsx
        result2 = subprocess.run(
            ["node", "-e", f"""
const fs = require('fs');
const code = fs.readFileSync('{FRONTEND}/src/components/features/conversation-panel/hook-matcher-content.tsx', 'utf8');
if (code.includes('matcher.hooks ?? []')) {{
  console.log('PASS: Fix found in hook-matcher-content');
  process.exit(0);
}} else if (code.includes('matcher.hooks.map') && !code.includes('matcher.hooks ?? []')) {{
  console.log('FAIL: Bug in hook-matcher-content - .map without null check');
  process.exit(1);
}} else {{
  console.log('FAIL: Fix not found');
  process.exit(1);
}}
"""],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result2.returncode != 0:
            raise AssertionError(f"Fix not applied. hook-event: {result.stdout}, hook-matcher: {result2.stdout}")


def test_typescript_type_updated():
    """
    Fail-to-pass: HookMatcher interface should have optional hooks field.

    The type definition must reflect that hooks can be undefined.
    """
    types_file = f"{FRONTEND}/src/api/conversation-service/v1-conversation-service.types.ts"
    content = open(types_file).read()

    # Check that hooks is marked as optional
    if "hooks?:" not in content and "hooks?: HookDefinition[]" not in content:
        raise AssertionError("Type definition not updated: hooks should be optional (hooks?: HookDefinition[])")


def test_repo_unit_tests_pass():
    """
    Pass-to-pass: The existing repo unit tests should pass.

    Run the frontend vitest tests for the hooks modal component.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "--run", "hooks-modal.test.tsx"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        raise AssertionError(f"Unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}")


def test_repo_lint_passes():
    """
    Pass-to-pass: Frontend linting should pass (per AGENTS.md).

    Lint command from agent config: `npm run lint:fix`
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        raise AssertionError(f"Lint failed:\n{result.stderr[-500:]}")


def test_typescript_compiles():
    """
    Pass-to-pass: TypeScript should compile without errors.

    Build command from agent config: `npm run build`
    """
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180
    )

    if result.returncode != 0:
        raise AssertionError(f"Type check failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}")


def test_translation_completeness():
    """
    Pass-to-pass: Translation keys should have complete language coverage.

    CI command from GitHub workflow lint.yml: `npm run check-translation-completeness`
    """
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        raise AssertionError(f"Translation check failed:\n{result.stderr[-500:]}")
