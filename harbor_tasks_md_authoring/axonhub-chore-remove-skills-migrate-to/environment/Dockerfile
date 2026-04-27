FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/axonhub && \
    cd /workspace/axonhub && \
    git remote add origin https://github.com/looplj/axonhub.git && \
    git fetch --depth=1 origin cae8a908e8837e1181b08b4b9bd4ff43965bf8ce && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/axonhub
