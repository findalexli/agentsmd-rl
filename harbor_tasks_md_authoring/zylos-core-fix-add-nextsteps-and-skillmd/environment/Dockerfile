FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/zylos-core && \
    cd /workspace/zylos-core && \
    git remote add origin https://github.com/zylos-ai/zylos-core.git && \
    git fetch --depth=1 origin 6378c19ca8eb56e19c3b7166b9f556becdc5d186 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/zylos-core
