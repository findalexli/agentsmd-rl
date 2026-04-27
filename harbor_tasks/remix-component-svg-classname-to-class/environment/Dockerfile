FROM node:24-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV CI=1
ENV PNPM_HOME=/root/.pnpm
ENV PATH=$PNPM_HOME:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5
ENV PATH=/opt/venv/bin:$PATH

RUN corepack enable && corepack prepare pnpm@10.26.0 --activate

WORKDIR /workspace
RUN git init /workspace/remix && \
    cd /workspace/remix && \
    git remote add origin https://github.com/remix-run/remix.git && \
    git fetch --depth=1 origin 1a2974fa4d1787844cfa6881bb10659f18850675 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/remix

RUN pnpm install --filter "@remix-run/component..." --filter "remix-the-scripts" --frozen-lockfile --ignore-scripts

RUN cd packages/component && pnpm add -D happy-dom@15.11.7

RUN mkdir -p /logs/verifier

CMD ["bash"]
