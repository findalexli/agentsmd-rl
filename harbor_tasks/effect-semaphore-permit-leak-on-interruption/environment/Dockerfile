FROM node:23.7.0-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PNPM_HOME=/usr/local/share/pnpm \
    PATH=/usr/local/share/pnpm:/usr/local/share/pnpm/global/5/node_modules/.bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@10.17.1 --activate

RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pyyaml==6.0.2
ENV PATH=/opt/venv/bin:$PATH

WORKDIR /workspace
RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/Effect-TS/effect.git && \
    git fetch --depth=1 origin 4eb5c008dfc7d2a97b191ca608948d994a2cce4c && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect
RUN pnpm install --frozen-lockfile --prefer-offline

RUN mkdir -p /logs/verifier

CMD ["bash"]
