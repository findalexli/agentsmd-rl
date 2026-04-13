# Fix calculateAverage for empty arrays

The `calculateAverage` function in `index.js` has a bug where it returns `null` for empty arrays. It should return `0` instead.

## Task

1. Modify `index.js` to fix the `calculateAverage` function
2. Change the return value from `null` to `0` when the input array is empty

## Expected Behavior

```javascript
calculateAverage([]);  // Should return 0, not null
calculateAverage([1, 2, 3]);  // Should return 2
```
