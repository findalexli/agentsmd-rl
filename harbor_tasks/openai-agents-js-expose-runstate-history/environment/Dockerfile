FROM node:22-slim

RUN corepack enable && corepack prepare pnpm@10.13.1 --activate
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*
RUN pip3 install pytest==8.3.4 --break-system-packages

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openai-agents-js

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /tmp/repo && \
    cd /tmp/repo && \
    git checkout 72cef622c6265dffcb51b1c54cb97121ec4c504c && \
    cp -r . /workspace/openai-agents-js/ && \
    rm -rf /tmp/repo

RUN pnpm install
RUN pnpm -F agents-core build
