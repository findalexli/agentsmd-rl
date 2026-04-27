FROM node:22.12-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        curl \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        pyyaml==6.0.2
ENV PATH=/opt/venv/bin:$PATH

RUN npm install -g corepack@0.34.0 \
    && corepack enable \
    && corepack prepare pnpm@10.15.1 --activate

WORKDIR /workspace

ARG REPO_URL=https://github.com/prisma/prisma.git
ARG BASE_COMMIT=658697212823ac3aae4b84c206ec091106eda1ae

RUN git clone --filter=blob:none ${REPO_URL} prisma \
    && cd prisma \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/prisma

RUN touch .db.env

RUN pnpm install --frozen-lockfile

RUN pnpm -r --filter "@prisma/param-graph..." \
            --filter "@prisma/param-graph-builder..." \
            --filter "@prisma/client-engine-runtime..." \
            --filter "@prisma/json-protocol..." \
            --filter "@prisma/client-common..." \
            --filter "@prisma/client-generator-js..." \
            --filter "@prisma/get-platform..." \
        run dev

RUN mkdir -p /logs/verifier

CMD ["bash"]
