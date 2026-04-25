# Agent Config Files for opencode-slash-cmd-image-preserve

Repo: anomalyco/opencode
Commit: 47d2ab120a4fbc92e72aca4d5b40d722d0e4d2be
Files found: 11


---
## AGENTS.md

```
   1 | - To regenerate the JavaScript SDK, run `./packages/sdk/js/script/build.ts`.
   2 | - ALWAYS USE PARALLEL TOOLS WHEN APPLICABLE.
   3 | - The default branch in this repo is `dev`.
   4 | - Local `main` ref may not exist; use `dev` or `origin/dev` for diffs.
   5 | - Prefer automation: execute requested actions without confirmation unless blocked by missing info or safety/irreversibility.
   6 | 
   7 | ## Style Guide
   8 | 
   9 | ### General Principles
  10 | 
  11 | - Keep things in one function unless composable or reusable
  12 | - Avoid `try`/`catch` where possible
  13 | - Avoid using the `any` type
  14 | - Prefer single word variable names where possible
  15 | - Use Bun APIs when possible, like `Bun.file()`
  16 | - Rely on type inference when possible; avoid explicit type annotations or interfaces unless necessary for exports or clarity
  17 | - Prefer functional array methods (flatMap, filter, map) over for loops; use type guards on filter to maintain type inference downstream
  18 | 
  19 | ### Naming
  20 | 
  21 | Prefer single word names for variables and functions. Only use multiple words if necessary.
  22 | 
  23 | ### Naming Enforcement (Read This)
  24 | 
  25 | THIS RULE IS MANDATORY FOR AGENT WRITTEN CODE.
  26 | 
  27 | - Use single word names by default for new locals, params, and helper functions.
  28 | - Multi-word names are allowed only when a single word would be unclear or ambiguous.
  29 | - Do not introduce new camelCase compounds when a short single-word alternative is clear.
  30 | - Before finishing edits, review touched lines and shorten newly introduced identifiers where possible.
  31 | - Good short names to prefer: `pid`, `cfg`, `err`, `opts`, `dir`, `root`, `child`, `state`, `timeout`.
  32 | - Examples to avoid unless truly required: `inputPID`, `existingClient`, `connectTimeout`, `workerPath`.
  33 | 
  34 | ```ts
  35 | // Good
  36 | const foo = 1
  37 | function journal(dir: string) {}
  38 | 
  39 | // Bad
  40 | const fooBar = 1
  41 | function prepareJournal(dir: string) {}
  42 | ```
  43 | 
  44 | Reduce total variable count by inlining when a value is only used once.
  45 | 
  46 | ```ts
  47 | // Good
  48 | const journal = await Bun.file(path.join(dir, "journal.json")).json()
  49 | 
  50 | // Bad
  51 | const journalPath = path.join(dir, "journal.json")
  52 | const journal = await Bun.file(journalPath).json()
  53 | ```
  54 | 
  55 | ### Destructuring
  56 | 
  57 | Avoid unnecessary destructuring. Use dot notation to preserve context.
  58 | 
  59 | ```ts
  60 | // Good
  61 | obj.a
  62 | obj.b
  63 | 
  64 | // Bad
  65 | const { a, b } = obj
  66 | ```
  67 | 
  68 | ### Variables
  69 | 
  70 | Prefer `const` over `let`. Use ternaries or early returns instead of reassignment.
  71 | 
  72 | ```ts
  73 | // Good
  74 | const foo = condition ? 1 : 2
  75 | 
  76 | // Bad
  77 | let foo
  78 | if (condition) foo = 1
  79 | else foo = 2
  80 | ```
  81 | 
  82 | ### Control Flow
  83 | 
  84 | Avoid `else` statements. Prefer early returns.
  85 | 
  86 | ```ts
  87 | // Good
  88 | function foo() {
  89 |   if (condition) return 1
  90 |   return 2
  91 | }
  92 | 
  93 | // Bad
  94 | function foo() {
  95 |   if (condition) return 1
  96 |   else return 2
  97 | }
  98 | ```
  99 | 
 100 | ### Schema Definitions (Drizzle)
 101 | 
 102 | Use snake_case for field names so column names don't need to be redefined as strings.
 103 | 
 104 | ```ts
 105 | // Good
 106 | const table = sqliteTable("session", {
 107 |   id: text().primaryKey(),
 108 |   project_id: text().notNull(),
 109 |   created_at: integer().notNull(),
 110 | })
 111 | 
 112 | // Bad
 113 | const table = sqliteTable("session", {
 114 |   id: text("id").primaryKey(),
 115 |   projectID: text("project_id").notNull(),
 116 |   createdAt: integer("created_at").notNull(),
 117 | })
 118 | ```
 119 | 
 120 | ## Testing
 121 | 
 122 | - Avoid mocks as much as possible
 123 | - Test actual implementation, do not duplicate logic into tests
 124 | - Tests cannot run from repo root (guard: `do-not-run-tests-from-root`); run from package dirs like `packages/opencode`.
 125 | 
 126 | ## Type Checking
 127 | 
 128 | - Always run `bun typecheck` from package directories (e.g., `packages/opencode`), never `tsc` directly.
```


---
## README.md

```
   1 | <p align="center">
   2 |   <a href="https://opencode.ai">
   3 |     <picture>
   4 |       <source srcset="packages/console/app/src/asset/logo-ornate-dark.svg" media="(prefers-color-scheme: dark)">
   5 |       <source srcset="packages/console/app/src/asset/logo-ornate-light.svg" media="(prefers-color-scheme: light)">
   6 |       <img src="packages/console/app/src/asset/logo-ornate-light.svg" alt="OpenCode logo">
   7 |     </picture>
   8 |   </a>
   9 | </p>
  10 | <p align="center">The open source AI coding agent.</p>
  11 | <p align="center">
  12 |   <a href="https://opencode.ai/discord"><img alt="Discord" src="https://img.shields.io/discord/1391832426048651334?style=flat-square&label=discord" /></a>
  13 |   <a href="https://www.npmjs.com/package/opencode-ai"><img alt="npm" src="https://img.shields.io/npm/v/opencode-ai?style=flat-square" /></a>
  14 |   <a href="https://github.com/anomalyco/opencode/actions/workflows/publish.yml"><img alt="Build status" src="https://img.shields.io/github/actions/workflow/status/anomalyco/opencode/publish.yml?style=flat-square&branch=dev" /></a>
  15 | </p>
  16 | 
  17 | <p align="center">
  18 |   <a href="README.md">English</a> |
  19 |   <a href="README.zh.md">简体中文</a> |
  20 |   <a href="README.zht.md">繁體中文</a> |
  21 |   <a href="README.ko.md">한국어</a> |
  22 |   <a href="README.de.md">Deutsch</a> |
  23 |   <a href="README.es.md">Español</a> |
  24 |   <a href="README.fr.md">Français</a> |
  25 |   <a href="README.it.md">Italiano</a> |
  26 |   <a href="README.da.md">Dansk</a> |
  27 |   <a href="README.ja.md">日本語</a> |
  28 |   <a href="README.pl.md">Polski</a> |
  29 |   <a href="README.ru.md">Русский</a> |
  30 |   <a href="README.bs.md">Bosanski</a> |
  31 |   <a href="README.ar.md">العربية</a> |
  32 |   <a href="README.no.md">Norsk</a> |
  33 |   <a href="README.br.md">Português (Brasil)</a> |
  34 |   <a href="README.th.md">ไทย</a> |
  35 |   <a href="README.tr.md">Türkçe</a> |
  36 |   <a href="README.uk.md">Українська</a> |
  37 |   <a href="README.bn.md">বাংলা</a> |
  38 |   <a href="README.gr.md">Ελληνικά</a> |
  39 |   <a href="README.vi.md">Tiếng Việt</a>
  40 | </p>
  41 | 
  42 | [![OpenCode Terminal UI](packages/web/src/assets/lander/screenshot.png)](https://opencode.ai)
  43 | 
  44 | ---
  45 | 
  46 | ### Installation
  47 | 
  48 | ```bash
  49 | # YOLO
  50 | curl -fsSL https://opencode.ai/install | bash
  51 | 
  52 | # Package managers
  53 | npm i -g opencode-ai@latest        # or bun/pnpm/yarn
  54 | scoop install opencode             # Windows
  55 | choco install opencode             # Windows
  56 | brew install anomalyco/tap/opencode # macOS and Linux (recommended, always up to date)
  57 | brew install opencode              # macOS and Linux (official brew formula, updated less)
  58 | sudo pacman -S opencode            # Arch Linux (Stable)
  59 | paru -S opencode-bin               # Arch Linux (Latest from AUR)
  60 | mise use -g opencode               # Any OS
  61 | nix run nixpkgs#opencode           # or github:anomalyco/opencode for latest dev branch
  62 | ```
  63 | 
  64 | > [!TIP]
  65 | > Remove versions older than 0.1.x before installing.
  66 | 
  67 | ### Desktop App (BETA)
  68 | 
  69 | OpenCode is also available as a desktop application. Download directly from the [releases page](https://github.com/anomalyco/opencode/releases) or [opencode.ai/download](https://opencode.ai/download).
  70 | 
  71 | | Platform              | Download                              |
  72 | | --------------------- | ------------------------------------- |
  73 | | macOS (Apple Silicon) | `opencode-desktop-darwin-aarch64.dmg` |
  74 | | macOS (Intel)         | `opencode-desktop-darwin-x64.dmg`     |
  75 | | Windows               | `opencode-desktop-windows-x64.exe`    |
  76 | | Linux                 | `.deb`, `.rpm`, or AppImage           |
  77 | 
  78 | ```bash
  79 | # macOS (Homebrew)
  80 | brew install --cask opencode-desktop
  81 | # Windows (Scoop)
  82 | scoop bucket add extras; scoop install extras/opencode-desktop
  83 | ```
  84 | 
  85 | #### Installation Directory
  86 | 
  87 | The install script respects the following priority order for the installation path:
  88 | 
  89 | 1. `$OPENCODE_INSTALL_DIR` - Custom installation directory
  90 | 2. `$XDG_BIN_DIR` - XDG Base Directory Specification compliant path
  91 | 3. `$HOME/bin` - Standard user binary directory (if it exists or can be created)
  92 | 4. `$HOME/.opencode/bin` - Default fallback
  93 | 
  94 | ```bash
  95 | # Examples
  96 | OPENCODE_INSTALL_DIR=/usr/local/bin curl -fsSL https://opencode.ai/install | bash
  97 | XDG_BIN_DIR=$HOME/.local/bin curl -fsSL https://opencode.ai/install | bash
  98 | ```
  99 | 
 100 | ### Agents
 101 | 
 102 | OpenCode includes two built-in agents you can switch between with the `Tab` key.
 103 | 
 104 | - **build** - Default, full-access agent for development work
 105 | - **plan** - Read-only agent for analysis and code exploration
 106 |   - Denies file edits by default
 107 |   - Asks permission before running bash commands
 108 |   - Ideal for exploring unfamiliar codebases or planning changes
 109 | 
 110 | Also included is a **general** subagent for complex searches and multistep tasks.
 111 | This is used internally and can be invoked using `@general` in messages.
 112 | 
 113 | Learn more about [agents](https://opencode.ai/docs/agents).
 114 | 
 115 | ### Documentation
 116 | 
 117 | For more info on how to configure OpenCode, [**head over to our docs**](https://opencode.ai/docs).
 118 | 
 119 | ### Contributing
 120 | 
 121 | If you're interested in contributing to OpenCode, please read our [contributing docs](./CONTRIBUTING.md) before submitting a pull request.
 122 | 
 123 | ### Building on OpenCode
 124 | 
 125 | If you are working on a project that's related to OpenCode and is using "opencode" as part of its name, for example "opencode-dashboard" or "opencode-mobile", please add a note to your README to clarify that it is not built by the OpenCode team and is not affiliated with us in any way.
 126 | 
 127 | ### FAQ
 128 | 
 129 | #### How is this different from Claude Code?
 130 | 
 131 | It's very similar to Claude Code in terms of capability. Here are the key differences:
 132 | 
 133 | - 100% open source
 134 | - Not coupled to any provider. Although we recommend the models we provide through [OpenCode Zen](https://opencode.ai/zen), OpenCode can be used with Claude, OpenAI, Google, or even local models. As models evolve, the gaps between them will close and pricing will drop, so being provider-agnostic is important.
 135 | - Out-of-the-box LSP support
 136 | - A focus on TUI. OpenCode is built by neovim users and the creators of [terminal.shop](https://terminal.shop); we are going to push the limits of what's possible in the terminal.
 137 | - A client/server architecture. This, for example, can allow OpenCode to run on your computer while you drive it remotely from a mobile app, meaning that the TUI frontend is just one of the possible clients.
 138 | 
 139 | ---
 140 | 
 141 | **Join our community** [Discord](https://discord.gg/opencode) | [X.com](https://x.com/opencode)
```


---
## packages/app/AGENTS.md

```
   1 | ## Debugging
   2 | 
   3 | - NEVER try to restart the app, or the server process, EVER.
   4 | 
   5 | ## Local Dev
   6 | 
   7 | - `opencode dev web` proxies `https://app.opencode.ai`, so local UI/CSS changes will not show there.
   8 | - For local UI changes, run the backend and app dev servers separately.
   9 | - Backend (from `packages/opencode`): `bun run --conditions=browser ./src/index.ts serve --port 4096`
  10 | - App (from `packages/app`): `bun dev -- --port 4444`
  11 | - Open `http://localhost:4444` to verify UI changes (it targets the backend at `http://localhost:4096`).
  12 | 
  13 | ## SolidJS
  14 | 
  15 | - Always prefer `createStore` over multiple `createSignal` calls
  16 | 
  17 | ## Tool Calling
  18 | 
  19 | - ALWAYS USE PARALLEL TOOLS WHEN APPLICABLE.
  20 | 
  21 | ## Browser Automation
  22 | 
  23 | Use `agent-browser` for web automation. Run `agent-browser --help` for all commands.
  24 | 
  25 | Core workflow:
  26 | 
  27 | 1. `agent-browser open <url>` - Navigate to page
  28 | 2. `agent-browser snapshot -i` - Get interactive elements with refs (@e1, @e2)
  29 | 3. `agent-browser click @e1` / `fill @e2 "text"` - Interact using refs
  30 | 4. Re-snapshot after page changes
```


---
## packages/app/README.md

```
   1 | ## Usage
   2 | 
   3 | Dependencies for these templates are managed with [pnpm](https://pnpm.io) using `pnpm up -Lri`.
   4 | 
   5 | This is the reason you see a `pnpm-lock.yaml`. That said, any package manager will work. This file can safely be removed once you clone a template.
   6 | 
   7 | ```bash
   8 | $ npm install # or pnpm install or yarn install
   9 | ```
  10 | 
  11 | ### Learn more on the [Solid Website](https://solidjs.com) and come chat with us on our [Discord](https://discord.com/invite/solidjs)
  12 | 
  13 | ## Available Scripts
  14 | 
  15 | In the project directory, you can run:
  16 | 
  17 | ### `npm run dev` or `npm start`
  18 | 
  19 | Runs the app in the development mode.<br>
  20 | Open [http://localhost:3000](http://localhost:3000) to view it in the browser.
  21 | 
  22 | The page will reload if you make edits.<br>
  23 | 
  24 | ### `npm run build`
  25 | 
  26 | Builds the app for production to the `dist` folder.<br>
  27 | It correctly bundles Solid in production mode and optimizes the build for the best performance.
  28 | 
  29 | The build is minified and the filenames include the hashes.<br>
  30 | Your app is ready to be deployed!
  31 | 
  32 | ## E2E Testing
  33 | 
  34 | Playwright starts the Vite dev server automatically via `webServer`, and UI tests need an opencode backend (defaults to `localhost:4096`).
  35 | Use the local runner to create a temp sandbox, seed data, and run the tests.
  36 | 
  37 | ```bash
  38 | bunx playwright install
  39 | bun run test:e2e:local
  40 | bun run test:e2e:local -- --grep "settings"
  41 | ```
  42 | 
  43 | Environment options:
  44 | 
  45 | - `PLAYWRIGHT_SERVER_HOST` / `PLAYWRIGHT_SERVER_PORT` (backend address, default: `localhost:4096`)
  46 | - `PLAYWRIGHT_PORT` (Vite dev server port, default: `3000`)
  47 | - `PLAYWRIGHT_BASE_URL` (override base URL, default: `http://localhost:<PLAYWRIGHT_PORT>`)
  48 | 
  49 | ## Deployment
  50 | 
  51 | You can deploy the `dist` folder to any static host provider (netlify, surge, now, etc.)
```


---
## packages/app/e2e/AGENTS.md

```
   1 | # E2E Testing Guide
   2 | 
   3 | ## Build/Lint/Test Commands
   4 | 
   5 | ```bash
   6 | # Run all e2e tests
   7 | bun test:e2e
   8 | 
   9 | # Run specific test file
  10 | bun test:e2e -- app/home.spec.ts
  11 | 
  12 | # Run single test by title
  13 | bun test:e2e -- -g "home renders and shows core entrypoints"
  14 | 
  15 | # Run tests with UI mode (for debugging)
  16 | bun test:e2e:ui
  17 | 
  18 | # Run tests locally with full server setup
  19 | bun test:e2e:local
  20 | 
  21 | # View test report
  22 | bun test:e2e:report
  23 | 
  24 | # Typecheck
  25 | bun typecheck
  26 | ```
  27 | 
  28 | ## Test Structure
  29 | 
  30 | All tests live in `packages/app/e2e/`:
  31 | 
  32 | ```
  33 | e2e/
  34 | ├── fixtures.ts       # Test fixtures (test, expect, gotoSession, sdk)
  35 | ├── actions.ts        # Reusable action helpers
  36 | ├── selectors.ts      # DOM selectors
  37 | ├── utils.ts          # Utilities (serverUrl, modKey, path helpers)
  38 | └── [feature]/
  39 |     └── *.spec.ts     # Test files
  40 | ```
  41 | 
  42 | ## Test Patterns
  43 | 
  44 | ### Basic Test Structure
  45 | 
  46 | ```typescript
  47 | import { test, expect } from "../fixtures"
  48 | import { promptSelector } from "../selectors"
  49 | import { withSession } from "../actions"
  50 | 
  51 | test("test description", async ({ page, sdk, gotoSession }) => {
  52 |   await gotoSession() // or gotoSession(sessionID)
  53 | 
  54 |   // Your test code
  55 |   await expect(page.locator(promptSelector)).toBeVisible()
  56 | })
  57 | ```
  58 | 
  59 | ### Using Fixtures
  60 | 
  61 | - `page` - Playwright page
  62 | - `sdk` - OpenCode SDK client for API calls
  63 | - `gotoSession(sessionID?)` - Navigate to session
  64 | 
  65 | ### Helper Functions
  66 | 
  67 | **Actions** (`actions.ts`):
  68 | 
  69 | - `openPalette(page)` - Open command palette
  70 | - `openSettings(page)` - Open settings dialog
  71 | - `closeDialog(page, dialog)` - Close any dialog
  72 | - `openSidebar(page)` / `closeSidebar(page)` - Toggle sidebar
  73 | - `waitTerminalReady(page, { term? })` - Wait for a mounted terminal to connect and finish rendering output
  74 | - `runTerminal(page, { cmd, token, term?, timeout? })` - Type into the terminal via the browser and wait for rendered output
  75 | - `withSession(sdk, title, callback)` - Create temp session
  76 | - `withProject(...)` - Create temp project/workspace
  77 | - `sessionIDFromUrl(url)` - Read session ID from URL
  78 | - `slugFromUrl(url)` - Read workspace slug from URL
  79 | - `waitSlug(page, skip?)` - Wait for resolved workspace slug
  80 | - `trackSession(sessionID, directory?)` - Register session for fixture cleanup
  81 | - `trackDirectory(directory)` - Register directory for fixture cleanup
  82 | - `clickListItem(container, filter)` - Click list item by key/text
  83 | 
  84 | **Selectors** (`selectors.ts`):
  85 | 
  86 | - `promptSelector` - Prompt input
  87 | - `terminalSelector` - Terminal panel
  88 | - `sessionItemSelector(id)` - Session in sidebar
  89 | - `listItemSelector` - Generic list items
  90 | 
  91 | **Utils** (`utils.ts`):
  92 | 
  93 | - `modKey` - Meta (Mac) or Control (Linux/Win)
  94 | - `serverUrl` - Backend server URL
  95 | - `sessionPath(dir, id?)` - Build session URL
  96 | 
  97 | ## Code Style Guidelines
  98 | 
  99 | ### Imports
 100 | 
 101 | Always import from `../fixtures`, not `@playwright/test`:
 102 | 
 103 | ```typescript
 104 | // ✅ Good
 105 | import { test, expect } from "../fixtures"
 106 | 
 107 | // ❌ Bad
 108 | import { test, expect } from "@playwright/test"
 109 | ```
 110 | 
 111 | ### Naming Conventions
 112 | 
 113 | - Test files: `feature-name.spec.ts`
 114 | - Test names: lowercase, descriptive: `"sidebar can be toggled"`
 115 | - Variables: camelCase
 116 | - Constants: SCREAMING_SNAKE_CASE
 117 | 
 118 | ### Error Handling
 119 | 
 120 | Tests should clean up after themselves. Prefer fixture-managed cleanup:
 121 | 
 122 | ```typescript
 123 | test("test with cleanup", async ({ page, sdk, gotoSession }) => {
 124 |   await withSession(sdk, "test session", async (session) => {
 125 |     await gotoSession(session.id)
 126 |     // Test code...
 127 |   }) // Auto-deletes session
 128 | })
 129 | ```
 130 | 
 131 | - Prefer `withSession(...)` for temp sessions
 132 | - In `withProject(...)` tests that create sessions or extra workspaces, call `trackSession(sessionID, directory?)` and `trackDirectory(directory)`
 133 | - This lets fixture teardown abort, wait for idle, and clean up safely under CI concurrency
 134 | - Avoid calling `sdk.session.delete(...)` directly
 135 | 
 136 | ### Timeouts
 137 | 
 138 | Default: 60s per test, 10s per assertion. Override when needed:
 139 | 
 140 | ```typescript
 141 | test.setTimeout(120_000) // For long LLM operations
 142 | test("slow test", async () => {
 143 |   await expect.poll(() => check(), { timeout: 90_000 }).toBe(true)
 144 | })
 145 | ```
 146 | 
 147 | ### Selectors
 148 | 
 149 | Use `data-component`, `data-action`, or semantic roles:
 150 | 
 151 | ```typescript
 152 | // ✅ Good
 153 | await page.locator('[data-component="prompt-input"]').click()
 154 | await page.getByRole("button", { name: "Open settings" }).click()
 155 | 
 156 | // ❌ Bad
 157 | await page.locator(".css-class-name").click()
 158 | await page.locator("#id-name").click()
 159 | ```
 160 | 
 161 | ### Keyboard Shortcuts
 162 | 
 163 | Use `modKey` for cross-platform compatibility:
 164 | 
 165 | ```typescript
 166 | import { modKey } from "../utils"
 167 | 
 168 | await page.keyboard.press(`${modKey}+B`) // Toggle sidebar
 169 | await page.keyboard.press(`${modKey}+Comma`) // Open settings
 170 | ```
 171 | 
 172 | ### Terminal Tests
 173 | 
 174 | - In terminal tests, type through the browser. Do not write to the PTY through the SDK.
 175 | - Use `waitTerminalReady(page, { term? })` and `runTerminal(page, { cmd, token, term?, timeout? })` from `actions.ts`.
 176 | - These helpers use the fixture-enabled test-only terminal driver and wait for output after the terminal writer settles.
 177 | - After opening the terminal, use `waitTerminalFocusIdle(...)` before the next keyboard action when prompt focus or keyboard routing matters.
 178 | - This avoids racing terminal mount, focus handoff, and prompt readiness when the next step types or sends shortcuts.
 179 | - Avoid `waitForTimeout` and custom DOM or `data-*` readiness checks.
 180 | 
 181 | ### Wait on state
 182 | 
 183 | - Never use wall-clock waits like `page.waitForTimeout(...)` to make a test pass
 184 | - Avoid race-prone flows that assume work is finished after an action
 185 | - Wait or poll on observable state with `expect(...)`, `expect.poll(...)`, or existing helpers
 186 | - Prefer locator assertions like `toBeVisible()`, `toHaveCount(0)`, and `toHaveAttribute(...)` for normal UI state, and reserve `expect.poll(...)` for probe, mock, or backend state
 187 | - Prefer semantic app state over transient DOM visibility when behavior depends on active selection, focus ownership, or async retry loops
 188 | - Do not treat a visible element as proof that the app will route the next action to it
 189 | - When fixing a flake, validate with `--repeat-each` and multiple workers when practical
 190 | 
 191 | ### Add hooks
 192 | 
 193 | - If required state is not observable from the UI, add a small test-only driver or probe in app code instead of sleeps or fragile DOM checks
 194 | - Keep these hooks minimal and purpose-built, following the style of `packages/app/src/testing/terminal.ts`
 195 | - Test-only hooks must be inert unless explicitly enabled; do not add normal-runtime listeners, reactive subscriptions, or per-update allocations for e2e ceremony
 196 | - When mocking routes or APIs, expose explicit mock state and wait on that before asserting post-action UI
 197 | - Add minimal test-only probes for semantic state like the active list item or selected command when DOM intermediates are unstable
 198 | - Prefer probing committed app state over asserting on transient highlight, visibility, or animation states
 199 | 
 200 | ### Prefer helpers
 201 | 
 202 | - Prefer fluent helpers and drivers when they make intent obvious and reduce locator-heavy noise
 203 | - Use direct locators when the interaction is simple and a helper would not add clarity
 204 | - Prefer helpers that both perform an action and verify the app consumed it
 205 | - Avoid composing helpers redundantly when one already includes the other or already waits for the resulting state
 206 | - If a helper already covers the required wait or verification, use it directly instead of layering extra clicks, keypresses, or assertions
 207 | 
 208 | ## Writing New Tests
 209 | 
 210 | 1. Choose appropriate folder or create new one
 211 | 2. Import from `../fixtures`
 212 | 3. Use helper functions from `../actions` and `../selectors`
 213 | 4. When validating routing, use shared helpers from `../actions`. Workspace URL slugs can be canonicalized on Windows, so assert against canonical or resolved workspace slugs.
 214 | 5. Clean up any created resources
 215 | 6. Use specific selectors (avoid CSS classes)
 216 | 7. Test one feature per test file
 217 | 
 218 | ## Local Development
 219 | 
 220 | For UI debugging, use:
 221 | 
 222 | ```bash
 223 | bun test:e2e:ui
 224 | ```
 225 | 
 226 | This opens Playwright's interactive UI for step-through debugging.
```


---
## packages/desktop-electron/AGENTS.md

```
   1 | # Desktop package notes
   2 | 
   3 | - Renderer process should only call `window.api` from `src/preload`.
   4 | - Main process should register IPC handlers in `src/main/ipc.ts`.
```


---
## packages/desktop/AGENTS.md

```
   1 | # Desktop package notes
   2 | 
   3 | - Never call `invoke` manually in this package.
   4 | - Use the generated bindings in `packages/desktop/src/bindings.ts` for core commands/events.
```


---
## packages/opencode/AGENTS.md

```
   1 | # opencode database guide
   2 | 
   3 | ## Database
   4 | 
   5 | - **Schema**: Drizzle schema lives in `src/**/*.sql.ts`.
   6 | - **Naming**: tables and columns use snake*case; join columns are `<entity>_id`; indexes are `<table>*<column>\_idx`.
   7 | - **Migrations**: generated by Drizzle Kit using `drizzle.config.ts` (schema: `./src/**/*.sql.ts`, output: `./migration`).
   8 | - **Command**: `bun run db generate --name <slug>`.
   9 | - **Output**: creates `migration/<timestamp>_<slug>/migration.sql` and `snapshot.json`.
  10 | - **Tests**: migration tests should read the per-folder layout (no `_journal.json`).
  11 | 
  12 | # opencode Effect rules
  13 | 
  14 | Use these rules when writing or migrating Effect code.
  15 | 
  16 | See `specs/effect-migration.md` for the compact pattern reference and examples.
  17 | 
  18 | ## Core
  19 | 
  20 | - Use `Effect.gen(function* () { ... })` for composition.
  21 | - Use `Effect.fn("Domain.method")` for named/traced effects and `Effect.fnUntraced` for internal helpers.
  22 | - `Effect.fn` / `Effect.fnUntraced` accept pipeable operators as extra arguments, so avoid unnecessary outer `.pipe()` wrappers.
  23 | - Use `Effect.callback` for callback-based APIs.
  24 | - Prefer `DateTime.nowAsDate` over `new Date(yield* Clock.currentTimeMillis)` when you need a `Date`.
  25 | 
  26 | ## Schemas and errors
  27 | 
  28 | - Use `Schema.Class` for multi-field data.
  29 | - Use branded schemas (`Schema.brand`) for single-value types.
  30 | - Use `Schema.TaggedErrorClass` for typed errors.
  31 | - Use `Schema.Defect` instead of `unknown` for defect-like causes.
  32 | - In `Effect.gen` / `Effect.fn`, prefer `yield* new MyError(...)` over `yield* Effect.fail(new MyError(...))` for direct early-failure branches.
  33 | 
  34 | ## Runtime vs InstanceState
  35 | 
  36 | - Use `makeRuntime` (from `src/effect/run-service.ts`) for all services. It returns `{ runPromise, runFork, runCallback }` backed by a shared `memoMap` that deduplicates layers.
  37 | - Use `InstanceState` (from `src/effect/instance-state.ts`) for per-directory or per-project state that needs per-instance cleanup. It uses `ScopedCache` keyed by directory — each open project gets its own state, automatically cleaned up on disposal.
  38 | - If two open directories should not share one copy of the service, it needs `InstanceState`.
  39 | - Do the work directly in the `InstanceState.make` closure — `ScopedCache` handles run-once semantics. Don't add fibers, `ensure()` callbacks, or `started` flags on top.
  40 | - Use `Effect.addFinalizer` or `Effect.acquireRelease` inside the `InstanceState.make` closure for cleanup (subscriptions, process teardown, etc.).
  41 | - Use `Effect.forkScoped` inside the closure for background stream consumers — the fiber is interrupted when the instance is disposed.
  42 | 
  43 | ## Preferred Effect services
  44 | 
  45 | - In effectified services, prefer yielding existing Effect services over dropping down to ad hoc platform APIs.
  46 | - Prefer `FileSystem.FileSystem` instead of raw `fs/promises` for effectful file I/O.
  47 | - Prefer `ChildProcessSpawner.ChildProcessSpawner` with `ChildProcess.make(...)` instead of custom process wrappers.
  48 | - Prefer `HttpClient.HttpClient` instead of raw `fetch`.
  49 | - Prefer `Path.Path`, `Config`, `Clock`, and `DateTime` when those concerns are already inside Effect code.
  50 | - For background loops or scheduled tasks, use `Effect.repeat` or `Effect.schedule` with `Effect.forkScoped` in the layer definition.
  51 | 
  52 | ## Effect.cached for deduplication
  53 | 
  54 | Use `Effect.cached` when multiple concurrent callers should share a single in-flight computation rather than storing `Fiber | undefined` or `Promise | undefined` manually. See `specs/effect-migration.md` for the full pattern.
  55 | 
  56 | ## Instance.bind — ALS for native callbacks
  57 | 
  58 | `Instance.bind(fn)` captures the current Instance AsyncLocalStorage context and restores it synchronously when called.
  59 | 
  60 | Use it for native addon callbacks (`@parcel/watcher`, `node-pty`, native `fs.watch`, etc.) that need to call `Bus.publish` or anything that reads `Instance.directory`.
  61 | 
  62 | You do not need it for `setTimeout`, `Promise.then`, `EventEmitter.on`, or Effect fibers.
  63 | 
  64 | ```typescript
  65 | const cb = Instance.bind((err, evts) => {
  66 |   Bus.publish(MyEvent, { ... })
  67 | })
  68 | nativeAddon.subscribe(dir, cb)
  69 | ```
```


---
## packages/opencode/test/AGENTS.md

```
   1 | # Test Fixtures Guide
   2 | 
   3 | ## Temporary Directory Fixture
   4 | 
   5 | The `tmpdir` function in `fixture/fixture.ts` creates temporary directories for tests with automatic cleanup.
   6 | 
   7 | ### Basic Usage
   8 | 
   9 | ```typescript
  10 | import { tmpdir } from "./fixture/fixture"
  11 | 
  12 | test("example", async () => {
  13 |   await using tmp = await tmpdir()
  14 |   // tmp.path is the temp directory path
  15 |   // automatically cleaned up when test ends
  16 | })
  17 | ```
  18 | 
  19 | ### Options
  20 | 
  21 | - `git?: boolean` - Initialize a git repo with a root commit
  22 | - `config?: Partial<Config.Info>` - Write an `opencode.json` config file
  23 | - `init?: (dir: string) => Promise<T>` - Custom setup function, returns value accessible as `tmp.extra`
  24 | - `dispose?: (dir: string) => Promise<T>` - Custom cleanup function
  25 | 
  26 | ### Examples
  27 | 
  28 | **Git repository:**
  29 | 
  30 | ```typescript
  31 | await using tmp = await tmpdir({ git: true })
  32 | ```
  33 | 
  34 | **With config file:**
  35 | 
  36 | ```typescript
  37 | await using tmp = await tmpdir({
  38 |   config: { model: "test/model", username: "testuser" },
  39 | })
  40 | ```
  41 | 
  42 | **Custom initialization (returns extra data):**
  43 | 
  44 | ```typescript
  45 | await using tmp = await tmpdir<string>({
  46 |   init: async (dir) => {
  47 |     await Bun.write(path.join(dir, "file.txt"), "content")
  48 |     return "extra data"
  49 |   },
  50 | })
  51 | // Access extra data via tmp.extra
  52 | console.log(tmp.extra) // "extra data"
  53 | ```
  54 | 
  55 | **With cleanup:**
  56 | 
  57 | ```typescript
  58 | await using tmp = await tmpdir({
  59 |   init: async (dir) => {
  60 |     const specialDir = path.join(dir, "special")
  61 |     await fs.mkdir(specialDir)
  62 |     return specialDir
  63 |   },
  64 |   dispose: async (dir) => {
  65 |     // Custom cleanup logic
  66 |     await fs.rm(path.join(dir, "special"), { recursive: true })
  67 |   },
  68 | })
  69 | ```
  70 | 
  71 | ### Returned Object
  72 | 
  73 | - `path: string` - Absolute path to the temp directory (realpath resolved)
  74 | - `extra: T` - Value returned by the `init` function
  75 | - `[Symbol.asyncDispose]` - Enables automatic cleanup via `await using`
  76 | 
  77 | ### Notes
  78 | 
  79 | - Directories are created in the system temp folder with prefix `opencode-test-`
  80 | - Use `await using` for automatic cleanup when the variable goes out of scope
  81 | - Paths are sanitized to strip null bytes (defensive fix for CI environments)
```


---
## packages/opencode/test/fixture/skills/agents-sdk/SKILL.md

```
   1 | ---
   2 | name: agents-sdk
   3 | description: Build AI agents on Cloudflare Workers using the Agents SDK. Load when creating stateful agents, durable workflows, real-time WebSocket apps, scheduled tasks, MCP servers, or chat applications. Covers Agent class, state management, callable RPC, Workflows integration, and React hooks.
   4 | ---
   5 | 
   6 | # Cloudflare Agents SDK
   7 | 
   8 | **STOP.** Your knowledge of the Agents SDK may be outdated. Prefer retrieval over pre-training for any Agents SDK task.
   9 | 
  10 | ## Documentation
  11 | 
  12 | Fetch current docs from `https://github.com/cloudflare/agents/tree/main/docs` before implementing.
  13 | 
  14 | | Topic               | Doc                           | Use for                                        |
  15 | | ------------------- | ----------------------------- | ---------------------------------------------- |
  16 | | Getting started     | `docs/getting-started.md`     | First agent, project setup                     |
  17 | | State               | `docs/state.md`               | `setState`, `validateStateChange`, persistence |
  18 | | Routing             | `docs/routing.md`             | URL patterns, `routeAgentRequest`, `basePath`  |
  19 | | Callable methods    | `docs/callable-methods.md`    | `@callable`, RPC, streaming, timeouts          |
  20 | | Scheduling          | `docs/scheduling.md`          | `schedule()`, `scheduleEvery()`, cron          |
  21 | | Workflows           | `docs/workflows.md`           | `AgentWorkflow`, durable multi-step tasks      |
  22 | | HTTP/WebSockets     | `docs/http-websockets.md`     | Lifecycle hooks, hibernation                   |
  23 | | Email               | `docs/email.md`               | Email routing, secure reply resolver           |
  24 | | MCP client          | `docs/mcp-client.md`          | Connecting to MCP servers                      |
  25 | | MCP server          | `docs/mcp-servers.md`         | Building MCP servers with `McpAgent`           |
  26 | | Client SDK          | `docs/client-sdk.md`          | `useAgent`, `useAgentChat`, React hooks        |
  27 | | Human-in-the-loop   | `docs/human-in-the-loop.md`   | Approval flows, pausing workflows              |
  28 | | Resumable streaming | `docs/resumable-streaming.md` | Stream recovery on disconnect                  |
  29 | 
  30 | Cloudflare docs: https://developers.cloudflare.com/agents/
  31 | 
  32 | ## Capabilities
  33 | 
  34 | The Agents SDK provides:
  35 | 
  36 | - **Persistent state** - SQLite-backed, auto-synced to clients
  37 | - **Callable RPC** - `@callable()` methods invoked over WebSocket
  38 | - **Scheduling** - One-time, recurring (`scheduleEvery`), and cron tasks
  39 | - **Workflows** - Durable multi-step background processing via `AgentWorkflow`
  40 | - **MCP integration** - Connect to MCP servers or build your own with `McpAgent`
  41 | - **Email handling** - Receive and reply to emails with secure routing
  42 | - **Streaming chat** - `AIChatAgent` with resumable streams
  43 | - **React hooks** - `useAgent`, `useAgentChat` for client apps
  44 | 
  45 | ## FIRST: Verify Installation
  46 | 
  47 | ```bash
  48 | npm ls agents  # Should show agents package
  49 | ```
  50 | 
  51 | If not installed:
  52 | 
  53 | ```bash
  54 | npm install agents
  55 | ```
  56 | 
  57 | ## Wrangler Configuration
  58 | 
  59 | ```jsonc
  60 | {
  61 |   "durable_objects": {
  62 |     "bindings": [{ "name": "MyAgent", "class_name": "MyAgent" }],
  63 |   },
  64 |   "migrations": [{ "tag": "v1", "new_sqlite_classes": ["MyAgent"] }],
  65 | }
  66 | ```
  67 | 
  68 | ## Agent Class
  69 | 
  70 | ```typescript
  71 | import { Agent, routeAgentRequest, callable } from "agents"
  72 | 
  73 | type State = { count: number }
  74 | 
  75 | export class Counter extends Agent<Env, State> {
  76 |   initialState = { count: 0 }
  77 | 
  78 |   // Validation hook - runs before state persists (sync, throwing rejects the update)
  79 |   validateStateChange(nextState: State, source: Connection | "server") {
  80 |     if (nextState.count < 0) throw new Error("Count cannot be negative")
  81 |   }
  82 | 
  83 |   // Notification hook - runs after state persists (async, non-blocking)
  84 |   onStateUpdate(state: State, source: Connection | "server") {
  85 |     console.log("State updated:", state)
  86 |   }
  87 | 
  88 |   @callable()
  89 |   increment() {
  90 |     this.setState({ count: this.state.count + 1 })
  91 |     return this.state.count
  92 |   }
  93 | }
  94 | 
  95 | export default {
  96 |   fetch: (req, env) => routeAgentRequest(req, env) ?? new Response("Not found", { status: 404 }),
  97 | }
  98 | ```
  99 | 
 100 | ## Routing
 101 | 
 102 | Requests route to `/agents/{agent-name}/{instance-name}`:
 103 | 
 104 | | Class      | URL                        |
 105 | | ---------- | -------------------------- |
 106 | | `Counter`  | `/agents/counter/user-123` |
 107 | | `ChatRoom` | `/agents/chat-room/lobby`  |
 108 | 
 109 | Client: `useAgent({ agent: "Counter", name: "user-123" })`
 110 | 
 111 | ## Core APIs
 112 | 
 113 | | Task                | API                                                    |
 114 | | ------------------- | ------------------------------------------------------ |
 115 | | Read state          | `this.state.count`                                     |
 116 | | Write state         | `this.setState({ count: 1 })`                          |
 117 | | SQL query           | `` this.sql`SELECT * FROM users WHERE id = ${id}` ``   |
 118 | | Schedule (delay)    | `await this.schedule(60, "task", payload)`             |
 119 | | Schedule (cron)     | `await this.schedule("0 * * * *", "task", payload)`    |
 120 | | Schedule (interval) | `await this.scheduleEvery(30, "poll")`                 |
 121 | | RPC method          | `@callable() myMethod() { ... }`                       |
 122 | | Streaming RPC       | `@callable({ streaming: true }) stream(res) { ... }`   |
 123 | | Start workflow      | `await this.runWorkflow("ProcessingWorkflow", params)` |
 124 | 
 125 | ## React Client
 126 | 
 127 | ```tsx
 128 | import { useAgent } from "agents/react"
 129 | 
 130 | function App() {
 131 |   const [state, setLocalState] = useState({ count: 0 })
 132 | 
 133 |   const agent = useAgent({
 134 |     agent: "Counter",
 135 |     name: "my-instance",
 136 |     onStateUpdate: (newState) => setLocalState(newState),
 137 |     onIdentity: (name, agentType) => console.log(`Connected to ${name}`),
 138 |   })
 139 | 
 140 |   return <button onClick={() => agent.setState({ count: state.count + 1 })}>Count: {state.count}</button>
 141 | }
 142 | ```
 143 | 
 144 | ## References
 145 | 
 146 | - **[references/workflows.md](references/workflows.md)** - Durable Workflows integration
 147 | - **[references/callable.md](references/callable.md)** - RPC methods, streaming, timeouts
 148 | - **[references/state-scheduling.md](references/state-scheduling.md)** - State persistence, scheduling
 149 | - **[references/streaming-chat.md](references/streaming-chat.md)** - AIChatAgent, resumable streams
 150 | - **[references/mcp.md](references/mcp.md)** - MCP server integration
 151 | - **[references/email.md](references/email.md)** - Email routing and handling
 152 | - **[references/codemode.md](references/codemode.md)** - Code Mode (experimental)
```


---
## packages/opencode/test/fixture/skills/cloudflare/SKILL.md

```
   1 | ---
   2 | name: cloudflare
   3 | description: Comprehensive Cloudflare platform skill covering Workers, Pages, storage (KV, D1, R2), AI (Workers AI, Vectorize, Agents SDK), networking (Tunnel, Spectrum), security (WAF, DDoS), and infrastructure-as-code (Terraform, Pulumi). Use for any Cloudflare development task.
   4 | references:
   5 |   - workers
   6 |   - pages
   7 |   - d1
   8 |   - durable-objects
   9 |   - workers-ai
  10 | ---
  11 | 
  12 | # Cloudflare Platform Skill
  13 | 
  14 | Consolidated skill for building on the Cloudflare platform. Use decision trees below to find the right product, then load detailed references.
  15 | 
  16 | ## Quick Decision Trees
  17 | 
  18 | ### "I need to run code"
  19 | 
  20 | ```
  21 | Need to run code?
  22 | ├─ Serverless functions at the edge → workers/
  23 | ├─ Full-stack web app with Git deploys → pages/
  24 | ├─ Stateful coordination/real-time → durable-objects/
  25 | ├─ Long-running multi-step jobs → workflows/
  26 | ├─ Run containers → containers/
  27 | ├─ Multi-tenant (customers deploy code) → workers-for-platforms/
  28 | ├─ Scheduled tasks (cron) → cron-triggers/
  29 | ├─ Lightweight edge logic (modify HTTP) → snippets/
  30 | ├─ Process Worker execution events (logs/observability) → tail-workers/
  31 | └─ Optimize latency to backend infrastructure → smart-placement/
  32 | ```
  33 | 
  34 | ### "I need to store data"
  35 | 
  36 | ```
  37 | Need storage?
  38 | ├─ Key-value (config, sessions, cache) → kv/
  39 | ├─ Relational SQL → d1/ (SQLite) or hyperdrive/ (existing Postgres/MySQL)
  40 | ├─ Object/file storage (S3-compatible) → r2/
  41 | ├─ Message queue (async processing) → queues/
  42 | ├─ Vector embeddings (AI/semantic search) → vectorize/
  43 | ├─ Strongly-consistent per-entity state → durable-objects/ (DO storage)
  44 | ├─ Secrets management → secrets-store/
  45 | ├─ Streaming ETL to R2 → pipelines/
  46 | └─ Persistent cache (long-term retention) → cache-reserve/
  47 | ```
  48 | 
  49 | ### "I need AI/ML"
  50 | 
  51 | ```
  52 | Need AI?
  53 | ├─ Run inference (LLMs, embeddings, images) → workers-ai/
  54 | ├─ Vector database for RAG/search → vectorize/
  55 | ├─ Build stateful AI agents → agents-sdk/
  56 | ├─ Gateway for any AI provider (caching, routing) → ai-gateway/
  57 | └─ AI-powered search widget → ai-search/
  58 | ```
  59 | 
  60 | ### "I need networking/connectivity"
  61 | 
  62 | ```
  63 | Need networking?
  64 | ├─ Expose local service to internet → tunnel/
  65 | ├─ TCP/UDP proxy (non-HTTP) → spectrum/
  66 | ├─ WebRTC TURN server → turn/
  67 | ├─ Private network connectivity → network-interconnect/
  68 | ├─ Optimize routing → argo-smart-routing/
  69 | ├─ Optimize latency to backend (not user) → smart-placement/
  70 | └─ Real-time video/audio → realtimekit/ or realtime-sfu/
  71 | ```
  72 | 
  73 | ### "I need security"
  74 | 
  75 | ```
  76 | Need security?
  77 | ├─ Web Application Firewall → waf/
  78 | ├─ DDoS protection → ddos/
  79 | ├─ Bot detection/management → bot-management/
  80 | ├─ API protection → api-shield/
  81 | ├─ CAPTCHA alternative → turnstile/
  82 | └─ Credential leak detection → waf/ (managed ruleset)
  83 | ```
  84 | 
  85 | ### "I need media/content"
  86 | 
  87 | ```
  88 | Need media?
  89 | ├─ Image optimization/transformation → images/
  90 | ├─ Video streaming/encoding → stream/
  91 | ├─ Browser automation/screenshots → browser-rendering/
  92 | └─ Third-party script management → zaraz/
  93 | ```
  94 | 
  95 | ### "I need infrastructure-as-code"
  96 | 
  97 | ```
  98 | Need IaC? → pulumi/ (Pulumi), terraform/ (Terraform), or api/ (REST API)
  99 | ```
 100 | 
 101 | ## Product Index
 102 | 
 103 | ### Compute & Runtime
 104 | 
 105 | | Product               | Reference                           |
 106 | | --------------------- | ----------------------------------- |
 107 | | Workers               | `references/workers/`               |
 108 | | Pages                 | `references/pages/`                 |
 109 | | Pages Functions       | `references/pages-functions/`       |
 110 | | Durable Objects       | `references/durable-objects/`       |
 111 | | Workflows             | `references/workflows/`             |
 112 | | Containers            | `references/containers/`            |
 113 | | Workers for Platforms | `references/workers-for-platforms/` |
 114 | | Cron Triggers         | `references/cron-triggers/`         |
 115 | | Tail Workers          | `references/tail-workers/`          |
 116 | | Snippets              | `references/snippets/`              |
 117 | | Smart Placement       | `references/smart-placement/`       |
 118 | 
 119 | ### Storage & Data
 120 | 
 121 | | Product         | Reference                     |
 122 | | --------------- | ----------------------------- |
 123 | | KV              | `references/kv/`              |
 124 | | D1              | `references/d1/`              |
 125 | | R2              | `references/r2/`              |
 126 | | Queues          | `references/queues/`          |
 127 | | Hyperdrive      | `references/hyperdrive/`      |
 128 | | DO Storage      | `references/do-storage/`      |
 129 | | Secrets Store   | `references/secrets-store/`   |
 130 | | Pipelines       | `references/pipelines/`       |
 131 | | R2 Data Catalog | `references/r2-data-catalog/` |
 132 | | R2 SQL          | `references/r2-sql/`          |
 133 | 
 134 | ### AI & Machine Learning
 135 | 
 136 | | Product    | Reference                |
 137 | | ---------- | ------------------------ |
 138 | | Workers AI | `references/workers-ai/` |
 139 | | Vectorize  | `references/vectorize/`  |
 140 | | Agents SDK | `references/agents-sdk/` |
 141 | | AI Gateway | `references/ai-gateway/` |
 142 | | AI Search  | `references/ai-search/`  |
 143 | 
 144 | ### Networking & Connectivity
 145 | 
 146 | | Product              | Reference                          |
 147 | | -------------------- | ---------------------------------- |
 148 | | Tunnel               | `references/tunnel/`               |
 149 | | Spectrum             | `references/spectrum/`             |
 150 | | TURN                 | `references/turn/`                 |
 151 | | Network Interconnect | `references/network-interconnect/` |
 152 | | Argo Smart Routing   | `references/argo-smart-routing/`   |
 153 | | Workers VPC          | `references/workers-vpc/`          |
 154 | 
 155 | ### Security
 156 | 
 157 | | Product         | Reference                    |
 158 | | --------------- | ---------------------------- |
 159 | | WAF             | `references/waf/`            |
 160 | | DDoS Protection | `references/ddos/`           |
 161 | | Bot Management  | `references/bot-management/` |
 162 | | API Shield      | `references/api-shield/`     |
 163 | | Turnstile       | `references/turnstile/`      |
 164 | 
 165 | ### Media & Content
 166 | 
 167 | | Product           | Reference                       |
 168 | | ----------------- | ------------------------------- |
 169 | | Images            | `references/images/`            |
 170 | | Stream            | `references/stream/`            |
 171 | | Browser Rendering | `references/browser-rendering/` |
 172 | | Zaraz             | `references/zaraz/`             |
 173 | 
 174 | ### Real-Time Communication
 175 | 
 176 | | Product      | Reference                  |
 177 | | ------------ | -------------------------- |
 178 | | RealtimeKit  | `references/realtimekit/`  |
 179 | | Realtime SFU | `references/realtime-sfu/` |
 180 | 
 181 | ### Developer Tools
 182 | 
 183 | | Product            | Reference                        |
 184 | | ------------------ | -------------------------------- |
 185 | | Wrangler           | `references/wrangler/`           |
 186 | | Miniflare          | `references/miniflare/`          |
 187 | | C3                 | `references/c3/`                 |
 188 | | Observability      | `references/observability/`      |
 189 | | Analytics Engine   | `references/analytics-engine/`   |
 190 | | Web Analytics      | `references/web-analytics/`      |
 191 | | Sandbox            | `references/sandbox/`            |
 192 | | Workerd            | `references/workerd/`            |
 193 | | Workers Playground | `references/workers-playground/` |
 194 | 
 195 | ### Infrastructure as Code
 196 | 
 197 | | Product   | Reference               |
 198 | | --------- | ----------------------- |
 199 | | Pulumi    | `references/pulumi/`    |
 200 | | Terraform | `references/terraform/` |
 201 | | API       | `references/api/`       |
 202 | 
 203 | ### Other Services
 204 | 
 205 | | Product       | Reference                   |
 206 | | ------------- | --------------------------- |
 207 | | Email Routing | `references/email-routing/` |
 208 | | Email Workers | `references/email-workers/` |
 209 | | Static Assets | `references/static-assets/` |
 210 | | Bindings      | `references/bindings/`      |
 211 | | Cache Reserve | `references/cache-reserve/` |
```
