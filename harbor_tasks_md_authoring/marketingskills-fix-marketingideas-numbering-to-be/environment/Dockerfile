FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/marketingskills && \
    cd /workspace/marketingskills && \
    git remote add origin https://github.com/coreyhaines31/marketingskills.git && \
    git fetch --depth=1 origin a83ca6953b1278e1e65befc3f9c4da9fcc0c5a35 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/marketingskills
