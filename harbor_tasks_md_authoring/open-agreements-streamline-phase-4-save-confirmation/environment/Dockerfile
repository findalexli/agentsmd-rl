FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/open-agreements && \
    cd /workspace/open-agreements && \
    git remote add origin https://github.com/open-agreements/open-agreements.git && \
    git fetch --depth=1 origin e09efd30276a52051128256cff6c74f556a06c65 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/open-agreements
