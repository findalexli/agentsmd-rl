FROM node:23.7.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@10.17.1 --activate

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir pytest==8.3.4 pytest-json-ctrf==0.4.1

ENV REPO_URL=https://github.com/Effect-TS/effect.git
ENV BASE_COMMIT=88a5260788d57bb0c31a645fa44b5a68f5c73c38

RUN git clone --filter=blob:none ${REPO_URL} /workspace/effect && \
    cd /workspace/effect && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/effect

ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH="${PNPM_HOME}:${PATH}"

RUN pnpm config set store-dir /root/.pnpm-store && \
    pnpm install --frozen-lockfile --prefer-offline 2>&1 | tail -50

RUN mkdir -p /logs/verifier
