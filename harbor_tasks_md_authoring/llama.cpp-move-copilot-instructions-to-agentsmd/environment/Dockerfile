FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/llama.cpp && \
    cd /workspace/llama.cpp && \
    git remote add origin https://github.com/ggml-org/llama.cpp.git && \
    git fetch --depth=1 origin fd05c51cec7e233bddf2d2bae85ddf8aa6b0226c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/llama.cpp
