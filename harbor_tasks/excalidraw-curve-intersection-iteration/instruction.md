# Fix Curve Intersection Calculation

## Problem

The curve intersection calculation in Excalidraw has convergence issues for certain edge cases. When computing intersections between cubic Bezier curves and line segments, the numerical solver sometimes fails to converge, causing incorrect intersection detection.

## Symptoms

- Intersection detection fails for curves that intersect near control points
- The solver may return null when it should find a valid intersection
- Some arrow bindings in the editor may not attach correctly to shapes

## Your Task

1. Examine the curve intersection logic in the math package
2. Identify why convergence fails for some curve-line intersection cases
3. Fix the underlying issue so intersection calculations reliably converge
4. Remove any code that becomes unnecessary after your fix

## Constraints

- Maintain TypeScript type safety (run `yarn test:typecheck`)
- The fix should be minimal and focused on the convergence issue
- Ensure the existing test suite passes: `yarn test:typecheck`, `yarn test:code`, `yarn test:other`, `yarn build:math`, and `npx vitest run packages/math/tests/curve.test.ts`
- Do not break the build or type checking

## Expected Outcome

After your fix, curve-line intersection calculations should reliably converge for all valid intersection cases, and the existing test suite should pass.