FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/safe-wallet-monorepo && \
    cd /workspace/safe-wallet-monorepo && \
    git remote add origin https://github.com/safe-global/safe-wallet-monorepo.git && \
    git fetch --depth=1 origin 32866c2b586d7baf8eb46da4c96765417b7d6427 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/safe-wallet-monorepo
