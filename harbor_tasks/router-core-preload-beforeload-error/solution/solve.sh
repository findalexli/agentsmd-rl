#!/bin/bash
set -e

cd /workspace/router

# Apply the fix for preload beforeLoad error handling using sed

# Fix 1: Change the loop break condition to check firstBadMatchIndex
sed -i 's/if (inner.serialError) {/if (inner.serialError || inner.firstBadMatchIndex != null) {/' packages/router-core/src/load-matches.ts

# Fix 2: Change the headMaxIndex calculation
# First remove the old 3-line pattern and replace with new 4-line pattern
sed -i '/let headMaxIndex = inner.serialError/,/inner.matches.length - 1/c\  let headMaxIndex =\n    inner.firstBadMatchIndex !== undefined\n      ? inner.firstBadMatchIndex\n      : inner.matches.length - 1' packages/router-core/src/load-matches.ts

# Fix 3: Add the regression test to load.test.ts
# Find the line with "test('exec if pending preload (error)'" and insert before it
cat >> /tmp/regression_test.txt << 'TESTEOF'

  test('skip child beforeLoad when parent beforeLoad throws during preload', async () => {
    const parentBeforeLoad = vi.fn<BeforeLoad>(async ({ preload }) => {
      if (preload) throw new Error('parent error')
    })
    const childBeforeLoad = vi.fn<BeforeLoad>()
    const parentHead = vi.fn(() => ({ meta: [{ title: 'Parent' }] }))
    const childHead = vi.fn(() => ({ meta: [{ title: 'Child' }] }))

    const rootRoute = new BaseRootRoute({})
    const parentRoute = new BaseRoute({
      getParentRoute: () => rootRoute,
      path: '/parent',
      beforeLoad: parentBeforeLoad,
      head: parentHead,
    })
    const childRoute = new BaseRoute({
      getParentRoute: () => parentRoute,
      path: '/child',
      beforeLoad: childBeforeLoad,
      head: childHead,
    })

    const router = createTestRouter({
      routeTree: rootRoute.addChildren([parentRoute.addChildren([childRoute])]),
      history: createMemoryHistory(),
    })

    await router.preloadRoute({ to: '/parent/child' })

    expect(parentBeforeLoad).toHaveBeenCalledTimes(1)
    expect(childBeforeLoad).not.toHaveBeenCalled()
    expect(parentHead).toHaveBeenCalledTimes(1)
    expect(childHead).not.toHaveBeenCalled()
  })
TESTEOF

# Insert the regression test before the "exec if pending preload (error)" test
sed -i "/test('exec if pending preload (error)'/e cat /tmp/regression_test.txt" packages/router-core/tests/load.test.ts
rm /tmp/regression_test.txt

# Verify the patch was applied (idempotency check)
if ! grep -q "if (inner.serialError || inner.firstBadMatchIndex != null)" packages/router-core/src/load-matches.ts; then
    echo "ERROR: Loop break fix was not applied successfully"
    exit 1
fi

if ! grep -q "inner.firstBadMatchIndex !== undefined" packages/router-core/src/load-matches.ts; then
    echo "ERROR: headMaxIndex fix was not applied successfully"
    exit 1
fi

if ! grep -q "skip child beforeLoad when parent beforeLoad throws during preload" packages/router-core/tests/load.test.ts; then
    echo "ERROR: Regression test was not added successfully"
    exit 1
fi

echo "Patch applied successfully"
