# Fix Curve Intersection Precision

## Problem

The curve-to-line-segment intersection calculation in `packages/math/src/curve.ts` is missing some valid intersections. Specifically, curves that are nearly flat or approach the line at shallow angles are not being detected.

The `curveIntersectLineSegment` function uses a Newton-Raphson solver (`solveWithAnalyticalJacobian`) to find intersections, starting from multiple initial guesses. However, the current iteration limit doesn't provide enough iterations for the solver to converge in all cases.

## Your Task

Modify `packages/math/src/curve.ts` to fix the curve intersection calculation so that:

1. The Newton-Raphson solver has sufficient iterations to converge on challenging intersections
2. The function correctly detects intersections with:
   - Nearly flat curves
   - Curves approaching lines at shallow angles
   - Intersections near curve endpoints

## Relevant Code

The key function is `curveIntersectLineSegment` in `packages/math/src/curve.ts`. Look at:

- The `calculate` helper function which calls `solveWithAnalyticalJacobian`
- The iteration limit parameter and how it affects convergence
- The fallback code that approximates curves with short segments

## Hints

- The Newton-Raphson method may need more iterations to converge when curves are nearly tangent to lines
- There's existing fallback code that tries to catch near-endpoint hits by approximating the curve with short line segments - consider whether this is still needed if the solver converges properly
- The solver starts with multiple initial guesses (at t=0.5, 0.2, and 0.8) - all of these should have enough iterations to potentially find a solution
- You may need to remove unused imports if you modify the code structure

## Testing

When fixed, the curve intersection should correctly detect:
- A nearly flat curve (control points with small y-deltas) intersecting with a crossing line
- Curves approaching lines at shallow angles
- Intersections occurring near the curve's start or end points
