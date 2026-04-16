"""
Tests for TanStack Router PR #6910: Fix deepEqual for promises

The deepEqual function in useRouterState.tsx incorrectly handles promise-like
objects. It would try to recursively compare promise properties, which is wrong.
The fix adds an isPromiseLike check that returns false early for any promise-like values.
"""
import subprocess
import os

REPO = "/workspace/router"


def test_deepequal_native_promises():
    """
    Test that deepEqual returns false when comparing two different native Promise objects.
    (fail_to_pass)

    The bug: Without the fix, deepEqual would try to recursively compare promise
    properties and might incorrectly return true or behave unexpectedly.
    """
    # Create a test that extracts deepEqual from source and tests it
    test_code = """
    const fs = require('fs');
    const path = require('path');

    // Read source and extract the functions
    const srcPath = path.join(process.cwd(), 'packages/solid-router/src/useRouterState.tsx');
    let src = fs.readFileSync(srcPath, 'utf8');

    // Extract the deepEqual function body (it's not exported)
    // We need to find and evaluate it
    const deepEqualMatch = src.match(/function deepEqual\\(a: any, b: any\\): boolean \\{([\\s\\S]*?)^\\}/m);
    const isPromiseLikeMatch = src.match(/function isPromiseLike\\(value: unknown\\)[^{]*\\{([\\s\\S]*?)^\\}/m);

    if (!deepEqualMatch) {
        console.error('ERROR: Could not find deepEqual function');
        process.exit(1);
    }

    // Build the functions (strip TypeScript types)
    let deepEqualBody = deepEqualMatch[0]
        .replace(/: any/g, '')
        .replace(/: boolean/g, '')
        .replace(/: unknown/g, '')
        .replace(/value is PromiseLike<unknown>/g, '')
        .replace(/as PromiseLike<unknown>/g, '');

    let isPromiseLikeBody = '';
    if (isPromiseLikeMatch) {
        isPromiseLikeBody = isPromiseLikeMatch[0]
            .replace(/: unknown/g, '')
            .replace(/\\)\\s*:[^{]*\\{/g, ') {')  // Strip return type annotation
            .replace(/as PromiseLike<unknown>/g, '');
    }

    // Create test context
    const testCode = isPromiseLikeBody + '\\n' + deepEqualBody + '\\n';

    // Use Function constructor to evaluate
    const testFn = new Function(testCode + `
        // Test with two different Promise objects
        const p1 = Promise.resolve(1);
        const p2 = Promise.resolve(1);

        // They should NOT be deep equal (different references)
        const result = deepEqual(p1, p2);
        if (result === true) {
            throw new Error('FAIL: deepEqual(Promise1, Promise2) should return false but returned true');
        }

        // Same promise should be equal (same reference)
        if (deepEqual(p1, p1) !== true) {
            throw new Error('FAIL: deepEqual(Promise1, Promise1) should return true');
        }

        return 'PASS';
    `);

    try {
        const result = testFn();
        console.log(result + ': deepEqual correctly handles native promises');
        process.exit(0);
    } catch (e) {
        console.error(e.message);
        process.exit(1);
    }
    """

    result = subprocess.run(
        ["node", "-e", test_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"


def test_deepequal_nested_promises():
    """
    Test that deepEqual returns false when objects contain different promise values.
    (fail_to_pass)

    Objects with promises at the same key should not be equal if the promises differ.
    """
    test_code = """
    const fs = require('fs');
    const path = require('path');

    const srcPath = path.join(process.cwd(), 'packages/solid-router/src/useRouterState.tsx');
    let src = fs.readFileSync(srcPath, 'utf8');

    const deepEqualMatch = src.match(/function deepEqual\\(a: any, b: any\\): boolean \\{([\\s\\S]*?)^\\}/m);
    const isPromiseLikeMatch = src.match(/function isPromiseLike\\(value: unknown\\)[^{]*\\{([\\s\\S]*?)^\\}/m);

    if (!deepEqualMatch) {
        console.error('ERROR: Could not find deepEqual function');
        process.exit(1);
    }

    let deepEqualBody = deepEqualMatch[0]
        .replace(/: any/g, '')
        .replace(/: boolean/g, '')
        .replace(/: unknown/g, '')
        .replace(/value is PromiseLike<unknown>/g, '')
        .replace(/as PromiseLike<unknown>/g, '');

    let isPromiseLikeBody = '';
    if (isPromiseLikeMatch) {
        isPromiseLikeBody = isPromiseLikeMatch[0]
            .replace(/: unknown/g, '')
            .replace(/\\)\\s*:[^{]*\\{/g, ') {')  // Strip return type annotation
            .replace(/as PromiseLike<unknown>/g, '');
    }

    const testCode = isPromiseLikeBody + '\\n' + deepEqualBody + '\\n';

    const testFn = new Function(testCode + `
        // Objects containing different promises at the same key
        const obj1 = { data: Promise.resolve(1) };
        const obj2 = { data: Promise.resolve(1) };

        // They should NOT be deep equal (the promises are different instances)
        const result = deepEqual(obj1, obj2);
        if (result === true) {
            throw new Error('FAIL: deepEqual(obj1, obj2) should return false when they contain different promises');
        }

        return 'PASS';
    `);

    try {
        const result = testFn();
        console.log(result + ': deepEqual correctly handles nested promises');
        process.exit(0);
    } catch (e) {
        console.error(e.message);
        process.exit(1);
    }
    """

    result = subprocess.run(
        ["node", "-e", test_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"


def test_deepequal_promises_in_array():
    """
    Test that deepEqual returns false when arrays contain different promises.
    (fail_to_pass)

    Arrays with promise elements at the same index should not be equal if promises differ.
    """
    test_code = """
    const fs = require('fs');
    const path = require('path');

    const srcPath = path.join(process.cwd(), 'packages/solid-router/src/useRouterState.tsx');
    let src = fs.readFileSync(srcPath, 'utf8');

    const deepEqualMatch = src.match(/function deepEqual\\(a: any, b: any\\): boolean \\{([\\s\\S]*?)^\\}/m);
    const isPromiseLikeMatch = src.match(/function isPromiseLike\\(value: unknown\\)[^{]*\\{([\\s\\S]*?)^\\}/m);

    if (!deepEqualMatch) {
        console.error('ERROR: Could not find deepEqual function');
        process.exit(1);
    }

    let deepEqualBody = deepEqualMatch[0]
        .replace(/: any/g, '')
        .replace(/: boolean/g, '')
        .replace(/: unknown/g, '')
        .replace(/value is PromiseLike<unknown>/g, '')
        .replace(/as PromiseLike<unknown>/g, '');

    let isPromiseLikeBody = '';
    if (isPromiseLikeMatch) {
        isPromiseLikeBody = isPromiseLikeMatch[0]
            .replace(/: unknown/g, '')
            .replace(/\\)\\s*:[^{]*\\{/g, ') {')  // Strip return type annotation
            .replace(/as PromiseLike<unknown>/g, '');
    }

    const testCode = isPromiseLikeBody + '\\n' + deepEqualBody + '\\n';

    const testFn = new Function(testCode + `
        // Arrays containing different promise objects
        const arr1 = [1, Promise.resolve('a'), 3];
        const arr2 = [1, Promise.resolve('a'), 3];

        // They should NOT be deep equal (the promises are different instances)
        const result = deepEqual(arr1, arr2);
        if (result === true) {
            throw new Error('FAIL: deepEqual(arr1, arr2) should return false when they contain different promises');
        }

        return 'PASS';
    `);

    try {
        const result = testFn();
        console.log(result + ': deepEqual correctly handles promises in arrays');
        process.exit(0);
    } catch (e) {
        console.error(e.message);
        process.exit(1);
    }
    """

    result = subprocess.run(
        ["node", "-e", test_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"


def test_deepequal_regular_objects_still_work():
    """
    Test that deepEqual still works correctly for regular objects (non-promises).
    (pass_to_pass)

    The fix should not break existing behavior for regular objects.
    """
    test_code = """
    const fs = require('fs');
    const path = require('path');

    const srcPath = path.join(process.cwd(), 'packages/solid-router/src/useRouterState.tsx');
    let src = fs.readFileSync(srcPath, 'utf8');

    const deepEqualMatch = src.match(/function deepEqual\\(a: any, b: any\\): boolean \\{([\\s\\S]*?)^\\}/m);
    const isPromiseLikeMatch = src.match(/function isPromiseLike\\(value: unknown\\)[^{]*\\{([\\s\\S]*?)^\\}/m);

    if (!deepEqualMatch) {
        console.error('ERROR: Could not find deepEqual function');
        process.exit(1);
    }

    let deepEqualBody = deepEqualMatch[0]
        .replace(/: any/g, '')
        .replace(/: boolean/g, '')
        .replace(/: unknown/g, '')
        .replace(/value is PromiseLike<unknown>/g, '')
        .replace(/as PromiseLike<unknown>/g, '');

    let isPromiseLikeBody = '';
    if (isPromiseLikeMatch) {
        isPromiseLikeBody = isPromiseLikeMatch[0]
            .replace(/: unknown/g, '')
            .replace(/\\)\\s*:[^{]*\\{/g, ') {')  // Strip return type annotation
            .replace(/as PromiseLike<unknown>/g, '');
    }

    const testCode = isPromiseLikeBody + '\\n' + deepEqualBody + '\\n';

    const testFn = new Function(testCode + `
        // Test regular objects
        const obj1 = { a: 1, b: { c: 2 } };
        const obj2 = { a: 1, b: { c: 2 } };
        const obj3 = { a: 1, b: { c: 3 } };

        if (deepEqual(obj1, obj2) !== true) {
            throw new Error('FAIL: deepEqual of identical objects should return true');
        }

        if (deepEqual(obj1, obj3) !== false) {
            throw new Error('FAIL: deepEqual of different objects should return false');
        }

        // Test primitives
        if (deepEqual(1, 1) !== true) {
            throw new Error('FAIL: deepEqual(1, 1) should return true');
        }

        if (deepEqual('hello', 'hello') !== true) {
            throw new Error('FAIL: deepEqual("hello", "hello") should return true');
        }

        // Test arrays
        if (deepEqual([1, 2, 3], [1, 2, 3]) !== true) {
            throw new Error('FAIL: deepEqual of identical arrays should return true');
        }

        return 'PASS';
    `);

    try {
        const result = testFn();
        console.log(result + ': deepEqual correctly handles regular objects');
        process.exit(0);
    } catch (e) {
        console.error(e.message);
        process.exit(1);
    }
    """

    result = subprocess.run(
        ["node", "-e", test_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"


def test_solid_router_build():
    """
    Test that the solid-router package builds successfully.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, f"Build failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"


def test_solid_router_typecheck():
    """
    Test that the solid-router package passes type checking.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, f"Type check failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"


def test_solid_router_eslint():
    """
    Test that the solid-router package passes ESLint checks.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:eslint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, f"ESLint failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"


def test_solid_router_unit_tests():
    """
    Test that the solid-router unit tests pass (via vitest).
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:unit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, f"Unit tests failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"


def test_solid_router_build_check():
    """
    Test that the solid-router package passes build checks (publint + attw).
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, f"Build check failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
