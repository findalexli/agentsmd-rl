# Fix the Appwrite installer

The repository at `/workspace/appwrite` contains the source for Appwrite
(a self-hosted Backend-as-a-Service platform built on PHP 8.3 + Swoole).
The installer flow is broken in two ways that need to be fixed, and the
top-level `AGENTS.md` needs to be rewritten.

The repo is checked out at base commit `ea032c28046c9f6cb1c2801fa80a9111f7e5fcd1`.

## Bug 1 — Web installer launches even when explicit CLI flags were passed

`bin/install` (the CLI entry point) accepts a number of installer-specific
flags such as `--http-port`, `--https-port`, `--organization`, `--image`,
`--no-start`, `--database`, and `--interactive`. Most of these flags
override defaults; `--interactive=Y` toggles whether the installer asks
the user questions interactively.

When a user runs `php bin/install --database=mariadb --http-port=80 ...`
in a terminal, the installer currently **still launches the browser-based
web installer** instead of running in CLI mode. The user passed explicit
overrides on the command line — the web installer should not appear.

The gating logic that decides whether to start the web installer must be
strengthened so that it skips the web flow whenever any installer-specific
double-dash flag was supplied on the command line. Add a private helper on
`Appwrite\Platform\Tasks\Install` named **`hasExplicitCliParams`** that
returns `true` when `$_SERVER['argv']` contains at least one `--<flag>`
argument **other than** `--interactive` (in any form: `--interactive`,
`--interactive=Y`, etc.). It must return `false` otherwise.

Examples (the table below documents the contract `hasExplicitCliParams`
must satisfy and is what the unit tests assert on):

| `$_SERVER['argv']` | `hasExplicitCliParams()` returns |
|---|---|
| `['install']` | `false` |
| `['install', '--http-port=80']` | `true` |
| `['install', '--database=mariadb']` | `true` |
| `['install', '--interactive=Y']` | `false` |
| `['install', '--interactive=Y', '--http-port=80']` | `true` |

The web-installer launch in the `action(...)` method must consult this
helper and only start the web installer when no explicit override flags
were passed.

## Bug 2 — SSE completion event is sent after slow tracking work

When the web installer finishes, the HTTP handler currently runs the
`trackSelfHostedInstall(...)` analytics call **before** writing the SSE
"done" event and ending the response. Tracking can be slow (DNS lookup
and an outbound HTTP request to the analytics service), so the browser
hangs after installation has actually completed. The frontend cannot
redirect to the dashboard until the SSE stream closes.

To fix this, the `Appwrite\Platform\Tasks\Install::performInstallation`
method must accept a new trailing parameter: an optional, nullable
`callable` named **`$onComplete`** with a default of `null`. The
caller (the HTTP `Install` action) builds a closure that:

1. Marks the install as `STATUS_COMPLETED` in the global lock,
2. Writes the SSE `done` event (or the JSON success response when not
   streaming),
3. Closes the response,

and passes that closure as `$onComplete`. Inside `performInstallation`,
once the install has fully succeeded, invoke `$onComplete()` *before*
running `trackSelfHostedInstall(...)` so the browser is unblocked
immediately, then run the tracking. Tracking must be wrapped in a
Swoole coroutine via `go(function () { ... })` when the call site is
running inside a Swoole worker (`Swoole\Coroutine::getCid() !== -1`),
falling back to a synchronous call when not.

The tracking call itself also needs to be hardened:

- `gethostbyname($domain)` must be error-suppressed (`@gethostbyname(...)`)
  so a DNS resolution failure does not raise a PHP warning.
- The payload field that previously was sent as `'hostIp'` must be
  renamed to `'ip'`, and must be set to `null` when `gethostbyname`
  returned `false` or returned the input domain unchanged.
- The `Utopia\Fetch\Client` used to POST analytics must have both
  `setConnectTimeout(5000)` and `setTimeout(5000)` configured so a
  hung analytics endpoint cannot stall the worker indefinitely.

## Bug 3 — Swoole runtime hooks not enabled in installer server

`Appwrite\Platform\Installer\Server::startSwooleServer` must enable
Swoole's runtime coroutine hooks at startup
(`Swoole\Runtime::enableCoroutine(SWOOLE_HOOK_ALL)`) so blocking I/O
inside request handlers (including the analytics tracking above) is
transparently coroutine-ised. Without this, the `go(...)` background
fire used in Bug 2 cannot run truly in parallel with the request worker.

## UI tweaks

Two small template adjustments accompany the fix:

- On the upgrade flow, the "Secret API key" review row in the step-4
  template must be hidden (only show it during a fresh install, not an
  upgrade).
- The progress-step heading text in step-5 must read **"Updating Appwrite…"**
  during an upgrade and **"Installing Appwrite…"** during a fresh install
  (instead of the current "Updating your app…" / "Installing your app…").
- Add a small CSS rule so that on the upgrade page
  (`.installer-page[data-upgrade='true']`) `.installer-step` has
  `min-height: 0`.
- When launching the web installer for an existing installation, treat
  it as an upgrade by passing `$isUpgrade || $existingInstallation` to
  `startWebServer(...)` (rather than just `$isUpgrade`).

## AGENTS.md rewrite

The top-level `AGENTS.md` is verbose and not optimised for AI agents.
Rewrite it as a concise reference document for an agent that needs
fast context on the repo. The rewrite should:

- Open with a one-line description of Appwrite (self-hosted BaaS,
  hybrid monolithic-microservice, PHP 8.3 + Swoole, Docker delivery)
  and drop the introductory "this guide provides context…" framing.
- Provide a `## Commands` table listing the canonical developer
  commands: `docker compose up -d --force-recreate --build`, the two
  `docker compose exec appwrite test ...` invocations for E2E tests
  (with and without `--filter`), `docker compose exec appwrite test tests/unit/`,
  `composer format`, `composer format <file>`, `composer lint <file>`,
  `composer analyze`, and `composer check`.
- Provide a `## Stack` bullet list naming PHP 8.3+ and Swoole 6.x
  (with a note that Swoole replaces PHP-FPM as the async runtime),
  the Utopia PHP framework, the supported databases (MongoDB default,
  MariaDB, MySQL, PostgreSQL via `utopia-php/database` adapters),
  Redis (cache/queue/pub-sub), Docker + Traefik, and the test/lint
  toolchain (PHPUnit 12, Pint for PSR-12, PHPStan level 3).
- Provide a `## Project layout` bullet list mapping the high-level
  directories (`src/Appwrite/Platform/Modules/` and the canonical
  module names, `src/Appwrite/Platform/Workers/`, `src/Appwrite/Platform/Tasks/`,
  `app/init.php` as bootstrap, `app/init/` for configs/constants/locales/etc.,
  `bin/` for CLI entry points with the worker/schedule/queue/doctor/install/etc.
  scripts called out, `tests/e2e/`, `tests/unit/`, `public/`).
- Provide a `## Module structure` section showing the inner layout
  of a module directory (`Module.php`, `Services/Http.php`,
  `Services/Workers.php`, `Services/Tasks.php`, `Http/{Service}/`
  with the canonical action filenames, `Workers/`, `Tasks/`).
  Include a worked example of HTTP nesting matching URL paths
  (`Http/Deployments/Template/Create.php` → `POST /v1/functions/:functionId/deployments/template`).
- Spell out the file-naming constraint: file names in `Http`
  directories must only be `Get.php`, `Create.php`, `Update.php`,
  `Delete.php`, or `XList.php`, with non-CRUD operations modelled
  as property updates (worked example: team-membership status update
  at `Teams/Http/Memberships/Status/Update.php` →
  `PATCH /v1/teams/:teamId/memberships/:membershipId/status`).
- Note that new modules must be registered in
  `src/Appwrite/Platform/Appwrite.php` and that the detailed module
  guide lives at `src/Appwrite/Platform/AGENTS.md`.
- Provide a `## Action pattern (HTTP endpoints)` section with a
  worked PHP code example showing an `Action` subclass with
  `getName()`, the constructor chain (`setHttpMethod`, `setHttpPath`,
  `desc`, `groups`, `label`, `param`, `inject`, `callback`), and
  the typed `action(...)` method receiving injected services.
  Follow with a one-line list of common injections (`$response`,
  `$request`, `$dbForProject`, `$dbForPlatform`, `$user`, `$project`,
  `$queueForEvents`, `$queueForMails`, `$queueForDeletes`).
- Provide a `## Conventions` bullet list covering: PSR-12 enforced
  by Pint, PSR-4 autoloading; `resourceType` values are always
  plural (`'functions'`, `'sites'`, `'deployments'`); document
  updates pass only changed attributes as a sparse Document (with
  a short before/after PHP code block) and the exceptions
  (migrations, `array_merge()` with `getArrayCopy()`, mass updates,
  complex nested relationship logic); avoid dependencies outside
  the `utopia-php` ecosystem; never hardcode credentials; container
  restart may be required and there is no central log location.
- Close with a `## Cross-repo context` section noting that Appwrite
  is the base server for `appwrite/cloud`; that changes to the
  Action pattern, module structure, DI system, or response models
  affect cloud; and that the `feat-dedicated-db` feature spans
  cloud, edge, and console.

Drop the existing `## Code Style Guidelines`, `## Performance
Patterns`, `## Security Considerations`, `## Dependencies`,
`## Adding new endpoints`, `## Pull Request Guidelines`, and
`## Known Issues and Gotchas` sections — their content is folded
into the new `## Conventions` and `## Module structure` sections
above (or dropped where redundant with the rest of the rewritten
document).

## Code Style Requirements

PHP code must conform to **PSR-12**, enforced by **Laravel Pint**
(`composer lint <file>` to check, `composer format <file>` to apply).
Static analysis runs through **PHPStan level 3** (`composer analyze`).
Existing PHPDoc style must be preserved.

## Out of scope

You do not need to actually run the installer end-to-end; the
installer requires Docker-in-Docker and a full Swoole runtime which is
not available in this environment. Tests verify the contract of the
new `hasExplicitCliParams()` helper, the new `$onComplete` parameter
on `performInstallation`, and that all modified PHP files still parse.
