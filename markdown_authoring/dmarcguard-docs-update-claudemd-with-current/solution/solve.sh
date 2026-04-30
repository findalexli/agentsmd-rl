#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dmarcguard

# Idempotency guard
if grep -qF "| Flag                                 | Env Var                                " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -4,7 +4,7 @@ A Go application that fetches DMARC reports from IMAP mailboxes, parses them, an
 
 ## Tech Stack
 
-- **Backend**: Go 1.25+ (see go.mod for exact version)
+- **Backend**: Go 1.25.4 (see go.mod for exact version)
 - **Frontend**: Vue.js 3 with Vite
 - **Database**: SQLite (supports both CGO and pure-Go variants)
 - **Package Manager**: Bun (for frontend)
@@ -51,11 +51,17 @@ parse-dmarc/
 │   ├── main.js                # Vue entry point
 │   ├── assets/
 │   │   └── base.css           # Base styles
+│   ├── stores/                # Pinia-like state management
+│   │   ├── index.js           # Store exports
+│   │   ├── theme.js           # Theme (dark/light/system) store
+│   │   └── settings.js        # API endpoint settings store
 │   └── components/
 │       ├── dashboard/
 │       │   ├── DashboardHero.vue   # Dashboard header/hero section
 │       │   ├── RecentReports.vue   # Recent reports list
 │       │   └── ReportDrawer.vue    # Report detail drawer
+│       ├── settings/
+│       │   └── SettingsModal.vue   # Settings modal (theme, API endpoint)
 │       └── tools/
 │           └── DnsGenerator.vue    # DMARC DNS record generator
 ├── public/                    # Static frontend assets (favicons, logos)
@@ -65,6 +71,7 @@ parse-dmarc/
 │   ├── captain-definition     # CapRover deployment
 │   ├── digitalocean/          # DigitalOcean Droplet/Marketplace
 │   │   ├── packer.pkr.hcl     # Packer image build
+│   │   ├── marketplace.yaml   # DO Marketplace metadata
 │   │   └── scripts/           # Setup scripts
 │   └── dokploy/               # Dokploy deployment
 │       ├── template.toml
@@ -77,6 +84,9 @@ parse-dmarc/
 ├── Dockerfile                 # Multi-stage Docker build
 ├── compose.yml                # Docker Compose for local dev
 ├── parse-dmarc.service        # systemd service file
+├── zeabur.yml                 # Zeabur deployment template
+├── render.yaml                # Render deployment config
+├── Northflank.json            # Northflank deployment config
 ├── ROADMAP.md                 # Product roadmap
 ├── CONTRIBUTING.md            # Contribution guidelines
 ├── .goreleaser.yml            # Release automation
@@ -112,6 +122,9 @@ just clean
 
 # Install binary to /usr/local/bin
 just install
+
+# Update Zeabur template
+just update-zeabur-template
 ```
 
 ## Building
@@ -170,19 +183,25 @@ go test -v ./internal/parser/...
 
 ## CLI Flags
 
-| Flag                   | Env Var                          | Description                               |
-| ---------------------- | -------------------------------- | ----------------------------------------- |
-| `--config, -c`         | `PARSE_DMARC_CONFIG`             | Config file path (default: config.json)   |
-| `--gen-config`         | `PARSE_DMARC_GEN_CONFIG`         | Generate sample config                    |
-| `--fetch-once`         | `PARSE_DMARC_FETCH_ONCE`         | Fetch reports once and exit               |
-| `--serve-only`         | `PARSE_DMARC_SERVE_ONLY`         | Dashboard only, no fetching               |
-| `--fetch-interval`     | `PARSE_DMARC_FETCH_INTERVAL`     | Fetch interval in seconds (default: 300)  |
-| `--metrics`            | `PARSE_DMARC_METRICS`            | Enable Prometheus metrics (default: true) |
-| `--mcp`                | `PARSE_DMARC_MCP`                | Run as MCP server over stdio              |
-| `--mcp-http`           | `PARSE_DMARC_MCP_HTTP`           | Run MCP over HTTP at address              |
-| `--mcp-oauth`          | `PARSE_DMARC_MCP_OAUTH`          | Enable OAuth2 for MCP HTTP                |
-| `--mcp-oauth-issuer`   | `PARSE_DMARC_MCP_OAUTH_ISSUER`   | OAuth2/OIDC issuer URL                    |
-| `--mcp-oauth-audience` | `PARSE_DMARC_MCP_OAUTH_AUDIENCE` | Expected token audience                   |
+| Flag                                 | Env Var                                        | Description                                           |
+| ------------------------------------ | ---------------------------------------------- | ----------------------------------------------------- |
+| `--config, -c`                       | `PARSE_DMARC_CONFIG`                           | Config file path (default: config.json)               |
+| `--gen-config`                       | `PARSE_DMARC_GEN_CONFIG`                       | Generate sample config                                |
+| `--fetch-once`                       | `PARSE_DMARC_FETCH_ONCE`                       | Fetch reports once and exit                           |
+| `--serve-only`                       | `PARSE_DMARC_SERVE_ONLY`                       | Dashboard only, no fetching                           |
+| `--fetch-interval`                   | `PARSE_DMARC_FETCH_INTERVAL`                   | Fetch interval in seconds (default: 300)              |
+| `--metrics`                          | `PARSE_DMARC_METRICS`                          | Enable Prometheus metrics (default: true)             |
+| `--mcp`                              | `PARSE_DMARC_MCP`                              | Run as MCP server over stdio                          |
+| `--mcp-http`                         | `PARSE_DMARC_MCP_HTTP`                         | Run MCP over HTTP at address                          |
+| `--mcp-oauth`                        | `PARSE_DMARC_MCP_OAUTH`                        | Enable OAuth2 for MCP HTTP                            |
+| `--mcp-oauth-issuer`                 | `PARSE_DMARC_MCP_OAUTH_ISSUER`                 | OAuth2/OIDC issuer URL                                |
+| `--mcp-oauth-audience`               | `PARSE_DMARC_MCP_OAUTH_AUDIENCE`               | Expected token audience                               |
+| `--mcp-oauth-client-id`              | `PARSE_DMARC_MCP_OAUTH_CLIENT_ID`              | OAuth2 client ID for token introspection              |
+| `--mcp-oauth-client-secret`          | `PARSE_DMARC_MCP_OAUTH_CLIENT_SECRET`          | OAuth2 client secret for token introspection          |
+| `--mcp-oauth-scopes`                 | `PARSE_DMARC_MCP_OAUTH_SCOPES`                 | Required scopes (comma-separated, default: mcp:tools) |
+| `--mcp-oauth-introspection-endpoint` | `PARSE_DMARC_MCP_OAUTH_INTROSPECTION_ENDPOINT` | Token introspection endpoint URL                      |
+| `--mcp-oauth-resource-name`          | `PARSE_DMARC_MCP_OAUTH_RESOURCE_NAME`          | Human-readable name for MCP server metadata           |
+| `--mcp-oauth-insecure`               | `PARSE_DMARC_MCP_OAUTH_INSECURE`               | Skip TLS certificate verification (dev only)          |
 
 ## Code Style
 
@@ -207,9 +226,12 @@ go test -v ./internal/parser/...
 ### Frontend
 
 - `src/App.vue` - Main Vue.js dashboard component
+- `src/stores/theme.js` - Theme state management (light/dark/system)
+- `src/stores/settings.js` - API endpoint settings management
 - `src/components/dashboard/DashboardHero.vue` - Statistics overview
 - `src/components/dashboard/RecentReports.vue` - Reports list
 - `src/components/dashboard/ReportDrawer.vue` - Report detail view
+- `src/components/settings/SettingsModal.vue` - Settings dialog (theme, API endpoint)
 - `src/components/tools/DnsGenerator.vue` - DMARC DNS record generator
 
 ## API Endpoints
@@ -274,6 +296,7 @@ The Vue.js dashboard includes:
 - **Report Drawer** - Detailed view of individual reports
 - **Top Sources** - Visualization of top sending source IPs
 - **DMARC DNS Generator** - Interactive tool to generate DMARC DNS TXT records
+- **Settings Modal** - Theme switching (light/dark/system) and custom API endpoint configuration
 
 ## Configuration
 
@@ -327,6 +350,9 @@ See `parse-dmarc.service` for systemd service configuration.
 - **Dokploy**: `deploy/dokploy/` - Docker Compose template
 - **Coolify**: `deploy/coolify.yaml`
 - **CapRover**: `deploy/captain-definition`
+- **Zeabur**: `zeabur.yml` - Zeabur platform template
+- **Render**: `render.yaml` - Render.com configuration
+- **Northflank**: `Northflank.json` - Northflank configuration
 
 ## CI/CD
 
@@ -342,9 +368,9 @@ See `parse-dmarc.service` for systemd service configuration.
 
 See `ROADMAP.md` for the comprehensive product roadmap including:
 
-- **Phase 1**: Delightful Defaults (dark mode, DNS generator ✅, health score, exports)
+- **Phase 1**: Delightful Defaults (dark mode, DNS generator, health score, exports)
 - **Phase 2**: Proactive Intelligence (alerting, trends, GeoIP maps, DNS validator)
-- **Phase 3**: Enterprise Ready (auth, multi-org, RBAC, Prometheus metrics ✅)
+- **Phase 3**: Enterprise Ready (auth, multi-org, RBAC, Prometheus metrics)
 - **Phase 4**: AI-Powered Security (AI assistant, anomaly detection, forensic reports)
 
 ## Contributing
@@ -370,6 +396,13 @@ See `CONTRIBUTING.md` for development setup and contribution guidelines. Key are
 
 The Vue.js frontend is built to `dist/`, copied to `internal/api/dist/`, and embedded via Go's `embed` directive. The binary is self-contained.
 
+### State Management
+
+The frontend uses a custom reactive store pattern (similar to Pinia):
+
+- `theme.js` - Manages light/dark/system theme with localStorage persistence
+- `settings.js` - Manages custom API endpoint with validation and connection testing
+
 ### MCP Integration
 
 The MCP server uses the official `modelcontextprotocol/go-sdk`. It supports:
PATCH

echo "Gold patch applied."
