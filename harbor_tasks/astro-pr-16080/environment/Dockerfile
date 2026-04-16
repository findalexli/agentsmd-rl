FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm@9

WORKDIR /workspace

# Clone at base commit (parent of merge)
RUN git clone --filter=blob:none --depth=1 https://github.com/withastro/astro.git
WORKDIR /workspace/astro
RUN git fetch --depth=1 origin 7661f48c84f048dafd26ac58d81acee2462fef4f
RUN git checkout 7661f48c84f048dafd26ac58d81acee2462fef4f

# Build astro package (needed for tests that import from dist/)
RUN pnpm install
RUN pnpm run build --filter=astro

# Verify dist/ exists
RUN ls packages/astro/dist/runtime/server/render/page.js

# Clean up
RUN rm -rf node_modules/.cache
