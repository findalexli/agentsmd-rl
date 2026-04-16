FROM node:22-slim

ENV PNPM_VERSION=10.17.1

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g pnpm@${PNPM_VERSION}

# Set up workspace
WORKDIR /workspace

# Clone the repo at the base commit
RUN git clone --filter=blob:none --depth=50 https://github.com/Effect-TS/effect.git \
    && cd effect \
    && git checkout 7b8165f45779380fea8ac8e09badef898b63eb41

# Remove the unavailable pkg.pr.new dependency and delete lockfile to reinstall fresh
RUN rm /workspace/effect/pnpm-lock.yaml

# Fix package.json using python3 to properly manipulate JSON
RUN python3 << 'EOF'
import json

with open('/workspace/effect/package.json', 'r') as f:
    pkg = json.load(f)

# Fix @effect/docgen version
if '@effect/docgen' in pkg.get('devDependencies', {}):
    pkg['devDependencies']['@effect/docgen'] = '^0.3.0'

# Remove the problematic patch entry
if 'pnpm' in pkg and 'patchedDependencies' in pkg['pnpm']:
    pkg['pnpm']['patchedDependencies'].pop('@changesets/get-github-info@0.6.0', None)

with open('/workspace/effect/package.json', 'w') as f:
    json.dump(pkg, f, indent=2)
    f.write('\n')
EOF

# Install dependencies for the effect monorepo
WORKDIR /workspace/effect
RUN pnpm install

# Create logs directory
RUN mkdir -p /logs/verifier
