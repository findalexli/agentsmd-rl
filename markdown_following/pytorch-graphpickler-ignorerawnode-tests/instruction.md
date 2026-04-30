# Missing test coverage for `ignore_raw_node` option in `GraphPickler.Options`

## Context

The `GraphPickler` class in `torch/fx/_graph_pickler.py` is used to serialize
`torch.fx.GraphModule` objects. A recent change added an `ignore_raw_node`
option to `GraphPickler.Options` that controls what happens when a raw
`torch.fx.Node` object is encountered in node metadata during pickling:

- **Default behavior** (`ignore_raw_node=False`): an `AssertionError` is
  raised when a raw Node appears in node metadata during pickling.
- **Opt-in behavior** (`ignore_raw_node=True`): the raw `Node` is silently
  replaced with `None` during serialization, and it round-trips as `None`
  after deserialization.

## Problem

There are no unit tests covering either of these behaviors. The existing test
file `test/fx/test_graph_pickler.py` already tests many `GraphPickler`
features but has no tests that exercise the `ignore_raw_node` option.

## What needs to happen

Add test coverage in `test/fx/test_graph_pickler.py` for the
`ignore_raw_node` option. You need to verify:

1. That pickling a `GraphModule` whose `node.meta` contains a raw
   `torch.fx.Node` reference raises `AssertionError` by default.
2. That with `Options(ignore_raw_node=True)`, pickling succeeds and the raw
   node reference deserializes as `None` after a round-trip.

Construct a simple traced graph module, inject a raw `Node` reference into
the metadata of one of its nodes, and exercise the `GraphPickler.dumps()` /
`GraphPickler.loads()` round-trip.

### Test requirements

- Test class name should contain `ignore_raw_node` (e.g., `TestIgnoreRawNode`)
- At least 2 test methods are required
- Each test method must contain at least one assertion
- The test class should inherit from `TestCase` (from `torch.testing._internal.common_utils`)
- Use `assertRaises` or `assertRaisesRegex` to catch `AssertionError` for the default behavior
- For the round-trip test, call both `dumps()` and `loads()` with `ignore_raw_node=True`

### Test file requirements

The existing `test/fx/test_graph_pickler.py` already has a `# Owner(s): [...]`
label and a `if __name__ == "__main__": run_tests()` block at the end. Your
added tests should be placed within this existing file structure. Do not
modify the `if __name__ == "__main__": run_tests()` line or the file-level
owner label.

## Relevant files

- `torch/fx/_graph_pickler.py` — `GraphPickler`, `Options` class
- `test/fx/test_graph_pickler.py` — existing test suite
