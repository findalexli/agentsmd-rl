FROM node:22.13.1-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PNPM_HOME="/root/.local/share/pnpm"
ENV PATH="/root/.local/share/pnpm:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir pytest==8.3.4

RUN npm install -g pnpm@10.13.1

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git openai-agents-js \
 && cd openai-agents-js \
 && git checkout f825f71f7e3c799e6f67b8782b2b3db82cd6a099

WORKDIR /workspace/openai-agents-js

RUN pnpm install --frozen-lockfile --ignore-scripts \
 && pnpm -F @openai/agents-core run prebuild \
 && pnpm build

RUN mkdir -p /logs/verifier

CMD ["bash"]
