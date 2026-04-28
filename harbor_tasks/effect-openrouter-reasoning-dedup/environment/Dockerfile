FROM node:23.7.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@10.17.1 --activate

RUN python3 -m venv /opt/pyvenv && \
    /opt/pyvenv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1
ENV PATH="/opt/pyvenv/bin:${PATH}"

WORKDIR /workspace
RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/Effect-TS/effect.git && \
    git fetch --depth=1 origin 52cd53115fe14e2b9c36dd0d51eb490aead74ee6 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect
ENV CI=true
RUN pnpm install --frozen-lockfile

# Test instrumentation: expose `makeStreamResponse` so unit tests can drive it.
# This patch is independent of the bug fix region (line ~713 vs ~796-830).
RUN sed -i 's/^const makeStreamResponse:/export const makeStreamResponse:/' \
    packages/ai/openrouter/src/OpenRouterLanguageModel.ts && \
    grep -q '^export const makeStreamResponse:' packages/ai/openrouter/src/OpenRouterLanguageModel.ts

RUN mkdir -p /logs/verifier

CMD ["bash"]
