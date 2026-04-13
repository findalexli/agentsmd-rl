#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trigger.dev

# Idempotent: skip if already applied
if grep -q 'normalizeApiUrlForBuild' packages/cli-v3/src/deploy/buildImage.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fix 1: CONTRIBUTING.md - update build instructions (line 71 and 73)
sed -i '71s/Build the server app/Build everything/' CONTRIBUTING.md
sed -i '73s|pnpm run build --filter webapp|pnpm run build --filter webapp \&\& pnpm run build --filter trigger.dev \&\& pnpm run build --filter @trigger.dev/sdk|' CONTRIBUTING.md

# Fix 2: apps/supervisor/README.md - change "reference" to "test" on line 39
sed -i '39s/reference/test/' apps/supervisor/README.md

# Fix 3: apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts - prefer API_ORIGIN (line 91)
sed -i '91s/processEnv.APP_ORIGIN/processEnv.API_ORIGIN ?? processEnv.APP_ORIGIN/' "apps/webapp/app/routes/api.v1.projects.\$projectRef.\$env.ts"

# Fix 4: packages/cli-v3/src/deploy/buildImage.ts - use normalizeApiUrlForBuild (line 330)
sed -i '330s|TRIGGER_API_URL=\${options.apiUrl}|TRIGGER_API_URL=\${normalizeApiUrlForBuild(options.apiUrl)}|' packages/cli-v3/src/deploy/buildImage.ts

# Append the normalizeApiUrlForBuild function at end of buildImage.ts
cat >> packages/cli-v3/src/deploy/buildImage.ts << 'FUNC'

// If apiUrl is something like http://localhost:3030, AND we are on macOS, we need to convert it to http://host.docker.internal:3030
// this way the indexing will work because the docker image can reach the local server
function normalizeApiUrlForBuild(apiUrl: string) {
  if (process.platform === "darwin") {
    return apiUrl.replace("localhost", "host.docker.internal");
  }

  return apiUrl;
}
FUNC

# Ensure trailing newline
echo "" >> packages/cli-v3/src/deploy/buildImage.ts

echo "Patch applied successfully."
