FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "bench@test" && \
    git config --global user.name "Bench"

ARG REPO=astral-sh/uv
ARG COMMIT=635a76cad321b1fe3593a71dc7533cabbca244aa

RUN git clone --filter=blob:none https://github.com/${REPO}.git /repo && \
    cd /repo && git checkout ${COMMIT}

RUN mkdir -p /logs/verifier

WORKDIR /repo

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff validate-pyproject 2>/dev/null || pip install --no-cache-dir ruff validate-pyproject
