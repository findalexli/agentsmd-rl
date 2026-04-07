#!/usr/bin/env bash
set -euo pipefail

cd /workspace/electric

# Idempotent: skip if already applied
if grep -q 'v1.0.13+ UPGRADE' AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index b62034269a..b312913349 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -197,7 +197,7 @@ shapeOptions: {

 1. **Use latest packages** - Check npm for `@electric-sql/*` & `@tanstack/*-db`
 2. **txid handshake required** - Prevents UI flicker when optimistic→synced state
-3. **Local dev slow shapes** - HTTP/1.1 6-connection limit. Fix: HTTP/2 proxy (Caddy/nginx) or Electric Cloud ([Electric][18])
+3. **Local dev slow shapes** - Fixed by default in `@electric-sql/client` v1.0.13+ UPGRADE!
 4. **Proxy must forward headers/params** - Preserve Electric query params
 5. **Parse custom types:**
 ```ts
diff --git a/examples/burn/Caddyfile b/examples/burn/Caddyfile
deleted file mode 100644
index a1627bce0c..0000000000
--- a/examples/burn/Caddyfile
+++ /dev/null
@@ -1,9 +0,0 @@
-localhost:4001 {
-	reverse_proxy localhost:4000
-	encode {
-		gzip
-	}
-	header {
-		Vary "Authorization"
-	}
-}
diff --git a/examples/burn/README.md b/examples/burn/README.md
index 1e9c80eb84..a251dca6aa 100644
--- a/examples/burn/README.md
+++ b/examples/burn/README.md
@@ -157,8 +157,6 @@ Some aspects of the demo app are simplified or not-yet implemented.
 Install the system dependencies in the electric repo root using [asdf](https://asdf-vm.com):

 ```sh
-# `asdf plugin add <name> <git-url> if you don't have the dependency plugin already, e.g.:
-# asdf plugin add caddy https://github.com/salasrod/asdf-caddy.git
 cd ../..
 asdf install
 ```
@@ -189,13 +187,7 @@ Start the Phoenix server:
 mix phx.server
 ```

-In a different terminal start Caddy (this proxies port `4001` to Phoenix running on `4000`):
-
-```sh
-caddy start
-```
-
-Open [localhost:4001](http://localhost:4001) in your web browser.
+Open [localhost:4000](http://localhost:4000) in your web browser.

 ## More info

diff --git a/examples/burn/assets/package.json b/examples/burn/assets/package.json
index ec23e2a5e7..94980de947 100644
--- a/examples/burn/assets/package.json
+++ b/examples/burn/assets/package.json
@@ -16,7 +16,7 @@
     "typecheck": "tsc -b"
   },
   "dependencies": {
-    "@electric-sql/client": "^1.0.7",
+    "@electric-sql/client": "^1.0.13",
     "@fontsource/open-sauce-one": "^5.2.5",
     "@griffel/react": "^1.5.30",
     "@radix-ui/react-icons": "^1.3.2",
diff --git a/examples/tanstack-db-web-starter/README.md b/examples/tanstack-db-web-starter/README.md
index f09c766631..a4c5325ff6 100644
--- a/examples/tanstack-db-web-starter/README.md
+++ b/examples/tanstack-db-web-starter/README.md
@@ -35,7 +35,7 @@ Follow these steps in order for a smooth first-time setup:
    pnpm run dev
    ```

-   This starts the dev server, Docker Compose (Postgres + Electric), and Caddy automatically.
+   This starts the dev server and Docker Compose (Postgres + Electric) automatically.

 3. **Run database migrations** (in a new terminal):

@@ -44,7 +44,7 @@ Follow these steps in order for a smooth first-time setup:
    ```

 4. **Visit the application:**
-   Open [https://tanstack-start-db-electric-starter.localhost](https://tanstack-start-db-electric-starter.localhost)
+   Open [http://localhost:5173](http://localhost:5173)

 If you run into issues, see the [pre-reqs](#pre-requisites) and [troubleshooting](#common-pitfalls) sections below.

@@ -214,83 +214,21 @@ That's it! Your new table is now fully integrated with Electric sync, tRPC mutat

 ## Pre-requisites

-This project uses [Docker](https://www.docker.com), [Node](https://nodejs.org/en) with [pnpm](https://pnpm.io) and [Caddy](https://caddyserver.com/). You can see compatible versions in the `.tool-versions` file.
+This project uses [Docker](https://www.docker.com) and [Node](https://nodejs.org/en) with [pnpm](https://pnpm.io). You can see compatible versions in the `.tool-versions` file.

 ### Docker

 Make sure you have Docker running. Docker is used to run the Postgres and Electric services defined in `docker-compose.yaml`.

-### Caddy
-
-#### Why Caddy?
-
-Electric SQL's shape delivery benefits significantly from **HTTP/2 multiplexing**. Without HTTP/2, each shape subscription creates a new HTTP/1.1 connection, which browsers limit to 6 concurrent connections per domain. This creates a bottleneck that makes shapes appear slow.
-
-Caddy provides HTTP/2 support with automatic HTTPS, giving you:
-
-- **Faster shape loading** - Multiple shapes load concurrently over a single connection
-- **Better development experience** - No connection limits or artificial delays
-- **Production-like performance** - Your local dev mirrors production HTTP/2 behavior
-
-The Vite development server runs on HTTP/1.1 only, so Caddy acts as a reverse proxy to upgrade the connection.
-
-#### Setup
-
-Once you've [installed Caddy](https://caddyserver.com/docs/install), install its root certificate using:
-
-```sh
-caddy trust
-```
-
-This is necessary for HTTP/2 to work [without SSL warnings/errors in the browser](https://caddyserver.com/docs/command-line#caddy-trust).
-
-#### How It Works
-
-- Caddy auto-starts via a Vite plugin when you run `pnpm dev`
-- The `Caddyfile` is automatically generated with your project name
-- Your app is available at `https://<project-name>.localhost`
-- Direct access to `http://localhost:5173` still works but will be slower for Electric shapes
-
-#### Troubleshooting Caddy
-
-If Caddy fails to start:
-
-1. **Test Caddy manually:**
-
-   ```sh
-   caddy start
-   ```
-
-2. **Check certificate trust:**
-
-   ```sh
-   caddy trust
-   # To remove later: caddy untrust
-   ```
-
-3. **Verify Caddyfile was generated:**
-   Look for a `Caddyfile` in your project root after running `pnpm dev`
-
-4. **Stop conflicting Caddy instances:**
-
-   ```sh
-   caddy stop
-   ```
-
-5. **Check for port conflicts:**
-   Caddy needs ports 80 and 443 available
-
 ## Troubleshooting

 ### Common Pitfalls

-| Issue                    | Symptoms                                   | Solution                                                           |
-| ------------------------ | ------------------------------------------ | ------------------------------------------------------------------ |
-| **Docker not running**   | `docker compose ps` shows nothing          | Start Docker Desktop/daemon                                        |
-| **Caddy not trusted**    | SSL warnings in browser                    | Run `caddy trust` (see Caddy section below)                        |
-| **Port conflicts**       | Postgres (54321) or Electric (3000) in use | Stop conflicting services or change ports in `docker-compose.yaml` |
-| **Missing .env**         | Database connection errors                 | Copy `.env.example` to `.env`                                      |
-| **Caddy fails to start** | `Caddy exited with code 1`                 | Run `caddy start` manually to see the error                        |
+| Issue                  | Symptoms                                   | Solution                                                           |
+| ---------------------- | ------------------------------------------ | ------------------------------------------------------------------ |
+| **Docker not running** | `docker compose ps` shows nothing          | Start Docker Desktop/daemon                                        |
+| **Port conflicts**     | Postgres (54321) or Electric (3000) in use | Stop conflicting services or change ports in `docker-compose.yaml` |
+| **Missing .env**       | Database connection errors                 | Copy `.env.example` to `.env`                                      |

 ### Debugging Commands

@@ -305,9 +243,6 @@ docker compose logs -f electric postgres

 # Test database connectivity
 psql $DATABASE_URL -c "SELECT 1"
-
-# Check Caddy status
-caddy start
 ```

 ## Building For Production
diff --git a/examples/tanstack-db-web-starter/package.json b/examples/tanstack-db-web-starter/package.json
index 9a4dc8ef6c..7d3a22a02d 100644
--- a/examples/tanstack-db-web-starter/package.json
+++ b/examples/tanstack-db-web-starter/package.json
@@ -17,7 +17,7 @@
     "format:check": "prettier --check ."
   },
   "dependencies": {
-    "@electric-sql/client": "^1.0.11",
+    "@electric-sql/client": "^1.0.13",
     "@tailwindcss/vite": "^4.0.6",
     "@tanstack/electric-db-collection": "^0.1.23",
     "@tanstack/react-db": "^0.1.21",
diff --git a/examples/tanstack-db-web-starter/src/vite-plugin-caddy.ts b/examples/tanstack-db-web-starter/src/vite-plugin-caddy.ts
deleted file mode 100644
index 681bfe37a0..0000000000
--- a/examples/tanstack-db-web-starter/src/vite-plugin-caddy.ts
+++ /dev/null
@@ -1,215 +0,0 @@
-import { spawn, type ChildProcess } from "child_process"
-import { writeFileSync } from "fs"
-import { readFileSync } from "fs"
-import { networkInterfaces } from "os"
-import type { Plugin } from "vite"
-
-interface CaddyPluginOptions {
-  host?: string
-  encoding?: boolean
-  autoStart?: boolean
-  configPath?: string
-}
-
-export function caddyPlugin(options: CaddyPluginOptions = {}): Plugin {
-  const {
-    host = "localhost",
-    encoding = true,
-    autoStart = true,
-    configPath = "Caddyfile",
-  } = options
-
-  let caddyProcess: ChildProcess | null = null
-  let vitePort: number | undefined
-  let caddyStarted = false
-
-  const generateCaddyfile = (projectName: string, vitePort: number) => {
-    // Get network IP for network access
-    const nets = networkInterfaces()
-    let networkIP = "192.168.1.1" // fallback
-
-    for (const name of Object.keys(nets)) {
-      const netInterfaces = nets[name]
-      if (netInterfaces) {
-        for (const net of netInterfaces) {
-          if (net.family === "IPv4" && !net.internal) {
-            networkIP = net.address
-            break
-          }
-        }
-      }
-    }
-
-    const config = `${projectName}.localhost {
-  reverse_proxy ${host}:${vitePort}${
-    encoding
-      ? `
-  encode {
-    gzip
-  }`
-      : ""
-  }
-}
-
-# Network access
-${networkIP} {
-  reverse_proxy ${host}:${vitePort}${
-    encoding
-      ? `
-  encode {
-    gzip
-  }`
-      : ""
-  }
-}
-`
-    return config
-  }
-
-  const startCaddy = (configPath: string) => {
-    if (caddyProcess) {
-      return
-    }
-
-    caddyProcess = spawn("caddy", ["run", "--config", configPath], {
-      // stdio: "inherit",
-      // shell: true,
-    })
-
-    caddyProcess.on("error", (error) => {
-      console.error("Failed to start Caddy:", error.message)
-    })
-
-    caddyProcess.on("exit", (code) => {
-      if (code !== 0 && code !== null) {
-        console.error(`Caddy exited with code ${code}`)
-      }
-      caddyProcess = null
-    })
-
-    // Handle process cleanup
-    const cleanup = () => {
-      if (caddyProcess && !caddyProcess.killed) {
-        caddyProcess.kill("SIGTERM")
-        // Force kill if it doesn't terminate gracefully
-        setTimeout(() => {
-          if (caddyProcess && !caddyProcess.killed) {
-            caddyProcess.kill("SIGKILL")
-            process.exit()
-          } else {
-            process.exit()
-          }
-        }, 1000)
-      }
-    }
-
-    process.on("SIGINT", cleanup)
-    process.on("SIGTERM", cleanup)
-    process.on("exit", cleanup)
-  }
-
-  const stopCaddy = () => {
-    if (caddyProcess && !caddyProcess.killed) {
-      caddyProcess.kill("SIGTERM")
-      // Force kill if it doesn't terminate gracefully
-      setTimeout(() => {
-        if (caddyProcess && !caddyProcess.killed) {
-          caddyProcess.kill("SIGKILL")
-        }
-      }, 3000)
-      caddyProcess = null
-    }
-  }
-
-  const startCaddyIfReady = (projectName: string) => {
-    if (autoStart && vitePort && !caddyStarted) {
-      caddyStarted = true
-      // Generate Caddyfile
-      const caddyConfig = generateCaddyfile(projectName, vitePort)
-      writeFileSync(configPath, caddyConfig)
-      // Start Caddy
-      startCaddy(configPath)
-    }
-  }
-
-  return {
-    name: "vite-plugin-caddy",
-    configureServer(server) {
-      let projectName = "app"
-
-      // Get project name from package.json
-      try {
-        const packageJsonContent = readFileSync(
-          process.cwd() + "/package.json",
-          "utf8"
-        )
-        const packageJson = JSON.parse(packageJsonContent)
-        projectName = packageJson.name || "app"
-      } catch (_error) {
-        console.warn(
-          'Could not read package.json for project name, using "app"'
-        )
-      }
-
-      // Override Vite's printUrls function
-      server.printUrls = function () {
-        // Get network IP
-        const nets = networkInterfaces()
-        let networkIP = "192.168.1.1" // fallback
-
-        for (const name of Object.keys(nets)) {
-          const netInterfaces = nets[name]
-          if (netInterfaces) {
-            for (const net of netInterfaces) {
-              if (net.family === "IPv4" && !net.internal) {
-                networkIP = net.address
-                break
-              }
-            }
-          }
-        }
-
-        console.log()
-        console.log(`  ➜  Local:   https://${projectName}.localhost/`)
-        console.log(`  ➜  Network: https://${networkIP}/`)
-        console.log(`  ➜  press h + enter to show help`)
-        console.log()
-      }
-
-      server.middlewares.use((_req, _res, next) => {
-        if (!vitePort && server.config.server.port) {
-          vitePort = server.config.server.port
-          startCaddyIfReady(projectName)
-        }
-        next()
-      })
-
-      const originalListen = server.listen
-      server.listen = function (port?: number, ...args: unknown[]) {
-        if (port) {
-          vitePort = port
-        }
-
-        const result = originalListen.call(this, port, ...args)
-
-        // Try to start Caddy after server is listening
-        if (result && typeof result.then === "function") {
-          result.then(() => {
-            // Check if we now have a port from the server
-            if (!vitePort && server.config.server.port) {
-              vitePort = server.config.server.port
-            }
-            startCaddyIfReady(projectName)
-          })
-        } else {
-          startCaddyIfReady(projectName)
-        }
-
-        return result
-      }
-    },
-    buildEnd() {
-      stopCaddy()
-    },
-  }
-}
diff --git a/examples/tanstack-db-web-starter/vite.config.ts b/examples/tanstack-db-web-starter/vite.config.ts
index 93f4d84236..aa5ae45937 100644
--- a/examples/tanstack-db-web-starter/vite.config.ts
+++ b/examples/tanstack-db-web-starter/vite.config.ts
@@ -3,19 +3,13 @@ import { tanstackStart } from "@tanstack/react-start/plugin/vite"
 import viteReact from "@vitejs/plugin-react"
 import viteTsConfigPaths from "vite-tsconfig-paths"
 import tailwindcss from "@tailwindcss/vite"
-import { caddyPlugin } from "./src/vite-plugin-caddy"

 const config = defineConfig({
-  server: {
-    host: true,
-  },
   plugins: [
     // this is the plugin that enables path aliases
     viteTsConfigPaths({
       projects: [`./tsconfig.json`],
     }),
-    // Local HTTPS with Caddy
-    caddyPlugin(),
     tailwindcss(),
     // TanStack Start must come before viteReact
     tanstackStart({
diff --git a/pnpm-lock.yaml b/pnpm-lock.yaml
index 18b780920f..393f482043 100644
--- a/pnpm-lock.yaml
+++ b/pnpm-lock.yaml
@@ -1090,14 +1090,14 @@ importers:
   examples/tanstack-db-web-starter:
     dependencies:
       '@electric-sql/client':
-        specifier: ^1.0.11
-        version: 1.0.11
+        specifier: ^1.0.13
+        version: 1.0.13
       '@tailwindcss/vite':
         specifier: ^4.0.6
         version: 4.1.11(vite@7.1.7(jiti@2.5.1)(lightningcss@1.30.1)(terser@5.44.0)(tsx@4.20.3)(yaml@2.6.0))
       '@tanstack/electric-db-collection':
         specifier: ^0.1.23
-        version: 0.1.23(@electric-sql/client@1.0.11)(typescript@5.7.2)
+        version: 0.1.23(@electric-sql/client@1.0.13)(typescript@5.7.2)
       '@tanstack/react-db':
         specifier: ^0.1.21
         version: 0.1.21(react@19.1.1)(typescript@5.7.2)
@@ -3178,8 +3178,8 @@ packages:
   '@electric-sql/client@1.0.0-beta.3':
     resolution: {integrity: sha512-x3bzYlX+IRwBAILPxzu3ARkXzmrAQtVOuJCKCxlSqENuJa4zvLPF4f8vC6HMOiiJiHPAntJjfI3Hb0lrt2PTxA==}

-  '@electric-sql/client@1.0.11':
-    resolution: {integrity: sha512-dbToMzqVKanBdm2SB4P6Oi3S80bTbLgReUcWUEUMhAUOeZ3IwQaaS1KTpekQxbMWfuy9Cv9FlFs7Y7uZA0+zug==}
+  '@electric-sql/client@1.0.13':
+    resolution: {integrity: sha512-bx+Obm4EpkZRVpN48kUg9Q2u9H0zTh/wnM4R0LVtoa5Nl/axDq/uL6ZpmhCwo+Y377oln4l4YNyok/wxNkOeqA==}

   '@electric-sql/client@1.0.7':
     resolution: {integrity: sha512-w9geRoZL1gn294Nn68YxicRvWFJEXWYPr+jZubSOyjaSa6tVQJk0rjYuFmOwpQyudFQrsL17HFrGga9UOaBhdA==}
@@ -14772,7 +14772,7 @@ snapshots:

   '@babel/helper-annotate-as-pure@7.27.3':
     dependencies:
-      '@babel/types': 7.28.2
+      '@babel/types': 7.28.4

   '@babel/helper-compilation-targets@7.25.9':
     dependencies:
@@ -15000,7 +15000,7 @@ snapshots:
   '@babel/helper-simple-access@7.25.9':
     dependencies:
       '@babel/traverse': 7.28.0
-      '@babel/types': 7.26.0
+      '@babel/types': 7.28.4
     transitivePeerDependencies:
       - supports-color

@@ -15759,7 +15759,7 @@ snapshots:
       '@babel/helper-module-imports': 7.27.1
       '@babel/helper-plugin-utils': 7.27.1
       '@babel/plugin-syntax-jsx': 7.27.1(@babel/core@7.28.0)
-      '@babel/types': 7.28.2
+      '@babel/types': 7.28.4
     transitivePeerDependencies:
       - supports-color

@@ -16520,7 +16520,7 @@ snapshots:
     optionalDependencies:
       '@rollup/rollup-darwin-arm64': 4.24.4

-  '@electric-sql/client@1.0.11':
+  '@electric-sql/client@1.0.13':
     dependencies:
       '@microsoft/fetch-event-source': 2.0.1(patch_hash=lgwcujj3mimdfutlwueisfm32u)
     optionalDependencies:
@@ -19566,9 +19566,9 @@ snapshots:
     transitivePeerDependencies:
       - supports-color

-  '@tanstack/electric-db-collection@0.1.23(@electric-sql/client@1.0.11)(typescript@5.7.2)':
+  '@tanstack/electric-db-collection@0.1.23(@electric-sql/client@1.0.13)(typescript@5.7.2)':
     dependencies:
-      '@electric-sql/client': 1.0.11
+      '@electric-sql/client': 1.0.13
       '@standard-schema/spec': 1.0.0
       '@tanstack/db': 0.3.2(typescript@5.7.2)
       '@tanstack/store': 0.7.7
@@ -21474,7 +21474,7 @@ snapshots:
   babel-plugin-jest-hoist@29.6.3:
     dependencies:
       '@babel/template': 7.27.2
-      '@babel/types': 7.28.2
+      '@babel/types': 7.28.4
       '@types/babel__core': 7.20.5
       '@types/babel__traverse': 7.20.6

@@ -24583,7 +24583,7 @@ snapshots:
   istanbul-lib-instrument@5.2.1:
     dependencies:
       '@babel/core': 7.28.0
-      '@babel/parser': 7.28.0
+      '@babel/parser': 7.28.4
       '@istanbuljs/schema': 0.1.3
       istanbul-lib-coverage: 3.2.2
       semver: 6.3.1
@@ -25411,7 +25411,7 @@ snapshots:

   metro-file-map@0.82.5:
     dependencies:
-      debug: 4.4.1
+      debug: 4.4.3
       fb-watchman: 2.0.2
       flow-enums-runtime: 0.0.6
       graceful-fs: 4.2.11
@@ -25466,7 +25466,7 @@ snapshots:
   metro-transform-plugins@0.82.5:
     dependencies:
       '@babel/core': 7.28.0
-      '@babel/generator': 7.28.0
+      '@babel/generator': 7.28.3
       '@babel/template': 7.27.2
       '@babel/traverse': 7.28.0
       flow-enums-runtime: 0.0.6
@@ -25477,9 +25477,9 @@ snapshots:
   metro-transform-worker@0.82.5:
     dependencies:
       '@babel/core': 7.28.0
-      '@babel/generator': 7.28.0
-      '@babel/parser': 7.28.0
-      '@babel/types': 7.28.2
+      '@babel/generator': 7.28.3
+      '@babel/parser': 7.28.4
+      '@babel/types': 7.28.4
       flow-enums-runtime: 0.0.6
       metro: 0.82.5
       metro-babel-transformer: 0.82.5
@@ -26078,7 +26078,7 @@ snapshots:
       '@next/env': 14.2.17
       '@swc/helpers': 0.5.5
       busboy: 1.6.0
-      caniuse-lite: 1.0.30001743
+      caniuse-lite: 1.0.30001677
       graceful-fs: 4.2.11
       postcss: 8.4.31
       react: 19.1.1
diff --git a/website/docs/guides/troubleshooting.md b/website/docs/guides/troubleshooting.md
index e5b1ee64fc..f3f0e84cad 100644
--- a/website/docs/guides/troubleshooting.md
+++ b/website/docs/guides/troubleshooting.md
@@ -21,34 +21,28 @@ Sometimes people encounter a mysterious slow-down with Electric in local develop

 With HTTP/1.1, browsers only allow 6 simultaneous requests to a specific backend. This is because each HTTP/1.1 request uses its own expensive TCP connection. As shapes are loaded over HTTP, this means only 6 shapes can be getting updates with HTTP/1.1 due to this browser restriction. All other requests pause until there's an opening.

-Luckily, HTTP/2, introduced in 2015, fixes this problem by _multiplexing_ each request to a server over the same TCP connection. This allows essentially unlimited connections. HTTP/2 is standard across the vast majority of hosts now. Unfortunately it's not yet standard in local dev environments.
+HTTP/2, introduced in 2015, fixes this problem by _multiplexing_ each request to a server over the same TCP connection. This allows essentially unlimited connections. HTTP/2 is standard across the vast majority of hosts now. Unfortunately it's not yet standard in local dev environments.

-##### Solution &mdash; run Caddy
+##### Solution &mdash; subdomain sharding

-To fix this, you can setup a local reverse-proxy using the popular [Caddy server](https://caddyserver.com). Caddy automatically sets up HTTP/2 and proxies requests to Electric, getting around the 6 requests limitation with HTTP/1.1 in the browser.
+As of version 1.0.13, the Electric TypeScript client automatically solves this problem using subdomain sharding. This assigns each shape a unique subdomain (e.g., `a7f2c.localhost`). This bypasses the browser's HTTP/1.1 connection limits.

-1. Install Caddy for your OS — https://caddyserver.com/docs/install
-2. Run `caddy trust` so Caddy can install its certificate into your OS. This is necessary for http/2 to Just Work™ without SSL warnings/errors in your browser — https://caddyserver.com/docs/command-line#caddy-trust
+Subdomain sharding is enabled by default for `localhost` and `*.localhost` URLs, so if you're running Electric (or your local API / proxy in front of it) on localhost, shapes will now be fast out of the box with no additional setup required.

-Note — it's really important you run Caddy directly from your computer and not in e.g. a Docker container as otherwise, Caddy won't be able to use http/2 and will fallback to http/1 defeating the purpose of using it!
+If you're using a custom domain in development, you can explicitly enable subdomain sharding:

-Once you have Caddy installed and have added its certs — you can run this command to start Caddy listening on port 3001 and proxying shape requests to Electric on port 3000. If you're loading shapes through your API or framework dev server, replace `3000` with the port that your API or dev server is listening on. The browser should talk directly to Caddy.
+```ts
+import { ShapeStream } from '@electric-sql/client'

-```sh
-caddy run \
-    --config - \
-    --adapter caddyfile \
-    <<EOF
-localhost:3001 {
-  reverse_proxy localhost:3000
-  encode {
-    gzip
-  }
-}
-EOF
+const stream = new ShapeStream({
+  url: 'http://example-dev-domain:3000/v1/shape',
+  shardSubdomain: 'always' // Enable subdomain sharding for all hosts
+})
 ```

-Now change your shape URLs in your frontend code to use port `3001` instead of port 3000 and everything will run much faster
+If you're using an older version of `@electric-sql/client` (before 1.0.13) then you should upgrade to get subdomain sharding.
+
+If you're using a custom client or otherwise need a different solution, you can run a reverse proxy, such as [Caddy](https://caddyserver.com) that supports HTTP/2. The Vite development server also supports running in HTTP/2 mode.

 ### Shape logs &mdash; how do I clear the server state?

PATCH

echo "Patch applied successfully."
