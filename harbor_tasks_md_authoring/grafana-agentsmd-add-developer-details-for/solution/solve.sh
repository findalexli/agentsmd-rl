#!/usr/bin/env bash
set -euo pipefail

cd /workspace/grafana

# Idempotency guard
if grep -qF "These built-in plugins require separate build steps: `azuremonitor`, `cloud-moni" "AGENTS.md" && grep -qF "Use triple backticks with language specifier for code blocks. Introduce each blo" "docs/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,297 +1,135 @@
 # AGENTS.md
 
-<!-- docs-ai-begin -->
+<!-- version: 2.0.0 -->
 
-<!-- version: 1.1.0 -->
+This file provides guidance to AI agents when working with code in the Grafana repository.
 
-## Documentation
+**Directory-scoped agent files exist for specialized areas — read them when working in those directories:**
 
-Instructions for documentation authoring in Markdown files.
+- `docs/AGENTS.md` — Documentation style guide (for work under `docs/`)
+- `public/app/features/alerting/unified/CLAUDE.md` — Alerting squad patterns
 
-DOCS.md contains all the Docs AI toolkit docs in one file.
+## Project Overview
 
-## Role
+Grafana is a monitoring and observability platform. Go backend, TypeScript/React frontend, monorepo with Yarn workspaces (frontend) and Go workspaces (backend).
 
-Act as an experienced software engineer and technical writer for Grafana Labs.
+## Principles
 
-Write for software developers and engineers who understand general programming concepts.
+- Follow existing patterns in the surrounding code
+- Write tests for new functionality
+- Keep changes focused — avoid over-engineering
+- Separate PRs for frontend and backend changes (deployed at different cadences)
+- Security: prevent XSS, SQL injection, command injection
 
-Focus on practical implementation and clear problem-solving guidance.
+## Commands
 
-### Grafana
+### Build & Run
 
-Use full product names on first mention, then short names:
-
-- Grafana Alloy (full), Alloy (short)
-- Grafana Beyla (full), Beyla (short)
-
-Use "OpenTelemetry Collector" on first mention, then "Collector" for subsequent references.
-Keep full name for distributions, headings, and links.
-
-Always use "Grafana Cloud" in full.
-
-Use complete terms:
-
-- "OpenTelemetry" (not "OTel")
-- "Kubernetes" (not "K8s")
-
-Present observability signals in order: metrics, logs, traces, and profiles.
-
-Focus content on Grafana solutions when discussing integrations or migrations.
-
-## Style
-
-### Structure
-
-Structure articles into sections with headings.
-
-Leave Markdown front matter content between two triple dashes `---`.
-
-The front matter YAML `title` and the content h1 (#) heading should be the same.
-Make sure there's an h1 heading in the content; this redundancy is required.
-
-Always include copy after a heading or between headings, for example:
-
-```markdown
-## Heading
-
-Immediately followed by copy and not another heading.
-
-## Sub heading
-```
-
-The immediate copy after a heading should introduce and provide an overview of what's covered in the section.
-
-Start articles with an introduction that covers the goal of the article. Example goals:
-
-- Learn concepts
-- Set up or install something
-- Configure something
-- Use a product to solve a business problem
-- Troubleshoot a problem
-- Integrate with other software or systems
-- Migrate from one thing to another
-- Refer to APIs or reference documentation
-
-Follow the goal with a list of prerequisites, for example:
-
-```markdown
-Before you begin, ensure you have the following:
-
-- <Prerequisite 1>
-- <Prerequisite 2>
-- ...
+```bash
+make run                          # Backend with hot reload (localhost:3000, admin/admin)
+make build-backend                # Backend only
+yarn start                        # Frontend dev server (watches for changes)
+yarn build                        # Frontend production build
 ```
 
-Suggest and link to next steps and related resources at the end of the article, for example:
-
-- Learn more about A, B, C
-- Configure X
-- Use X to achieve Y
-- Use X to achieve Z
-- Project homepage or documentation
-- Project repository (for example, GitHub, GitLab)
-- Project package (for example, pip or NPM)
-
-You don't need to use the "Refer to..." syntax for next steps; use the link text directly.
-
-### Copy
-
-Write simple, direct copy with short sentences and paragraphs.
-
-Use contractions:
-
-- it's, isn't, that's, you're, don't
-
-Choose simple words:
-
-- use (not utilize)
-- help (not assist)
-- show (not demonstrate)
-
-Write with verbs and nouns. Use minimal adjectives except when describing Grafana Labs products.
-
-## Tense
-
-Write in present simple tense.
-
-Avoid present continuous tense.
-
-Only write in future tense to show future actions.
-
-### Voice
-
-Always write in an active voice.
-
-Change passive voice to active voice.
-
-### Perspective
+### Test
 
-Address users as "you".
+```bash
+# Backend
+go test -run TestName ./pkg/services/myservice/   # Specific test
+make test-go-unit                                  # All unit tests
+make test-go-integration                           # Integration tests
 
-Use second person perspective consistently.
+# Frontend
+yarn test path/to/file                             # Specific file
+yarn test -t "pattern"                             # By name pattern
+yarn test -u                                       # Update snapshots
 
-### Wordlist
-
-Use allowlist/blocklist instead of whitelist/blacklist.
-
-Use primary/secondary instead of master/slave.
-
-Use "refer to" instead of "see", "consult", "check out", and other phrases.
-
-### Formatting
-
-Use sentence case for titles and headings.
-
-Use inline Markdown links: [Link text](https://example.com).
-
-Link to other sections using descriptive phrases that include the section name:
-"For setup details, refer to the [Lists](#lists) section."
-
-Bold text with two asterisks: **bold**
-
-Emphasize text with one underscore: _italics_
-
-Format UI elements using sentence case as they appear:
-
-- Click **Submit**.
-- Navigate to **User settings**.
-- Configure **Alerting rules**.
-
-### Lists
-
-Write complete sentences for lists:
-
-- Works with all languages and frameworks (correct)
-- All languages and frameworks (incorrect)
-
-Use dashes for unordered lists.
-
-Bold keywords at list start and follow with a colon.
-
-### Images
-
-Include descriptive alt text that conveys the essential information or purpose.
-
-Write alt text without "Image of..." or "Picture of..." prefixes.
-
-### Code
-
-Use single code backticks for:
-
-- user input
-- placeholders in markdown, for example _`<PLACEHOLDER_NAME>`_
-- files and directories, for example `/opt/file.md`
-- source code keywords and identifiers,
-  for example variables, function and class names
-- configuration options and values, for example `PORT` and `80`
-- status codes, for example `404`
-
-Use triple code backticks followed by the syntax for code blocks, for example:
-
-```javascript
-console.log('Hello World!');
+# E2E
+yarn e2e:playwright path/to/test.spec.ts           # Specific test
 ```
 
-Introduce each code block with a short description.
-End the introduction with a colon if the code sample follows it, for example:
-
-```markdown
-The code sample outputs "Hello World!" to the browser console:
+### Lint & Format
 
-<CODE_BLOCK>
+```bash
+make lint-go                      # Go linter
+yarn lint                         # ESLint
+yarn lint:fix                     # ESLint auto-fix
+yarn prettier:write               # Prettier auto-format
+yarn typecheck                    # TypeScript check
 ```
 
-Use descriptive placeholder names in code samples.
-Use uppercase letters with underscores to separate words in placeholders,
-for example:
+### Code Generation
 
-```sh
-OTEL_RESOURCE_ATTRIBUTES="service.name=<SERVICE_NAME>
-OTEL_EXPORTER_OTLP_ENDPOINT=<OTLP_ENDPOINT>
+```bash
+make gen-go                       # Wire DI (after changing service init)
+make gen-cue                      # CUE schemas (after changing kinds/)
+make gen-apps                     # App SDK apps
+make swagger-gen                  # OpenAPI/Swagger specs
+make gen-feature-toggles          # Feature flags (pkg/services/featuremgmt/)
+make i18n-extract                 # i18n strings
+make update-workspace             # Go workspace (after adding modules)
 ```
 
-The placeholder includes the name and the less than and greater than symbols,
-for example <PLACEHOLDER_NAME>.
-
-If the placeholder is markdown emphasize it with underscores,
-for example _`<PLACEHOLDER_NAME>`_.
-
-In code blocks use the placeholder without additional backticks or emphasis,
-for example <PLACEHOLDER_NAME>.
-
-Provide an explanation for each placeholder,
-typically in the text following the code block or in a configuration section.
-
-Follow code samples with an explanation
-and configuration options for placeholders, for example:
-
-```markdown
-<CODE_BLOCK>
+### Dev Environment
 
-This code sets required environment variables
-to send OTLP data to an OTLP endpoint.
-To configure the code refer to the configuration section.
-
-<CONFIGURATION>
+```bash
+yarn install --immutable                          # Install frontend deps
+make devenv sources=postgres,influxdb,loki        # Start backing services
+make devenv-down                                  # Stop backing services
+make lefthook-install                             # Pre-commit hooks
 ```
 
-Put configuration for a code block after the code block.
-
-## APIs
-
-When documenting API endpoints specify the HTTP method,
-for example `GET`, `POST`, `PUT`, `DELETE`.
-
-Provide the full request path, using backticks.
-
-Use backticks for parameter names and example values.
+## Architecture
 
-Use placeholders like `{userId}` for path parameters, for example:
+### Backend (`pkg/`)
 
-- To retrieve user details, make a `GET` request to `/api/v1/users/{userId}`.
+| Directory         | Purpose                                                     |
+| ----------------- | ----------------------------------------------------------- |
+| `pkg/api/`        | HTTP API handlers and routes                                |
+| `pkg/services/`   | Business logic by domain (alerting, dashboards, auth, etc.) |
+| `pkg/server/`     | Server init and Wire DI setup (`wire.go`)                   |
+| `pkg/tsdb/`       | Time series database query backends                         |
+| `pkg/plugins/`    | Plugin system and loader                                    |
+| `pkg/infra/`      | Logging, metrics, database access                           |
+| `pkg/middleware/` | HTTP middleware                                             |
+| `pkg/setting/`    | Configuration management                                    |
 
-### CLI commands
+**Patterns**: Wire DI (regenerate with `make gen-go`), services implement interfaces in same package, business logic in `pkg/services/<domain>/` not in API handlers, database via `sqlstore`, plugin communication via gRPC/protobuf.
 
-When presenting CLI commands and their output,
-introduce the command with a brief explanation of its purpose.
-Clearly distinguish the command from its output.
+### Frontend (`public/app/`)
 
-For commands, use `sh` to specify the code block language.
+| Directory              | Purpose                                               |
+| ---------------------- | ----------------------------------------------------- |
+| `public/app/core/`     | Shared services, components, utilities                |
+| `public/app/features/` | Feature code by domain (dashboard, alerting, explore) |
+| `public/app/plugins/`  | Built-in plugins (many are Yarn workspaces)           |
+| `public/app/types/`    | TypeScript type definitions                           |
+| `public/app/store/`    | Redux store configuration                             |
 
-For output, use a generic specifier like `text`, `console`,
-or `json`/`yaml` if the output is structured.
+**Patterns**: Redux Toolkit with slices (not old Redux), function components with hooks, Emotion CSS-in-JS via `useStyles2`, RTK Query for data fetching, React Testing Library for tests.
 
-For example:
+### Shared Packages (`packages/`)
 
-```markdown
-To list all running pods in the `default` namespace, use the following command:
+`@grafana/data` (data structures), `@grafana/ui` (components), `@grafana/runtime` (runtime services), `@grafana/schema` (CUE-generated types), `@grafana/scenes` (dashboard framework).
 
-<CODE_BLOCK>
-```
-
-The output will resemble the following:
+### Backend Apps (`apps/`)
 
-```text
-NAME                               READY   STATUS    RESTARTS   AGE
-my-app-deployment-7fdb6c5f65-abcde   1/1     Running   0          2d1h
-another-service-pod-xyz123           2/2     Running   0          5h30m
-```
+Standalone Go apps using Grafana App SDK: `apps/dashboard/`, `apps/folder/`, `apps/alerting/`.
 
-### Shortcodes
+### Plugin Workspaces
 
-Leave Hugo shortcodes in the content when editing.
+These built-in plugins require separate build steps: `azuremonitor`, `cloud-monitoring`, `grafana-postgresql-datasource`, `loki`, `tempo`, `jaeger`, `mysql`, `parca`, `zipkin`, `grafana-pyroscope-datasource`, `grafana-testdata-datasource`.
 
-Use our custom admonition Hugo shortcode for notes, cautions, or warnings,
-with `<TYPE>` as "note", "caution", or "warning":
-
-```markdown
-{{< admonition type="<TYPE>" >}}
-...
-{{< /admonition >}}
-```
+Build a specific plugin: `yarn workspace @grafana-plugins/<name> dev`
 
-Use admonitions sparingly.
-Only include exceptional information in admonitions.
+## Key Notes
 
-<!-- docs-ai-end -->
+- **Wire DI**: Backend service init changes require `make gen-go`. Wire catches circular deps at compile time.
+- **CUE schemas**: Dashboard/panel schemas in `kinds/` generate both Go and TS code via `make gen-cue`.
+- **Feature toggles**: Defined in `pkg/services/featuremgmt/`, auto-generate code. Run `make gen-feature-toggles` after changes.
+- **Go workspace**: Defined in `go.work`. Run `make update-workspace` when adding Go modules.
+- **Build tags**: `oss` (default), `enterprise`, `pro`.
+- **Config**: Defaults in `conf/defaults.ini`, overrides in `conf/custom.ini`.
+- **Database migrations**: Live in `pkg/services/sqlstore/migrations/`. Test with `make devenv sources=postgres_tests,mysql_tests` then `make test-go-integration-postgres`.
+- **CI sharding**: Backend tests use `SHARD`/`SHARDS` env vars for parallelization.
diff --git a/docs/AGENTS.md b/docs/AGENTS.md
@@ -0,0 +1,150 @@
+# Documentation Style Guide for AI Agents
+
+<!-- docs-ai-begin -->
+
+This file provides guidance for AI agents when authoring or editing documentation in the `docs/` directory.
+
+## Role
+
+Act as an experienced software engineer and technical writer for Grafana Labs.
+
+Write for software developers and engineers who understand general programming concepts.
+
+Focus on practical implementation and clear problem-solving guidance.
+
+### Grafana Product Naming
+
+Use full product names on first mention, then short names:
+
+- Grafana Alloy (full), Alloy (short)
+- Grafana Beyla (full), Beyla (short)
+
+Use "OpenTelemetry Collector" on first mention, then "Collector" for subsequent references.
+Keep full name for distributions, headings, and links.
+
+Always use "Grafana Cloud" in full.
+
+Use complete terms:
+
+- "OpenTelemetry" (not "OTel")
+- "Kubernetes" (not "K8s")
+
+Present observability signals in order: metrics, logs, traces, and profiles.
+
+Focus content on Grafana solutions when discussing integrations or migrations.
+
+## Style
+
+### Structure
+
+Structure articles into sections with headings.
+
+Leave Markdown front matter content between two triple dashes `---`.
+
+The front matter YAML `title` and the content h1 (#) heading should be the same.
+Make sure there's an h1 heading in the content; this redundancy is required.
+
+Always include copy after a heading or between headings, for example:
+
+```markdown
+## Heading
+
+Immediately followed by copy and not another heading.
+
+## Sub heading
+```
+
+The immediate copy after a heading should introduce and provide an overview of what's covered in the section.
+
+Start articles with an introduction that covers the goal of the article. Example goals:
+
+- Learn concepts
+- Set up or install something
+- Configure something
+- Use a product to solve a business problem
+- Troubleshoot a problem
+- Integrate with other software or systems
+- Migrate from one thing to another
+- Refer to APIs or reference documentation
+
+Follow the goal with a list of prerequisites, for example:
+
+```markdown
+Before you begin, ensure you have the following:
+
+- <Prerequisite 1>
+- <Prerequisite 2>
+- ...
+```
+
+Suggest and link to next steps and related resources at the end of the article.
+
+### Copy
+
+Write simple, direct copy with short sentences and paragraphs.
+
+Use contractions: it's, isn't, that's, you're, don't.
+
+Choose simple words: use (not utilize), help (not assist), show (not demonstrate).
+
+Write with verbs and nouns. Use minimal adjectives except when describing Grafana Labs products.
+
+### Tense
+
+Write in present simple tense. Avoid present continuous tense. Only use future tense for future actions.
+
+### Voice and Perspective
+
+Always write in active voice. Address users as "you" (second person).
+
+### Wordlist
+
+- Use allowlist/blocklist (not whitelist/blacklist)
+- Use primary/secondary (not master/slave)
+- Use "refer to" (not "see", "consult", "check out")
+
+### Formatting
+
+Use sentence case for titles and headings.
+
+Use inline Markdown links: `[Link text](https://example.com)`.
+
+Bold text with `**bold**`. Emphasize with `_italics_`.
+
+Format UI elements in sentence case as they appear: Click **Submit**.
+
+### Lists
+
+Write complete sentences for list items. Use dashes for unordered lists. Bold keywords at list start and follow with a colon.
+
+### Images
+
+Include descriptive alt text. No "Image of..." or "Picture of..." prefixes.
+
+### Code
+
+Use single backticks for: user input, placeholders (_`<PLACEHOLDER_NAME>`_), files/directories, source code identifiers, config options/values, status codes.
+
+Use triple backticks with language specifier for code blocks. Introduce each block with a short description. Use `UPPER_SNAKE_CASE` for placeholder names in code samples (e.g., `<SERVICE_NAME>`). Provide explanations for all placeholders after the code block.
+
+## APIs
+
+When documenting API endpoints, specify the HTTP method (`GET`, `POST`, `PUT`, `DELETE`). Provide the full request path in backticks. Use `{paramName}` for path parameters.
+
+### CLI Commands
+
+Introduce commands with a brief explanation. Use `sh` for command blocks and `text`/`console`/`json`/`yaml` for output blocks.
+
+### Shortcodes
+
+Leave Hugo shortcodes in content when editing. Use the admonition shortcode for notes/cautions/warnings:
+
+```markdown
+{{< admonition type="note" >}}
+...
+{{< /admonition >}}
+```
+
+Use admonitions sparingly — only for exceptional information.
+
+<!-- docs-ai-end -->
PATCH

echo "Gold patch applied."
