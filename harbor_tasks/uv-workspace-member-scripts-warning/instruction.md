# Workspace member scripts skipped without warning

When `uv sync` installs a project that declares `[project.scripts]` but has
neither a `[build-system]` table nor `tool.uv.package = true`, those entry
points cannot be installed and are silently skipped. The user is supposed to
get a warning so they can fix their `pyproject.toml`. There are two related
defects in the current behavior:

## Defect 1 — non-root workspace members are skipped silently

Consider this layout:

```
.
├── pyproject.toml          # workspace root, no scripts
└── member/
    └── pyproject.toml      # has [project.scripts], no [build-system]
```

Run `uv sync --all-packages` from the root. The `member` package's entry
points are silently dropped — no warning is emitted. The check that should
trigger the warning currently inspects only the workspace root's
`pyproject.toml`, so any non-root member with the same misconfiguration
slips through.

After the fix, the warning must fire whenever a workspace member that is
part of the active sync target has `[project.scripts]` without a
`[build-system]` (and without `tool.uv.package = true`).

## Defect 2 — the warning does not name the offending package

Today, when the warning *does* fire (i.e. for the workspace root), the text
reads:

```
warning: Skipping installation of entry points (`project.scripts`) because this project is not packaged; to install entry points, set `tool.uv.package = true` or define a `build-system`
```

This is unactionable when more than one package is involved, because the
user can't tell which package is the source of the problem.

The warning must include the package name in the format
`` for package `<name>` `` immediately after `(``project.scripts``)`. The
exact corrected message is:

```
warning: Skipping installation of entry points (`project.scripts`) for package `<name>` because this project is not packaged; to install entry points, set `tool.uv.package = true` or define a `build-system`
```

…where `<name>` is the package name from `[project].name` of the offending
member (or root). This must apply to *every* warning emitted by this code
path — both single-project syncs and workspace-member syncs.

## Scope: only members in the sync target

The warning must not over-fire. If a workspace member is not part of the
active sync target — for example, when running `uv sync` (without
`--all-packages`) from the root, only the root is being synced — no warning
should be emitted for the unsynced member, even if that member would
otherwise qualify.

Likewise, a member that has `tool.uv.package = true` (or a `[build-system]`
table) is correctly packaged and must not produce a warning.

## Reproduction

1. Make a workspace with the layout above (root `pyproject.toml` declaring
   `[tool.uv.workspace] members = ["member"]`, no `[project.scripts]`; a
   `member/pyproject.toml` with `[project.scripts]` but no
   `[build-system]`).
2. Run `uv sync --all-packages` from the root.
3. **Expected**: a warning naming `` `member` `` appears on stderr.
4. **Actual**: no warning. The entry point is silently skipped.

A correct fix makes the test fixtures behave as described in the "Defect"
sections above.

## Code Style Requirements

- This is a Rust project (`cargo` workspace). Your fix must compile cleanly
  with `cargo check -p uv --bin uv`.
- Follow the conventions in `CLAUDE.md` at the repository root. In
  particular: avoid `panic!` / `unreachable!` / `.unwrap()`, prefer
  `if let` for fallibility, and avoid abbreviated identifier names (use
  full words for variables).
- Do not introduce new clippy warnings.
