FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/aiida-core && \
    cd /workspace/aiida-core && \
    git remote add origin https://github.com/aiidateam/aiida-core.git && \
    git fetch --depth=1 origin 5974f8b7472b8784ee66f71a1899e9ff11e9061a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/aiida-core
