FROM node:22.11.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4

RUN npm install -g pnpm@10.17.1

WORKDIR /workspace

RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/effect-ts/effect.git && \
    git fetch --depth=1 origin ab3b64c20a039eb4d573fe757c41278925b22687 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect

RUN pnpm install --frozen-lockfile --ignore-scripts

RUN mkdir -p /logs/verifier
