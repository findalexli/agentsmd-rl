FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --break-system-packages pytest==8.3.4

WORKDIR /workspace

RUN git clone --filter=blob:none --depth=1 https://github.com/mantinedev/mantine.git mantine_repo

WORKDIR /workspace/mantine_repo

RUN git fetch --filter=blob:none origin a6f627b6cfc877eaddd0a95d8245cbd0f7c97f1b && git checkout a6f627b6cfc877eaddd0a95d8245cbd0f7c97f1b

RUN corepack enable && corepack prepare yarn@4.10.3 --activate && yarn install --no-immutable

RUN mkdir -p /logs/verifier

COPY test.sh /tests/test.sh