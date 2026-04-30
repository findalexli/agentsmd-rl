#!/usr/bin/env bash
set -euo pipefail

cd /workspace/crawlchat

# Idempotency guard
if grep -qF "docker exec crawlchat-local-database-1 mongosh --eval 'db.getSiblingDB(\"crawlcha" "skills/claw/setup-collection/SKILL.md" && grep -qF "skills/claw/setup-collection/setup-collection.md" "skills/claw/setup-collection/setup-collection.md" && grep -qF "- **Login page crashes with \"RESEND_KEY must be set\"**: Ensure `SELF_HOSTED=true" "skills/claw/setup-dev/SKILL.md" && grep -qF "skills/claw/setup-dev/setup-dev.md" "skills/claw/setup-dev/setup-dev.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/claw/setup-collection/SKILL.md b/skills/claw/setup-collection/SKILL.md
@@ -0,0 +1,138 @@
+---
+name: crawlchat-setup-collection
+description: |
+  CrawlChat knowledge collection creation and syncing.
+  Use when:
+  - Creating knowledge collections (web sources)
+  - Debugging MongoDB/pgvector/embedding issues
+  - Troubleshooting source-sync OOM or connection pool errors
+---
+
+# CrawlChat Knowledge Collection Setup Guide
+
+This guide covers creating and syncing a knowledge collection (web source) in CrawlChat.
+
+## Prerequisites
+
+Follow setup-dev skill first to have the dev server running.
+
+## Create a Knowledge Group
+
+### 1. Navigate to Knowledge page
+
+Open: http://localhost:5173/knowledge
+
+### 2. Create a new group
+
+Click **"Add group"** and fill in:
+
+- **Name:** Docs (or your preferred name)
+- **URL:** https://docs.crawlchat.app (or your target website)
+- **Source Type:** Web
+
+Click **"Create"** to add the group.
+
+### 3. Start fetching
+
+On the knowledge page, find your group and click **"Refetch it"** to start crawling.
+
+---
+
+## Common Issues & Fixes
+
+### Issue 1: MongoDB Unique Constraint Error
+
+**Error:**
+```
+PrismaClientKnownRequestError: Unique constraint failed on the constraint: `ScrapeItem_knowledgeGroupId_sourcePageId_key`
+```
+
+**Fix:** Drop the unique index from MongoDB:
+
+```bash
+docker exec crawlchat-local-database-1 mongosh --eval 'db.getSiblingDB("crawlchat").getCollection("ScrapeItem").dropIndex("ScrapeItem_knowledgeGroupId_sourcePageId_key")'
+```
+
+### Issue 2: Source-sync OOM / Connection Pool Exhausted
+
+**Symptoms:**
+- `sorry, too many clients already` (pgvector)
+- Process killed by OOM killer
+
+**Fix:** Reduce worker concurrency in `source-sync/src/worker.ts`:
+
+```typescript
+// Change from:
+concurrency: 4,
+
+// To:
+concurrency: 1,
+```
+
+### Issue 3: OpenRouter API Key Missing
+
+**Error:** Embedding API calls fail
+
+**Fix:** Add your OpenRouter API key to `.env`:
+
+```
+OPENROUTER_API_KEY=sk-or-v1-your-key-here
+```
+
+Get a free key from: https://openrouter.ai
+
+### Issue 4: Embedding API Response Error
+
+**Error:**
+```
+Cannot read properties of undefined (reading '0')
+```
+
+**Cause:** The embedding API response validation is missing in `packages/indexer/src/earth-indexer.ts`.
+
+**Fix:** Add null-safe check in `makeEmbedding()`:
+
+```typescript
+const data = await response.json();
+if (!data?.data?.[0]?.embedding) {
+  throw new Error(`Embedding API error: ${JSON.stringify(data)}`);
+}
+return data.data[0].embedding;
+```
+
+---
+
+## Useful Commands
+
+### Check embeddings in pgvector
+
+```bash
+docker exec crawlchat-local-pgvector-1 psql -U postgres -d crawlchat -c "SELECT COUNT(*) FROM earth_embeddings;"
+```
+
+### Restart dev server
+
+```bash
+cd /root/.openclaw/workspace/crawlchat
+pkill -9 -f "tsx"
+npm run dev:core
+```
+
+### Restart only front (if server crashes)
+
+```bash
+cd /root/.openclaw/workspace/crawlchat/front
+npm run dev
+```
+
+---
+
+## Troubleshooting
+
+| Symptom | Solution |
+|---------|----------|
+| "too many clients already" pgvector | Restart pgvector: `docker restart crawlchat-local-pgvector-1` |
+| OOM kills processes | Reduce concurrency to 1, or run only needed services |
+| Frontend not loading | Check port 5173, try `fuser -k 5173/tcp` to free port |
+| Login page crashes | Ensure `SELF_HOSTED=true` in `.env` |
+| Magic link not working | Check server logs for the link URL |
diff --git a/skills/claw/setup-collection/setup-collection.md b/skills/claw/setup-collection/setup-collection.md

diff --git a/skills/claw/setup-dev/SKILL.md b/skills/claw/setup-dev/SKILL.md
@@ -0,0 +1,152 @@
+---
+name: crawlchat-setup-dev
+description: |
+  CrawlChat development server setup, login flow, and troubleshooting.
+  Use when:
+  - Starting/stopping the CrawlChat dev environment
+  - Logging in with magic links during development
+  - Debugging common dev issues (ports, MongoDB, Redis)
+  - Following best practices (browser size, git branches)
+---
+
+# CrawlChat Dev Server Setup Guide
+
+## Prerequisites
+
+- MongoDB running on port 27017 (with replicaSet rs0)
+- Redis running on port 6379
+- Node.js 22+
+
+## Steps to Start Dev Server
+
+### 1. Kill any existing processes on port 3000
+
+```bash
+lsof -ti:3000 | xargs -r kill -9
+```
+
+### 2. Start the dev server
+
+```bash
+cd /root/.openclaw/workspace/crawlchat
+npm run dev:core
+```
+
+This runs:
+- Frontend on `http://localhost:5173/`
+- Server on `http://localhost:3000/`
+- Source-sync on `http://localhost:3007/`
+
+**Note:** If you get `EADDRINUSE: address already in use :::3000`, kill the process first using step 1.
+
+### 3. Create the .env file (if missing)
+
+```bash
+cp .env.example .env
+```
+
+### 4. Configure default indexer and signup plan
+
+Edit `.env`:
+
+```env
+DEFAULT_INDEXER=earth
+DEFAULT_SIGNUP_PLAN_ID=accelerate-yearly
+```
+
+### 5. Restart the dev server to apply .env changes
+
+```bash
+# Kill the running dev server (Ctrl+C or pkill)
+pkill -9 -f "node.*crawlchat"
+pkill -9 -f "turbo"
+
+# Restart
+npm run dev:core
+```
+
+---
+
+## Login Flow (Magic Link)
+
+### 1. Navigate to login page
+
+Open: http://localhost:5173/login
+
+### 2. Enter email and click Login
+
+Enter `test@test.com` (or any email) in the email field.
+
+### 3. Find the magic link in server logs
+
+The magic link will be logged to the terminal where `npm run dev:core` is running:
+
+```
+Send email {
+  to: 'test@test.com',
+  subject: 'Login to CrawlChat',
+  text: '...http://localhost:5173/login/verify?token=U2FsdGVkX...'
+}
+```
+
+### 4. Visit the magic link
+
+Open the URL from the logs in your browser to complete login.
+
+---
+
+## Useful Commands
+
+### Check if MongoDB is running
+
+```bash
+pgrep -la mongod
+# Should show: mongod --replSet rs0 --bind_ip_all --noauth
+```
+
+### Kill all dev processes
+
+```bash
+pkill -9 -f "node.*crawlchat"
+pkill -9 -f "turbo"
+```
+
+### Set browser to desktop 16:9 size (1920x1080)
+
+```bash
+# Using OpenClaw browser control
+browser act --profile openclaw --request '{"kind": "resize", "width": 1920, "height": 1080}'
+```
+
+---
+
+## Troubleshooting
+
+- **Login page crashes with "RESEND_KEY must be set"**: Ensure `SELF_HOSTED=true` is in `.env` (copied from `.env.example`)
+- **Port 3000 already in use**: Kill the existing process first
+- **Redis connection error**: Ensure Redis is running on `redis://localhost:6379`
+
+---
+
+## Best Practices
+
+### Browser Resolution
+- Always use browser in desktop 16:9 resolution (1920x1080) for consistent UI testing:
+
+```bash
+browser act --profile openclaw --request '{"kind": "resize", "width": 1920, "height": 1080}'
+```
+
+### UI Changes & Screenshots
+- When making UI-related changes, always include browser screenshots in:
+  - Pull requests
+  - Chat discussions for review
+
+### Git Branching
+- Always create new branches from `main` unless a specific feature branch is required:
+
+```bash
+git checkout main
+git pull main
+git checkout -b feature/your-feature-name
+```
diff --git a/skills/claw/setup-dev/setup-dev.md b/skills/claw/setup-dev/setup-dev.md

PATCH

echo "Gold patch applied."
