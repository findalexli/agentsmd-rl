#!/usr/bin/env bash
set -euo pipefail

cd /workspace/payload

# Idempotent: skip if already applied
if grep -q 'payload-monorepo' test/docker-compose.yml 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# 1. Delete old per-database docker-compose files
rm -f test/__helpers/shared/db/postgres/docker-compose.yml
rm -f test/__helpers/shared/db/mongodb/docker-compose.yml
rm -f test/__helpers/shared/db/mongodb-atlas/docker-compose.yml
rm -f packages/storage-s3/docker-compose.yml

# 2. Replace package.json docker scripts
python3 -c "
import json, re

with open('package.json', 'r') as f:
    pkg = json.loads(f.read())

scripts = pkg['scripts']

# Remove all old per-database docker scripts
old_keys = [k for k in scripts if re.match(r'docker:(mongodb|postgres|mongodb-atlas):', k)]
for k in old_keys:
    del scripts[k]

# Remove old docker:restart
scripts.pop('docker:restart', None)

# Set new unified scripts
scripts['docker:start'] = 'docker compose -f test/docker-compose.yml --profile all down -v --remove-orphans 2>/dev/null; docker compose -f test/docker-compose.yml --profile all up -d --wait'
scripts['docker:stop'] = 'docker compose -f test/docker-compose.yml --profile all down --remove-orphans'
scripts['docker:test'] = 'pnpm runts test/__helpers/shared/db/mongodb/run-test-connection.ts && pnpm runts test/__helpers/shared/db/mongodb-atlas/run-test-connection.ts'

with open('package.json', 'w') as f:
    json.dump(pkg, f, indent=2)
    f.write('\n')
"

# 3. Write unified test/docker-compose.yml
cat > test/docker-compose.yml <<'COMPOSE'
name: payload-monorepo

# Unified Docker Compose for all Payload test services
#
# Usage:
#   pnpm docker:start  - Start ALL services with fresh data
#   pnpm docker:stop   - Stop all services
#
# Profiles (used by CI to start individual services):
#   --profile all       - Everything
#   --profile postgres  - PostgreSQL only
#   --profile mongodb   - MongoDB + mongot only
#   --profile mongodb-atlas - MongoDB Atlas Local only
#   --profile storage   - LocalStack (S3), Azure Storage, fake GCS

services:
  # ── PostgreSQL (PostGIS + pgvector) ──────────────────────────
  # Connection: postgres://payload:payload@localhost:5433/payload
  postgres:
    profiles: [all, postgres]
    image: ghcr.io/payloadcms/postgis-vector:latest
    container_name: postgres-payload-test
    ports:
      - '5433:5432'
    environment:
      POSTGRES_USER: payload
      POSTGRES_PASSWORD: payload
      POSTGRES_DB: payload
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U payload -d payload']
      interval: 1s
      timeout: 5s
      retries: 30
      start_period: 2s
    restart: unless-stopped

  # ── MongoDB Community 8.2 (replica set + search) ────────────
  # Connection: mongodb://payload:payload@localhost:27018/payload?authSource=admin&directConnection=true&replicaSet=rs0
  mongodb:
    profiles: [all, mongodb]
    image: mongodb/mongodb-community-server:8.2-ubi9
    container_name: mongodb-payload-test
    ports:
      - '27018:27017'
    volumes:
      - mongodb_data:/data/db
      - mongodb_configdb:/data/configdb
      - ./__helpers/shared/db/mongodb/keyfile:/etc/mongodb/keyfile:ro
      - ./__helpers/shared/db/mongodb/docker-compose-entrypoint.sh:/docker-compose-entrypoint.sh:ro
    entrypoint: ['/bin/bash', '/docker-compose-entrypoint.sh']
    healthcheck:
      test:
        [
          'CMD',
          'mongosh',
          '-u',
          'admin',
          '-p',
          'adminPassword',
          '--authenticationDatabase',
          'admin',
          '--eval',
          "db.adminCommand('ping')",
        ]
      interval: 2s
      timeout: 5s
      retries: 30
      start_period: 5s
    restart: unless-stopped

  # mongot - MongoDB Community Search for $search and $vectorSearch
  mongot:
    profiles: [all, mongodb]
    image: mongodb/mongodb-community-search:latest
    container_name: mongot-payload-test
    depends_on:
      mongodb:
        condition: service_healthy
    volumes:
      - mongot_data:/var/lib/mongot
      - ./__helpers/shared/db/mongodb/mongot-config.yml:/etc/mongot/config-readonly.yml:ro
      - ./__helpers/shared/db/mongodb/passwordFile:/etc/mongot/secrets/passwordFile-readonly:ro
    entrypoint: ['/bin/sh', '-c']
    command:
      - |
        cp /etc/mongot/config-readonly.yml /var/lib/mongot/config.yml
        cp /etc/mongot/secrets/passwordFile-readonly /var/lib/mongot/passwordFile
        chmod 400 /var/lib/mongot/passwordFile
        sed -i 's|/etc/mongot/secrets/passwordFile|/var/lib/mongot/passwordFile|g' /var/lib/mongot/config.yml
        /mongot-community/mongot --config /var/lib/mongot/config.yml
    healthcheck:
      test: ['CMD-SHELL', 'curl -sf http://localhost:8080/health || exit 1']
      interval: 2s
      timeout: 5s
      retries: 60
      start_period: 5s
    restart: unless-stopped

  # ── MongoDB Atlas Local (all-in-one with Atlas Search) ──────
  # Connection: mongodb://localhost:27019/payload?directConnection=true&replicaSet=mongodb-atlas-local
  mongodb-atlas:
    profiles: [all, mongodb-atlas]
    image: mongodb/mongodb-atlas-local:latest
    container_name: mongodb-atlas-payload-test
    hostname: mongodb-atlas-local
    ports:
      - '27019:27017'
    volumes:
      - mongodb_atlas_data:/data/db
      - mongodb_atlas_configdb:/data/configdb
    environment:
      - MONGODB_INITDB_ROOT_USERNAME=
      - MONGODB_INITDB_ROOT_PASSWORD=
    healthcheck:
      test: ['CMD', 'mongosh', '--eval', "db.adminCommand('ping')"]
      interval: 2s
      timeout: 5s
      retries: 30
      start_period: 5s
    restart: unless-stopped

  # ── LocalStack (S3 emulator) ────────────────────────────────
  localstack:
    profiles: [all, storage]
    image: localstack/localstack:latest
    container_name: localstack_demo
    ports:
      - '4563-4599:4563-4599'
      - '8055:8080'
    environment:
      - SERVICES=s3
      - DEBUG=1
      - DATA_DIR=/tmp/localstack/data
    volumes:
      - localstack_data:/var/lib/localstack
      - '/var/run/docker.sock:/var/run/docker.sock'

  # ── Azure Storage (Azurite emulator) ────────────────────────
  azure-storage:
    profiles: [all, storage]
    image: mcr.microsoft.com/azure-storage/azurite:latest
    platform: linux/amd64
    restart: always
    command: 'azurite --loose --blobHost 0.0.0.0 --tableHost 0.0.0.0 --queueHost 0.0.0.0 --skipApiVersionCheck'
    ports:
      - '10000:10000'
      - '10001:10001'
      - '10002:10002'
    volumes:
      - azurestoragedata:/data

  # ── Google Cloud Storage (fake-gcs-server) ──────────────────
  google-cloud-storage:
    profiles: [all, storage]
    image: fsouza/fake-gcs-server
    restart: always
    command:
      [
        '-scheme',
        'http',
        '-port',
        '4443',
        '-public-host',
        'http://localhost:4443',
        '-external-url',
        'http://localhost:4443',
        '-backend',
        'memory',
      ]
    ports:
      - '4443:4443'
    volumes:
      - google_cloud_storage_data:/data

volumes:
  postgres_data:
  mongodb_data:
  mongodb_configdb:
  mongot_data:
  mongodb_atlas_data:
  mongodb_atlas_configdb:
  localstack_data:
  azurestoragedata:
  google_cloud_storage_data:
COMPOSE

# 4. Update CI action to use unified compose file
sed -i 's|docker compose -f test/__helpers/shared/db/mongodb/docker-compose.yml up -d --wait|docker compose -f test/docker-compose.yml --profile mongodb up -d --wait|' .github/actions/start-database/action.yml
sed -i 's|docker compose -f test/__helpers/shared/db/mongodb-atlas/docker-compose.yml up -d --wait|docker compose -f test/docker-compose.yml --profile mongodb-atlas up -d --wait|' .github/actions/start-database/action.yml
sed -i 's|docker compose -f test/__helpers/shared/db/postgres/docker-compose.yml up -d --wait|docker compose -f test/docker-compose.yml --profile postgres up -d --wait|' .github/actions/start-database/action.yml

# 5. Update CLAUDE.md — replace docker:restart with docker:test
sed -i "s|pnpm docker:stop\` / \`pnpm docker:restart\`|pnpm docker:stop\` / \`pnpm docker:test\`|" CLAUDE.md

# 6. Update CONTRIBUTING.md — replace per-DB docker section with unified commands
python3 << 'PYEOF'
import re

with open("CONTRIBUTING.md", "r") as f:
    content = f.read()

old_block = """Then use Docker to start your database.

On MacOS, the easiest way to install Docker is to use brew. Simply run `pnpm install --cask docker`, open the docker desktop app, apply the recommended settings and you're good to go.

### PostgreSQL

```bash
pnpm docker:postgres:start         # Start (persists data)
pnpm docker:postgres:restart:clean # Start fresh (removes data)
pnpm docker:postgres:stop          # Stop
```

URL: `postgres://payload:payload@127.0.0.1:5433/payload`

### MongoDB (with vector search)

```bash
pnpm docker:mongodb:start          # Start (persists data)
pnpm docker:mongodb:restart:clean  # Start fresh (removes data)
pnpm docker:mongodb:stop           # Stop
```

URL: `mongodb://payload:payload@localhost:27018/payload?authSource=admin&directConnection=true&replicaSet=rs0`

### MongoDB Atlas Local

```bash
pnpm docker:mongodb-atlas:start         # Start (persists data)
pnpm docker:mongodb-atlas:restart:clean # Start fresh (removes data)
pnpm docker:mongodb-atlas:stop          # Stop
```

URL: `mongodb://localhost:27019/payload?directConnection=true&replicaSet=mongodb-atlas-local` (no auth required)

### SQLite

SQLite databases don't require Docker - they're stored as files in the project."""

new_block = """Then use Docker to start your databases and storage emulators.

On MacOS, the easiest way to install Docker is to use brew. Simply run `brew install --cask docker`, open the docker desktop app, apply the recommended settings and you're good to go.

```bash
pnpm docker:start  # Start all services (PostgreSQL, MongoDB, storage emulators) with fresh data
pnpm docker:stop   # Stop all services
pnpm docker:test   # Test database connections
```

Every `docker:start` automatically removes old data and starts fresh, so you always get a clean environment.

All services are defined in a single `test/docker-compose.yml` using Docker Compose profiles (`postgres`, `mongodb`, `mongodb-atlas`, `storage`, `all`).

**Connection URLs:**

| Database            | URL                                                                                                       |
| ------------------- | --------------------------------------------------------------------------------------------------------- |
| PostgreSQL          | `postgres://payload:payload@127.0.0.1:5433/payload`                                                       |
| MongoDB             | `mongodb://payload:payload@localhost:27018/payload?authSource=admin&directConnection=true&replicaSet=rs0` |
| MongoDB Atlas Local | `mongodb://localhost:27019/payload?directConnection=true&replicaSet=mongodb-atlas-local` (no auth)        |

SQLite databases don\u2019t require Docker \u2014 they\u2019re stored as files in the project."""

content = content.replace(old_block, new_block)

with open("CONTRIBUTING.md", "w") as f:
    f.write(content)
PYEOF

# 7. Update generateDatabaseAdapter.ts comment
sed -i 's|Start with: pnpm docker:mongodb-atlas:start|Start with: pnpm docker:start (or --profile mongodb-atlas for just this service)|' test/generateDatabaseAdapter.ts

echo "Patch applied successfully."
