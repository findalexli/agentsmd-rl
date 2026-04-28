# Drop `trust_remote_code` from a native model and add a linter rule that prevents its return

## Background

Inside `huggingface/transformers` (cloned at `/workspace/transformers`), native model
integrations live under `src/transformers/models/<model_name>/`. Native integrations
must be auditable and maintainable by the project itself, so they must never opt
into running unverified third-party code at load time.

The `LightGlue` keypoint-matching model currently violates this contract: it
exposes a `trust_remote_code` knob on its config and threads it down into
`AutoConfig.from_pretrained(...)` and `AutoModelForKeypointDetection.from_config(...)`.
When set, this lets the loader execute arbitrary Python from a remote
repository as part of constructing a *native* model — a security footgun that
should not exist for shipped, in-tree models. It must be removed.

This task has two parts: clean up the LightGlue model so it never references
`trust_remote_code` again, and add a new structural-lint rule that flags any
future attempt to put it back.

## Part 1 — Remove `trust_remote_code` from LightGlue

Touch the three LightGlue files under `src/transformers/models/lightglue/`
(`modular_lightglue.py`, `configuration_lightglue.py`, `modeling_lightglue.py`)
so that:

- The `LightGlueConfig` class no longer **declares** an attribute named
  `trust_remote_code` (no class-body assignment, no annotated assignment).
- The `LightGlueConfig` class **docstring** no longer documents a
  `trust_remote_code` argument.
- No callable in any of these three files is invoked with `trust_remote_code`
  as a keyword argument, a `**{"trust_remote_code": ...}` splat, or a
  `**dict(trust_remote_code=...)` splat. In particular, the
  `AutoConfig.from_pretrained(...)` and `AutoModelForKeypointDetection.from_config(...)`
  call sites must no longer pass it.
- The behavior of `LightGlueConfig.__post_init__` for the
  `keypoint_detector_config = <dict>` branch should fall through to the
  `CONFIG_MAPPING[...]` lookup unconditionally — there is no longer a need to
  branch on whether the model type is registered, because supporting unregistered
  detectors required `trust_remote_code` and that path is now gone.

`modular_lightglue.py` is the source-of-truth file for this model
(`make fix-repo` regenerates `modeling_lightglue.py` and
`configuration_lightglue.py` from it), so all three must end up consistent —
the modeling and configuration files cannot still reference
`trust_remote_code` while the modular file no longer does.

## Part 2 — Add a new mlinter rule `TRF014`

The repository ships its own structural linter at `utils/mlinter/`. It
discovers each rule from a `trfNNN.py` module that defines a top-level
`check(tree, file_path, source_lines) -> list[Violation]` function and a
matching `[rules.TRFNNN]` block in `utils/mlinter/rules.toml`. See the
existing modules `trf001.py` … `trf013.py` and their entries in
`rules.toml` for the contract.

You must add **TRF014**, defined as follows:

### Rule semantics

Walk every `ast.Call` node in the file and report a violation in **exactly**
these three patterns:

1. **Direct keyword argument** — `foo(..., trust_remote_code=...)`.
2. **Inline-dict splat** — `foo(..., **{"trust_remote_code": ...})`,
   where the splatted value is an `ast.Dict` whose keys are constants and one
   of the constant keys equals `"trust_remote_code"`.
3. **`dict(...)` constructor splat (dict constructor case)** — `foo(..., **dict(trust_remote_code=...))`,
   where the splatted value is a `Call` whose `func` is the `Name` `dict` and
   one of its keyword names is `trust_remote_code`.

A pre-bound variable case (`kw = {"trust_remote_code": True}; foo(**kw)`) is
explicitly **out of scope** for this rule — do not try to handle it.

The rule's emitted message must mention the literal substring
`trust_remote_code` so downstream tooling can grep/match on it.

`check()` returns a list of `Violation` (imported from `._helpers`); each
`Violation` carries `file_path`, `line_number`, and a `message`.

### Module layout

- File path: `utils/mlinter/trf014.py`.
- Define `RULE_ID = ""` at module top — the discovery mechanism in
  `utils/mlinter/mlinter.py` rebinds this to `"TRF014"` when it loads the
  module. Use `RULE_ID` (read at violation-emission time, not capture time)
  in the violation messages.
- Implement the visitor as an `ast.NodeVisitor` that collects violations and
  expose the `check()` function as the module's entry point.

### `rules.toml` spec block

Append a `[rules.TRF014]` block to `utils/mlinter/rules.toml`. Required fields
(see how existing rules populate them):

- `description` — non-empty string.
- `default_enabled = true`. **TRF014 must be on by default**; this is a
  security rule and should not require opt-in.
- `allowlist_models = []`.
- A `[rules.TRF014.explanation]` sub-table with **all four** keys:
  `what_it_does`, `why_bad`, `bad_example`, `good_example`.

The mlinter loader (`utils/mlinter/mlinter.py::_load_rule_specs`) validates
this schema and will refuse to import if any field is missing or wrongly
typed.

## Code Style Requirements

The repo enforces style with `ruff` in CI; per `.ai/AGENTS.md`, run
`make style` (or `make fix-repo`) before submitting. Keep the diff
minimal — per `.github/copilot-instructions.md`, security/bugfix PRs should
be as brief as possible; don't refactor unrelated code, rename symbols, or
introduce new abstractions.

## Where to work

Code is checked out at `/workspace/transformers` at the relevant base commit.
You should edit files in place under that directory.
