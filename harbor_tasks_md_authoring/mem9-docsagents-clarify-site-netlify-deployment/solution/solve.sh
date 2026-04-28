#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mem9

# Idempotency guard
if grep -qF "| `site/public/beta/SKILL.md` | **Beta** SKILL.md \u2014 served at `https://mem9.ai/b" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -18,7 +18,7 @@ and a small Astro site.
 | `opencode-plugin/`   | OpenCode plugin (`@mem9/opencode`)                           |
 | `claude-plugin/`     | Claude Code plugin (hooks + skills)                          |
 | `docs/design/`       | Architecture/proposal notes and design drafts                |
-| `site/`              | Astro marketing/docs site                                    |
+| `site/`              | Astro static site — deployed to Netlify from `main` branch   |
 | `e2e/`               | Live end-to-end scripts against a running server             |
 | `k8s/`               | Deployment and gateway manifests                             |
 | `benchmark/MR-NIAH/` | Benchmark harness for OpenClaw memory evaluation             |
@@ -112,6 +112,26 @@ cd server && MNEMO_DSN="user:pass@tcp(host:4000)/db?parseTime=true" go run ./cmd
 | OpenCode wiring      | `opencode-plugin/src/index.ts`              |
 | OpenClaw wiring      | `openclaw-plugin/index.ts`                  |
 | Site copy/content    | `site/src/content/site.ts`                  |
+| Production SKILL.md  | `site/public/SKILL.md`                      |
+| Beta SKILL.md        | `site/public/beta/SKILL.md`                 |
+
+## site/ — Netlify deployment
+
+`/site/` is the deployment directory for the mem9.ai static website.
+It is hosted on Netlify and **automatically deployed from the `main` branch**.
+
+| File | Purpose |
+|---|---|
+| `site/public/SKILL.md` | **Production** SKILL.md — served at `https://mem9.ai/SKILL.md` |
+| `site/public/beta/SKILL.md` | **Beta** SKILL.md — served at `https://mem9.ai/beta/SKILL.md` |
+
+When updating the SKILL.md that agents fetch, edit **only** these two files:
+
+- `site/public/SKILL.md` — production, changes go live within seconds after merging to `main`
+- `site/public/beta/SKILL.md` — beta, same deployment pipeline
+
+Do **not** edit any other copy (e.g. `clawhub-skill/mem9/SKILL.md` has been removed).
+Do **not** manually sync to clawhub — Netlify handles publishing automatically.
 
 ## Hierarchical AGENTS.md files
 
PATCH

echo "Gold patch applied."
