FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/webmcp-tools && \
    cd /workspace/webmcp-tools && \
    git remote add origin https://github.com/GoogleChromeLabs/webmcp-tools.git && \
    git fetch --depth=1 origin 014a72d860ec523de79ba6de8531dc2421f4b173 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/webmcp-tools
