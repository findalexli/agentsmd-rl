# Missing test coverage for `ignore_raw_node` option in `GraphPickler.Options`

## Context

The `GraphPickler` class in `torch/fx/_graph_pickler.py` is used to serialize
`torch.fx.GraphModule` objects. A recent change added an `ignore_raw_node`
option to `GraphPickler.Options` that controls what happens when a raw
`torch.fx.Node` object is encountered in node metadata during pickling:

- **Default behavior** (`ignore_raw_node=False`): an `AssertionError` is
  raised with the message `"Unexpected raw Node during pickling"`.
- **Opt-in behavior** (`ignore_raw_node=True`): the raw `Node` is silently
  replaced with `None` during serialization, and it round-trips as `None`
  after deserialization.

## Problem

There are no unit tests covering either of these behaviors. The existing test
file `test/fx/test_graph_pickler.py` already tests many `GraphPickler`
features but has no tests that exercise the `ignore_raw_node` option.

## What needs to happen

Add test coverage in `test/fx/test_graph_pickler.py` for the
`ignore_raw_node` option. The tests should verify:

1. That pickling a `GraphModule` whose `node.meta` contains a raw
   `torch.fx.Node` reference raises `AssertionError` by default.
2. That with `Options(ignore_raw_node=True)`, pickling succeeds and the raw
   node reference deserializes as `None` after a round-trip.

The test should construct a simple traced graph module, inject a raw `Node`
reference into the metadata of one of its nodes (using `node.meta["key"] = node`
or similar assignment to `node.meta`), and exercise the
`GraphPickler.dumps()` / `GraphPickler.loads()` round-trip.

### Required test patterns

The test class(es) and methods you add must satisfy the following structural
requirements (the test oracle enforces these via AST inspection):

| Check | Required pattern |
|-------|-----------------|
| Error assertion | Use `self.assertRaises(AssertionError, ...)` or `self.assertRaisesRegex(AssertionError, ...)` to catch the default-raise error, combined with a call to `self.GraphPickler.dumps(...)` |
| Round-trip verification | Call `self.GraphPickler.loads(...)` to verify deserialization after a successful dump with `ignore_raw_node=True` |
| Raw node injection | Assign a raw `Node` reference into `node.meta` (e.g., `call_node.meta["raw_ref"] = call_node` or similar subscript assignment to `.meta`) |
| Test class name | The test class(es) must contain the string `ignore_raw_node` in the class name (used by the AST scanner to find your tests) |
| Minimum test count | At least 2 test methods are required |
| Assertions | Each test method must contain at least one assertion (e.g., `self.assertIsNone`, `self.assertIsNotNone`, `self.assertRaises`, `self.assertIn`) |
| Statement count | Each test method must contain at least 3 statements |

### Test file requirements

The existing `test/fx/test_graph_pickler.py` already has a `# Owner(s): [...]`
label and a `if __name__ == "__main__": run_tests()` block at the end. Your
added tests should be placed within this existing file structure. Do not
modify the `if __name__ == "__main__": run_tests()` line or the file-level
owner label.

## Relevant files

- `torch/fx/_graph_pickler.py` — `GraphPickler`, `Options` class
- `test/fx/test_graph_pickler.py` — existing test suite
