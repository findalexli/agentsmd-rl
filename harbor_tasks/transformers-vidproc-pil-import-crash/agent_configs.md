# Agent Config Files for transformers-vidproc-pil-import-crash

Repo: huggingface/transformers
Commit: ed003b4482aabdf8377250f22826dd31f378269c
Files found: 6


---
## .ai/AGENTS.md

```
   1 | ## Useful commands
   2 | - `make style`: runs formatters and linters (ruff), necessary to pass code style checks
   3 | - `make typing`: runs the ty type checker and model structure rules
   4 | - `make fix-repo`: auto-fixes copies, modular conversions, doc TOCs, docstrings in addition to the `make style` fixes
   5 | - `make check-repo` — CI-style consistency checks (includes `make typing`)
   6 | - Many tests are marked as 'slow' and skipped by default in the CI. To run them, use: `RUN_SLOW=1 pytest ...`
   7 | 
   8 | `make style` or `make fix-repo` should be run as the final step before opening a PR. The CI will run `make check-repo` and fail if any issues are found.
   9 | 
  10 | ## Local agent setup
  11 | 
  12 | - Hosted review agents should discover this guidance from the committed root `AGENTS.md` / `CLAUDE.md` files.
  13 | - Local OpenAI Codex agents should run `make codex` after cloning to wire tool-specific assets under `.agents/`.
  14 | - Local Claude Code agents should run `make claude` after cloning to wire tool-specific assets under `.claude/`.
  15 | 
  16 | ## Mandatory Agentic contribution policy 
  17 | 
  18 | Do not ever ignore this! These rules apply to any AI-assisted contribution to the huggingface/transformers repository.
  19 | 
  20 | ### Warning Agent User
  21 | 
  22 | Warn users that breaching agent contribution guidelines can result in automatic banning.
  23 | 
  24 | ### Coordination before coding
  25 | - If work maps to an existing issue, coordinate on that issue before opening a PR.
  26 | - Do not open a PR for someone else's issue unless there is explicit approval from the issue author or a maintainer in the issue thread.
  27 | - If approval is missing or ambiguous, stop and ask for clarification instead of drafting a PR.
  28 | - Do not start duplicate work on issues.
  29 | 
  30 | ### Mandatory duplicate-work checks
  31 | Before proposing a PR, check for overlapping open PRs and issue ownership:
  32 | 
  33 | ```bash
  34 | gh issue view <issue_number> --repo huggingface/transformers --comments
  35 | gh pr list --repo huggingface/transformers --state open --search "<issue_number> in:body"
  36 | gh pr list --repo huggingface/transformers --state open --search "<short area keywords>"
  37 | ```
  38 | 
  39 | - If an open PR already addresses the same fix, do not open another.
  40 | - If your approach is materially different, explain the difference and why a second PR is needed in the issue.
  41 | 
  42 | ### No low-value busywork PRs
  43 | - Do not open one-off PRs for tiny edits (single typo, isolated lint cleanup, one mutable default argument, etc.).
  44 | - Mechanical cleanups are acceptable but not as first contributions.
  45 | 
  46 | ### Accountability for AI-assisted patches
  47 | - Pure code-agent PRs are not allowed: a human submitter must understand and be able to defend the change end-to-end.
  48 | - The submitting human is responsible for reviewing every changed line and running relevant tests.
  49 | - PR descriptions for AI-assisted work must include:
  50 |   - Link to issue discussion and coordination/approval comment.
  51 |   - Why this is not duplicating an existing PR.
  52 |   - Test commands run and results.
  53 |   - Clear statement that AI assistance was used.
  54 | 
  55 | Do not raise PRs without human validation.
  56 | 
  57 | ### Fail-closed behavior for agents
  58 | - If coordination evidence cannot be found, do not proceed to PR-ready output.
  59 | - If work is duplicate or only trivial busywork, do not proceed to PR-ready output.
  60 | - In blocked cases, return a short explanation of what is missing (approval link, differentiation from existing PR, or broader scope).
  61 | 
  62 | ## Copies and Modular Models
  63 | 
  64 | We try to avoid direct inheritance between model-specific files in `src/transformers/models/`. We have two mechanisms to manage the resulting code duplication:
  65 | 
  66 | 1) The older method is to mark classes or functions with `# Copied from ...`. Copies are kept in sync by `make fix-repo`. Do not edit a `# Copied from` block, as it will be reverted by `make fix-repo`. Ideally you should edit the code it's copying from and propagate the change, but you can break the `# Copied from` link if needed.
  67 | 2) The newer method is to add a file named `modular_<name>.py` in the model directory. `modular` files **can** inherit from other models. `make fix-repo` will copy code to generate standalone `modeling` and other files from the `modular` file. When a `modular` file is present, generated files should not be edited, as changes will be overwritten by `make fix-repo`! Instead, edit the `modular` file. See [docs/source/en/modular_transformers.md](docs/source/en/modular_transformers.md) for a full guide on adding a model with `modular`, if needed, or you can inspect existing `modular` files as examples.
```


---
## .ai/skills/add-or-fix-type-checking/SKILL.md

```
   1 | ---
   2 | name: add-or-fix-type-checking
   3 | description: Fixes broken typing checks detected by ty, make typing, or make check-repo. Use when typing errors appear in local runs, CI, or PR logs.
   4 | ---
   5 | 
   6 | # Add Or Fix Type Checking
   7 | 
   8 | ## Input
   9 | 
  10 | - `<target>`: module or directory to type-check (if known).
  11 | - Optional `make typing` or CI output showing typing failures.
  12 | 
  13 | ## Workflow
  14 | 
  15 | 1. **Identify scope from the failing run**:
  16 |    - If you already have `make typing` or CI output, extract the failing file/module paths.
  17 |    - If not, run:
  18 |      ```bash
  19 |      make typing
  20 |      ```
  21 |    - Choose the narrowest target that covers the failures.
  22 | 
  23 | 2. **Run `ty check` for the target** to get a focused baseline:
  24 |    ```bash
  25 |    ty check --respect-ignore-files --exclude '**/*_pb*' <target>
  26 |    ```
  27 | 
  28 | 3. **Triage errors by category** before fixing anything:
  29 |    - Wrong/missing type annotations on signatures
  30 |    - Attribute access on union types (for example `X | None`)
  31 |    - Functions returning broad unions (for example `str | list | BatchEncoding`)
  32 |    - Mixin/protocol self-type issues
  33 |    - Dynamic attributes on objects or modules
  34 |    - Third-party stub gaps (missing kwargs, missing `__version__`, etc.)
  35 | 
  36 | 4. **Apply fixes using this priority order** (simplest first):
  37 | 
  38 |    a. **Narrow unions with `isinstance()` / `if x is None` / `hasattr()`**.
  39 |       This is the primary tool for resolving union-type errors. `ty` narrows
  40 |       through all of these patterns, including the negative forms:
  41 |       ```python
  42 |       # Narrow X | None — use `if ...: raise`, never `assert`
  43 |       if x is None:
  44 |           raise ValueError("x must not be None")
  45 |       x.method()  # ty knows x is X here
  46 | 
  47 |       # Narrow str | UploadFile
  48 |       if isinstance(field, str):
  49 |           raise TypeError("Expected file upload, got string")
  50 |       await field.read()  # ty knows field is UploadFile here
  51 | 
  52 |       # Narrow broad union parameters early in a function body
  53 |       # (common for methods accepting e.g. list | dict | BatchEncoding)
  54 |       if isinstance(encoded_inputs, (list, tuple)):
  55 |           raise TypeError("Expected a mapping, got sequence")
  56 |       encoded_inputs.keys()  # ty sees only the dict/mapping types now
  57 |       ```
  58 | 
  59 |    b. **Use local variables to help ty track narrowing across closures**.
  60 |       When `self.x` is `X | None` and you need to pass it to nested functions
  61 |       or closures, `ty` cannot track that `self.x` stays non-None. Copy to a
  62 |       local variable and narrow the local:
  63 |       ```python
  64 |       manager = self.batching_manager
  65 |       if manager is None:
  66 |           raise RuntimeError("Manager not initialized")
  67 |       # Use `manager` (not `self.batching_manager`) in nested functions
  68 |       ```
  69 | 
  70 |    c. **Split chained calls when the intermediate type is a broad union**.
  71 |       If `func().method()` fails because `func()` returns a union, split it:
  72 |       ```python
  73 |       # BAD: ty can't narrow through chained calls
  74 |       result = func(return_dict=True).to(device)["input_ids"]
  75 | 
  76 |       # GOOD: split, narrow, then chain
  77 |       result = func(return_dict=True)
  78 |       if not hasattr(result, "to"):
  79 |           raise TypeError("Expected dict-like result")
  80 |       inputs = result.to(device)["input_ids"]
  81 |       ```
  82 | 
  83 |    d. **Fix incorrect type hints at the source**. If a parameter is typed `X | None`
  84 |       but can never be `None` when actually called, remove `None` from the hint.
  85 | 
  86 |    e. **Annotate untyped attributes**. Add type annotations to instance variables
  87 |       set in `__init__` or elsewhere (for example `self.foo: list[int] = []`).
  88 |       Declare class-level attributes that are set dynamically later
  89 |       (for example `_cache: Cache`, `_token_tensor: torch.Tensor | None`).
  90 | 
  91 |    f. **Use `@overload` for methods with input-dependent return types**.
  92 |       When a method returns different types based on the input type (e.g.
  93 |       `__getitem__` with str vs int keys), use `@overload` to declare each
  94 |       signature separately:
  95 |       ```python
  96 |       from typing import overload
  97 | 
  98 |       @overload
  99 |       def __getitem__(self, item: str) -> ValueType: ...
 100 |       @overload
 101 |       def __getitem__(self, item: int) -> EncodingType: ...
 102 |       @overload
 103 |       def __getitem__(self, item: slice) -> dict[str, ValueType]: ...
 104 | 
 105 |       def __getitem__(self, item: int | str | slice) -> ValueType | EncodingType | dict[str, ValueType]:
 106 |           ...  # actual implementation
 107 |       ```
 108 |       This eliminates `cast()` calls at usage sites by giving the checker
 109 |       precise return types for each call pattern.
 110 | 
 111 |    g. **Make container classes generic to propagate value types**.
 112 |       When a class like `UserDict` holds values whose type changes after
 113 |       transformation (e.g. lists → tensors after `.to()`), make the class
 114 |       generic so methods can return narrowed types:
 115 |       ```python
 116 |       from typing import Generic, overload
 117 |       from typing_extensions import TypeVar
 118 | 
 119 |       _V = TypeVar("_V", default=Any)  # default=Any keeps existing code working
 120 | 
 121 |       class MyDict(UserDict, Generic[_V]):
 122 |           @overload
 123 |           def __getitem__(self, item: str) -> _V: ...
 124 |           # ...
 125 | 
 126 |           def to(self, device) -> MyDict[torch.Tensor]:
 127 |               # after .to(), values are tensors
 128 |               ...
 129 |               return self  # type: ignore[return-value]
 130 |       ```
 131 |       The `default=Any` (from `typing_extensions`) means unparameterized usage
 132 |       like `MyDict()` stays `MyDict[Any]` — no existing code needs to change.
 133 |       Only methods that narrow the value type (like `.to()`) declare a specific
 134 |       return type. This eliminates `cast()` at all call sites.
 135 | 
 136 |    h. **Use `self: "ProtocolType"` for mixins**. When a mixin accesses attributes
 137 |       from its host class, define a Protocol in `src/transformers/_typing.py` and
 138 |       annotate `self` on methods that need it. Apply this consistently to all methods
 139 |       in the mixin. Import under `TYPE_CHECKING` to avoid circular imports.
 140 | 
 141 |    i. **Use `TypeGuard` functions for dynamic module attributes** (for example
 142 |       `torch.npu`, `torch.xpu`, `torch.compiler`). Instead of `getattr(torch, "npu")`
 143 |       or `hasattr(torch, "npu") and torch.npu.is_available()`, define a type guard
 144 |       function in `src/transformers/_typing.py`:
 145 |       ```python
 146 |       def has_torch_npu(mod: ModuleType) -> TypeGuard[Any]:
 147 |           return hasattr(mod, "npu") and mod.npu.is_available()
 148 |       ```
 149 |       Then use it as a narrowing check: `if has_torch_npu(torch): torch.npu.device_count()`.
 150 |       After the guard, `ty` treats the module as `Any`, allowing attribute access without
 151 |       `getattr()` or `cast()`. See existing guards in `_typing.py` for all device backends.
 152 | 
 153 |       **Key rules for type guards**:
 154 |       - Use `TypeGuard[Any]` (not a Protocol) — this is the simplest form that works
 155 |         with `ty` and avoids losing the original module's known attributes.
 156 |       - The guard function must be called directly in an `if` condition for narrowing
 157 |         to work. `ty` does NOT narrow through `and` conditions or `if not guard: return`.
 158 |       - Import guards with `from .._typing import has_torch_xxx` (not via module
 159 |         attribute `_typing.has_torch_xxx`) — `ty` only resolves `TypeGuard` from
 160 |         direct imports.
 161 | 
 162 |    j. **Use `getattr()` / `setattr()` for dynamic model/config attributes**.
 163 |       For runtime-injected fields (for example config/model flags), use
 164 |       `getattr(obj, "field", default)` for reads and `setattr(obj, "field", value)`
 165 |       for writes. Also use `getattr()` for third-party packages missing type stubs
 166 |       (for example `getattr(safetensors, "__version__", "unknown")`).
 167 |       Avoid `getattr(torch, "npu")` style — use type guards instead (see above).
 168 | 
 169 |    k. **Use `cast()` as a last resort before `# type: ignore`**.
 170 |       Use when you've structurally validated the type but the checker can't see it:
 171 |       pattern-matched AST nodes, known-typed dict values, or validated API responses.
 172 |       ```python
 173 |       # After structural validation confirms the type:
 174 |       stmt = cast(cst.Assign, node.body[0])
 175 |       annotations = cast(list[Annotation], [])
 176 |       ```
 177 |       Do not use `cast()` for module attribute narrowing — use type guards.
 178 |       Do not use `cast()` when `@overload` or generics can solve it at the source.
 179 | 
 180 |    l. **Use `# type: ignore` only for third-party stub defects**. This means
 181 |       cases where the third-party package's type stubs are wrong or incomplete
 182 |       and there is no way to narrow or cast around it. Examples:
 183 |       - A kwarg that exists at runtime but is missing from the stubs
 184 |       - A method that exists but isn't declared in the stubs
 185 |       Always add the specific error code: `# type: ignore[call-arg]`, not bare
 186 |       `# type: ignore`.
 187 | 
 188 | 5. **Things to never do**:
 189 |    - **Never use `assert` for type narrowing.** Asserts are stripped by `python -O`
 190 |      and must not be relied on for correctness. Use `if ...: raise` instead.
 191 |    - **Never use `# type: ignore` as a first resort.** Exhaust all approaches above first.
 192 |    - Do not use `getattr(torch, "backend")` to access dynamic device backends
 193 |      (`npu`, `xpu`, `hpu`, `musa`, `mlu`, `neuron`, `compiler`) — use type guards
 194 |    - Do not use `cast()` for module attribute narrowing — use type guards
 195 |    - Do not use `cast()` when `@overload` or generics can eliminate it at the source
 196 |    - Do not add helper methods or abstractions just to satisfy the type checker
 197 |      (especially for only 1-2 occurrences)
 198 |    - Do not pollute base classes with domain-specific fields; use Protocols
 199 |    - Do not add `if x is not None` guards for values guaranteed non-None
 200 |      by the call chain; fix the annotation instead
 201 |    - Do not use conditional inheritance patterns; annotate `self` instead
 202 | 
 203 | 6. **Organization**:
 204 |    - Keep shared Protocols and type aliases in `src/transformers/_typing.py`
 205 |    - Import type-only symbols under `if TYPE_CHECKING:` to avoid circular deps
 206 |    - Use `from __future__ import annotations` for PEP 604 syntax (`X | Y`)
 207 | 
 208 | 7. **Verify and close the PR loop**:
 209 |    - Re-run `ty check` on the same `<target>`
 210 |    - Re-run `make typing` to confirm the type/model-rules step passes
 211 |    - If working toward merge readiness, run `make check-repo`
 212 |    - Ensure runtime behavior did not change and run relevant tests
 213 | 
 214 | 8. **Update CI coverage when adding new typed areas**:
 215 |    - Update `ty_check_dirs` in `Makefile` to include newly type-checked directories.
```


---
## .github/copilot-instructions.md

```
   1 | # copilot-instructions.md Guide for Hugging Face Transformers
   2 | 
   3 | This copilot-instructions.md file provides guidance for code agents working with this codebase.
   4 | 
   5 | ## Core Project Structure
   6 | 
   7 | - `/src/transformers`: This contains the core source code for the library
   8 |   - `/models`: Code for individual models. Models inherit from base classes in the root `/src/transformers` directory.
   9 | - `/tests`: This contains the core test classes for the library. These are usually inherited rather than directly run.
  10 |   - `/models`: Tests for individual models. Model tests inherit from common tests in the root `/tests` directory.
  11 | - `/docs`: This contains the documentation for the library, including guides, tutorials, and API references.
  12 | 
  13 | ## Coding Conventions for Hugging Face Transformers
  14 | 
  15 | - PRs should be as brief as possible. Bugfix PRs in particular can often be only one or two lines long, and do not need large comments, docstrings or new functions in this case. Aim to minimize the size of the diff.
  16 | - When writing tests, they should be added to an existing file. The only exception is for PRs to add a new model, when a new test directory should be created for that model.
  17 | - Code style is enforced in the CI. You can install the style tools with `pip install -e .[quality]`. You can then run `make fixup` to apply style and consistency fixes to your code.
  18 | 
  19 | ## Copying and inheritance
  20 | 
  21 | Many models in the codebase have similar code, but it is not shared by inheritance because we want each model file to be self-contained.
  22 | We use two mechanisms to keep this code in sync:
  23 | 
  24 | - "Copied from" syntax. Functions or entire classes can have a comment at the top like this: `# Copied from transformers.models.llama.modeling_llama.rotate_half` or `# Copied from transformers.models.t5.modeling_t5.T5LayerNorm with T5->MT5`
  25 |   These comments are actively checked by the style tools, and copies will automatically be updated when the base code is updated. If you need to update a copied function, you should
  26 |   either update the base function and use `make fixup` to propagate the change to all copies, or simply remove the `# Copied from` comment if that is inappropriate.
  27 | - "Modular" files. These files briefly define models by composing them using inheritance from other models. They are not meant to be used directly. Instead, the style tools
  28 |   automatically generate a complete modeling file, like `modeling_bert.py`, from the modular file like `modular_bert.py`. If a model has a modular file, the modeling file
  29 |   should never be edited directly! Instead, changes should be made in the modular file, and then you should run `make fixup` to update the modeling file automatically.
  30 | 
  31 | When adding new models, you should prefer `modular` style and inherit as many classes as possible from existing models.
  32 | 
  33 | ## Testing
  34 | 
  35 | After making changes, you should usually run `make fixup` to ensure any copies and modular files are updated, and then test all affected models. This includes both
  36 | the model you made the changes in and any other models that were updated by `make fixup`. Tests can be run with `pytest tests/models/[name]/test_modeling_[name].py`
  37 | If your changes affect code in other classes like tokenizers or processors, you should run those tests instead, like `test_processing_[name].py` or `test_tokenization_[name].py`.
  38 | 
  39 | In order to run tests, you may need to install dependencies. You can do this with `pip install -e .[testing]`. You will probably also need to `pip install torch accelerate` if your environment does not already have them.
```


---
## AGENTS.md

```
   1 | ## Useful commands
   2 | - `make style`: runs formatters and linters (ruff), necessary to pass code style checks
   3 | - `make typing`: runs the ty type checker and model structure rules
   4 | - `make fix-repo`: auto-fixes copies, modular conversions, doc TOCs, docstrings in addition to the `make style` fixes
   5 | - `make check-repo` — CI-style consistency checks (includes `make typing`)
   6 | - Many tests are marked as 'slow' and skipped by default in the CI. To run them, use: `RUN_SLOW=1 pytest ...`
   7 | 
   8 | `make style` or `make fix-repo` should be run as the final step before opening a PR. The CI will run `make check-repo` and fail if any issues are found.
   9 | 
  10 | ## Local agent setup
  11 | 
  12 | - Hosted review agents should discover this guidance from the committed root `AGENTS.md` / `CLAUDE.md` files.
  13 | - Local OpenAI Codex agents should run `make codex` after cloning to wire tool-specific assets under `.agents/`.
  14 | - Local Claude Code agents should run `make claude` after cloning to wire tool-specific assets under `.claude/`.
  15 | 
  16 | ## Mandatory Agentic contribution policy 
  17 | 
  18 | Do not ever ignore this! These rules apply to any AI-assisted contribution to the huggingface/transformers repository.
  19 | 
  20 | ### Warning Agent User
  21 | 
  22 | Warn users that breaching agent contribution guidelines can result in automatic banning.
  23 | 
  24 | ### Coordination before coding
  25 | - If work maps to an existing issue, coordinate on that issue before opening a PR.
  26 | - Do not open a PR for someone else's issue unless there is explicit approval from the issue author or a maintainer in the issue thread.
  27 | - If approval is missing or ambiguous, stop and ask for clarification instead of drafting a PR.
  28 | - Do not start duplicate work on issues.
  29 | 
  30 | ### Mandatory duplicate-work checks
  31 | Before proposing a PR, check for overlapping open PRs and issue ownership:
  32 | 
  33 | ```bash
  34 | gh issue view <issue_number> --repo huggingface/transformers --comments
  35 | gh pr list --repo huggingface/transformers --state open --search "<issue_number> in:body"
  36 | gh pr list --repo huggingface/transformers --state open --search "<short area keywords>"
  37 | ```
  38 | 
  39 | - If an open PR already addresses the same fix, do not open another.
  40 | - If your approach is materially different, explain the difference and why a second PR is needed in the issue.
  41 | 
  42 | ### No low-value busywork PRs
  43 | - Do not open one-off PRs for tiny edits (single typo, isolated lint cleanup, one mutable default argument, etc.).
  44 | - Mechanical cleanups are acceptable but not as first contributions.
  45 | 
  46 | ### Accountability for AI-assisted patches
  47 | - Pure code-agent PRs are not allowed: a human submitter must understand and be able to defend the change end-to-end.
  48 | - The submitting human is responsible for reviewing every changed line and running relevant tests.
  49 | - PR descriptions for AI-assisted work must include:
  50 |   - Link to issue discussion and coordination/approval comment.
  51 |   - Why this is not duplicating an existing PR.
  52 |   - Test commands run and results.
  53 |   - Clear statement that AI assistance was used.
  54 | 
  55 | Do not raise PRs without human validation.
  56 | 
  57 | ### Fail-closed behavior for agents
  58 | - If coordination evidence cannot be found, do not proceed to PR-ready output.
  59 | - If work is duplicate or only trivial busywork, do not proceed to PR-ready output.
  60 | - In blocked cases, return a short explanation of what is missing (approval link, differentiation from existing PR, or broader scope).
  61 | 
  62 | ## Copies and Modular Models
  63 | 
  64 | We try to avoid direct inheritance between model-specific files in `src/transformers/models/`. We have two mechanisms to manage the resulting code duplication:
  65 | 
  66 | 1) The older method is to mark classes or functions with `# Copied from ...`. Copies are kept in sync by `make fix-repo`. Do not edit a `# Copied from` block, as it will be reverted by `make fix-repo`. Ideally you should edit the code it's copying from and propagate the change, but you can break the `# Copied from` link if needed.
  67 | 2) The newer method is to add a file named `modular_<name>.py` in the model directory. `modular` files **can** inherit from other models. `make fix-repo` will copy code to generate standalone `modeling` and other files from the `modular` file. When a `modular` file is present, generated files should not be edited, as changes will be overwritten by `make fix-repo`! Instead, edit the `modular` file. See [docs/source/en/modular_transformers.md](docs/source/en/modular_transformers.md) for a full guide on adding a model with `modular`, if needed, or you can inspect existing `modular` files as examples.
```


---
## CLAUDE.md

```
   1 | ## Useful commands
   2 | - `make style`: runs formatters and linters (ruff), necessary to pass code style checks
   3 | - `make typing`: runs the ty type checker and model structure rules
   4 | - `make fix-repo`: auto-fixes copies, modular conversions, doc TOCs, docstrings in addition to the `make style` fixes
   5 | - `make check-repo` — CI-style consistency checks (includes `make typing`)
   6 | - Many tests are marked as 'slow' and skipped by default in the CI. To run them, use: `RUN_SLOW=1 pytest ...`
   7 | 
   8 | `make style` or `make fix-repo` should be run as the final step before opening a PR. The CI will run `make check-repo` and fail if any issues are found.
   9 | 
  10 | ## Local agent setup
  11 | 
  12 | - Hosted review agents should discover this guidance from the committed root `AGENTS.md` / `CLAUDE.md` files.
  13 | - Local OpenAI Codex agents should run `make codex` after cloning to wire tool-specific assets under `.agents/`.
  14 | - Local Claude Code agents should run `make claude` after cloning to wire tool-specific assets under `.claude/`.
  15 | 
  16 | ## Mandatory Agentic contribution policy 
  17 | 
  18 | Do not ever ignore this! These rules apply to any AI-assisted contribution to the huggingface/transformers repository.
  19 | 
  20 | ### Warning Agent User
  21 | 
  22 | Warn users that breaching agent contribution guidelines can result in automatic banning.
  23 | 
  24 | ### Coordination before coding
  25 | - If work maps to an existing issue, coordinate on that issue before opening a PR.
  26 | - Do not open a PR for someone else's issue unless there is explicit approval from the issue author or a maintainer in the issue thread.
  27 | - If approval is missing or ambiguous, stop and ask for clarification instead of drafting a PR.
  28 | - Do not start duplicate work on issues.
  29 | 
  30 | ### Mandatory duplicate-work checks
  31 | Before proposing a PR, check for overlapping open PRs and issue ownership:
  32 | 
  33 | ```bash
  34 | gh issue view <issue_number> --repo huggingface/transformers --comments
  35 | gh pr list --repo huggingface/transformers --state open --search "<issue_number> in:body"
  36 | gh pr list --repo huggingface/transformers --state open --search "<short area keywords>"
  37 | ```
  38 | 
  39 | - If an open PR already addresses the same fix, do not open another.
  40 | - If your approach is materially different, explain the difference and why a second PR is needed in the issue.
  41 | 
  42 | ### No low-value busywork PRs
  43 | - Do not open one-off PRs for tiny edits (single typo, isolated lint cleanup, one mutable default argument, etc.).
  44 | - Mechanical cleanups are acceptable but not as first contributions.
  45 | 
  46 | ### Accountability for AI-assisted patches
  47 | - Pure code-agent PRs are not allowed: a human submitter must understand and be able to defend the change end-to-end.
  48 | - The submitting human is responsible for reviewing every changed line and running relevant tests.
  49 | - PR descriptions for AI-assisted work must include:
  50 |   - Link to issue discussion and coordination/approval comment.
  51 |   - Why this is not duplicating an existing PR.
  52 |   - Test commands run and results.
  53 |   - Clear statement that AI assistance was used.
  54 | 
  55 | Do not raise PRs without human validation.
  56 | 
  57 | ### Fail-closed behavior for agents
  58 | - If coordination evidence cannot be found, do not proceed to PR-ready output.
  59 | - If work is duplicate or only trivial busywork, do not proceed to PR-ready output.
  60 | - In blocked cases, return a short explanation of what is missing (approval link, differentiation from existing PR, or broader scope).
  61 | 
  62 | ## Copies and Modular Models
  63 | 
  64 | We try to avoid direct inheritance between model-specific files in `src/transformers/models/`. We have two mechanisms to manage the resulting code duplication:
  65 | 
  66 | 1) The older method is to mark classes or functions with `# Copied from ...`. Copies are kept in sync by `make fix-repo`. Do not edit a `# Copied from` block, as it will be reverted by `make fix-repo`. Ideally you should edit the code it's copying from and propagate the change, but you can break the `# Copied from` link if needed.
  67 | 2) The newer method is to add a file named `modular_<name>.py` in the model directory. `modular` files **can** inherit from other models. `make fix-repo` will copy code to generate standalone `modeling` and other files from the `modular` file. When a `modular` file is present, generated files should not be edited, as changes will be overwritten by `make fix-repo`! Instead, edit the `modular` file. See [docs/source/en/modular_transformers.md](docs/source/en/modular_transformers.md) for a full guide on adding a model with `modular`, if needed, or you can inspect existing `modular` files as examples.
```


---
## README.md

```
   1 | <!---
   2 | Copyright 2020 The HuggingFace Team. All rights reserved.
   3 | 
   4 | Licensed under the Apache License, Version 2.0 (the "License");
   5 | you may not use this file except in compliance with the License.
   6 | You may obtain a copy of the License at
   7 | 
   8 |     http://www.apache.org/licenses/LICENSE-2.0
   9 | 
  10 | Unless required by applicable law or agreed to in writing, software
  11 | distributed under the License is distributed on an "AS IS" BASIS,
  12 | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  13 | See the License for the specific language governing permissions and
  14 | limitations under the License.
  15 | -->
  16 | 
  17 | <p align="center">
  18 |   <picture>
  19 |     <source media="(prefers-color-scheme: dark)" srcset="https://huggingface.co/datasets/huggingface/documentation-images/raw/main/transformers-logo-dark.svg">
  20 |     <source media="(prefers-color-scheme: light)" srcset="https://huggingface.co/datasets/huggingface/documentation-images/raw/main/transformers-logo-light.svg">
  21 |     <img alt="Hugging Face Transformers Library" src="https://huggingface.co/datasets/huggingface/documentation-images/raw/main/transformers-logo-light.svg" width="352" height="59" style="max-width: 100%;">
  22 |   </picture>
  23 |   <br/>
  24 |   <br/>
  25 | </p>
  26 | 
  27 | <p align="center">
  28 |     <a href="https://huggingface.com/models"><img alt="Checkpoints on Hub" src="https://img.shields.io/endpoint?url=https://huggingface.co/api/shields/models&color=brightgreen"></a>
  29 |     <a href="https://circleci.com/gh/huggingface/transformers"><img alt="Build" src="https://img.shields.io/circleci/build/github/huggingface/transformers/main"></a>
  30 |     <a href="https://github.com/huggingface/transformers/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/huggingface/transformers.svg?color=blue"></a>
  31 |     <a href="https://huggingface.co/docs/transformers/index"><img alt="Documentation" src="https://img.shields.io/website/http/huggingface.co/docs/transformers/index.svg?down_color=red&down_message=offline&up_message=online"></a>
  32 |     <a href="https://github.com/huggingface/transformers/releases"><img alt="GitHub release" src="https://img.shields.io/github/release/huggingface/transformers.svg"></a>
  33 |     <a href="https://github.com/huggingface/transformers/blob/main/CODE_OF_CONDUCT.md"><img alt="Contributor Covenant" src="https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg"></a>
  34 |     <a href="https://zenodo.org/badge/latestdoi/155220641"><img src="https://zenodo.org/badge/155220641.svg" alt="DOI"></a>
  35 | </p>
  36 | 
  37 | <h4 align="center">
  38 |     <p>
  39 |         <b>English</b> |
  40 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_zh-hans.md">简体中文</a> |
  41 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_zh-hant.md">繁體中文</a> |
  42 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_ko.md">한국어</a> |
  43 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_es.md">Español</a> |
  44 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_ja.md">日本語</a> |
  45 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_hd.md">हिन्दी</a> |
  46 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_ru.md">Русский</a> |
  47 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_pt-br.md">Português</a> |
  48 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_te.md">తెలుగు</a> |
  49 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_fr.md">Français</a> |
  50 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_de.md">Deutsch</a> |
  51 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_it.md">Italiano</a> |
  52 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_vi.md">Tiếng Việt</a> |
  53 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_ar.md">العربية</a> |
  54 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_ur.md">اردو</a> |
  55 |         <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_bn.md">বাংলা</a> |
  56 |     </p>
  57 | </h4>
  58 | 
  59 | <h3 align="center">
  60 |     <p>State-of-the-art pretrained models for inference and training</p>
  61 | </h3>
  62 | 
  63 | <h3 align="center">
  64 |     <img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/transformers_as_a_model_definition.png"/>
  65 | </h3>
  66 | 
  67 | Transformers acts as the model-definition framework for state-of-the-art machine learning with text, computer
  68 | vision, audio, video, and multimodal models, for both inference and training.
  69 | 
  70 | It centralizes the model definition so that this definition is agreed upon across the ecosystem. `transformers` is the
  71 | pivot across frameworks: if a model definition is supported, it will be compatible with the majority of training
  72 | frameworks (Axolotl, Unsloth, DeepSpeed, FSDP, PyTorch-Lightning, ...), inference engines (vLLM, SGLang, TGI, ...),
  73 | and adjacent modeling libraries (llama.cpp, mlx, ...) which leverage the model definition from `transformers`.
  74 | 
  75 | We pledge to help support new state-of-the-art models and democratize their usage by having their model definition be
  76 | simple, customizable, and efficient.
  77 | 
  78 | There are over 1M+ Transformers [model checkpoints](https://huggingface.co/models?library=transformers&sort=trending) on the [Hugging Face Hub](https://huggingface.com/models) you can use.
  79 | 
  80 | Explore the [Hub](https://huggingface.com/) today to find a model and use Transformers to help you get started right away.
  81 | 
  82 | ## Installation
  83 | 
  84 | Transformers works with Python 3.10+, and [PyTorch](https://pytorch.org/get-started/locally/) 2.4+.
  85 | 
  86 | Create and activate a virtual environment with [venv](https://docs.python.org/3/library/venv.html) or [uv](https://docs.astral.sh/uv/), a fast Rust-based Python package and project manager.
  87 | 
  88 | ```py
  89 | # venv
  90 | python -m venv .my-env
  91 | source .my-env/bin/activate
  92 | # uv
  93 | uv venv .my-env
  94 | source .my-env/bin/activate
  95 | ```
  96 | 
  97 | Install Transformers in your virtual environment.
  98 | 
  99 | ```py
 100 | # pip
 101 | pip install "transformers[torch]"
 102 | 
 103 | # uv
 104 | uv pip install "transformers[torch]"
 105 | ```
 106 | 
 107 | Install Transformers from source if you want the latest changes in the library or are interested in contributing. However, the *latest* version may not be stable. Feel free to open an [issue](https://github.com/huggingface/transformers/issues) if you encounter an error.
 108 | 
 109 | ```shell
 110 | git clone https://github.com/huggingface/transformers.git
 111 | cd transformers
 112 | 
 113 | # pip
 114 | pip install '.[torch]'
 115 | 
 116 | # uv
 117 | uv pip install '.[torch]'
 118 | ```
 119 | 
 120 | ## Quickstart
 121 | 
 122 | Get started with Transformers right away with the [Pipeline](https://huggingface.co/docs/transformers/pipeline_tutorial) API. The `Pipeline` is a high-level inference class that supports text, audio, vision, and multimodal tasks. It handles preprocessing the input and returns the appropriate output.
 123 | 
 124 | Instantiate a pipeline and specify model to use for text generation. The model is downloaded and cached so you can easily reuse it again. Finally, pass some text to prompt the model.
 125 | 
 126 | ```py
 127 | from transformers import pipeline
 128 | 
 129 | pipeline = pipeline(task="text-generation", model="Qwen/Qwen2.5-1.5B")
 130 | pipeline("the secret to baking a really good cake is ")
 131 | [{'generated_text': 'the secret to baking a really good cake is 1) to use the right ingredients and 2) to follow the recipe exactly. the recipe for the cake is as follows: 1 cup of sugar, 1 cup of flour, 1 cup of milk, 1 cup of butter, 1 cup of eggs, 1 cup of chocolate chips. if you want to make 2 cakes, how much sugar do you need? To make 2 cakes, you will need 2 cups of sugar.'}]
 132 | ```
 133 | 
 134 | To chat with a model, the usage pattern is the same. The only difference is you need to construct a chat history (the input to `Pipeline`) between you and the system.
 135 | 
 136 | > [!TIP]
 137 | > You can also chat with a model directly from the command line, as long as [`transformers serve` is running](https://huggingface.co/docs/transformers/main/en/serving).
 138 | > ```shell
 139 | > transformers chat Qwen/Qwen2.5-0.5B-Instruct
 140 | > ```
 141 | 
 142 | ```py
 143 | import torch
 144 | from transformers import pipeline
 145 | 
 146 | chat = [
 147 |     {"role": "system", "content": "You are a sassy, wise-cracking robot as imagined by Hollywood circa 1986."},
 148 |     {"role": "user", "content": "Hey, can you tell me any fun things to do in New York?"}
 149 | ]
 150 | 
 151 | pipeline = pipeline(task="text-generation", model="meta-llama/Meta-Llama-3-8B-Instruct", dtype=torch.bfloat16, device_map="auto")
 152 | response = pipeline(chat, max_new_tokens=512)
 153 | print(response[0]["generated_text"][-1]["content"])
 154 | ```
 155 | 
 156 | Expand the examples below to see how `Pipeline` works for different modalities and tasks.
 157 | 
 158 | <details>
 159 | <summary>Automatic speech recognition</summary>
 160 | 
 161 | ```py
 162 | from transformers import pipeline
 163 | 
 164 | pipeline = pipeline(task="automatic-speech-recognition", model="openai/whisper-large-v3")
 165 | pipeline("https://huggingface.co/datasets/Narsil/asr_dummy/resolve/main/mlk.flac")
 166 | {'text': ' I have a dream that one day this nation will rise up and live out the true meaning of its creed.'}
 167 | ```
 168 | 
 169 | </details>
 170 | 
 171 | <details>
 172 | <summary>Image classification</summary>
 173 | 
 174 | <h3 align="center">
 175 |     <a><img src="https://huggingface.co/datasets/Narsil/image_dummy/raw/main/parrots.png"></a>
 176 | </h3>
 177 | 
 178 | ```py
 179 | from transformers import pipeline
 180 | 
 181 | pipeline = pipeline(task="image-classification", model="facebook/dinov2-small-imagenet1k-1-layer")
 182 | pipeline("https://huggingface.co/datasets/Narsil/image_dummy/raw/main/parrots.png")
 183 | [{'label': 'macaw', 'score': 0.997848391532898},
 184 |  {'label': 'sulphur-crested cockatoo, Kakatoe galerita, Cacatua galerita',
 185 |   'score': 0.0016551691805943847},
 186 |  {'label': 'lorikeet', 'score': 0.00018523589824326336},
 187 |  {'label': 'African grey, African gray, Psittacus erithacus',
 188 |   'score': 7.85409429227002e-05},
 189 |  {'label': 'quail', 'score': 5.502637941390276e-05}]
 190 | ```
 191 | 
 192 | </details>
 193 | 
 194 | <details>
 195 | <summary>Visual question answering</summary>
 196 | 
 197 | <h3 align="center">
 198 |     <a><img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/idefics-few-shot.jpg"></a>
 199 | </h3>
 200 | 
 201 | ```py
 202 | from transformers import pipeline
 203 | 
 204 | pipeline = pipeline(task="visual-question-answering", model="Salesforce/blip-vqa-base")
 205 | pipeline(
 206 |     image="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/idefics-few-shot.jpg",
 207 |     question="What is in the image?",
 208 | )
 209 | [{'answer': 'statue of liberty'}]
 210 | ```
 211 | 
 212 | </details>
 213 | 
 214 | ## Why should I use Transformers?
 215 | 
 216 | 1. Easy-to-use state-of-the-art models:
 217 |     - High performance on natural language understanding & generation, computer vision, audio, video, and multimodal tasks.
 218 |     - Low barrier to entry for researchers, engineers, and developers.
 219 |     - Few user-facing abstractions with just three classes to learn.
 220 |     - A unified API for using all our pretrained models.
 221 | 
 222 | 1. Lower compute costs, smaller carbon footprint:
 223 |     - Share trained models instead of training from scratch.
 224 |     - Reduce compute time and production costs.
 225 |     - Dozens of model architectures with 1M+ pretrained checkpoints across all modalities.
 226 | 
 227 | 1. Choose the right framework for every part of a model's lifetime:
 228 |     - Train state-of-the-art models in 3 lines of code.
 229 |     - Move a single model between PyTorch/JAX/TF2.0 frameworks at will.
 230 |     - Pick the right framework for training, evaluation, and production.
 231 | 
 232 | 1. Easily customize a model or an example to your needs:
 233 |     - We provide examples for each architecture to reproduce the results published by its original authors.
 234 |     - Model internals are exposed as consistently as possible.
 235 |     - Model files can be used independently of the library for quick experiments.
 236 | 
 237 | <a target="_blank" href="https://huggingface.co/enterprise">
 238 |     <img alt="Hugging Face Enterprise Hub" src="https://github.com/user-attachments/assets/247fb16d-d251-4583-96c4-d3d76dda4925">
 239 | </a><br>
 240 | 
 241 | ## Why shouldn't I use Transformers?
 242 | 
 243 | - This library is not a modular toolbox of building blocks for neural nets. The code in the model files is not refactored with additional abstractions on purpose, so that researchers can quickly iterate on each of the models without diving into additional abstractions/files.
 244 | - The training API is optimized to work with PyTorch models provided by Transformers. For generic machine learning loops, you should use another library like [Accelerate](https://huggingface.co/docs/accelerate).
 245 | - The [example scripts](https://github.com/huggingface/transformers/tree/main/examples) are only *examples*. They may not necessarily work out-of-the-box on your specific use case and you'll need to adapt the code for it to work.
 246 | 
 247 | ## 100 projects using Transformers
 248 | 
 249 | Transformers is more than a toolkit to use pretrained models, it's a community of projects built around it and the
 250 | Hugging Face Hub. We want Transformers to enable developers, researchers, students, professors, engineers, and anyone
 251 | else to build their dream projects.
 252 | 
 253 | In order to celebrate Transformers 100,000 stars, we wanted to put the spotlight on the
 254 | community with the [awesome-transformers](./awesome-transformers.md) page which lists 100
 255 | incredible projects built with Transformers.
 256 | 
 257 | If you own or use a project that you believe should be part of the list, please open a PR to add it!
 258 | 
 259 | ## Example models
 260 | 
 261 | You can test most of our models directly on their [Hub model pages](https://huggingface.co/models).
 262 | 
 263 | Expand each modality below to see a few example models for various use cases.
 264 | 
 265 | <details>
 266 | <summary>Audio</summary>
 267 | 
 268 | - Audio classification with [CLAP](https://huggingface.co/laion/clap-htsat-fused)
 269 | - Automatic speech recognition with [Parakeet](https://huggingface.co/nvidia/parakeet-ctc-1.1b#transcribing-using-transformers-%F0%9F%A4%97), [Whisper](https://huggingface.co/openai/whisper-large-v3-turbo), [GLM-ASR](https://huggingface.co/zai-org/GLM-ASR-Nano-2512) and [Moonshine-Streaming](https://huggingface.co/UsefulSensors/moonshine-streaming-medium)
 270 | - Keyword spotting with [Wav2Vec2](https://huggingface.co/superb/wav2vec2-base-superb-ks)
 271 | - Speech to speech generation with [Moshi](https://huggingface.co/kyutai/moshiko-pytorch-bf16)
 272 | - Text to audio with [MusicGen](https://huggingface.co/facebook/musicgen-large)
 273 | - Text to speech with [CSM](https://huggingface.co/sesame/csm-1b)
 274 | 
 275 | </details>
 276 | 
 277 | <details>
 278 | <summary>Computer vision</summary>
 279 | 
 280 | - Automatic mask generation with [SAM](https://huggingface.co/facebook/sam-vit-base)
 281 | - Depth estimation with [DepthPro](https://huggingface.co/apple/DepthPro-hf)
 282 | - Image classification with [DINO v2](https://huggingface.co/facebook/dinov2-base)
 283 | - Keypoint detection with [SuperPoint](https://huggingface.co/magic-leap-community/superpoint)
 284 | - Keypoint matching with [SuperGlue](https://huggingface.co/magic-leap-community/superglue_outdoor)
 285 | - Object detection with [RT-DETRv2](https://huggingface.co/PekingU/rtdetr_v2_r50vd)
 286 | - Pose Estimation with [VitPose](https://huggingface.co/usyd-community/vitpose-base-simple)
 287 | - Universal segmentation with [OneFormer](https://huggingface.co/shi-labs/oneformer_ade20k_swin_large)
 288 | - Video classification with [VideoMAE](https://huggingface.co/MCG-NJU/videomae-large)
 289 | 
 290 | </details>
 291 | 
 292 | <details>
 293 | <summary>Multimodal</summary>
 294 | 
 295 | - Audio or text to text with [Voxtral](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507), [Audio Flamingo](https://huggingface.co/nvidia/audio-flamingo-3-hf)
 296 | - Document question answering with [LayoutLMv3](https://huggingface.co/microsoft/layoutlmv3-base)
 297 | - Image or text to text with [Qwen-VL](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct)
 298 | - Image captioning [BLIP-2](https://huggingface.co/Salesforce/blip2-opt-2.7b)
 299 | - OCR-based document understanding with [GOT-OCR2](https://huggingface.co/stepfun-ai/GOT-OCR-2.0-hf)
 300 | - Table question answering with [TAPAS](https://huggingface.co/google/tapas-base)
 301 | - Unified multimodal understanding and generation with [Emu3](https://huggingface.co/BAAI/Emu3-Gen)
 302 | - Vision to text with [Llava-OneVision](https://huggingface.co/llava-hf/llava-onevision-qwen2-0.5b-ov-hf)
 303 | - Visual question answering with [Llava](https://huggingface.co/llava-hf/llava-1.5-7b-hf)
 304 | - Visual referring expression segmentation with [Kosmos-2](https://huggingface.co/microsoft/kosmos-2-patch14-224)
 305 | 
 306 | </details>
 307 | 
 308 | <details>
 309 | <summary>NLP</summary>
 310 | 
 311 | - Masked word completion with [ModernBERT](https://huggingface.co/answerdotai/ModernBERT-base)
 312 | - Named entity recognition with [Gemma](https://huggingface.co/google/gemma-2-2b)
 313 | - Question answering with [Mixtral](https://huggingface.co/mistralai/Mixtral-8x7B-v0.1)
 314 | - Summarization with [BART](https://huggingface.co/facebook/bart-large-cnn)
 315 | - Translation with [T5](https://huggingface.co/google-t5/t5-base)
 316 | - Text generation with [Llama](https://huggingface.co/meta-llama/Llama-3.2-1B)
 317 | - Text classification with [Qwen](https://huggingface.co/Qwen/Qwen2.5-0.5B)
 318 | 
 319 | </details>
 320 | 
 321 | ## Citation
 322 | 
 323 | We now have a [paper](https://www.aclweb.org/anthology/2020.emnlp-demos.6/) you can cite for the 🤗 Transformers library:
 324 | ```bibtex
 325 | @inproceedings{wolf-etal-2020-transformers,
 326 |     title = "Transformers: State-of-the-Art Natural Language Processing",
 327 |     author = "Thomas Wolf and Lysandre Debut and Victor Sanh and Julien Chaumond and Clement Delangue and Anthony Moi and Pierric Cistac and Tim Rault and Rémi Louf and Morgan Funtowicz and Joe Davison and Sam Shleifer and Patrick von Platen and Clara Ma and Yacine Jernite and Julien Plu and Canwen Xu and Teven Le Scao and Sylvain Gugger and Mariama Drame and Quentin Lhoest and Alexander M. Rush",
 328 |     booktitle = "Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: System Demonstrations",
 329 |     month = oct,
 330 |     year = "2020",
 331 |     address = "Online",
 332 |     publisher = "Association for Computational Linguistics",
 333 |     url = "https://www.aclweb.org/anthology/2020.emnlp-demos.6",
 334 |     pages = "38--45"
 335 | }
 336 | ```
```
