FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm

WORKDIR /workspace

# Clone at merge commit, then checkout to base (parent) for unfixed state
RUN git init astro && cd astro && \
    git remote add origin https://github.com/withastro/astro.git && \
    git fetch --depth=10000 origin 47a394d7cf2eb735fcee8e90830737f9e900a274 && \
    git checkout FETCH_HEAD && \
    git checkout HEAD~1

WORKDIR /workspace/astro

# Install dependencies
RUN pnpm install

RUN python3 -m pip install pytest --break-system-packages

RUN mkdir -p /logs/verifier