FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone next.js at the base commit (before the fix)
RUN git init /workspace/next.js && \
    cd /workspace/next.js && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin e6bf5f69a23e6b8681dbc9cb59e7c1cdbe3b9b3c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js

# Install create-next-app deps in isolation (root package.json has workspace:* refs npm can't parse)
RUN mkdir /tmp/cna-deps && cp packages/create-next-app/package.json /tmp/cna-deps/ \
    && cd /tmp/cna-deps && npm install --ignore-scripts 2>/dev/null \
    && npm install "typescript@~5.7" 2>/dev/null \
    && cp -r /tmp/cna-deps/node_modules /workspace/next.js/packages/create-next-app/node_modules \
    && rm -rf /tmp/cna-deps

# Install workspace dep not in CNA's package.json but imported by templates/index.ts
RUN mkdir /tmp/sema && cd /tmp/sema && npm init -y >/dev/null 2>&1 \
    && npm install async-sema 2>/dev/null \
    && cp -r node_modules/async-sema /workspace/next.js/packages/create-next-app/node_modules/ \
    && rm -rf /tmp/sema

# Install tsx, ncc, and typescript globally (ncc needs TS compiler at build time)
RUN npm install -g tsx @vercel/ncc typescript

# Configure git
RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test"

ENV NODE_OPTIONS="--max-old-space-size=4096"