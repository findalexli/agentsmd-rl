FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment for Python packages
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /workspace

RUN git clone --depth=100 https://github.com/continuedev/continue.git continue_dev

WORKDIR /workspace/continue_dev

RUN git fetch --depth=100 origin d10ee679245e4e2337181f69b345f1905c8253c3 && \
    git checkout d10ee679245e4e2337181f69b345f1905c8253c3

WORKDIR /workspace/continue_dev/packages/openai-adapters

RUN npm install && npm run build

RUN mkdir -p /logs/verifier

ENV NODE_ENV=test