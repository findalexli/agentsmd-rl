FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/spawn && \
    cd /workspace/spawn && \
    git remote add origin https://github.com/OpenRouterTeam/spawn.git && \
    git fetch --depth=1 origin ac5ef953f978f37fccfc37ffc96b20b1e7886a73 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/spawn
