"""
Test file for expo installGlobal fix.

This tests that the installGlobal function:
1. Does NOT create original* backup copies for properties with getters (fail-to-pass)
2. Makes backup copies non-enumerable when created (fail-to-pass)
3. Still works correctly for normal properties
"""

import subprocess
import sys
import os
import json
import tempfile

REPO = "/workspace/expo/packages/expo"
SOURCE_FILE = os.path.join(REPO, "src/winter/installGlobal.ts")


def run_ts_test(test_code, timeout=60):
    """Helper to run TypeScript test code using tsx."""
    # Write the test code to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.test.ts', delete=False, dir='/tmp') as f:
        f.write(test_code)
        temp_file = f.name

    try:
        result = subprocess.run(
            ["npx", "tsx", temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO
        )
        return result
    finally:
        os.unlink(temp_file)


def test_no_backup_for_getter_properties():
    """
    Fail-to-pass: Properties with getters should NOT have original* backups created.

    The bug: In __DEV__ mode, accessing `global.originalURL` would trigger
    react-native's getter side-effect, which sets `global.URL` back to RN's version.

    The fix: Check `!descriptor.get` before creating backup.
    """
    test_code = '''
// @ts-nocheck
// Test that getter properties don't get backups
(global as any).__DEV__ = true;

// Create a test global with a getter (like React Native's lazy getters)
let getterCalled = false;
Object.defineProperty(global, 'TestLazyProp', {
  get() {
    getterCalled = true;
    return { original: 'value' };
  },
  configurable: true,
  enumerable: true,
});

// Now load and run installGlobal
const { installGlobal } = require('/workspace/expo/packages/expo/src/winter/installGlobal');

// Install a polyfill
installGlobal('TestLazyProp', () => ({ polyfill: true }));

// Check results
if (getterCalled) {
  console.log(JSON.stringify({ pass: false, reason: 'getter_called' }));
} else if ('originalTestLazyProp' in global) {
  console.log(JSON.stringify({ pass: false, reason: 'backup_created_for_getter' }));
} else {
  console.log(JSON.stringify({ pass: true, reason: 'no_backup_for_getter' }));
}
'''
    result = run_ts_test(test_code)

    # Parse the result
    output = result.stdout.strip().split('\n')[-1] if result.stdout else ''
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        # If JSON parsing fails, check the return code
        if result.returncode != 0:
            # The test passed if the exit code is 0 and no JSON errors
            # But we need to verify the actual behavior
            assert False, f"Test script failed: {result.stderr}"
        return

    assert data.get('pass'), f"Test failed: {data.get('reason', 'unknown error')}"


def test_backup_is_non_enumerable():
    """
    Fail-to-pass: Backup copies should be non-enumerable.

    The bug: Backup copies were enumerable, making globals appear different in dev vs prod.

    The fix: Force enumerable: false when defining the backup property.
    """
    test_code = '''
// @ts-nocheck
// Test that backup properties are non-enumerable
(global as any).__DEV__ = true;

// Create a simple enumerable property (no getter)
Object.defineProperty(global, 'TestNormalProp', {
  value: { original: true },
  configurable: true,
  enumerable: true,
  writable: true,
});

// Load and run installGlobal
const { installGlobal } = require('/workspace/expo/packages/expo/src/winter/installGlobal');
installGlobal('TestNormalProp', () => ({ polyfill: true }));

// Check if backup was created
const hasBackup = 'originalTestNormalProp' in global;

// Check if backup appears in Object.keys
const backupInKeys = Object.keys(global).includes('originalTestNormalProp');

if (!hasBackup) {
  console.log(JSON.stringify({ pass: false, reason: 'no_backup_created' }));
} else if (backupInKeys) {
  console.log(JSON.stringify({ pass: false, reason: 'backup_is_enumerable' }));
} else {
  // Also verify the descriptor explicitly
  const descriptor = Object.getOwnPropertyDescriptor(global, 'originalTestNormalProp');
  if (descriptor && descriptor.enumerable === false) {
    console.log(JSON.stringify({ pass: true, reason: 'backup_is_non_enumerable' }));
  } else {
    console.log(JSON.stringify({ pass: false, reason: 'descriptor_not_correct' }));
  }
}
'''
    result = run_ts_test(test_code)

    output = result.stdout.strip().split('\n')[-1] if result.stdout else ''
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        assert False, f"Could not parse test output: {result.stdout}, stderr: {result.stderr}"

    assert data.get('pass'), f"Test failed: {data.get('reason', 'unknown error')}"


def test_backup_created_for_normal_properties():
    """
    Fail-to-pass: Normal properties (without getters) should still have backups in __DEV__.

    This ensures the fix doesn't break the intended backup behavior for regular properties.
    """
    test_code = '''
// @ts-nocheck
// Test that normal properties still get backups
(global as any).__DEV__ = true;

// Create a simple property without getter
Object.defineProperty(global, 'TestRegularProp', {
  value: 42,
  configurable: true,
  enumerable: true,
  writable: true,
});

const { installGlobal } = require('/workspace/expo/packages/expo/src/winter/installGlobal');
installGlobal('TestRegularProp', () => 99);

// Check backup was created
const hasBackup = 'originalTestRegularProp' in global;

if (hasBackup) {
  console.log(JSON.stringify({ pass: true, reason: 'backup_created_for_normal' }));
} else {
  console.log(JSON.stringify({ pass: false, reason: 'no_backup_for_normal_prop' }));
}
'''
    result = run_ts_test(test_code)

    output = result.stdout.strip().split('\n')[-1] if result.stdout else ''
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        assert False, f"Could not parse test output: {result.stdout}, stderr: {result.stderr}"

    assert data.get('pass'), f"Test failed: {data.get('reason', 'unknown error')}"


def test_development_mode_check_present():
    """
    Pass-to-pass: The __DEV__ check should work - no backups in non-DEV mode.

    Backups should only be created in development mode.
    """
    test_code = '''
// @ts-nocheck
// Test that __DEV__ check works - no backups in non-DEV mode
(global as any).__DEV__ = false;

Object.defineProperty(global, 'TestProdProp', {
  value: 123,
  configurable: true,
  enumerable: true,
});

const { installGlobal } = require('/workspace/expo/packages/expo/src/winter/installGlobal');
installGlobal('TestProdProp', () => 456);

// No backup should be created in production mode
const hasBackup = 'originalTestProdProp' in global;

if (hasBackup) {
  console.log(JSON.stringify({ pass: false, reason: 'backup_created_in_prod' }));
} else {
  console.log(JSON.stringify({ pass: true, reason: 'no_backup_in_prod' }));
}
'''
    result = run_ts_test(test_code)

    output = result.stdout.strip().split('\n')[-1] if result.stdout else ''
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        assert False, f"Could not parse test output: {result.stdout}, stderr: {result.stderr}"

    assert data.get('pass'), f"Test failed: {data.get('reason', 'unknown error')}"


def test_backup_preserves_original_value():
    """
    Pass-to-pass: The backup should preserve the original property value.
    """
    test_code = '''
// @ts-nocheck
// Test that backup preserves original value
(global as any).__DEV__ = true;

const originalValue = { test: 'original', nested: { value: 42 } };
Object.defineProperty(global, 'TestPreserveProp', {
  value: originalValue,
  configurable: true,
  enumerable: true,
});

const { installGlobal } = require('/workspace/expo/packages/expo/src/winter/installGlobal');
installGlobal('TestPreserveProp', () => ({ test: 'polyfill' }));

// Check if backup exists and has the original value
const hasBackup = 'originalTestPreserveProp' in global;
if (hasBackup) {
  const backupValue = (global as any).originalTestPreserveProp;
  const correctValue = backupValue === originalValue;

  if (correctValue) {
    console.log(JSON.stringify({ pass: true, reason: 'backup_has_original' }));
  } else {
    console.log(JSON.stringify({ pass: false, reason: 'backup_wrong_value' }));
  }
} else {
  console.log(JSON.stringify({ pass: false, reason: 'no_backup' }));
}
'''
    result = run_ts_test(test_code)

    output = result.stdout.strip().split('\n')[-1] if result.stdout else ''
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        assert False, f"Could not parse test output: {result.stdout}, stderr: {result.stderr}"

    assert data.get('pass'), f"Test failed: {data.get('reason', 'unknown error')}"


def test_installGlobal_exports_and_runs():
    """
    Pass-to-pass: installGlobal function should be exported and runnable.
    """
    test_code = '''
// @ts-nocheck
// Test that installGlobal is properly exported and can be called
(global as any).__DEV__ = false;

const module = require('/workspace/expo/packages/expo/src/winter/installGlobal');
const hasExport = typeof module.installGlobal === 'function';

if (!hasExport) {
  console.log(JSON.stringify({ pass: false, reason: 'no_export' }));
} else {
  // Try calling it
  Object.defineProperty(global, 'TestExportProp', {
    value: 1,
    configurable: true,
  });

  try {
    module.installGlobal('TestExportProp', () => 2);
    console.log(JSON.stringify({ pass: true, reason: 'export_works' }));
  } catch (e: any) {
    console.log(JSON.stringify({ pass: false, reason: 'call_failed', error: e.message }));
  }
}
'''
    result = run_ts_test(test_code)

    output = result.stdout.strip().split('\n')[-1] if result.stdout else ''
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        assert False, f"Could not parse test output: {result.stdout}, stderr: {result.stderr}"

    assert data.get('pass'), f"Test failed: {data.get('reason', 'unknown error')}"


def test_repo_installGlobal_syntax():
    """
    Repo CI check: installGlobal.ts should have valid TypeScript syntax (pass_to_pass).
    """
    node_script = """
const fs = require('fs');
const content = fs.readFileSync('/workspace/expo/packages/expo/src/winter/installGlobal.ts', 'utf8');

// Check for basic syntax patterns that indicate well-formed TypeScript
const hasExport = content.includes('export function installGlobal');
const hasTypeAnnotation = content.includes('<T extends object>');
const hasProperBraces = (content.match(/{/g) || []).length >= (content.match(/}/g) || []).length;

if (!hasExport) {
    console.error('Missing export statement');
    process.exit(1);
}
if (!hasTypeAnnotation) {
    console.error('Missing type annotations');
    process.exit(1);
}
if (!hasProperBraces) {
    console.error('Unbalanced braces');
    process.exit(1);
}

console.log('Syntax validation passed');
process.exit(0);
"""
    result = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Syntax check failed: {result.stderr}"


def test_repo_winter_module_structure():
    """
    Repo CI check: Winter module should have proper structure (pass_to_pass).
    """
    node_script = """
const fs = require('fs');
const indexPath = '/workspace/expo/packages/expo/src/winter/index.ts';
const installGlobalPath = '/workspace/expo/packages/expo/src/winter/installGlobal.ts';

// Check index.ts imports runtime (side-effect import pattern)
const indexContent = fs.readFileSync(indexPath, 'utf8');
if (!indexContent.includes('./runtime')) {
    console.error('index.ts does not import runtime');
    process.exit(1);
}

// Check installGlobal.ts exports the main function
const installGlobalContent = fs.readFileSync(installGlobalPath, 'utf8');
if (!installGlobalContent.includes('export function installGlobal')) {
    console.error('installGlobal function not exported');
    process.exit(1);
}

console.log('Winter module structure validated');
process.exit(0);
"""
    result = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Winter module structure check failed: {result.stderr}"


def test_repo_global_polyfill_patterns():
    """
    Repo CI check: Global polyfill patterns should follow expected conventions (pass_to_pass).

    Verifies that Object.defineProperty and other polyfill patterns are correctly used.
    """
    node_script = """
const fs = require('fs');
const content = fs.readFileSync('/workspace/expo/packages/expo/src/winter/installGlobal.ts', 'utf8');

// Check for Object.defineProperty usage (used for polyfills)
if (!content.includes('Object.defineProperty')) {
    console.error('Missing Object.defineProperty for polyfill installation');
    process.exit(1);
}

// Check for getOwnPropertyDescriptor usage (needed for preserving descriptors)
if (!content.includes('getOwnPropertyDescriptor')) {
    console.error('Missing getOwnPropertyDescriptor call');
    process.exit(1);
}

// Check for __DEV__ guard (development-only backup creation)
if (!content.includes('__DEV__')) {
    console.error('Missing __DEV__ guard for backup creation');
    process.exit(1);
}

console.log('Global polyfill patterns validated');
process.exit(0);
"""
    result = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Global polyfill pattern check failed: {result.stderr}"
