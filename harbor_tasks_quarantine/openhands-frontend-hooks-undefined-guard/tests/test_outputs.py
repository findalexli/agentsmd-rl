"""Tests for OpenHands hooks modal undefined guards fix."""

import subprocess
import sys
import os

REPO = "/workspace/OpenHands"
FRONTEND = f"{REPO}/frontend"


def test_vitest_base():
    """Frontend vitest test framework runs without crashing (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "--run", "--reporter=dot"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )
    # Just check vitest runs without crashing - we don't care about test results
    assert "ERR_RUNTIME" not in result.stderr, f"Vitest runtime error:\n{result.stderr}"
    assert "ERR_ASSERTION" not in result.stderr, f"Vitest assertion error:\n{result.stderr}"


def test_hook_event_item_undefined_hooks():
    """HookEventItem handles undefined matcher.hooks without crashing (fail_to_pass)."""
    # Use node to evaluate the component behavior by checking the reduce implementation
    test_code = """
const fs = require('fs');
const path = '/workspace/OpenHands/frontend/src/components/features/conversation-panel/hook-event-item.tsx';
const src = fs.readFileSync(path, 'utf8');

// The bug: matcher.hooks.length throws when hooks is undefined
// Find the reduce callback that accesses matcher.hooks - must have a guard
// Look for the pattern in the multiline reduce
const lines = src.split('\\n');
let reduceStart = -1;
for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('reduce') && lines[i].includes('matcher')) {
        reduceStart = i;
        break;
    }
}

if (reduceStart === -1) {
    console.log('ERROR: could not find reduce with matcher');
    process.exit(1);
}

// Extract the reduce callback (next 2-3 lines contain the arrow function body)
let reduceCallback = '';
for (let i = reduceStart; i < Math.min(reduceStart + 4, lines.length); i++) {
    reduceCallback += lines[i] + '\\n';
}

// Check if the reduce callback has a guard for undefined hooks
const hasGuard = (
    reduceCallback.includes('?? []') ||
    reduceCallback.includes('?? 0') ||
    reduceCallback.includes('|| []') ||
    reduceCallback.includes('|| 0') ||
    reduceCallback.includes('?.') ||
    reduceCallback.includes('if ')
);

if (hasGuard) {
    console.log('SUCCESS: reduce has undefined guard');
    process.exit(0);
} else {
    console.log('ERROR: reduce lacks undefined guard in callback: ' + reduceCallback.split('\\n')[1].trim());
    process.exit(1);
}
"""
    result = subprocess.run(
        ["node", "-e", test_code],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"HookEventItem undefined guard test failed: {result.stderr[-500:]}"


def test_hook_matcher_content_undefined_hooks():
    """HookMatcherContent handles undefined matcher.hooks without crashing (fail_to_pass)."""
    test_code = """
const fs = require('fs');
const path = '/workspace/OpenHands/frontend/src/components/features/conversation-panel/hook-matcher-content.tsx';
const src = fs.readFileSync(path, 'utf8');

// Find the hooks.map call - it must have a guard
const lines = src.split('\\n');
let mapLineIdx = -1;
for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('matcher.hooks') && lines[i].includes('map')) {
        mapLineIdx = i;
        break;
    }
}

if (mapLineIdx === -1) {
    console.log('ERROR: could not find matcher.hooks.map');
    process.exit(1);
}

// Get context around the map call (might span multiple lines)
let mapContext = '';
for (let i = Math.max(0, mapLineIdx - 1); i < Math.min(lines.length, mapLineIdx + 3); i++) {
    mapContext += lines[i] + '\\n';
}

// Check if the map call has a guard
const hasGuard = (
    mapContext.includes('(matcher.hooks ?? []).map') ||
    mapContext.includes('(matcher.hooks || []).map') ||
    mapContext.includes('matcher.hooks?.map') ||
    mapContext.includes('matcher.hooks ? matcher.hooks.map')
);

if (hasGuard) {
    console.log('SUCCESS: map has undefined guard');
    process.exit(0);
} else {
    console.log('ERROR: map lacks undefined guard around line ' + (mapLineIdx + 1));
    process.exit(1);
}
"""
    result = subprocess.run(
        ["node", "-e", test_code],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"HookMatcherContent undefined guard test failed: {result.stderr[-500:]}"


def test_hooks_modal_unit_tests():
    """Repo's hooks-modal unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "__tests__/components/features/conversation-panel/hooks-modal.test.tsx", "--run", "--reporter=dot"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Hooks-modal tests failed:\n{result.stderr[-500:]}"


def test_typecheck():
    """Frontend TypeScript typecheck passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"TypeScript typecheck failed:\n{result.stderr[-500:]}"


def test_lint():
    """Frontend linting passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-500:]}"


def test_translation_completeness():
    """Translation keys have complete language coverage (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Translation check failed:\n{result.stderr[-500:]}"


def test_nullish_coalescing_or_equivalent_event_item():
    """HookEventItem reduce function guards against undefined matcher.hooks (structural)."""
    with open(f"{FRONTEND}/src/components/features/conversation-panel/hook-event-item.tsx") as f:
        content = f.read()

    # Find the reduce function and extract its callback body
    lines = content.split('\n')
    reduce_start = -1
    for i, line in enumerate(lines):
        if 'reduce' in line and 'matcher' in line:
            reduce_start = i
            break

    assert reduce_start != -1, "Could not find reduce function in HookEventItem"

    # Extract the reduce callback (it spans multiple lines)
    reduce_lines = []
    for i in range(reduce_start, min(reduce_start + 5, len(lines))):
        reduce_lines.append(lines[i])

    reduce_block = '\n'.join(reduce_lines)

    # Check for guard pattern in the reduce block
    has_guard = (
        '?? []' in reduce_block or
        '?? 0' in reduce_block or
        '|| []' in reduce_block or
        '|| 0' in reduce_block or
        '?.' in reduce_block or
        'if ' in reduce_block.lower()
    )
    assert has_guard, f"HookEventItem reduce function lacks undefined guard in: {reduce_block.strip()}"


def test_matcher_content_map_guard():
    """HookMatcherContent map call guards against undefined matcher.hooks (structural)."""
    with open(f"{FRONTEND}/src/components/features/conversation-panel/hook-matcher-content.tsx") as f:
        content = f.read()

    # Look for the hooks.map call with guard
    has_guard = (
        '(matcher.hooks ?? []).map' in content or
        '(matcher.hooks || []).map' in content or
        'matcher.hooks?.map' in content or
        'matcher.hooks ? matcher.hooks.map' in content
    )
    assert has_guard, "HookMatcherContent map call lacks undefined guard"


def test_hooks_type_optional():
    """HookMatcher type definition marks hooks as optional (structural)."""
    with open(f"{FRONTEND}/src/api/conversation-service/v1-conversation-service.types.ts") as f:
        content = f.read()

    in_interface = False
    has_optional_hooks = False
    for line in content.split('\n'):
        if 'interface HookMatcher' in line:
            in_interface = True
        if in_interface and 'hooks' in line:
            if 'hooks?:' in line or 'hooks?.' in line:
                has_optional_hooks = True
                break
            elif 'hooks:' in line and '?:' not in line and '?.' not in line:
                has_optional_hooks = False
                break

    assert has_optional_hooks, "HookMatcher interface hooks field is not marked as optional (hooks?: or hooks?.)"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))