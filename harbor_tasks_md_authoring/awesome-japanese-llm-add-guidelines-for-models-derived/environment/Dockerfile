FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/awesome-japanese-llm && \
    cd /workspace/awesome-japanese-llm && \
    git remote add origin https://github.com/llm-jp/awesome-japanese-llm.git && \
    git fetch --depth=1 origin 8b206d167f1c32d76db8c4f7a77c6fc0725bdd5f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/awesome-japanese-llm
