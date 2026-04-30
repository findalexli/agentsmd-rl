FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/llamafactory && \
    cd /workspace/llamafactory && \
    git remote add origin https://github.com/hiyouga/LlamaFactory.git && \
    git fetch --depth=1 origin a754604c1117592f948536a03f217e697ecc3c0c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/llamafactory
