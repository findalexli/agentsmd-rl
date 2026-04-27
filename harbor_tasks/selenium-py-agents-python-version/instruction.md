# Add Python 3.10+ rules to the Selenium Python Bindings agent guide

## Background

The Selenium monorepo has a per-binding `AGENTS.md` file under `py/` that tells
AI agents how to work in the Python bindings. The current Python AGENTS.md
covers logging, deprecation warnings, type hints (in general), and Google-style
docstrings, but it is **missing two important rules** that have led agents to
produce code that is inconsistent with the rest of the Python bindings:

1. **Type-annotation style.** Agents frequently reach for
   `typing.Optional[T]` when writing type hints. The Python bindings codebase
   has standardized on the **PEP 604 union notation** (`T | None`). The AGENTS
   guide does not say so today, so agents have no way to know.

2. **Python version target.** Agents sometimes write code that only works on
   newer Python versions, or — more often — fall back to legacy patterns
   ("just to be safe") that this codebase no longer supports. The Python
   bindings target **Python 3.10 or later**, and that floor needs to be
   stated explicitly so agents can confidently use modern syntax. Agents who
   do run ad-hoc scripts also need a reminder to check their local Python
   version first.

Your task is to update the Python bindings agent guide so it captures these
two rules.

## Scope

Update `py/AGENTS.md` (and only that file) so that an AI agent reading it
gets the following guidance:

### 1. Prefer union notation over `Optional`

Extend the existing `### Type hints` section with a rule that says agents
should use **union notation** (the `|` operator) instead of
`typing.Optional`. Show a small `# Preferred` example using `<type> | None`
syntax, and a contrasting `# Avoid` example that imports `Optional` from
`typing` and uses `Optional[T]`. The phrase **"Use union notation"** must
appear, and the preferred example must include a `<name> | None` form
(for instance, `str | None` or `int | None`).

### 2. State the Python 3.10+ floor

Add a new section under `## Code conventions` titled with a heading that
contains the words **"Python version"** (e.g. `### Python version`). The
section must:

- State that **Python 3.10** is the minimum — code must work with
  Python 3.10 or later.
- Cross-reference the type-hints guidance (modern union syntax is part of
  what 3.10+ enables).
- Tell agents that for ad-hoc terminal use they should check their local
  Python version before running anything, and include the literal command
  `python --version` in a fenced shell code block.

### 3. Stay tightly scoped

- Edit **only** `py/AGENTS.md`. Do not touch the root `AGENTS.md` or any
  other binding's AGENTS file.
- Keep the existing logging, deprecation, and Google-style-docstring
  sections intact — your additions extend the type-hints area and add a
  new Python-version section, they don't rewrite what's already there.
- The diff should be a small, reversible documentation edit, in keeping
  with the repo's "small, reversible diffs" rule from the root AGENTS.md.

## Repository-wide guidance you should still follow

The root `AGENTS.md` and `py/AGENTS.md` apply. In particular:

- Maintain API/ABI compatibility — do not silently remove rules that
  existing readers may rely on.
- PRs should focus on one thing; this edit is one thing (Python 3.10+
  agent guidance), so don't fold in unrelated cleanups.
- Existing Python conventions in `py/AGENTS.md` (logging via
  `logging.getLogger(__name__)`, `warnings.warn(...)` with
  `DeprecationWarning` and `stacklevel=2`, Google-style docstrings) must
  remain unchanged.

## Done when

- `py/AGENTS.md` contains a heading whose text includes the words
  "Python version".
- It mentions **Python 3.10** as the minimum.
- It mentions **union notation** as the preferred alternative to
  `Optional`, with a `<type> | None` example.
- It contains the literal `python --version` command (in a code block) for
  local Python-version checking.
- No other files in the repository are modified.
