# Fix calculateAverage for empty arrays

The `calculateAverage` function in `index.js` returns `null` when given an empty array. It should return `0` instead.

The repository at `/workspace/sample_repo` must be in a clean state:
- `index.js` exports `calculateAverage` and `calculateSum` functions
- `package.json` exists
- `npm run lint` passes
- `npm test` passes

## Expected Behavior

`calculateAverage([])` must return `0` (not `null`)
`calculateAverage([1, 2, 3, 4, 5])` must return `3.0`
`calculateSum([1, 2, 3, 4, 5])` must return `15`
