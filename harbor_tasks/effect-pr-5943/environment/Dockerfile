FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git curl patch \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm@10.17.1

WORKDIR /workspace

# Clone with filter for shallow clone
RUN git clone --filter=blob:none --depth=500 https://github.com/effect-ts/effect.git effect-checkout

WORKDIR /workspace/effect-checkout
RUN git fetch origin e88f289c1d9fd4ec584ee793c264597aa84c9352 --depth=1
RUN git checkout e88f289c1d9fd4ec584ee793c264597aa84c9352

# Remove inaccessible pkg.pr.new dependency before install
RUN sed -i '/"@effect\/docgen": "https:\/\/pkg.pr.new/d' package.json

# Install deps
RUN pnpm install --frozen-lockfile --ignore-scripts || pnpm install --ignore-scripts

# Build only what's needed for type-checking
RUN pnpm build 2>&1 | tail -5 || true

RUN mkdir -p /logs/verifier

WORKDIR /workspace/effect-checkout