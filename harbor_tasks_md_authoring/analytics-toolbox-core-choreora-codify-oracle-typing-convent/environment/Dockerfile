FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/analytics-toolbox-core && \
    cd /workspace/analytics-toolbox-core && \
    git remote add origin https://github.com/CartoDB/analytics-toolbox-core.git && \
    git fetch --depth=1 origin a09bff4d8327b3c6026d4cad1b2e0e1737347887 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/analytics-toolbox-core
