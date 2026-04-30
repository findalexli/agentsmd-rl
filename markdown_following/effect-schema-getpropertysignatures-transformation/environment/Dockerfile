FROM node:22.11.0-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH=$PNPM_HOME:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.39.5-0+deb12u2 \
    ca-certificates \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/pyvenv \
    && /opt/pyvenv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        pytest-json-ctrf==0.4.1
ENV PATH=/opt/pyvenv/bin:$PATH

RUN npm install -g pnpm@10.17.1

WORKDIR /workspace

RUN git init effect \
    && cd effect \
    && git remote add origin https://github.com/Effect-TS/effect.git \
    && git fetch --depth 1 origin ab3b64c20a039eb4d573fe757c41278925b22687 \
    && git checkout FETCH_HEAD

WORKDIR /workspace/effect

RUN pnpm install --frozen-lockfile --filter "effect..." --filter "@effect/vitest..."

RUN mkdir -p /logs/verifier
