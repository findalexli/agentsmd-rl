# syntax=docker/dockerfile:1.4
FROM node:20-bullseye-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv \
        git make ca-certificates curl patch \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.7

# yarn 1.22.22 ships with node:20-bullseye-slim — no install needed.

WORKDIR /workspace
RUN git init /workspace/pulumi && \
    cd /workspace/pulumi && \
    git remote add origin https://github.com/pulumi/pulumi.git && \
    git fetch --depth=1 origin 002a84f99b15fdfc720b237c04a6509ced970827 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/pulumi/sdk/nodejs

# Install all SDK deps (yarn 1) and compile to bin/.
# bin/ is required because tests/sxs_ts_test/index.ts imports from "../../bin".
RUN yarn install --frozen-lockfile --network-timeout 600000
RUN yarn run tsc
# Mirror the parts of `make build_package` needed for downstream typechecking:
# bin/log/*.d.ts and friends reference ../proto/* so bin/proto/ must be populated.
RUN mkdir -p bin/proto && cp -R proto/. bin/proto/

# Pre-warm tests/sxs_ts_test/node_modules with typescript@^6 + @pulumi/pulumi@latest
# so that the test (run after the agent applies the fix) does not need network.
# We materialize a temporary package.json mirroring the fix's package^6.json,
# install, then remove it so the base-commit state is preserved (no leakage of the fix).
WORKDIR /workspace/pulumi/sdk/nodejs/tests/sxs_ts_test
RUN cat > package.json <<'JSON'
{
    "name": "sxs",
    "version": "0.0.1",
    "license": "Apache-2.0",
    "dependencies": {
        "@pulumi/pulumi": "latest",
        "typescript": "^6"
    },
    "devDependencies": {
        "@types/node": "^18.0.0"
    }
}
JSON
RUN yarn install --network-timeout 600000 \
    && rm -f package.json \
    && rm -f yarn.lock

# Sanity check: the @pulumi/pulumi package and typescript binary are in place.
RUN test -d node_modules/@pulumi/pulumi && test -x node_modules/.bin/tsc

# Verify the local SDK was compiled.
RUN test -f /workspace/pulumi/sdk/nodejs/bin/index.d.ts

WORKDIR /workspace/pulumi/sdk/nodejs

RUN mkdir -p /logs/verifier
