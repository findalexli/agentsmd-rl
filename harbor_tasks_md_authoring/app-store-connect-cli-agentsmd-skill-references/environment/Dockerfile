FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/app-store-connect-cli && \
    cd /workspace/app-store-connect-cli && \
    git remote add origin https://github.com/rorkai/App-Store-Connect-CLI.git && \
    git fetch --depth=1 origin 9fa3608ed6a60667b45bc43333ce67c9300e23c3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/app-store-connect-cli
