# Treat abi3 wheel Python tag as a lower bound

## Context

`uv` is a Rust-based Python package manager. When `uv` resolves wheels, it
derives a set of "implied" PEP 508 environment markers from the wheel's
filename tags so the resolver knows which environments a wheel is
compatible with. The relevant logic lives in:

  `crates/uv-distribution-types/src/prioritized_distribution.rs`

inside the function `implied_python_markers(filename: &WheelFilename)`,
called by the public `implied_markers(filename: &WheelFilename)` wrapper.

## Bug

A wheel filename like

  `flashinfer_jit_cache-0.5.3+cu130-cp39-abi3-manylinux_2_28_x86_64.whl`

uses the **abi3** stable ABI. Per the wheel spec and PEP 384, an `abi3`
wheel built for Python tag `cpXY` is compatible with **CPython X.Y or
later** — the Python tag is a *lower bound*, not an exact version.

The current implementation in `implied_python_markers` does NOT special-case
the abi3 tag. It treats every CPython-tagged wheel as exactly that minor
version. Concretely, for the cp39-abi3 wheel above it currently produces a
marker of the form:

  `python_full_version >= '3.9' and python_full_version < '3.10'`

which is wrong — it should be `python_full_version >= '3.9'` with **no**
upper cap. As a consequence, when a project pins `requires-python = ">=3.12"`
and an `abi3` wheel built for `cp37` or `cp39` is the only available
distribution, the resolver wrongly rejects the wheel as incompatible with
the 3.12+ environment.

## What the fix must do

Adjust `implied_python_markers` (and only the Python-tag branch — platform
markers and implementation markers must remain unchanged) so that:

1. **abi3 wheels** — i.e. wheels whose `abi_tags()` contain `AbiTag::Abi3` —
   produce a `python_full_version >= 'X.Y'` marker (a lower bound), with
   **no** upper cap.

   For example, `example-1.0-cp39-abi3-any.whl` must yield exactly:

   `python_full_version >= '3.9' and platform_python_implementation == 'CPython'`

   Concretely, the following filenames must produce the marker strings
   below verbatim (after `MarkerTree::contents().write_str(...)`):

   | wheel filename | implied python marker |
   |---|---|
   | `example-1.0-cp39-abi3-any.whl` | `python_full_version >= '3.9' and platform_python_implementation == 'CPython'` |
   | `example-1.0-cp312-abi3-any.whl` | `python_full_version >= '3.12' and platform_python_implementation == 'CPython'` |
   | `example-1.0-cp3-abi3-any.whl` | `python_full_version >= '3' and platform_python_implementation == 'CPython'` |

   And the full implied marker (Python + platform) for
   `example-1.0-cp39-abi3-manylinux_2_28_x86_64.whl` must be:

   `python_full_version >= '3.9' and platform_python_implementation == 'CPython' and sys_platform == 'linux' and platform_machine == 'x86_64'`

2. **Non-abi3 wheels** — behaviour must be **unchanged**. In particular:

   - `example-1.0-cp39-cp39-any.whl` must still produce a marker that
     contains both `python_full_version >= '3.9'` AND
     `python_full_version < '3.10'` (i.e. the `==3.9.*` semantics).
   - `example-1.0-py3-none-any.whl` must still produce a marker that
     contains both `python_full_version >= '3'` AND
     `python_full_version < '4'`.

3. The Python tag handling for abi3 must apply both for the
   `LanguageTag::Python { major, minor: None } | LanguageTag::CPythonMajor`
   branch (e.g. `cp3-abi3`) and for the Python/CPython/Pyston branches
   that carry both `major` and `minor` (e.g. `cp39-abi3`, `cp312-abi3`).

The relevant helpers you will likely use are
`VersionSpecifier::greater_than_equal_version(...)` (mirroring the existing
`VersionSpecifier::equals_star_version(...)` call) and
`AbiTag::Abi3` (already in scope via the existing imports of the abi /
language tag types).

## Adding tests

Per `CLAUDE.md`, you MUST add a test case for the changed behaviour. Follow
the style of the existing `assert_python_markers` /
`assert_implied_markers` helpers in
`crates/uv-distribution-types/src/prioritized_distribution.rs::mod tests`.

## Code Style Requirements

The repo enforces a strict style — see `CLAUDE.md` at the repo root.
Notably:

- AVOID `panic!`, `unreachable!`, `.unwrap()`, unsafe code, and clippy rule
  ignores in non-test code.
- PREFER `#[expect()]` over `#[allow()]` if clippy must be disabled.
- PREFER top-level imports over local imports or fully qualified names.
- AVOID shortening variable names.
- PREFER let chains (`if let` combined with `&&`) over nested `if let`.
- ALWAYS attempt to add a test case for changed behavior.
- PREFER integration tests at `it/...` over unit tests when feasible.

## Out of scope

Do not modify the lockfile, do not change unrelated functions, and do not
update workspace dependencies. The change is scoped to
`prioritized_distribution.rs` (and a corresponding test).
