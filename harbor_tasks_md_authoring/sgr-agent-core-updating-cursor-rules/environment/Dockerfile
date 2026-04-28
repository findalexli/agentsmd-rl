FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/sgr-agent-core && \
    cd /workspace/sgr-agent-core && \
    git remote add origin https://github.com/vamplabAI/sgr-agent-core.git && \
    git fetch --depth=1 origin 582c14e086ed8e0f8d254f9d284dcc74c98b843e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sgr-agent-core
