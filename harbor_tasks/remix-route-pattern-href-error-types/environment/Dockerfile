FROM node:24.2.0-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV CI=true

RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.* \
        ca-certificates \
        python3=3.11.* \
        python3-pip=23.0.* \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir pytest==8.3.4 pytest-json-ctrf==0.4.1

RUN npm install -g pnpm@10.26.0

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/remix-run/remix.git remix \
    && cd remix \
    && git checkout 96c3f0c095dc8de98543af55df0b9400656f961b

WORKDIR /workspace/remix

RUN pnpm install --frozen-lockfile --ignore-scripts

RUN mkdir -p /logs/verifier

ENV NODE_OPTIONS="--disable-warning=ExperimentalWarning"
