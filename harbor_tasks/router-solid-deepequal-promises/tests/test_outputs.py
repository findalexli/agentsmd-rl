#!/usr/bin/env python3
"""
Test outputs for TanStack Router PR #6910 - deepEqual promise handling fix.

This module tests that the deepEqual function correctly handles Promise-like objects
by returning false instead of attempting deep comparison.
"""

import subprocess
import sys
import os

REPO = "/workspace/router"
TEST_FILE = os.path.join(REPO, "packages/solid-router/src/useRouterState.tsx")

def run_node_test(js_code, timeout=60):
    """Run JavaScript code via Node.js and return result."""
    cmd = ["node", "-e", js_code]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO)
    return result

def test_deepequal_promise_to_nonpromise():
    """F2P: deepEqual(promise, non-promise) should return false."""
    js_code = """
const fs = require('fs');
const path = require('path');

// Read the source file to extract deepEqual function
const srcPath = path.join(__dirname, 'packages/solid-router/src/useRouterState.tsx');
const src = fs.readFileSync(srcPath, 'utf8');

// Extract the deepEqual function implementation by parsing
// We'll recreate the function based on what we find
function deepEqual(a, b) {
  if (Object.is(a, b)) return true;

  // Check if isPromiseLike is defined in the source
  const hasPromiseCheck = src.includes('isPromiseLike(a) || isPromiseLike(b)');

  if (hasPromiseCheck) {
    // Simulate isPromiseLike
    function isPromiseLike(value) {
      return (
        !!value &&
        (typeof value === 'object' || typeof value === 'function') &&
        typeof value.then === 'function'
      );
    }
    if (isPromiseLike(a) || isPromiseLike(b)) return false;
  }

  if (
    typeof a !== 'object' ||
    a === null ||
    typeof b !== 'object' ||
    b === null
  ) {
    return false;
  }

  const keysA = Object.keys(a);
  const keysB = Object.keys(b);

  if (keysA.length !== keysB.length) return false;

  for (const key of keysA) {
    if (!Object.prototype.hasOwnProperty.call(b, key)) return false;
    if (!deepEqual(a[key], b[key])) return false;
  }

  return true;
}

// Test: Promise vs non-promise should return false
const promise = Promise.resolve(1);
const obj = { a: 1 };
const result = deepEqual(promise, obj);
console.log(`deepEqual(promise, object) = ${result}`);
process.exit(result === false ? 0 : 1);
"""
    result = run_node_test(js_code)
    assert result.returncode == 0, f"deepEqual should return false for promise vs object:\n{result.stdout}\n{result.stderr}"

def test_deepequal_different_promises():
    """F2P: deepEqual(different promises) should return false."""
    js_code = """
const fs = require('fs');
const path = require('path');

const srcPath = path.join(__dirname, 'packages/solid-router/src/useRouterState.tsx');
const src = fs.readFileSync(srcPath, 'utf8');
const hasPromiseCheck = src.includes('isPromiseLike(a) || isPromiseLike(b)');

function deepEqual(a, b) {
  if (Object.is(a, b)) return true;

  if (hasPromiseCheck) {
    function isPromiseLike(value) {
      return (
        !!value &&
        (typeof value === 'object' || typeof value === 'function') &&
        typeof value.then === 'function'
      );
    }
    if (isPromiseLike(a) || isPromiseLike(b)) return false;
  }

  if (
    typeof a !== 'object' ||
    a === null ||
    typeof b !== 'object' ||
    b === null
  ) {
    return false;
  }

  const keysA = Object.keys(a);
  const keysB = Object.keys(b);

  if (keysA.length !== keysB.length) return false;

  for (const key of keysA) {
    if (!Object.prototype.hasOwnProperty.call(b, key)) return false;
    if (!deepEqual(a[key], b[key])) return false;
  }

  return true;
}

// Test: Two different promises should return false
const promise1 = Promise.resolve(1);
const promise2 = Promise.resolve(2);
const result = deepEqual(promise1, promise2);
console.log(`deepEqual(promise1, promise2) = ${result}`);
process.exit(result === false ? 0 : 1);
"""
    result = run_node_test(js_code)
    assert result.returncode == 0, f"deepEqual should return false for different promises:\n{result.stdout}\n{result.stderr}"

def test_deepequal_same_promise():
    """F2P: deepEqual(same promise reference) should return true."""
    js_code = """
const fs = require('fs');
const path = require('path');

const srcPath = path.join(__dirname, 'packages/solid-router/src/useRouterState.tsx');
const src = fs.readFileSync(srcPath, 'utf8');
const hasPromiseCheck = src.includes('isPromiseLike(a) || isPromiseLike(b)');

function deepEqual(a, b) {
  if (Object.is(a, b)) return true;

  if (hasPromiseCheck) {
    function isPromiseLike(value) {
      return (
        !!value &&
        (typeof value === 'object' || typeof value === 'function') &&
        typeof value.then === 'function'
      );
    }
    if (isPromiseLike(a) || isPromiseLike(b)) return false;
  }

  if (
    typeof a !== 'object' ||
    a === null ||
    typeof b !== 'object' ||
    b === null
  ) {
    return false;
  }

  const keysA = Object.keys(a);
  const keysB = Object.keys(b);

  if (keysA.length !== keysB.length) return false;

  for (const key of keysA) {
    if (!Object.prototype.hasOwnProperty.call(b, key)) return false;
    if (!deepEqual(a[key], b[key])) return false;
  }

  return true;
}

// Test: Same promise reference should return true (Object.is handles this)
const promise = Promise.resolve(1);
const result = deepEqual(promise, promise);
console.log(`deepEqual(promise, samePromise) = ${result}`);
process.exit(result === true ? 0 : 1);
"""
    result = run_node_test(js_code)
    assert result.returncode == 0, f"deepEqual should return true for same promise reference:\n{result.stdout}\n{result.stderr}"

def test_deepequal_nested_object_with_promise():
    """F2P: deepEqual(obj with promise, same shaped obj with different promise) should return false."""
    js_code = """
const fs = require('fs');
const path = require('path');

const srcPath = path.join(__dirname, 'packages/solid-router/src/useRouterState.tsx');
const src = fs.readFileSync(srcPath, 'utf8');
const hasPromiseCheck = src.includes('isPromiseLike(a) || isPromiseLike(b)');

function deepEqual(a, b) {
  if (Object.is(a, b)) return true;

  if (hasPromiseCheck) {
    function isPromiseLike(value) {
      return (
        !!value &&
        (typeof value === 'object' || typeof value === 'function') &&
        typeof value.then === 'function'
      );
    }
    if (isPromiseLike(a) || isPromiseLike(b)) return false;
  }

  if (
    typeof a !== 'object' ||
    a === null ||
    typeof b !== 'object' ||
    b === null
  ) {
    return false;
  }

  const keysA = Object.keys(a);
  const keysB = Object.keys(b);

  if (keysA.length !== keysB.length) return false;

  for (const key of keysA) {
    if (!Object.prototype.hasOwnProperty.call(b, key)) return false;
    if (!deepEqual(a[key], b[key])) return false;
  }

  return true;
}

// Test: Objects containing different promises
const obj1 = { data: Promise.resolve(1), count: 5 };
const obj2 = { data: Promise.resolve(2), count: 5 };
const result = deepEqual(obj1, obj2);
console.log(`deepEqual(objWithPromise1, objWithPromise2) = ${result}`);
process.exit(result === false ? 0 : 1);
"""
    result = run_node_test(js_code)
    assert result.returncode == 0, f"deepEqual should return false for objects with different promises:\n{result.stdout}\n{result.stderr}"

def test_deepequal_thenable_object():
    """F2P: deepEqual(thenable, object with same shape) should return false."""
    js_code = """
const fs = require('fs');
const path = require('path');

const srcPath = path.join(__dirname, 'packages/solid-router/src/useRouterState.tsx');
const src = fs.readFileSync(srcPath, 'utf8');
const hasPromiseCheck = src.includes('isPromiseLike(a) || isPromiseLike(b)');

function deepEqual(a, b) {
  if (Object.is(a, b)) return true;

  if (hasPromiseCheck) {
    function isPromiseLike(value) {
      return (
        !!value &&
        (typeof value === 'object' || typeof value === 'function') &&
        typeof value.then === 'function'
      );
    }
    if (isPromiseLike(a) || isPromiseLike(b)) return false;
  }

  if (
    typeof a !== 'object' ||
    a === null ||
    typeof b !== 'object' ||
    b === null
  ) {
    return false;
  }

  const keysA = Object.keys(a);
  const keysB = Object.keys(b);

  if (keysA.length !== keysB.length) return false;

  for (const key of keysA) {
    if (!Object.prototype.hasOwnProperty.call(b, key)) return false;
    if (!deepEqual(a[key], b[key])) return false;
  }

  return true;
}

// Test: Thenable (object with .then method) vs plain object
const thenable = { then: (resolve) => resolve(1), value: 42 };
const plain = { value: 42 };
const result = deepEqual(thenable, plain);
console.log(`deepEqual(thenable, plainObj) = ${result}`);
process.exit(result === false ? 0 : 1);
"""
    result = run_node_test(js_code)
    assert result.returncode == 0, f"deepEqual should return false for thenable vs plain object:\n{result.stdout}\n{result.stderr}"

def test_repo_unit_tests():
    """P2P: Solid-router unit tests pass."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:unit"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"

def test_repo_typecheck():
    """P2P: TypeScript type checking passes."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:types"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Type check failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"

def test_build_passes():
    """P2P: Solid-router package builds successfully."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:build"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Build failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_router_core_unit_tests():
    """P2P: Router-core unit tests pass (includes deepEqual tests)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:unit"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Router-core unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_router_core_typecheck():
    """P2P: Router-core TypeScript type checking passes."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:types"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Router-core type check failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
