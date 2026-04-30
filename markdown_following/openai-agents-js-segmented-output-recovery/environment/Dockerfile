FROM node:22.12.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      git \
      ca-certificates \
      python3 \
      python3-pip \
      python3-venv \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/pyenv \
    && /opt/pyenv/bin/pip install --no-cache-dir \
       pytest==8.3.4 \
       pytest-json-report==1.5.0
ENV PATH=/opt/pyenv/bin:$PATH

RUN npm install -g pnpm@10.32.1

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git openai-agents-js
WORKDIR /workspace/openai-agents-js
RUN git checkout 4f1824fa1c63c8f7d84dc1a614a77fbd85fbd298

ENV CI=1
ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH=$PNPM_HOME:$PATH

RUN pnpm install

RUN CI=1 pnpm build:ci

RUN mkdir -p /logs/verifier

CMD ["bash"]
