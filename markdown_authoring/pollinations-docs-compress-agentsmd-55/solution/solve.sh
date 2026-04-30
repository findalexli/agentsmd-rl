#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pollinations

# Idempotency guard
if grep -qF "Platforms (auto-detected; comma-separated for multi): `web` (default w/ URL), `a" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -2,477 +2,196 @@
 
 ## App Submission Handling
 
-App submissions use a **two-phase review** via `app-review-submission.yml`: AI review + human approval.
+Two-phase review via `app-review-submission.yml` (AI + human). Source of truth: `apps/APPS.md`.
 
-**Source of truth:** `apps/APPS.md` - A single markdown table with all apps.
+Flow: user opens issue with `TIER-APP` → workflow validates + AI generates preview → bot posts `APP_REVIEW_DATA` JSON + labels `TIER-APP-REVIEW` → maintainer adds `TIER-APP-APPROVED` → workflow prepends row to `apps/APPS.md`, opens PR with auto-merge, closes issue via `Fixes #NNN`.
 
-**How it works:**
+Label state machine:
+- `TIER-APP` → `TIER-APP-REJECTED` (duplicate/spore) | `TIER-APP-INCOMPLETE` (not registered) | `TIER-APP-REVIEW` → `TIER-APP-APPROVED` (merged) | `TIER-APP-REJECTED` (closed)
 
-1. User opens issue with `TIER-APP` label
-2. Workflow validates (Enter registration, duplicates), AI generates emoji + description
-3. Bot posts preview comment with `APP_REVIEW_DATA` JSON block, labels `TIER-APP-REVIEW`
-4. Maintainer reviews preview, adds `TIER-APP-APPROVED` label
-5. Workflow creates branch, prepends row to `apps/APPS.md`, creates PR with auto-merge
-6. After checks pass, PR merges automatically, issue auto-closed via `Fixes #NNN`
+Manual edits: edit `apps/APPS.md`, run `node .github/scripts/app-update-readme.js`.
 
-**Label state machine:**
+APPS.md columns: `Emoji | Name | Web_URL | Description (~80 chars) | Language (ISO code, no flags) | Category | Platform | GitHub (@user) | GitHub_ID | Repo | Stars (⭐N) | Discord | Other | Submitted_Date (issue created) | Issue_URL (#N) | Approved_Date (PR merged)`.
 
-```
-TIER-APP (new issue)
-  → TIER-APP-REJECTED (validation failed: duplicate/spore)
-  → TIER-APP-INCOMPLETE (not registered, user needs to fix)
-  → TIER-APP-REVIEW (AI review passed, preview posted, awaiting human)
-    → TIER-APP-APPROVED (maintainer approves → PR created + auto-merged → issue closed)
-    → TIER-APP-REJECTED (maintainer closes issue)
-```
-
-**Manual edits (if needed):**
-
-- Edit `apps/APPS.md` directly
-- Run `node .github/scripts/app-update-readme.js` to refresh README
-
-**Table format in APPS.md:**
-
-```markdown
-| Emoji | Name     | Web_URL | Description                   | Language | Category | Platform | GitHub  | GitHub_ID | Repo                   | Stars | Discord | Other | Submitted_Date | Issue_URL | Approved_Date |
-| ----- | -------- | ------- | ----------------------------- | -------- | -------- | -------- | ------- | --------- | ---------------------- | ----- | ------- | ----- | -------------- | --------- | ------------- |
-| 🎨    | App Name | url     | Brief description (~80 chars) |          | creative | web      | @github | 12345678  | https://github.com/... | ⭐123 |         |       | 2025-01-01     | #1234     | 2025-01-02    |
-```
-
-- **Submitted_Date**: Issue creation date (when user submitted)
-- **Issue_URL**: Link to original GitHub issue
-- **Approved_Date**: PR merge date (when app was approved)
-
-**Platform values** (auto-detected from URL + description):
-
-| Value | When to use |
-|-------|-------------|
-| `web` | Browser-based app (default when URL exists) |
-| `android` | Google Play Store app |
-| `ios` | App Store or Apple Shortcuts (routinehub.co) |
-| `windows` | Windows desktop / .exe |
-| `macos` | macOS native app |
-| `desktop` | Cross-platform desktop (Python/Qt, Electron, etc.) |
-| `cli` | Command-line tool |
-| `discord` | Discord bot or app |
-| `telegram` | Telegram bot |
-| `whatsapp` | WhatsApp bot |
-| `library` | npm/PyPI/Go package, SDK, API wrapper |
-| `browser-ext` | Browser extension (Firefox, Chrome) |
-| `roblox` | Roblox game |
-| `wordpress` | WordPress plugin |
-| `api` | Backend/server with no public UI (default when no URL) |
-
-Multiple platforms: comma-separated, e.g. `telegram,whatsapp`
-
-**Categories:**
-
-- 🖼️ Image (`image`): Image gen, editing, design, avatars, stickers
-- 🎬 Video & Audio (`video_audio`): Video gen, animation, music, TTS
-- ✍️ Write (`writing`): Content creation, storytelling, copy, slides
-- 💬 Chat (`chat`): Assistants, companions, AI studio, multi-modal chat
-- 🎮 Play (`games`): AI games, interactive fiction, Roblox worlds
-- 📚 Learn (`learn`): Education, tutoring, language learning
-- 🤖 Bots (`bots`): Discord, Telegram, WhatsApp bots
-- 🛠️ Build (`build`): Dev tools, SDKs, integrations, vibe coding
-- 💼 Business (`business`): Productivity, finance, marketing, health, food
-
-## Non-English Apps
+Platforms (auto-detected; comma-separated for multi): `web` (default w/ URL), `android`, `ios` (App Store or routinehub.co), `windows`, `macos`, `desktop` (cross-platform), `cli`, `discord`, `telegram`, `whatsapp`, `library` (npm/PyPI/SDK), `browser-ext`, `roblox`, `wordpress`, `api` (default w/o URL).
 
-- Use ISO language code in the `Language` column (e.g., `zh-CN`, `es`, `pt-BR`, `ja`)
-- No flags in the table - use language codes only
+Categories: `image`, `video_audio`, `writing`, `chat`, `games`, `learn`, `bots`, `build`, `business`.
 
-## Discord Configuration
+## Discord
 
-**pollinations.ai Discord Server:**
-
-- **Guild ID**: `885844321461485618`
-- **Server**: https://discord.gg/pollinations-ai-885844321461485618
-
-Use this guild ID when interacting with Discord MCP tools for announcements, community management, etc.
+Guild ID `885844321461485618` (https://discord.gg/pollinations-ai-885844321461485618) — use for Discord MCP tools.
 
 ## Repository Structure
 
-Key directories and their purposes:
-
-```
-pollinations/
-├── enter.pollinations.ai/     # Auth gateway + billing (Cloudflare Worker)
-├── gen.pollinations.ai/       # Edge router → enter gateway
-├── image.pollinations.ai/     # Image generation backend (EC2 + Vast.ai)
-├── text.pollinations.ai/      # Text generation backend (EC2)
-├── pollinations.ai/           # Main React frontend
-├── packages/
-│   ├── sdk/                   # @pollinations_ai/sdk - Client library with React hooks
-│   └── mcp/                   # @pollinations_ai/model-context-protocol - MCP server
-├── shared/                    # Shared utilities (auth, registry, IP queue)
-│   └── registry/              # Model registries (image.ts, text.ts, audio.ts, video.ts)
-├── apps/                      # Community apps + APPS.md showcase
-└── social/                    # Social media automation (Discord, Reddit, GitHub)
-```
+- `enter.pollinations.ai/` — Auth gateway + billing (Cloudflare Worker)
+- `gen.pollinations.ai/` — Edge router → enter gateway
+- `image.pollinations.ai/` — Image backend (EC2 + Vast.ai)
+- `text.pollinations.ai/` — Text backend (EC2)
+- `pollinations.ai/` — React frontend
+- `packages/sdk/` — `@pollinations_ai/sdk` (client + React hooks)
+- `packages/mcp/` — `@pollinations_ai/model-context-protocol` (MCP server; see `packages/mcp/AGENTS.md`)
+- `shared/` — auth, registry, IP queue; `shared/registry/` holds model registries
+- `apps/` — Community apps + `APPS.md`
+- `social/` — Discord/Reddit/GitHub automation
 
 ## API Gateway
 
-**Primary endpoint:** `https://gen.pollinations.ai`
-
-All API requests go through `gen.pollinations.ai`, which routes to the `enter.pollinations.ai` gateway for authentication and billing.
-
-- **Authentication**: Publishable keys (`pk_`) for frontend, Secret keys (`sk_`) for backend
-- **Billing**: Pollen credits ($1 ≈ 1 Pollen)
-- **Get API keys**: [enter.pollinations.ai](https://enter.pollinations.ai)
-- **Full API docs**: [APIDOCS.md](./APIDOCS.md)
+Primary: `https://gen.pollinations.ai` → routes to `enter.pollinations.ai` for auth/billing.
 
-**Services behind enter gateway:**
-- **Text**: OpenAI-compatible API via Portkey (multi-provider: OpenAI, Google, Anthropic, DeepSeek, etc.)
-- **Image**: Flux, Turbo, and other models on EC2/Vast.ai/io.net GPU instances
-- **Video**: Wan (via Airforce/Alibaba), Veo, LTX on GPU instances
-- **Audio**: ElevenLabs TTS/STT, text-to-music
-- **Tier system**: microbe → spore → seed → flower → router (nectar is a legacy tier, still supported for existing users but no longer granted; see `enter.pollinations.ai/src/tier-config.ts`)
+- Auth: `pk_` (frontend), `sk_` (backend). Keys: https://enter.pollinations.ai
+- Billing: Pollen credits ($1 ≈ 1 Pollen). Full docs: `./APIDOCS.md`
+- Services: Text (Portkey, multi-provider), Image (Flux/Turbo on EC2/Vast.ai/io.net), Video (Wan/Veo/LTX), Audio (ElevenLabs, TTM)
+- Tiers: microbe → spore → seed → flower → router (nectar is legacy — still supported, no longer granted; see `enter.pollinations.ai/src/tier-config.ts`)
 
 ### Local Development
 
-**Service Ports:**
-- **enter.pollinations.ai**: `http://localhost:3000` (API under `/api/*`)
-- **text.pollinations.ai**: `http://localhost:16385`
-- **image.pollinations.ai**: `http://localhost:16384`
+Ports: enter `3000` (API at `/api/*`), text `16385`, image `16384`. Run `npm run dev` per service.
 
-**Local API Testing:**
+To point enter at local backends, edit `enter.pollinations.ai/wrangler.toml` `IMAGE_SERVICE_URL`/`TEXT_SERVICE_URL` to `http://localhost:1638[45]`. EC2 hostnames in wrangler.toml may change — check actual values.
+
+Local API test:
 ```bash
-# Enter gateway (local)
 curl "http://localhost:3000/api/generate/image/test?model=flux" -H "Authorization: Bearer $TOKEN"
 curl "http://localhost:3000/api/generate/v1/chat/completions" -H "Authorization: Bearer $TOKEN" ...
 ```
 
-**Testing Enter with Local Services:**
-To test enter.pollinations.ai with local text/image services, edit `enter.pollinations.ai/wrangler.toml`:
-```toml
-# Default (remote EC2):
-IMAGE_SERVICE_URL = "http://ec2-54-147-14-220.compute-1.amazonaws.com:16384"
-TEXT_SERVICE_URL = "http://ec2-54-147-14-220.compute-1.amazonaws.com:16385"
+## API Quick Reference
 
-# For local testing (env.local):
-IMAGE_SERVICE_URL = "http://localhost:16384"
-TEXT_SERVICE_URL = "http://localhost:16385"
-```
-Use `npm run dev` in each service directory to start them.
+- Image: `GET gen.pollinations.ai/image/{prompt}` (bearer token)
+- Text (OpenAI): `POST gen.pollinations.ai/v1/chat/completions` with `{model, messages}` (bearer token)
+- Simple text: `GET gen.pollinations.ai/text/{prompt}?key=...`
+- Audio: `GET gen.pollinations.ai/audio/{text}?voice=nova&key=...`
+- Models: `/image/models`, `/v1/models`
+- See `./APIDOCS.md`, `.claude/skills/enter-services/SKILL.md`
 
-**Note:** EC2 hostnames in wrangler.toml may change. Check the actual values in `enter.pollinations.ai/wrangler.toml`.
+## ⚠️ YAGNI — You Aren't Gonna Need It (CRITICAL)
 
-## Model Context Protocol (MCP)
+**Follow YAGNI religiously:**
 
-The `packages/mcp/` directory contains a Model Context Protocol server that allows AI agents to directly generate images, text, and audio using the pollinations.ai API.
+- Only implement what's needed now. Remove unused functions.
+- No speculative abstractions, "just in case" helpers, preemptive test utils/wrappers.
+- No backward-compat fallbacks — clean breaks beat bloat. When changing tokens/headers/APIs, update all consumers at once.
+- When user says "keep it simple" — one function, one price, one config. Simplest thing that works.
 
-For detailed implementation notes, design principles, and troubleshooting, see:
+## Tinybird Deployment Safety
 
-- `packages/mcp/README.md` - Installation and usage
-- `packages/mcp/AGENTS.md` - Implementation guidelines and debugging
+**CRITICAL — These rules apply whenever deploying to Tinybird:**
 
-## API Quick Reference
+- Validate first: `tb --cloud deploy --check --wait`
+- Never `--allow-destructive-operations` without explicit permission
+- Never `tb push` (deprecated); use `tb --cloud deploy --wait`
+- Always `--cloud` (otherwise CLI hits Tinybird Local/Docker)
+- Run from `enter.pollinations.ai/observability`
+- Pipes are shared — verify all consumers before modifying any pipe
+- Timeouts: use `uniq()` not `uniqExact()`; avoid CTE+JOIN; single-pass queries; for large time ranges use `start_date` parameter week-by-week
+- Full procedure: `.claude/skills/tinybird-deploy/SKILL.md`
 
-### Image Generation
+## Code Style & Workflow
 
-```bash
-curl 'https://gen.pollinations.ai/image/{prompt}' -H 'Authorization: Bearer YOUR_API_KEY'
-```
+- Modern JS/TS, ES modules (all `.js` are ESM). Follow existing formatting. Comment complex logic.
+- Run `npx biome check --write <file>` after edits and before commits.
+- Before implementing: verify assumptions on web (APIs change), read related files, check related PRs/issues, check existing utilities in `shared/` before writing new ones (auth, queue, registry, SSE parsing, retry wrappers), confirm branch via `git branch --show-current`.
+- When continuing prior work: read relevant code first; identify clear next steps.
+- Don't reimplement existing logic — search first.
 
-### Text Generation (OpenAI-compatible)
+## Common Mistakes to Avoid
 
-```bash
-curl 'https://gen.pollinations.ai/v1/chat/completions' \
-  -H 'Authorization: Bearer YOUR_API_KEY' \
-  -H 'Content-Type: application/json' \
-  -d '{"model": "openai", "messages": [{"role": "user", "content": "Hello"}]}'
-```
+**IMPORTANT — Agents often make these mistakes (learned from session history):**
 
-### Simple Text
+- Don't use `cd` in bash; use `cwd` parameter.
+- Don't run `pytest`; use `npm run test` or `npx vitest run`.
+- Don't create `.md` docs unless asked.
+- Always use absolute paths.
+- Don't edit files manually during a Claude Code session (busts cache).
+- Don't run `/compact` unless necessary (busts cache).
+- Don't let searches run wild — use targeted paths.
+- Don't modify test files to make tests pass — fix the code.
+- Run `npm run decrypt-vars` before tests in enter.pollinations.ai.
+- Test API keys in `enter.pollinations.ai/.testingtokens`.
+- Request PR reviews by including lowercase `polly` in a PR comment.
 
-```bash
-curl 'https://gen.pollinations.ai/text/{prompt}?key=YOUR_API_KEY'
-```
+## Testing
 
-### Audio (Text-to-Speech)
+Commands:
+- enter.pollinations.ai: `cd enter.pollinations.ai && npm run test` (vitest + CF Workers pool)
+- image.pollinations.ai: `cd image.pollinations.ai && npm run test` (vitest)
+- text.pollinations.ai: no runner yet
 
+Run individually — full suite is slow:
 ```bash
-curl 'https://gen.pollinations.ai/audio/{text}?voice=nova&key=YOUR_API_KEY' -o speech.mp3
+npx vitest run --testNamePattern="name"
+npx vitest run test/file.test.ts
 ```
 
-### Model Discovery
-
-- **Image models**: `https://gen.pollinations.ai/image/models`
-- **Text models**: `https://gen.pollinations.ai/v1/models`
-
-### Documentation
-
-- **[Full API Documentation](./APIDOCS.md)**
-- **[Enter Services Deployment](.claude/skills/enter-services/SKILL.md)** - Deploy and manage services on AWS EC2
-
-## ⚠️ YAGNI - You Aren't Gonna Need It
-
-**THIS IS CRITICAL. Follow YAGNI religiously:**
-
-- **Don't keep code for "potential futures"** - Only implement what's needed NOW
-- **Remove unused functions** - Even if they "might be useful someday"
-- **No speculative abstractions** - If we need it later, we'll add it then
-- **No "just in case" helpers** - Don't create test utilities or wrappers preemptively
-- **Keep the codebase minimal** - Less code = fewer bugs = easier maintenance
-- **No fallbacks for backward compatibility** - Clean breaks are better than complexity bloat. When changing tokens, headers, or APIs, update all consumers at once rather than supporting both old and new patterns
-- **When user says "keep it simple" — they mean it** - Don't add layers, wrappers, or abstractions. One function, one price, one config. The simplest thing that works.
-
-## Code Style
+- Test real code, not mocks — use direct imports. Don't create mock infrastructure.
+- Read existing tests before adding; prefer extending existing files; follow existing conventions.
+- Snapshots (enter): VCR-style, replayed by default. `TEST_VCR_MODE=record` to record; default `replay-or-record`.
+- `.testingtokens` contains: `ENTER_API_TOKEN_LOCAL`, `ENTER_API_TOKEN_REMOTE`, `ENTER_TOKEN`, `GITHUB_TOKEN`, `POLAR_ACCESS_TOKEN`.
+- Production API tests should hit `gen.pollinations.ai`.
 
-**Prefer functional, elegant, and minimal solutions:**
+## Architecture & Common Tasks
 
-- Don't implement things we're not using anymore
-- Check assumptions on the web and codebase regularly
-- When continuing work from a previous session, read all relevant code first
-- Check related PRs including comments, description, and history
-- If in the middle of a feature/fix, identify clear next steps before proceeding
-
-**Before implementing:**
-- **Verify assumptions on the web** - APIs, libraries, and patterns change frequently
-- **Read related files into context** - Get the full picture before making changes
-- **Check existing implementations** - Don't reinvent what already exists in the codebase
-- **Check which branch you're on** - Run `git branch --show-current` before starting work
-- **Check related PRs and issues** - Use GitHub MCP tools to find context before implementing
-- **Look for existing utility functions** in `shared/` before writing new ones (auth, queue, registry)
-
-## Tinybird Deployment Safety
-
-**CRITICAL — These rules apply whenever deploying to Tinybird:**
-
-- **Always validate first**: `tb --cloud deploy --check --wait` before any deploy
-- **Never use `--allow-destructive-operations`** without explicit user permission
-- **Never use `tb push`** — it's deprecated; use `tb --cloud deploy --wait`
-- **Always use `--cloud`** — without it, CLI tries Tinybird Local (Docker)
-- **Run from `enter.pollinations.ai/observability`** — not from repo root
-- **Pipes are shared** — multiple apps/dashboards may consume the same pipe. Verify all consumers before modifying any pipe
-- **Timeout mitigation**: Use `uniq()` over `uniqExact()`, avoid CTE+JOIN, prefer single-pass queries. For large time ranges, use `start_date` parameter pattern for week-by-week querying
-- Full deploy procedure: see `.claude/skills/tinybird-deploy/SKILL.md`
-
-## Common Mistakes to Avoid
-
-**IMPORTANT - Agents often make these mistakes (learned from session history):**
-
-- **Don't use `cd` in bash commands** - Use the `cwd` parameter instead
-- **Don't run `pytest`** - Use `npm run test` or `npx vitest run`
-- **Don't create .md documentation files** unless explicitly asked
-- **Always use absolute paths** for file operations
-- **Don't edit files manually during a Claude Code session** - this busts the cache
-- **Don't run `/compact`** unless absolutely necessary - it busts cache
-- **Don't let searches run wild** - Use targeted file paths, not broad searches
-- **Don't modify test files to make tests pass** - Fix the actual code instead
-- **Run `npm run decrypt-vars`** before running tests in enter.pollinations.ai
-- **Check `.testingtokens`** file for test API keys: `enter.pollinations.ai/.testingtokens`
-- **Confirm which branch you're on** before making changes — branch mix-ups are a recurring problem
-- **Don't reimplement existing logic** — search for existing functions before writing new ones (e.g. SSE parsing, retry wrappers, auth extraction)
-- **Request PR reviews by mentioning `polly`** — include lowercase `polly` in a PR comment (e.g. "polly please review") to trigger the Polly bot reviewer
-
-## Development Guidelines
-
-1. Code Style:
-
-   - Use modern JavaScript/TypeScript features
-   - Use ES modules (import/export) - all .js files are treated as ES modules
-   - Follow existing code formatting patterns
-   - Add descriptive comments for complex logic
-   - **Run biome check** after making changes: `npx biome check --write <file>`
-
-2. Testing:
-
-   - Add tests for new features in appropriate test directories
-   - Follow existing test patterns in /test directories
-   - **Test with real production code, not mocks** - Tests should validate actual behavior
-   - Avoid creating mock infrastructure - use direct function imports instead
-
-   **Test Commands by Service:**
-   - **enter.pollinations.ai**: `cd enter.pollinations.ai && npm run test` (vitest + Cloudflare Workers pool)
-   - **image.pollinations.ai**: `cd image.pollinations.ai && npm run test` (vitest)
-   - **text.pollinations.ai**: No test runner configured yet
-
-   **⚡ Run tests individually** - Full suite takes time. Use:
-   ```bash
-   npx vitest run --testNamePattern="specific test name"
-   npx vitest run test/specific-file.test.ts
-   ```
-
-   **Snapshot System:** enter.pollinations.ai uses VCR-style snapshots for API responses:
-   - Snapshots stored in test fixtures, replayed during tests
-   - Set `TEST_VCR_MODE=record` to record new snapshots
-   - Default mode is `replay-or-record`
-
-   **Testing Tokens:** `enter.pollinations.ai/.testingtokens` contains:
-   - `ENTER_API_TOKEN_LOCAL` / `ENTER_API_TOKEN_REMOTE` - API keys
-   - `ENTER_TOKEN`, `GITHUB_TOKEN`, `POLAR_ACCESS_TOKEN`
-
-   **Testing Best Practices:**
-   - Read existing tests entirely to understand patterns before adding new ones
-   - Prefer adding to existing test files over creating new ones
-   - Test core functionality - minimal, short, and sweet
-   - Don't create new testing patterns - follow existing conventions
-   - Make requests to `gen.pollinations.ai` for production API testing
-
-3. Documentation:
-
-   - Update API docs for new endpoints
-   - Add JSDoc comments for new functions
-   - Update README.md for user-facing changes
-   - **Avoid creating markdown documentation files while working** unless explicitly requested
-   - If temporary files are needed for testing/debugging, create them in a `temp/` folder clearly labeled as temporary
-
-4. Architecture Considerations:
-
-   - Frontend changes should be in pollinations.ai/
-   - Image generation in image.pollinations.ai/
-   - Text generation in text.pollinations.ai/
-   - SDK and React components in packages/sdk/
-   - AI assistant integrations in packages/mcp/
-
-6. Security:
-   - Never expose API keys or secrets
-   - Use environment variables for sensitive data
-   - Implement proper input validation
-
-## Common Tasks
-
-1. Adding New Models:
-
-   - **Text models**: Add config in `text.pollinations.ai/configs/modelConfigs.ts`, add entry in `availableModels.ts`
-   - **Image models**: Add handler in `image.pollinations.ai/src/`, register in `shared/registry/image.ts`
-   - Provider configs (Portkey, Bedrock, OpenAI-compatible) go in `text.pollinations.ai/configs/providerConfigs.js`
-   - Update API documentation and model registry
-
-2. Frontend Updates:
-
-   - Follow React best practices
-   - Use existing UI components
-   - Maintain responsive design
-
-3. API Changes:
-
-   - Maintain backward compatibility
-   - Update documentation
-   - Add appropriate error handling
-
-4. API Documentation Guidelines:
-   - Keep documentation strictly technical and user-focused
-   - Avoid marketing language or promotional content
-   - Link to dynamic endpoints (like /models) rather than hardcoding lists that may change
-   - Don't include internal implementation details or environment variables
-   - Focus on endpoints, parameters, and response formats
-   - For new features, document both simplified endpoints and OpenAI-compatible endpoints
-   - Include minimal, clear code examples that demonstrate basic usage
+- Frontend → `pollinations.ai/`; image → `image.pollinations.ai/`; text → `text.pollinations.ai/`; SDK/React → `packages/sdk/`; MCP → `packages/mcp/`.
+- Text models: add config in `text.pollinations.ai/configs/modelConfigs.ts`, entry in `availableModels.ts`. Provider configs (Portkey/Bedrock/OpenAI-compat) in `text.pollinations.ai/configs/providerConfigs.js`.
+- Image models: handler in `image.pollinations.ai/src/`, register in `shared/registry/image.ts`.
+- Update API docs + model registry for new models.
+- API changes: maintain backward compatibility; document; handle errors.
+- API docs: strictly technical, no marketing; link dynamic endpoints (e.g. `/models`) vs hardcoded lists; no internal impl/env vars; minimal examples for both simplified and OpenAI-compatible endpoints.
+- Security: never expose keys/secrets; use env vars; validate input.
+- Temp scratch files go in `temp/` clearly labeled.
 
 ## Workflow Orchestration
 
-### 1. Plan Mode Default
-- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
-- If something goes sideways, STOP and re-plan immediately – don't keep pushing
-- Use plan mode for verification steps, not just building
-- Write detailed specs upfront to reduce ambiguity
-
-### 2. Subagent Strategy
-- Use subagents liberally to keep main context window clean
-- Offload research, exploration, and parallel analysis to subagents
-- For complex problems, throw more compute at it via subagents
-- One task per subagent for focused execution
-
-### 3. Self-Improvement Loop
-- After ANY correction from the user: propose an update to this `AGENTS.md` with the learned pattern
-- Write rules for yourself that prevent the same mistake
-- Ruthlessly iterate on these lessons until mistake rate drops
-- Review AGENTS.md at session start for relevant project
-
-### 4. Verification Before Done
-- Never mark a task complete without proving it works
-- Diff behavior between main and your changes when relevant
-- Ask yourself: "Would a staff engineer approve this?"
-- Run tests, check logs, demonstrate correctness
-
-### 5. Demand Elegance (Balanced)
-- For non-trivial changes: pause and ask "is there a more elegant way?"
-- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
-- Skip this for simple, obvious fixes – don't over-engineer
-- Challenge your own work before presenting it
-
-### 6. Autonomous Bug Fixing
-- When given a bug report: just fix it. Don't ask for hand-holding
-- Point at logs, errors, failing tests – then resolve them
-- Zero context switching required from the user
-- Go fix failing CI tests without being told how
+- Plan mode for any non-trivial task (3+ steps or architectural). If things go sideways, STOP and re-plan. Write specs upfront.
+- Use subagents liberally for research, exploration, parallel analysis — one task per subagent.
+- After user correction: propose an AGENTS.md update capturing the pattern; iterate until mistake rate drops.
+- Never mark complete without proving it works — run tests, check logs, diff vs main when relevant.
+- Non-trivial changes: ask "is there a more elegant way?" If fix feels hacky, redo elegantly. Skip for obvious fixes.
+- Bug reports: just fix them — point at logs/errors/failing tests and resolve. Fix failing CI without being asked how.
 
 ## Task Management
 
-1. **Plan First**: Outline steps before implementing (use todo tools or plan mode)
-2. **Verify Plan**: Check in before starting implementation
-3. **Track Progress**: Mark items complete as you go
-4. **Explain Changes**: High-level summary at each step
-5. **Capture Lessons**: When corrected, update this AGENTS.md with the pattern to prevent recurrence
+1. Plan first (todos or plan mode). 2. Verify plan before implementing. 3. Track progress. 4. Summarize changes. 5. Capture lessons in AGENTS.md.
 
 ## Compact Instructions
 
-When compacting conversation context, preserve:
-- Full list of modified files with paths and line numbers
-- All code snippets, diffs, and implementation details
-- Test output, error messages, and command results
-- Complete task plan, progress, and pending items
-- User preferences and corrections from this session
-- Key architectural decisions and their rationale
+Preserve during compaction: modified files + line numbers, all code/diffs/impl details, test output + errors + command results, full plan + progress + pending, user preferences/corrections this session, architectural decisions + rationale.
 
 ## Core Principles
 
-- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
-- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
-- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
+- Simplicity first — minimal code impact.
+- No laziness — find root causes, no temp fixes, senior standards.
+- Minimal impact — touch only what's necessary.
 
-# Git Workflow
+## Git Workflow
 
-- If the user asks to send to git or something similar do all these steps:
-- Git status, diff, create branch, commit all, push and write a PR description
-- **Verify branch before committing**: Run `git branch --show-current` and confirm with user if unsure — branch mix-ups have caused wasted work multiple times
-- **Avoid force pushes**: Prefer follow-up commits over `git push --force` or `--force-with-lease`. Force pushes rewrite history and can cause issues for others working on the same branch.
-- **Run biome check before committing**: `npx biome check --write <file>` to fix formatting/linting issues
-- **If PR was already merged**: Open a new branch/PR for follow-up changes, don't try to push to merged branches
+- "send to git" = git status, diff, branch, commit all, push, PR description.
+- Verify branch: `git branch --show-current` and confirm if unsure (branch mix-ups are a recurring mistake).
+- Avoid force pushes (`--force`, `--force-with-lease`) — prefer follow-up commits.
+- Run biome check before committing.
+- If PR already merged: open a new branch/PR for follow-ups.
 
 ## Communication Style
 
-**BE CONCISE. All PRs, comments, issues: bullet points, <200 words, NO FLUFF.**
+Be concise. PRs/comments/issues: bullets, <200 words, no fluff.
 
-**PR Format:**
-- Use "- Adds X", "- Fix Y" format
-- 3-5 bullets max
-- Simple titles: "fix:", "feat:", "Add"
-- No long paragraphs, no marketing language
-
-**Issue Comments:**
-- Bullet points only
-- State facts, not opinions
-- Link to relevant code/files
-- No "I think" or "maybe" - be direct
-
-**Code Reviews:**
-- Focus on parts that need improving, not what's already good
-- Be concise and information-dense
-- Link to specific lines/files
-- Don't praise code that's fine
-- Don't repeat obvious things
+- PRs: "- Adds X", "- Fix Y"; 3-5 bullets; titles "fix:"/"feat:"/"Add"; no marketing.
+- Issue comments: bullets only; facts not opinions; link code; be direct (no "I think"/"maybe").
+- Code reviews: focus on what needs improving; link specific lines; don't praise fine code or repeat obvious things.
 
 ## GitHub Labels
 
-- Only use established labels (check with `mcp1_list_issues`)
-- Avoid creating new labels unless part of broader strategy
-- Keep names consistent with existing patterns
+Only use established labels (check with `mcp1_list_issues`). Don't create new labels ad-hoc; keep names consistent.
 
 ## Contributor Attribution
 
-**Commit format:**
-
+Commit format:
 ```
 feat: add feature
 
 Co-authored-by: username <user_id+username@users.noreply.github.com>
 Fixes #issue
 ```
 
-- Use "Fixes #issue" or "Addresses #issue" in PR descriptions
-- Email format: `{username} <{user_id}+{username}@users.noreply.github.com>`
-- Find user_id in issue API response
+- Use "Fixes #issue" or "Addresses #issue" in PRs.
+- Email: `{username} <{user_id}+{username}@users.noreply.github.com>` (user_id from issue API).
PATCH

echo "Gold patch applied."
