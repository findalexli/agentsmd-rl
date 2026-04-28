FROM node:22-slim

RUN corepack enable && corepack prepare pnpm@10.28.0 --activate

RUN apt-get update && apt-get install -y git python3 python3-pip --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/openai-agents-js

RUN git config --global http.sslVerify false && \
    git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js && \
    git checkout 98e47658f70f3ba60dcb37cff3e36b7c4a41e302

RUN pnpm install --frozen-lockfile

RUN pnpm build

RUN mkdir -p /logs/verifier

RUN pip3 install pytest==8.3.4 --break-system-packages --quiet
