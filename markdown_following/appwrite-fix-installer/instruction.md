# Fix the Appwrite installer's upgrade-mode UX and refresh `AGENTS.md`

You're working in a clone of `appwrite/appwrite` checked out at the parent
of merge commit `ec20fb5` (PR #11689). There are **two** related problems
to fix.

## Repo layout

```
/workspace/appwrite/
├── AGENTS.md                                          # agent-instruction file
├── app/views/install/installer/
│   ├── css/styles.css                                 # installer styles
│   └── templates/steps/
│       ├── step-4.phtml                               # "Review" step
│       └── step-5.phtml                               # "Installing"/"Updating" step
└── src/Appwrite/Platform/...                          # PHP backend (out of scope)
```

## Problem 1 — Installer upgrade-mode UX

The web installer has both a fresh-install flow and an upgrade flow,
controlled by a `$isUpgrade` boolean that the templates read. The current
templates have leftover placeholder copy and an unconditional review row
that should not appear when upgrading. Fix the following symptoms:

### 1a. Step 5 still says "your app", not "Appwrite"

`app/views/install/installer/templates/steps/step-5.phtml` is the screen
shown while installation/upgrade is running. With `$isUpgrade = true` it
renders `Updating your app…`; with `$isUpgrade = false` it renders
`Installing your app…`. Marketing wants the product name in both copies:

- When `$isUpgrade` is true the banner must read **`Updating Appwrite…`**
  (with the Unicode horizontal-ellipsis `…`, U+2026, exactly as in the
  existing template).
- When `$isUpgrade` is false the banner must read **`Installing Appwrite…`**.
- The legacy phrases `Updating your app…` and `Installing your app…` must
  no longer appear in the rendered output.

### 1b. Step 4 leaks a "Secret API key" row during upgrades

`step-4.phtml` is the review screen shown before installation begins. It
lists rows like *Hostname*, *Database*, *HTTP port*, *Appwrite Assistant*,
and *Secret API key*. The "Secret API key" row only makes sense for a
fresh install — on an upgrade we are not generating a new key.

Fix the template so that:

- When `$isUpgrade` is true the rendered HTML contains **no** occurrence
  of the literal string `Secret API key`.
- When `$isUpgrade` is false the rendered HTML still contains the
  `Secret API key` review row (regression guard).

### 1c. Installer step has wrong min-height during upgrades

`app/views/install/installer/css/styles.css` enforces a `min-height` on
each `.installer-step` block. On upgrade pages this leaves a large empty
gap below the (much shorter) upgrade-step content. The installer markup
sets `data-upgrade="true"` on `.installer-page` when running an upgrade.

Add a CSS rule so that when `.installer-page` has `data-upgrade='true'`,
its descendant `.installer-step` elements are scoped to `min-height: 0`.
The selector must match the form `.installer-page[data-upgrade='true']
.installer-step` and the body must set `min-height: 0`.

## Problem 2 — Rewrite `AGENTS.md`

The repo's `AGENTS.md` (the agent-instruction file at the repo root) is
out of date and badly organised. Rewrite it from scratch into the
following structure, in this order:

1. **Top-line tagline** — describe Appwrite as a *self-hosted
   Backend-as-a-Service platform* with a *hybrid monolithic-microservice
   architecture* built with *PHP 8.3+ on Swoole*, delivered as Docker
   containers.
2. **`## Commands`** table — a markdown table mapping each project
   command to its purpose (Docker compose up, e2e tests, unit tests,
   `composer format`, `composer lint`, `composer analyze`, `composer
   check`).
3. **`## Stack`** bullet list — list PHP 8.3+ + Swoole 6.x, Utopia PHP,
   the supported databases, Redis, Docker + Traefik, and the testing
   stack `PHPUnit 12, Pint (PSR-12), PHPStan level 3`.
4. **`## Project layout`** — bullet list mapping the major top-level
   directories (`src/Appwrite/Platform/Modules/`,
   `src/Appwrite/Platform/Workers/`, `src/Appwrite/Platform/Tasks/`,
   `app/init.php`, `app/init/`, `bin/`, `tests/e2e/`, `tests/unit/`,
   `public/`).
5. **`## Module structure`** — explain the `Module.php` / `Services` /
   `Http` / `Workers` / `Tasks` layout under
   `src/Appwrite/Platform/Modules/{Name}/`. Include the rule that file
   names in `Http` directories must only be `Get.php`, `Create.php`,
   `Update.php`, `Delete.php`, or `XList.php`, and the property-update
   pattern for non-CRUD operations (e.g. team-membership status update).
6. **`## Action pattern (HTTP endpoints)`** — a runnable PHP code block
   showing a sample `class Create extends Action` with `getName`,
   `__construct` builder chain (`setHttpMethod`, `setHttpPath`, `desc`,
   `groups`, `label`, `param`, `inject`, `callback`), and the typed
   `action(...)` method.
7. **`## Conventions`** — bullet list preserving the actionable rules
   from the old `AGENTS.md`:
     - PSR-12 enforced by Pint, PSR-4 autoloading.
     - `resourceType` values are always **plural** (`'functions'`,
       `'sites'`, `'deployments'`).
     - When updating documents, pass only changed attributes as a sparse
       `Document` (with the same correct/incorrect code-block pair as the
       old file, and the same exception list — migrations,
       `array_merge()` with `getArrayCopy()`, near-full-document updates,
       complex nested relationships).
     - Avoid introducing dependencies outside the `utopia-php` ecosystem.
     - Never hardcode credentials — use environment variables.
8. **`## Cross-repo context`** — note that Appwrite is the base server
   for `appwrite/cloud` and that the `feat-dedicated-db` feature spans
   cloud, edge, and console.

The old top-level headings `## Project Overview`, `## Development
Commands`, `## Code Style Guidelines`, `## Performance Patterns`, `##
Security Considerations`, `## Pull Request Guidelines`, and `## Known
Issues and Gotchas` should be **removed** — their content either moves
into the new sections above or is dropped (PR/release-process bullets,
"hot reload" gotcha).

## Code Style Requirements

- All modified PHP files must conform to **PSR-12** formatting (this
  repo's Pint config enforces it). Don't introduce trailing whitespace
  or mismatched indentation.
- Use **strict type declarations** (`: bool`, `?callable`, `: void`,
  etc.) on any new methods or modified signatures, consistent with the
  surrounding file.

## Out of scope

The PHP installer-server / SSE-stream / Swoole-coroutine refactor in
`src/Appwrite/Platform/Tasks/Install.php`,
`src/Appwrite/Platform/Installer/Http/Installer/Install.php`, and
`src/Appwrite/Platform/Installer/Server.php` is out of scope for this
benchmark task — those changes require a running Swoole HTTP server and
are evaluated in a separate task. You should leave those files
untouched (or only modify them if needed to preserve PHP syntax).

## How you'll be evaluated

- **Track 1** runs PHP behavioral tests: it renders `step-4.phtml` and
  `step-5.phtml` with `$isUpgrade` ∈ {true, false} and asserts on the
  output, parses `styles.css` for the new rule, and structurally checks
  `AGENTS.md` for the new section headings and signal phrases.
- **Track 2** is a semantic comparison of your `AGENTS.md` against the
  intended rewrite, judged by an LLM.

You only need to edit files under `/workspace/appwrite/`.
