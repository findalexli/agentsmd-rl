FROM node:22-slim

RUN apt-get update && apt-get install -y git python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/mantine

RUN git clone --depth=500 https://github.com/mantinedev/mantine.git . && \
    git checkout 50526dd9df22b8d51f9890d92604a7b53ee85dc1 && \
    rm -rf .git

RUN corepack enable && yarn install

RUN pip3 install --break-system-packages pytest==8.3.4

RUN mkdir -p /logs/verifier
