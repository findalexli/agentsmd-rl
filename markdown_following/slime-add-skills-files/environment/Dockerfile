FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pytest==8.3.4 pytest-json-ctrf==0.4.1 PyYAML==6.0.2

WORKDIR /workspace

RUN git init /workspace/slime && \
    cd /workspace/slime && \
    git remote add origin https://github.com/THUDM/slime.git && \
    git fetch --depth=1 origin 6a3bb90e3210171e27ab7d799c8c2888e7465a1f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slime
