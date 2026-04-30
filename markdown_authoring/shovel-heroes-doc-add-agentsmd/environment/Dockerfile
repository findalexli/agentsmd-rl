FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/shovel-heroes && \
    cd /workspace/shovel-heroes && \
    git remote add origin https://github.com/shovel-heroes-org/shovel-heroes.git && \
    git fetch --depth=1 origin 0216127f224f491eaafb099cb0e0b720ea82acfd && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/shovel-heroes
