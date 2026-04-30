# Task: action-pins pre-commit hook

This MLflow checkout has every remote GitHub Action `uses:` declaration
pinned to a 40-character commit SHA, with a trailing `# vX.Y.Z` comment that
records the human-readable tag the SHA corresponds to. There is, however,
nothing today that *enforces* this convention — a contributor can introduce a
moving-tag pin (for example `actions/checkout@v4`) and CI will silently
accept it, which defeats the security guarantees of SHA pinning.

Your job is to add a pre-commit hook that catches these regressions.

## What to deliver

1. **A new validator script at `dev/check_action_pins.py`.** It scans the
   repository's GitHub Action YAML files (those under `.github/workflows/`
   and `.github/actions/`) and reports every `uses:` line that is not pinned
   to a full SHA with a matching version-tag comment.

2. **A new entry in `.pre-commit-config.yaml`** that registers the hook with
   id `action-pins`, runs `dev/check_action_pins.py`, and matches files
   under both `.github/workflows/` and `.github/actions/` (with `.yml` or
   `.yaml` extensions).

3. **A cache step in `.github/workflows/lint.yml`** that caches
   `.cache/action-pins.json` between runs so the GitHub API is hit at most
   once per pin per CI run. (See "Caching" below for why this file matters.)

## Specification of the validator script

### Discovery

When invoked **without arguments**, the script must discover every Action
YAML file under the current working directory by globbing the following
patterns:

- `.github/workflows/*.yml`
- `.github/workflows/*.yaml`
- `.github/actions/**/*.yml`     (recursive)
- `.github/actions/**/*.yaml`    (recursive)

When invoked **with positional arguments**, the script treats each argument
as a path to scan and ignores the default globs. (This is how `pre-commit`
will call it — it passes the changed files as arguments.)

### Per-line rules

For every line in a scanned file that is a `uses:` directive, apply the
following rules in order. The script must report a violation if **any** rule
is broken; multiple violations across multiple files must all be reported in
a single run.

1. **Local references are ignored.** A `uses:` whose target begins with
   `./` is a local action defined in this repo — leave it alone.

2. **Remote references must be SHA-pinned.** The portion after the `@` must
   be a full 40-character lower-case hexadecimal SHA. Anything else (a tag
   like `v4`, a branch like `main`, a 7-char short SHA) is a violation.

3. **A version-tag comment is required.** The `uses:` line must end with a
   trailing `# vX.Y.Z` comment, where `X`, `Y`, and `Z` are non-negative
   integers (additional dotted components are permitted, e.g. `v1.2.3.4`).
   Single- or two-component versions like `# v4` or `# v4.2` are rejected
   because they correspond to moving major/minor tags.

4. **The SHA must actually correspond to the named tag.** Resolve the tag
   on `github.com/{owner}/{repo}` via `git ls-remote --tags
   https://github.com/{owner}/{repo}.git {tag}` and assert that one of the
   returned ref lines starts with the SHA. If the lookup fails (network
   error, repo doesn't exist), treat that as a violation as well — the user
   should be able to tell the difference between "could not verify" and
   "definitely does not match", but in both cases the run fails.

   Subpath references like `actions/cache/restore@<sha>` use the parent
   `owner/repo` (`actions/cache`) for the `git ls-remote` call.

### Caching

Verifying the SHA against the tag requires a remote round-trip. To keep
pre-commit fast and to avoid hammering GitHub on every commit, persist
verification results in a JSON file at `.cache/action-pins.json` (relative
to the current working directory).

- The cache key for a single check is `"{action}@{sha}#{tag}"` —
  for example `"actions/checkout@692973...#v5.0.0"`.
- The cached value is a boolean: `true` if the SHA matches the tag,
  `false` if it definitely does not.
- On a cache hit, return the cached boolean without doing any network I/O.
- On a cache miss that successfully resolves, store the result and persist
  the cache file (creating the `.cache/` directory if necessary).
- On a cache miss that fails (e.g., `git ls-remote` raises
  `subprocess.CalledProcessError`), do **not** cache anything — just report
  the unverifiable pin as a violation for this run.
- A pre-existing cache file that is malformed JSON or unreadable should be
  treated as an empty cache rather than crashing.

### Exit behaviour

- If no violations are found across all scanned files: exit `0` and emit
  nothing (or only stdout chatter). Stderr should be empty in the clean
  case.
- If at least one violation is found: write a human-readable report to
  **stderr** describing every violation, then exit `1`.

### Implementation constraints

- **Stdlib only.** No third-party imports. The hook runs inside the `lint`
  uv group and we do not want to drag extra dependencies into it.
- Target Python 3.10+. The repo's `pyproject.toml` declares
  `requires-python = ">=3.10"` and you may rely on PEP 604 unions, PEP 634
  `match` statements, slotted dataclasses, etc.

## Wiring in the pre-commit config

Add a new entry to the `local` repos block of `.pre-commit-config.yaml`
with the following shape:

- `id: action-pins`
- `name: action-pins`
- `entry:` runs `dev/check_action_pins.py` (the existing local hooks call
  scripts via `uv run --only-group lint dev/<script>.py`; follow the same
  convention)
- `language: system`
- `files:` a regex restricted to YAML files under `.github/workflows/` or
  `.github/actions/`
- `stages: [pre-commit]`
- `require_serial: true`

## Wiring the cache into CI

In `.github/workflows/lint.yml`, before the `Install pre-commit hooks`
step, add an `actions/cache@<sha> # <version>` step that caches the path
`.cache/action-pins.json`. The cache key should change whenever the
validator script changes (e.g., key off
`hashFiles('dev/check_action_pins.py')`). Pin the cache action itself with
a 40-char SHA and `# vX.Y.Z` comment so it satisfies your own hook.

## Code Style Requirements

The repository's `CLAUDE.md` specifies:

- **Use top-level imports** — only use lazy/in-function imports when
  strictly necessary.
- **Only add comments that explain non-obvious logic or provide
  additional context** — avoid restating what the code does.
- If you add tests, **only include docstrings when they convey context
  not obvious from the test name**.
