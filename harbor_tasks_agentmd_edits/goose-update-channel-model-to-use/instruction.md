# Adapt Channel Translation to New Model

## Problem

The Go-to-Goose translation (goose) needs to be updated to work with the new generic channel model. The current translation generates code that is incompatible with the new model's API.

The main issues are:

1. **Channel operations need element type**: Every channel operation (`chan.send`, `chan.receive`, `chan.len`, `chan.cap`, `chan.close`, `chan.for_range`) now requires the channel element type as an explicit argument because they are implemented using generic Go code.

2. **Select statement model changed**: The select model now uses two separate functions:
   - `chan.select_blocking` - for blocking selects (no default case)
   - `chan.select_nonblocking` - for non-blocking selects (with default case)
   - This replaces the old model that used `chan.select_no_default` or a default case in the list.

3. **Select operation argument order changed**: `chan.select_send` now takes the channel element type first, then the channel, then the value.

4. **Bootstrap configuration needs `direct_calls`**: A new option needs to be added to support direct function calls without global state for bootstrapping.

5. **Remove obsolete hand-translated tests**: The `TestAllHandXlatedChannelTests` test function tests hand-translated channel code that is no longer needed once channel translation is working.

## Files to Look At

- `goose.go` - Main translation logic for Go to Gallina/Coq
- `glang/coq.go` - Coq code generation, specifically `ForRangeChanExpr`
- `declfilter/declfilter.go` - Bootstrap configuration struct
- `examples_test.go` - Contains the hand-translated channel tests to remove
- `testdata/examples/unittest/unittest.gold.v` - Expected Coq output for tests
- `.github/workflows/build.yml` - CI configuration
- `types.go` - Helper functions for type extraction

## Expected Behavior

After the changes:
- `chan.send #stringT "$chan" "$v"` (with element type)
- `chan.receive #stringT (...)` (with element type)
- `chan.select_blocking [...]` (blocking select)
- `chan.select_nonblocking [...] (λ: <>, ...)` (non-blocking select with default)
- `chan.select_send #intT (![...] "c2") (![...] "i2") ...` (type first)
- Bootstrap config has `direct_calls` field for function/method calls
- CI runs tests in `testdata/examples/`
- Hand-translated channel tests are removed
