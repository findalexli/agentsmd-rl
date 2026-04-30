// Tiny subset of lodash sufficient for the hook (uses `last`).
function last(arr) {
  if (!arr || arr.length === 0) return undefined;
  return arr[arr.length - 1];
}
module.exports = { last };
module.exports.default = module.exports;
