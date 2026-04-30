FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/super-agent-party && \
    cd /workspace/super-agent-party && \
    git remote add origin https://github.com/heshengtao/super-agent-party.git && \
    git fetch --depth=1 origin e97c06c904096cf2f6a7df3f10a3da718bd0ccb8 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/super-agent-party
