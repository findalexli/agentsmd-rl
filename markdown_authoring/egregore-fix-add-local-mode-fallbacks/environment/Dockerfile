FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/egregore && \
    cd /workspace/egregore && \
    git remote add origin https://github.com/egregore-labs/egregore.git && \
    git fetch --depth=1 origin 22ea4dfc555c6bd0bf523e81bc133230d9a372ce && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/egregore
