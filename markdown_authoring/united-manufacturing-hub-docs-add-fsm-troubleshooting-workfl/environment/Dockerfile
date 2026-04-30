FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/united-manufacturing-hub && \
    cd /workspace/united-manufacturing-hub && \
    git remote add origin https://github.com/united-manufacturing-hub/united-manufacturing-hub.git && \
    git fetch --depth=1 origin 761887ab179b84ddacc017b2247ba593568723bc && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/united-manufacturing-hub
