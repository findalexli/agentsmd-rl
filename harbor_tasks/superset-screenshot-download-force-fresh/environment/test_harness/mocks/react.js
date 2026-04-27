// Minimal React stand-in for testing custom hooks without a renderer.
// useCallback / useEffect / useRef behave as plain JavaScript.
function useCallback(fn, _deps) {
  return fn;
}
function useEffect(_fn, _deps) {
  // no-op: we never run cleanup in this harness
}
function useRef(initial) {
  return { current: initial };
}
module.exports = { useCallback, useEffect, useRef };
module.exports.default = module.exports;
