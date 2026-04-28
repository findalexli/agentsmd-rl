FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/relay && \
    cd /workspace/relay && \
    git remote add origin https://github.com/AgentWorkforce/relay.git && \
    git fetch --depth=1 origin 1c0c9ad9e4e34f66828cb5271eae72a4bbe892ef && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/relay
