#!/usr/bin/env bash
set -euo pipefail

cd /workspace/electric

# Idempotent: skip if already applied
if grep -q 'v1.0.13+ UPGRADE' AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply changes using Python for better control
python3 << 'PYEOF'
import os
import re
import json

# 1. Update AGENTS.md
with open("AGENTS.md", "r") as f:
    content = f.read()
content = content.replace(
    "3. **Local dev slow shapes** - HTTP/1.1 6-connection limit. Fix: HTTP/2 proxy (Caddy/nginx) or Electric Cloud ([Electric][18])",
    "3. **Local dev slow shapes** - Fixed by default in `@electric-sql/client` v1.0.13+ UPGRADE!"
)
with open("AGENTS.md", "w") as f:
    f.write(content)
print("Updated AGENTS.md")

# 2. Delete Caddyfile from burn example
if os.path.exists("examples/burn/Caddyfile"):
    os.remove("examples/burn/Caddyfile")
    print("Deleted examples/burn/Caddyfile")

# 3. Update burn README.md
with open("examples/burn/README.md", "r") as f:
    content = f.read()
# Remove caddy plugin lines
content = content.replace(
    "# `asdf plugin add <name> <git-url> if you don't have the dependency plugin already, e.g.:\n# asdf plugin add caddy https://github.com/salasrod/asdf-caddy.git\n",
    ""
)
# Replace Caddy section
content = content.replace(
    """In a different terminal start Caddy (this proxies port `4001` to Phoenix running on `4000`):

```sh
caddy start
```

Open [localhost:4001](http://localhost:4001) in your web browser.""",
    "Open [localhost:4000](http://localhost:4000) in your web browser."
)
with open("examples/burn/README.md", "w") as f:
    f.write(content)
print("Updated examples/burn/README.md")

# 4. Update burn package.json
with open("examples/burn/assets/package.json", "r") as f:
    pkg = json.load(f)
pkg["dependencies"]["@electric-sql/client"] = "^1.0.13"
with open("examples/burn/assets/package.json", "w") as f:
    f.write(json.dumps(pkg, indent=2) + "\n")
print("Updated examples/burn/assets/package.json")

# 5. Update tanstack README.md
with open("examples/tanstack-db-web-starter/README.md", "r") as f:
    content = f.read()
content = content.replace(
    "This starts the dev server, Docker Compose (Postgres + Electric), and Caddy automatically.",
    "This starts the dev server and Docker Compose (Postgres + Electric) automatically."
)
content = content.replace(
    "Open [https://tanstack-start-db-electric-starter.localhost](https://tanstack-start-db-electric-starter.localhost)",
    "Open [http://localhost:5173](http://localhost:5173)"
)
# Remove Caddy prerequisites section
caddy_section = """This project uses [Docker](https://www.docker.com), [Node](https://nodejs.org/en) with [pnpm](https://pnpm.io) and [Caddy](https://caddyserver.com/). You can see compatible versions in the `.tool-versions` file.

### Docker

Make sure you have Docker running. Docker is used to run the Postgres and Electric services defined in `docker-compose.yaml`.

### Caddy

#### Why Caddy?

Electric SQL's shape delivery benefits significantly from **HTTP/2 multiplexing**. Without HTTP/2, each shape subscription creates a new HTTP/1.1 connection, which browsers limit to 6 concurrent connections per domain. This creates a bottleneck that makes shapes appear slow.

Caddy provides HTTP/2 support with automatic HTTPS, giving you:

- **Faster shape loading** - Multiple shapes load concurrently over a single connection
- **Better development experience** - No connection limits or artificial delays
- **Production-like performance** - Your local dev mirrors production HTTP/2 behavior

The Vite development server runs on HTTP/1.1 only, so Caddy acts as a reverse proxy to upgrade the connection.

#### Setup

Once you've [installed Caddy](https://caddyserver.com/docs/install), install its root certificate using:

```sh
caddy trust
```

This is necessary for HTTP/2 to work [without SSL warnings/errors in the browser](https://caddyserver.com/docs/command-line#caddy-trust).

#### How It Works

- Caddy auto-starts via a Vite plugin when you run `pnpm dev`
- The `Caddyfile` is automatically generated with your project name
- Your app is available at `https://<project-name>.localhost`
- Direct access to `http://localhost:5173` still works but will be slower for Electric shapes

#### Troubleshooting Caddy

If Caddy fails to start:

1. **Test Caddy manually:**

   ```sh
   caddy start
   ```

2. **Check certificate trust:**

   ```sh
   caddy trust
   # To remove later: caddy untrust
   ```

3. **Verify Caddyfile was generated:**
   Look for a `Caddyfile` in your project root after running `pnpm dev`

4. **Stop conflicting Caddy instances:**

   ```sh
   caddy stop
   ```

5. **Check for port conflicts:**
   Caddy needs ports 80 and 443 available

"""
new_prereqs = """This project uses [Docker](https://www.docker.com) and [Node](https://nodejs.org/en) with [pnpm](https://pnpm.io). You can see compatible versions in the `.tool-versions` file.

### Docker

Make sure you have Docker running. Docker is used to run the Postgres and Electric services defined in `docker-compose.yaml`.

"""
content = content.replace(caddy_section, new_prereqs)
# Update troubleshooting table
caddy_table = """| Issue                    | Symptoms                                   | Solution                                                           |
| ------------------------ | ------------------------------------------ | ------------------------------------------------------------------ |
| **Docker not running**   | `docker compose ps` shows nothing          | Start Docker Desktop/daemon                                        |
| **Caddy not trusted**    | SSL warnings in browser                    | Run `caddy trust` (see Caddy section below)                        |
| **Port conflicts**       | Postgres (54321) or Electric (3000) in use | Stop conflicting services or change ports in `docker-compose.yaml` |
| **Missing .env**         | Database connection errors                 | Copy `.env.example` to `.env`                                      |
| **Caddy fails to start** | `Caddy exited with code 1`                 | Run `caddy start` manually to see the error                        |"""
new_table = """| Issue                  | Symptoms                                   | Solution                                                           |
| ---------------------- | ------------------------------------------ | ------------------------------------------------------------------ |
| **Docker not running** | `docker compose ps` shows nothing          | Start Docker Desktop/daemon                                        |
| **Port conflicts**     | Postgres (54321) or Electric (3000) in use | Stop conflicting services or change ports in `docker-compose.yaml` |
| **Missing .env**       | Database connection errors                 | Copy `.env.example` to `.env`                                      |"""
content = content.replace(caddy_table, new_table)
# Remove caddy from debugging commands
content = content.replace(
    "# Check Caddy status\ncaddy start\n",
    ""
)
with open("examples/tanstack-db-web-starter/README.md", "w") as f:
    f.write(content)
print("Updated examples/tanstack-db-web-starter/README.md")

# 6. Update tanstack package.json
with open("examples/tanstack-db-web-starter/package.json", "r") as f:
    pkg = json.load(f)
pkg["dependencies"]["@electric-sql/client"] = "^1.0.13"
with open("examples/tanstack-db-web-starter/package.json", "w") as f:
    f.write(json.dumps(pkg, indent=2) + "\n")
print("Updated examples/tanstack-db-web-starter/package.json")

# 7. Delete vite-plugin-caddy.ts
if os.path.exists("examples/tanstack-db-web-starter/src/vite-plugin-caddy.ts"):
    os.remove("examples/tanstack-db-web-starter/src/vite-plugin-caddy.ts")
    print("Deleted examples/tanstack-db-web-starter/src/vite-plugin-caddy.ts")

# 8. Update vite.config.ts
with open("examples/tanstack-db-web-starter/vite.config.ts", "r") as f:
    content = f.read()
content = content.replace('import { caddyPlugin } from "./src/vite-plugin-caddy"\n', "")
content = content.replace(
    """const config = defineConfig({
  server: {
    host: true,
  },
  plugins: [
    // this is the plugin that enables path aliases
    viteTsConfigPaths({
      projects: [`./tsconfig.json`],
    }),
    // Local HTTPS with Caddy
    caddyPlugin(),
    tailwindcss(),""",
    """const config = defineConfig({
  plugins: [
    // this is the plugin that enables path aliases
    viteTsConfigPaths({
      projects: [`./tsconfig.json`],
    }),
    tailwindcss(),"""
)
with open("examples/tanstack-db-web-starter/vite.config.ts", "w") as f:
    f.write(content)
print("Updated examples/tanstack-db-web-starter/vite.config.ts")

# 9. Update troubleshooting.md
with open("website/docs/guides/troubleshooting.md", "r") as f:
    content = f.read()
content = content.replace("Luckily, HTTP/2", "HTTP/2")
content = content.replace("##### Solution &mdash; run Caddy", "##### Solution &mdash; subdomain sharding")
# Replace the entire Caddy solution section
old_caddy = """To fix this, you can setup a local reverse-proxy using the popular [Caddy server](https://caddyserver.com). Caddy automatically sets up HTTP/2 and proxies requests to Electric, getting around the 6 requests limitation with HTTP/1.1 in the browser.

1. Install Caddy for your OS — https://caddyserver.com/docs/install
2. Run `caddy trust` so Caddy can install its certificate into your OS. This is necessary for http/2 to Just Work™ without SSL warnings/errors in your browser — https://caddyserver.com/docs/command-line#caddy-trust

Note — it's really important you run Caddy directly from your computer and not in e.g. a Docker container as otherwise, Caddy won't be able to use http/2 and will fallback to http/1 defeating the purpose of using it!

Once you have Caddy installed and have added its certs — you can run this command to start Caddy listening on port 3001 and proxying shape requests to Electric on port 3000. If you're loading shapes through your API or framework dev server, replace `3000` with the port that your API or dev server is listening on. The browser should talk directly to Caddy.

```sh
caddy run \\
    --config - \\
    --adapter caddyfile \\
    <<EOF
localhost:3001 {
  reverse_proxy localhost:3000
  encode {
    gzip
  }
}
EOF
```

Now change your shape URLs in your frontend code to use port `3001` instead of port 3000 and everything will run much faster 🚀"""
new_sharding = """As of version 1.0.13, the Electric TypeScript client automatically solves this problem using subdomain sharding. This assigns each shape a unique subdomain (e.g., `a7f2c.localhost`). This bypasses the browser's HTTP/1.1 connection limits.

Subdomain sharding is enabled by default for `localhost` and `*.localhost` URLs, so if you're running Electric (or your local API / proxy in front of it) on localhost, shapes will now be fast out of the box with no additional setup required.

If you're using a custom domain in development, you can explicitly enable subdomain sharding:

```ts
import { ShapeStream } from '@electric-sql/client'

const stream = new ShapeStream({
  url: 'http://example-dev-domain:3000/v1/shape',
  shardSubdomain: 'always' // Enable subdomain sharding for all hosts
})
```

If you're using an older version of `@electric-sql/client` (before 1.0.13) then you should upgrade to get subdomain sharding.

If you're using a custom client or otherwise need a different solution, you can run a reverse proxy, such as [Caddy](https://caddyserver.com) that supports HTTP/2. The Vite development server also supports running in HTTP/2 mode."""
content = content.replace(old_caddy, new_sharding)
with open("website/docs/guides/troubleshooting.md", "w") as f:
    f.write(content)
print("Updated website/docs/guides/troubleshooting.md")

# 10. Update pnpm-lock.yaml - carefully handle the resolution section
with open("pnpm-lock.yaml", "r") as f:
    content = f.read()

# Define the correct resolution for @electric-sql/client@1.0.13
correct_hash = "sha512-bx+Obm4EpkZRVpN48kUg9Q2u9H0zTh/wnM4R0LVtoa5Nl/axDq/uL6ZpmhCwo+Y377oln4l4YNyok/wxNkOeqA=="

# Replace ALL @electric-sql/client resolution entries with a single correct one
# First, find and replace the entire packages section for @electric-sql/client
# The pattern needs to match from "  '@electric-sql/client@X.Y.Z':" to the next blank line or next package

# Replace all versions with 1.0.13 in importers
content = re.sub(r"specifier: \^1\.0\.(?:7|11)\n", "specifier: ^1.0.13\n", content)
content = re.sub(r"version: 1\.0\.(?:7|11)\n", "version: 1.0.13\n", content)

# Update all package references in snapshots to use @electric-sql/client@1.0.13
content = re.sub(r"@electric-sql/client@1\.0\.(?:7|11)", "@electric-sql/client@1.0.13", content)

# Now handle the packages section - remove all @electric-sql/client entries and add one correct one
# First, let's remove duplicate @electric-sql/client@1.0.13 entries
pattern = r"(  '@electric-sql/client@1\.0\.13':\n    resolution: \{integrity: [^}]+\}\n)\n+(  '@electric-sql/client@1\.0\.13':\n    resolution: \{integrity: [^}]+\}\n)*"
replacement = r"  '@electric-sql/client@1.0.13':\n    resolution: {integrity: sha512-bx+Obm4EpkZRVpN48kUg9Q2u9H0zTh/wnM4R0LVtoa5Nl/axDq/uL6ZpmhCwo+Y377oln4l4YNyok/wxNkOeqA==}\n\n"
content = re.sub(pattern, replacement, content)

with open("pnpm-lock.yaml", "w") as f:
    f.write(content)

# Now run pnpm install to fix any remaining issues
print("Running pnpm install to regenerate lockfile...")
PYEOF

# Install pnpm and run install to fix the lockfile
npm install -g pnpm 2>/dev/null
cd /workspace/electric

# Run pnpm install to update the lockfile properly
pnpm install --no-frozen-lockfile 2>&1 | grep -E "(Lockfile|Already|added|packages)" || true

echo "Patch applied successfully."
