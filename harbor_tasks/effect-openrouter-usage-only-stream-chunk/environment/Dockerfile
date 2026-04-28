FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

RUN npm install -g pnpm@10.17.1 tsx

WORKDIR /workspace

RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/Effect-TS/effect.git && \
    git fetch --depth=1 origin fc82e81448bd9136a37580139ce46a2c61b11b54 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect

RUN pnpm install --frozen-lockfile --ignore-scripts --filter='@effect/ai-openrouter...'

RUN mkdir -p /logs/verifier
