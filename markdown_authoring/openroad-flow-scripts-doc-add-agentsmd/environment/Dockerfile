FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/openroad-flow-scripts && \
    cd /workspace/openroad-flow-scripts && \
    git remote add origin https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts.git && \
    git fetch --depth=1 origin 6cc99179b5f852b45686cf204ada7e4062b9b05a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openroad-flow-scripts
