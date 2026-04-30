FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/agent-starter-python && \
    cd /workspace/agent-starter-python && \
    git remote add origin https://github.com/livekit-examples/agent-starter-python.git && \
    git fetch --depth=1 origin cd59007f25bc07e76072cc2a7a173ac855695dfd && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/agent-starter-python
