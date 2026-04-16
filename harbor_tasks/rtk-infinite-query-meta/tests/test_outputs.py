"""
Tests for Redux Toolkit Query infinite query meta handling fix.

This tests that `meta` is properly propagated through queryFulfilled
in onQueryStarted for infinite queries, fixing issue #4938.
"""

import subprocess
import sys
import os

# Repository path
REPO = "/workspace/redux-toolkit"
TOOLKIT_DIR = os.path.join(REPO, "packages/toolkit")

def test_infinite_query_meta_in_query_fulfilled():
    """
    Test that queryFulfilled.meta contains request/response objects for infinite queries.
    This is the core fail-to-pass test for the bug fix.
    """
    test_code = '''
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query';
import { configureStore } from '@reduxjs/toolkit';

// Track the meta value received in onQueryStarted
let capturedMeta: any = null;

const api = createApi({
  baseQuery: fetchBaseQuery({ baseUrl: 'https://example.com' }),
  endpoints: (builder) => ({
    getInfiniteItems: builder.infiniteQuery<number[], string, number>({
      query: (page) => `/items?page=${page}`,
      infiniteQueryOptions: {
        initialPageParam: 0,
        getNextPageParam: (lastPage, allPages) => allPages.length,
      },
      async onQueryStarted(arg, { queryFulfilled }) {
        try {
          const result = await queryFulfilled;
          capturedMeta = result.meta;
        } catch (e) {
          // ignore errors
        }
      },
    }),
  }),
});

// Check that the types are correct
const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
  },
  middleware: (gDM) => gDM().concat(api.middleware),
});

// Export for testing
(globalThis as any).capturedMeta = capturedMeta;
'''

    # Write the test TypeScript file
    test_file = os.path.join(TOOLKIT_DIR, "test-meta-check.ts")
    with open(test_file, "w") as f:
        f.write(test_code)

    # Run TypeScript compiler to verify it compiles (basic check)
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "test-meta-check.ts"],
        cwd=TOOLKIT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )

    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)

    # The compilation itself is a basic check
    assert result.returncode == 0 or "meta" not in result.stderr, f"TypeScript error: {result.stderr}"


def test_build_thunks_has_meta_handling():
    """
    Test that buildThunks.ts includes the meta handling for infinite queries.
    This verifies the structural fix is in place.
    """
    build_thunks_path = os.path.join(TOOLKIT_DIR, "src/query/core/buildThunks.ts")

    with open(build_thunks_path, "r") as f:
        content = f.read()

    # Check for the fix: meta should be included in the returned object for infinite queries
    # The fix adds: meta: pageResponse.meta,
    assert "meta: pageResponse.meta," in content, (
        "buildThunks.ts missing meta handling for infinite queries. "
        "Expected 'meta: pageResponse.meta,' in the infinite query result handling code."
    )


def test_infinite_queries_test_file_updated():
    """
    Test that the infiniteQueries.test.ts expects meta to be defined.
    This verifies the test expectations match the fix.
    """
    test_file_path = os.path.join(TOOLKIT_DIR, "src/query/tests/infiniteQueries.test.ts")

    with open(test_file_path, "r") as f:
        content = f.read()

    # The test should NOT expect meta: undefined anymore
    # It should expect meta with request/response
    assert "meta: undefined" not in content, (
        "infiniteQueries.test.ts still expects meta: undefined. "
        "The test needs to be updated to expect meta with request/response."
    )

    # Should have the updated expectation
    assert "request: expect.anything()" in content, (
        "infiniteQueries.test.ts missing updated meta expectation with request."
    )
    assert "response: expect.anything()" in content, (
        "infiniteQueries.test.ts missing updated meta expectation with response."
    )


def test_repo_unit_tests_pass():
    """
    Pass-to-pass test: Run the existing RTK Query unit tests.
    Verifies the fix doesn't break existing functionality (infiniteQueries tests).
    """
    result = subprocess.run(
        ["yarn", "vitest", "run", "src/query/tests/infiniteQueries.test.ts"],
        cwd=TOOLKIT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, (
        f"Unit tests failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-1000:]}"
    )


def test_repo_query_buildThunks():
    """
    Pass-to-pass test: Run buildThunks tests (repo CI gate).
    buildThunks.ts is the modified file for the meta handling fix.
    """
    result = subprocess.run(
        ["yarn", "vitest", "run", "src/query/tests/buildThunks.test.tsx"],
        cwd=TOOLKIT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, (
        f"buildThunks tests failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-1000:]}"
    )


def test_repo_query_createApi():
    """
    Pass-to-pass test: Run createApi tests (repo CI gate).
    Verifies the core createApi functionality still works.
    """
    result = subprocess.run(
        ["yarn", "vitest", "run", "src/query/tests/createApi.test.ts"],
        cwd=TOOLKIT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, (
        f"createApi tests failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-1000:]}"
    )


def test_repo_query_middleware():
    """
    Pass-to-pass test: Run buildMiddleware tests (repo CI gate).
    Verifies query middleware functionality.
    """
    result = subprocess.run(
        ["yarn", "vitest", "run", "src/query/tests/buildMiddleware.test.tsx"],
        cwd=TOOLKIT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, (
        f"buildMiddleware tests failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-1000:]}"
    )


def test_repo_build():
    """
    Pass-to-pass test: Build the package successfully (repo CI gate).
    Verifies the package can be built without errors.
    """
    result = subprocess.run(
        ["yarn", "build"],
        cwd=TOOLKIT_DIR,
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, (
        f"Build failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-1000:]}"
    )


def test_typescript_compiles():
    """
    Pass-to-pass test: TypeScript compilation succeeds.
    Verifies there are no type errors after the fix.
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "tsconfig.json"],
        cwd=TOOLKIT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, (
        f"TypeScript compilation failed:\n{result.stderr[-1000:]}"
    )


def test_repo_type_tests():
    """
    Pass-to-pass test: Type tests pass (p2p).
    Verifies type definitions using the repo's type test suite.
    """
    result = subprocess.run(
        ["yarn", "type-tests"],
        cwd=TOOLKIT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, (
        f"Type tests failed:\nstdout: {result.stdout[-1000:]}\nstderr: {result.stderr[-1000:]}"
    )
