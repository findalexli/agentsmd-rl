FROM oven/bun:1.3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        git \
        ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git opencode \
 && cd opencode \
 && git fetch --depth=1 origin 5181f9b4e141fc6c0c3c3d26169721af9e63ca51 \
 && git checkout 5181f9b4e141fc6c0c3c3d26169721af9e63ca51

WORKDIR /test-sandbox
RUN printf '%s\n' \
    '{' \
    '  "name": "test-sandbox",' \
    '  "type": "module",' \
    '  "dependencies": {' \
    '    "effect": "4.0.0-beta.48",' \
    '    "zod": "4.1.8"' \
    '  }' \
    '}' > package.json \
 && bun install --ignore-scripts \
 && rm -rf /root/.bun/install/cache 2>/dev/null || true

# Make `effect` and `zod` resolvable from inside the cloned opencode tree so
# that bun's module resolver finds them when the new config/layout.ts and
# config/server.ts modules `import { Schema } from "effect"`.
RUN mkdir -p /workspace/opencode/node_modules \
 && ln -sf /test-sandbox/node_modules/effect /workspace/opencode/node_modules/effect \
 && ln -sf /test-sandbox/node_modules/zod /workspace/opencode/node_modules/zod

COPY validate_schemas.ts /test-sandbox/validate_schemas.ts
COPY smoke.test.ts /test-sandbox/smoke.test.ts

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
