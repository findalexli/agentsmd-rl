FROM node:24-slim

RUN corepack enable

RUN apt-get update && apt-get install -y git python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install pytest==8.3.4

RUN git clone --filter=blob:none https://github.com/remix-run/remix.git /workspace/remix && \
    cd /workspace/remix && \
    git checkout 0d96010ac7180893364f308a1b1f7768eed09458

WORKDIR /workspace/remix
RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier
