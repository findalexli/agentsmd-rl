FROM node:22.12.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates curl python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0
ENV PATH="/opt/venv/bin:${PATH}"

RUN npm install -g pnpm@10.17.1 tsx@4.19.4

ARG REPO_URL=https://github.com/Effect-TS/effect.git
ARG BASE_COMMIT=82996bce8debffcb44feb98bb862cf2662bd56b7

WORKDIR /workspace
RUN git init effect \
    && cd effect \
    && git remote add origin ${REPO_URL} \
    && git -c protocol.version=2 fetch --depth=1 --filter=blob:none origin ${BASE_COMMIT} \
    && git checkout FETCH_HEAD

WORKDIR /workspace/effect

ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH="${PNPM_HOME}:${PATH}"

RUN pnpm config set side-effects-cache false \
    && pnpm install --filter "@effect/ai..." --frozen-lockfile --ignore-scripts

RUN mkdir -p /logs/verifier

CMD ["bash"]
