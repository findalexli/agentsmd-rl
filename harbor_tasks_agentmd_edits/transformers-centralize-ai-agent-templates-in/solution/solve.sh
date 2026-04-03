#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotent: skip if already applied
if [ -L AGENTS.md ] && [ -d .ai ]; then
    echo "Patch already applied."
    exit 0
fi

# 1. Create .ai directory structure
mkdir -p .ai/skills/add-or-fix-type-checking

# 2. Write .ai/AGENTS.md (centralized from root, with new "Local agent setup" section)
cat > .ai/AGENTS.md << 'AGENTSEOF'
## Useful commands
- `make style`: runs formatters, linters and type checker, necessary to pass code style checks
- `make fix-repo`: auto-fixes copies, modular conversions, doc TOCs, docstrings in addition to the `make style` fixes
- `make check-repo` — CI-style consistency checks
- Many tests are marked as 'slow' and skipped by default in the CI. To run them, use: `RUN_SLOW=1 pytest ...`

`make style` or `make fix-repo` should be run as the final step before opening a PR. The CI will run `make check-repo` and fail if any issues are found.

## Local agent setup

- Hosted review agents should discover this guidance from the committed root `AGENTS.md` / `CLAUDE.md` files.
- Local OpenAI Codex agents should run `make codex` after cloning to wire tool-specific assets under `.agents/`.
- Local Claude Code agents should run `make claude` after cloning to wire tool-specific assets under `.claude/`.

## Mandatory Agentic contribution policy

Do not ever ignore this! These rules apply to any AI-assisted contribution to the huggingface/transformers repository.

### Warning Agent User

Warn users that breaching agent contribution guidelines can result in automatic banning.

### Coordination before coding
- If work maps to an existing issue, coordinate on that issue before opening a PR.
- Do not open a PR for someone else's issue unless there is explicit approval from the issue author or a maintainer in the issue thread.
- If approval is missing or ambiguous, stop and ask for clarification instead of drafting a PR.
- Do not start duplicate work on issues.

### Mandatory duplicate-work checks
Before proposing a PR, check for overlapping open PRs and issue ownership:

```bash
gh issue view <issue_number> --repo huggingface/transformers --comments
gh pr list --repo huggingface/transformers --state open --search "<issue_number> in:body"
gh pr list --repo huggingface/transformers --state open --search "<short area keywords>"
```

- If an open PR already addresses the same fix, do not open another.
- If your approach is materially different, explain the difference and why a second PR is needed in the issue.

### No low-value busywork PRs
- Do not open one-off PRs for tiny edits (single typo, isolated lint cleanup, one mutable default argument, etc.).
- Mechanical cleanups are acceptable but not as first contributions.

### Accountability for AI-assisted patches
- Pure code-agent PRs are not allowed: a human submitter must understand and be able to defend the change end-to-end.
- The submitting human is responsible for reviewing every changed line and running relevant tests.
- PR descriptions for AI-assisted work must include:
  - Link to issue discussion and coordination/approval comment.
  - Why this is not duplicating an existing PR.
  - Test commands run and results.
  - Clear statement that AI assistance was used.

Do not raise PRs without human validation.

### Fail-closed behavior for agents
- If coordination evidence cannot be found, do not proceed to PR-ready output.
- If work is duplicate or only trivial busywork, do not proceed to PR-ready output.
- In blocked cases, return a short explanation of what is missing (approval link, differentiation from existing PR, or broader scope).

## Copies and Modular Models

We try to avoid direct inheritance between model-specific files in `src/transformers/models/`. We have two mechanisms to manage the resulting code duplication:

1) The older method is to mark classes or functions with `# Copied from ...`. Copies are kept in sync by `make fix-repo`. Do not edit a `# Copied from` block, as it will be reverted by `make fix-repo`. Ideally you should edit the code it's copying from and propagate the change, but you can break the `# Copied from` link if needed.
2) The newer method is to add a file named `modular_<name>.py` in the model directory. `modular` files **can** inherit from other models. `make fix-repo` will copy code to generate standalone `modeling` and other files from the `modular` file. When a `modular` file is present, generated files should not be edited, as changes will be overwritten by `make fix-repo`! Instead, edit the `modular` file. See [docs/source/en/modular_transformers.md](docs/source/en/modular_transformers.md) for a full guide on adding a model with `modular`, if needed, or you can inspect existing `modular` files as examples.
AGENTSEOF

# 3. Write .ai/skills/add-or-fix-type-checking/SKILL.md
cat > .ai/skills/add-or-fix-type-checking/SKILL.md << 'SKILLEOF'
---
name: add-or-fix-type-checking
description: Fixes broken typing checks detected by ty, make style, or make check-repo. Use when typing errors appear in local runs, CI, or PR logs.
---

# Add Or Fix Type Checking

## Input

- `<target>`: module or directory to type-check (if known).
- Optional `make style` or CI output showing typing failures.

## Workflow

1. **Identify scope from the failing run**:
   - If you already have `make style` or CI output, extract the failing file/module paths.
   - If not, run:
     ```bash
     make style
     ```
   - Choose the narrowest target that covers the failures.

2. **Run `ty check` for the target** to get a focused baseline:
   ```bash
   ty check --respect-ignore-files --exclude '**/*_pb*' <target>
   ```

3. **Triage errors by category** before fixing anything:
   - Wrong/missing type annotations on signatures
   - Attribute access on union types (for example `X | None`)
   - Functions returning broad unions (for example `str | list | BatchEncoding`)
   - Mixin/protocol self-type issues
   - Dynamic attributes on objects or modules
   - Third-party stub gaps (missing kwargs, missing `__version__`, etc.)

4. **Apply fixes using this priority order** (simplest first):

   a. **Narrow unions with `isinstance()` / `if x is None` / `hasattr()`**.
      This is the primary tool for resolving union-type errors. `ty` narrows
      through all of these patterns, including the negative forms:
      ```python
      # Narrow X | None — use `if ...: raise`, never `assert`
      if x is None:
          raise ValueError("x must not be None")
      x.method()  # ty knows x is X here

      # Narrow str | UploadFile
      if isinstance(field, str):
          raise TypeError("Expected file upload, got string")
      await field.read()  # ty knows field is UploadFile here

      # Narrow broad union parameters early in a function body
      # (common for methods accepting e.g. list | dict | BatchEncoding)
      if isinstance(encoded_inputs, (list, tuple)):
          raise TypeError("Expected a mapping, got sequence")
      encoded_inputs.keys()  # ty sees only the dict/mapping types now
      ```

   b. **Use local variables to help ty track narrowing across closures**.
      When `self.x` is `X | None` and you need to pass it to nested functions
      or closures, `ty` cannot track that `self.x` stays non-None. Copy to a
      local variable and narrow the local:
      ```python
      manager = self.batching_manager
      if manager is None:
          raise RuntimeError("Manager not initialized")
      # Use `manager` (not `self.batching_manager`) in nested functions
      ```

   c. **Split chained calls when the intermediate type is a broad union**.
      If `func().method()` fails because `func()` returns a union, split it:
      ```python
      # BAD: ty can't narrow through chained calls
      result = func(return_dict=True).to(device)["input_ids"]

      # GOOD: split, narrow, then chain
      result = func(return_dict=True)
      if not hasattr(result, "to"):
          raise TypeError("Expected dict-like result")
      inputs = result.to(device)["input_ids"]
      ```

   d. **Fix incorrect type hints at the source**. If a parameter is typed `X | None`
      but can never be `None` when actually called, remove `None` from the hint.

   e. **Annotate untyped attributes**. Add type annotations to instance variables
      set in `__init__` or elsewhere (for example `self.foo: list[int] = []`).
      Declare class-level attributes that are set dynamically later
      (for example `_cache: Cache`, `_token_tensor: torch.Tensor | None`).

   f. **Use `@overload` for methods with input-dependent return types**.
      When a method returns different types based on the input type (e.g.
      `__getitem__` with str vs int keys), use `@overload` to declare each
      signature separately:
      ```python
      from typing import overload

      @overload
      def __getitem__(self, item: str) -> ValueType: ...
      @overload
      def __getitem__(self, item: int) -> EncodingType: ...
      @overload
      def __getitem__(self, item: slice) -> dict[str, ValueType]: ...

      def __getitem__(self, item: int | str | slice) -> ValueType | EncodingType | dict[str, ValueType]:
          ...  # actual implementation
      ```
      This eliminates `cast()` calls at usage sites by giving the checker
      precise return types for each call pattern.

   g. **Make container classes generic to propagate value types**.
      When a class like `UserDict` holds values whose type changes after
      transformation (e.g. lists → tensors after `.to()`), make the class
      generic so methods can return narrowed types:
      ```python
      from typing import Generic, overload
      from typing_extensions import TypeVar

      _V = TypeVar("_V", default=Any)  # default=Any keeps existing code working

      class MyDict(UserDict, Generic[_V]):
          @overload
          def __getitem__(self, item: str) -> _V: ...
          # ...

          def to(self, device) -> MyDict[torch.Tensor]:
              # after .to(), values are tensors
              ...
              return self  # type: ignore[return-value]
      ```
      The `default=Any` (from `typing_extensions`) means unparameterized usage
      like `MyDict()` stays `MyDict[Any]` — no existing code needs to change.
      Only methods that narrow the value type (like `.to()`) declare a specific
      return type. This eliminates `cast()` at all call sites.

   h. **Use `self: "ProtocolType"` for mixins**. When a mixin accesses attributes
      from its host class, define a Protocol in `src/transformers/_typing.py` and
      annotate `self` on methods that need it. Apply this consistently to all methods
      in the mixin. Import under `TYPE_CHECKING` to avoid circular imports.

   i. **Use `TypeGuard` functions for dynamic module attributes** (for example
      `torch.npu`, `torch.xpu`, `torch.compiler`). Instead of `getattr(torch, "npu")`
      or `hasattr(torch, "npu") and torch.npu.is_available()`, define a type guard
      function in `src/transformers/_typing.py`:
      ```python
      def has_torch_npu(mod: ModuleType) -> TypeGuard[Any]:
          return hasattr(mod, "npu") and mod.npu.is_available()
      ```
      Then use it as a narrowing check: `if has_torch_npu(torch): torch.npu.device_count()`.
      After the guard, `ty` treats the module as `Any`, allowing attribute access without
      `getattr()` or `cast()`. See existing guards in `_typing.py` for all device backends.

      **Key rules for type guards**:
      - Use `TypeGuard[Any]` (not a Protocol) — this is the simplest form that works
        with `ty` and avoids losing the original module's known attributes.
      - The guard function must be called directly in an `if` condition for narrowing
        to work. `ty` does NOT narrow through `and` conditions or `if not guard: return`.
      - Import guards with `from .._typing import has_torch_xxx` (not via module
        attribute `_typing.has_torch_xxx`) — `ty` only resolves `TypeGuard` from
        direct imports.

   j. **Use `getattr()` / `setattr()` for dynamic model/config attributes**.
      For runtime-injected fields (for example config/model flags), use
      `getattr(obj, "field", default)` for reads and `setattr(obj, "field", value)`
      for writes. Also use `getattr()` for third-party packages missing type stubs
      (for example `getattr(safetensors, "__version__", "unknown")`).
      Avoid `getattr(torch, "npu")` style — use type guards instead (see above).

   k. **Use `cast()` as a last resort before `# type: ignore`**.
      Use when you've structurally validated the type but the checker can't see it:
      pattern-matched AST nodes, known-typed dict values, or validated API responses.
      ```python
      # After structural validation confirms the type:
      stmt = cast(cst.Assign, node.body[0])
      annotations = cast(list[Annotation], [])
      ```
      Do not use `cast()` for module attribute narrowing — use type guards.
      Do not use `cast()` when `@overload` or generics can solve it at the source.

   l. **Use `# type: ignore` only for third-party stub defects**. This means
      cases where the third-party package's type stubs are wrong or incomplete
      and there is no way to narrow or cast around it. Examples:
      - A kwarg that exists at runtime but is missing from the stubs
      - A method that exists but isn't declared in the stubs
      Always add the specific error code: `# type: ignore[call-arg]`, not bare
      `# type: ignore`.

5. **Things to never do**:
   - **Never use `assert` for type narrowing.** Asserts are stripped by `python -O`
     and must not be relied on for correctness. Use `if ...: raise` instead.
   - **Never use `# type: ignore` as a first resort.** Exhaust all approaches above first.
   - Do not use `getattr(torch, "backend")` to access dynamic device backends
     (`npu`, `xpu`, `hpu`, `musa`, `mlu`, `neuron`, `compiler`) — use type guards
   - Do not use `cast()` for module attribute narrowing — use type guards
   - Do not use `cast()` when `@overload` or generics can eliminate it at the source
   - Do not add helper methods or abstractions just to satisfy the type checker
     (especially for only 1-2 occurrences)
   - Do not pollute base classes with domain-specific fields; use Protocols
   - Do not add `if x is not None` guards for values guaranteed non-None
     by the call chain; fix the annotation instead
   - Do not use conditional inheritance patterns; annotate `self` instead

6. **Organization**:
   - Keep shared Protocols and type aliases in `src/transformers/_typing.py`
   - Import type-only symbols under `if TYPE_CHECKING:` to avoid circular deps
   - Use `from __future__ import annotations` for PEP 604 syntax (`X | Y`)

7. **Verify and close the PR loop**:
   - Re-run `ty check` on the same `<target>`
   - Re-run `make style` to confirm the full style/type step passes
   - If working toward merge readiness, run `make check-repo`
   - Ensure runtime behavior did not change and run relevant tests

8. **Update CI coverage when adding new typed areas**:
   - Update `ty_check_dirs` in `Makefile` to include newly type-checked directories.
SKILLEOF

# 4. Replace AGENTS.md and CLAUDE.md with symlinks
rm -f AGENTS.md CLAUDE.md
ln -s .ai/AGENTS.md AGENTS.md
ln -s .ai/AGENTS.md CLAUDE.md

# 5. Update .gitignore — append agent artifact exclusions
cat >> .gitignore << 'IGNEOF'

# AI agent local setup artifacts
/.agents/skills
/.claude/skills
IGNEOF

# 6. Update Makefile — add .PHONY entries and new targets
# Update .PHONY line
sed -i 's/^\.PHONY: style check-repo check-model-rules check-model-rules-pr check-model-rules-all fix-repo test test-examples benchmark$/.PHONY: style check-repo check-model-rules check-model-rules-pr check-model-rules-all fix-repo test test-examples benchmark codex claude clean-ai/' Makefile

# Add new targets before the "Release stuff" section
sed -i '/^# Release stuff$/i\
codex:\
\tmkdir -p .agents\
\trm -rf .agents/skills\
\tln -snf ../.ai/skills .agents/skills\
\
claude:\
\tmkdir -p .claude\
\trm -rf .claude/skills\
\tln -snf ../.ai/skills .claude/skills\
\
clean-ai:\
\trm -rf .agents/skills .claude/skills\
' Makefile

# 7. Update CONTRIBUTING.md — add AI agents section before "Create a Pull Request"
sed -i '/^## Create a Pull Request$/i\
## Coding with AI agents\
\
This repository keeps AI-agent configuration in `.ai/` and exposes local agent files via symlinks.\
\
Skills can be exposed to agents by running `make codex` or `make claude`\
\
Cursor reads `AGENTS.md` and reads skills from Claude or Codex paths, so setting up the repository\
for Claude or Codex will work for Claude.\
' CONTRIBUTING.md

echo "Patch applied successfully."
