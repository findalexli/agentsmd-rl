FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update &&     apt-get install -y --no-install-recommends         git curl ca-certificates build-essential tmux &&     rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo — use blob filter)
RUN git init /workspace/beam && \
    cd /workspace/beam && \
    git remote add origin https://github.com/apache/beam.git && \
    git fetch --depth=1 origin 8044fcb3e6e394db4be60a7883eb9572ebd41eac && \
    git checkout FETCH_HEAD     git config user.email "agent@test" &&     git config user.name "Agent"

WORKDIR /workspace/beam

# Install beam Python SDK (editable so agent changes take effect)
# plus the specific GCP package needed by the module under test
RUN pip install --no-cache-dir     -e "sdks/python/"     google-cloud-recommendations-ai     cachetools     mock     pytest     pytest-json-ctrf

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
